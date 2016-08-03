#coding=utf-8
import time
import math

'''
Циклический обмен одной валюты на другую
с целью увеличить количество одной из валют,
названной базовой. Базовая определяется параметром
mode.
0 - увеличиваем вторую валюту в паре: покупаем дешевле, продаем дороже
1 - увеличиваем первую валюту в паре: продаем дороже, покупаем дешевле
'''
def run(capi, logger, storage, conf=None, **params):

    #ввод параметров
    #параметры передаваемые при вызове функции имеют приоритет
    #перед параметрами заданными в файле конфигурации

    #с какой валютной парой работаем
    pair = set_param(conf=conf, params=params, key='pair', default_value='BTC_USD')

    #имя стратегии
    name = set_param(conf=conf, params=params, key='name', default_value='FLIP_' + pair)

    #режим обмена
    mode = set_param(conf=conf, params=params, key='mode', default_value=0, param_type='int')

    #минимальный профит при выставлении ордера не по верху стакана
    min_profit = set_param(conf=conf, params=params, key='min_profit', default_value=0.005, param_type='float')

    #id сессии
    session_id = set_param(conf=conf, params=params, key='session_id', default_value='0')

    #лимит использования депозита по второй валюте в паре
    limit = set_param(conf=conf, params=params, key='limit', default_value=1000000000.0, param_type='float')

    #print mode, pair, session_id
    #return

    #префикс для логгера
    prefix = capi.name + ' ' + name

    logger.info('-'*40, prefix)
    logger.info('pair: %s  mode: %i' % (pair, mode), prefix)

    #удаляем неактуальные записи об ордерах
    delete_orders_not_actual(capi, storage, session_id)

    #удаляем ордера по валютной паре, поставленные в своей сессии
    logger.info('Удаляем ордера по %s в сессии %s' % (pair, session_id), prefix)
    delete_own_orders(capi, storage, session_id, pair, logger, prefix)

    #удаляем все ордера по паре
    #capi.orders_cancel([pair])

    #получаем существующие ордера по валютной паре
    orders = capi.orders([pair])
    #print orders

    #получаем лучшие цены покупки и продажи
    ask = orders[pair]['ask'][0][0]
    bid = orders[pair]['bid'][0][0]
    logger.info('pair %s: ask=%f  bid=%f' % (pair, ask, bid), prefix)

    #получаем наличие своих средств
    balance = capi.balance()
    primary_balance = min(balance[pair.split('_')[0]], limit/ask)
    secondary_balance = min(balance[pair.split('_')[1]], limit)

    logger.info('Balance: %s = %f; %s = %f' % (pair.split('_')[0], balance[pair.split('_')[0]], pair.split('_')[1], balance[pair.split('_')[1]]), prefix)
    logger.info('Balance with limit: %s = %f; %s = %f' % (pair.split('_')[0], primary_balance, pair.split('_')[1], secondary_balance), prefix)

    #комиссия
    fee = capi.fee[pair]

    #минимальный шаг
    if 'decimal_places' in capi.pair_settings[pair]:
        min_price_step = 1.0/(10**(capi.pair_settings[pair]['decimal_places']))
    else:
        min_price_step = 0.000001

    #logger.info(min_price_step)

    #минимальный баланс первой валюты в паре для создания ордера
    if 'min_quantity' in capi.pair_settings[pair] and capi.pair_settings[pair]['min_quantity'] != 0:
        min_primary_balance = capi.pair_settings[pair]['min_quantity']
    elif 'min_amount' in capi.pair_settings[pair]:
        min_primary_balance = capi.pair_settings[pair]['min_amount']
    else:
        min_primary_balance = 0.0001

    #минимальный баланс второй валюты в паре для создания ордера
    if 'min_quantity' in capi.pair_settings[pair] and capi.pair_settings[pair]['min_quantity'] != 0:
        min_secondary_balance = capi.pair_settings[pair]['min_quantity'] * ask
    elif 'min_amount' in capi.pair_settings[pair]:
        min_secondary_balance = capi.pair_settings[pair]['min_amount'] * ask
    else:
        min_secondary_balance = 0.0001

    #logger.info(min_primary_balance)
    #logger.info(min_secondary_balance)

    #если наращиваем вторую валюту в паре(игра на повышении)
    if mode == 0:
        #получаем цену предыдущей покупки
        prev_price = storage.load(pair.split('_')[0] + '_buy_price', session_id)
        #logger.info('prev_price=%s' % str(prev_price), prefix)

        #если есть на балансе первая валюта
        if primary_balance > min_primary_balance:
            #новые цены продажи и покупки
            new_ask = ask - min_price_step
            new_bid = bid + min_price_step
            if prev_price is not None:
                #если монеты уже покупались
                #вычисляем профит на основе верхней цены продажи и цены покупки
                profit = new_ask/prev_price*(1-fee)*(1-fee) - 1
                if profit <= min_profit:
                    #если профита нет, то цену ставим побольше (пониже по стакану) но с профитом
                    new_ask = prev_price * (1 + (2*fee + min_profit))
            else:
                #если монеты не покупались
                #вычисляем профит на основе верхней цены и нижней цены
                profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                if profit <= min_profit:
                    #вычисляем цену продажи исходя из текущей цены покупки и небольшого профита
                    new_ask = new_bid * (1 + (2*fee + min_profit))

            #ставим ордер на продажу
            try:
                res = capi.order_create(pair=pair, quantity=primary_balance, price=new_ask, order_type='sell')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "sell": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "sell": %s: price=%f' % (pair, new_ask), prefix)
                    #сохраняем данные по поставленному ордеру
                    storage.order_add(res['order_id'], pair, primary_balance, new_ask, 'sell', session_id)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "sell": %s' % ex.message, prefix)

        else:
            #если первой валюты на балансе нет удаляем цену покупки
            storage.delete(pair.split('_')[0] + '_buy_price', session_id)

        time.sleep(2)

        #если есть на балансе вторая валюта
        if secondary_balance > min_secondary_balance:
            #новые цены продажи и покупки
            new_ask = ask - min_price_step
            new_bid = bid + min_price_step
            #вычисляем профит на основе верхней цены и нижней цены
            profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
            if profit <= min_profit:
                #если профита нет выставляем цену покупки ниже, на основе цены продажи и профита
                new_bid = new_ask * (1 - (2*fee + min_profit))
            #выставляем ордер на покупку и запоминаем цену покупки
            try:
                res = capi.order_create(pair=pair, quantity=secondary_balance/new_bid, price=new_bid, order_type='buy')
                if not res['result']:
                    logger.info('1.Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "buy": %s: price=%f' % (pair, new_bid), prefix)
                    storage.save(pair.split('_')[0] + '_buy_price', new_bid, 'float', session_id)
                    #сохраняем данные по поставленному ордеру
                    storage.order_add(res['order_id'], pair, secondary_balance/new_bid, new_bid, 'buy', session_id)
            except Exception, ex:
                logger.info('2.Ошибка выставления ордера "buy": %s' % ex.message, prefix)

    #если наращиваем первую валюту в паре (игра на понижении)
    elif mode == 1:
         #если есть на балансе вторая валюта
        if secondary_balance > min_secondary_balance:
            #получаем цену предыдущей продажи
            prev_price = storage.load(pair.split('_')[0] + '_sell_price', session_id)
            #logger.info('prev_price=%s' % str(prev_price), prefix)

            #новые цены продажи и покупки
            new_ask = ask - min_price_step
            new_bid = bid + min_price_step

            if prev_price is not None:
                #если монеты уже продавались
                #вычисляем профит на основе верхней цены покупки и цены продажи
                profit = prev_price/new_bid*(1-fee)*(1-fee) - 1
                if profit <= min_profit:
                    #если профита нет, то цену ставим поменьше (пониже по стакану) но с профитом
                    new_bid = prev_price * (1 - (2*fee + min_profit))
            else:
                #если монеты не продавались
                #вычисляем профит на основе верхней цены и нижней цены
                profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                if profit <= min_profit:
                    #вычисляем цену покупки исходя из текущей цены продажи и небольшого профита
                    new_bid = new_ask * (1 - (2*fee + min_profit))

            #выставляем ордер на покупку
            try:
                res = capi.order_create(pair=pair, quantity=secondary_balance/new_bid, price=new_bid, order_type='buy')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "buy": %s: price=%f' % (pair, new_bid), prefix)
                    #сохраняем данные по поставленному ордеру
                    storage.order_add(res['order_id'], pair, secondary_balance/new_bid, new_bid, 'buy', session_id)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "buy": %s' % ex.message, prefix)

        else:
            #если второй валюты на балансе нет, то удаляем цену продажи
            storage.delete(pair.split('_')[0] + '_sell_price', session_id)

        time.sleep(2)

        #если есть на балансе первая валюта
        if primary_balance > min_primary_balance:
            #новые цены продажи и покупки
            new_ask = ask - min_price_step
            new_bid = bid + min_price_step
            #вычисляем профит на основе лучшей цены продажи и покупки
            profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
            if profit <= min_profit:
                #если профита нет выставляем цену продажи выше, на основе цены покупки и профита
                new_ask = new_bid * (1 + (2*fee + min_profit))
            #ставим ордер на продажу и запоминаем цену продажи
            try:
                res = capi.order_create(pair=pair, quantity=primary_balance, price=new_ask, order_type='sell')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "sell": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "sell": %s: price=%f' % (pair, new_ask), prefix)
                    storage.save(pair.split('_')[0] + '_sell_price', new_ask, 'float', session_id)
                    #сохраняем данные по поставленному ордеру
                    storage.order_add(res['order_id'], pair, primary_balance, new_ask, 'sell', session_id)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "sell": %s' % ex.message, prefix)


    else:
        #если неправильно задан mode
        raise Exception('incorrect mode value: expected 0 or 1!')



#---------------------------------------------------------------------------------------------------------------
'''
установка значения параметра
@param conf объект парсера конфиг файла
@param params словарь именованных параметров
@param key имя параметра
@param default_value значение по умолчанию
@param param_type тип
@return значение параметра
'''
def set_param(conf, params, key, default_value, param_type=None):
    if key in params:
        param = params['pair']
    elif conf.has_option('common', key):
        param = conf.get('common', key)
    else:
        param = default_value
    if param_type is not None:
        if param_type == 'int':
            param = int(param)
        elif param_type == 'float':
            param = float(param)
        else:
            param = str(param)
    return param


'''
удаляем неактуальные записи об ордерах в базе данных
@param capi объект CommonAPI
@param storage объект Storage
@param session_id ID сессии
'''
def delete_orders_not_actual(capi, storage, session_id):
    user_orders = capi.user_orders()
    stored_orders = storage.orders(session_id=session_id)
    for stored_order in stored_orders:
        order_exists = False
        for curr_pair, user_orders_for_pair in user_orders.items():
            for user_order_for_pair in user_orders_for_pair:
                if (user_order_for_pair['order_id'] == stored_order['order_id']) and (user_order_for_pair['type'] == stored_order['order_type']):
                    order_exists = True
                    break
        if not order_exists:
            storage.order_delete(pair=stored_order['pair'], order_id=stored_order['order_id'], session_id=session_id)

'''
отменяем ордера поставленные в своей сессии
по заданной валютной паре
@param capi объект CommonAPI
@param storage объект Storage
@param session_id ID сессии
@param pair валютная пара
@param logger объект Logger
@param prefix префикс для логгера
'''
def delete_own_orders(capi, storage, session_id, pair, logger, prefix):
    own_orders = storage.orders(pair, session_id)
    for own_order in own_orders:
        res = capi.order_cancel(own_order['order_id'])
        if res['result']:
            storage.order_delete(own_order['order_id'], pair, session_id)
        else:
            logger.info('Ошибка отмены ордера %i "%s" на паре %s в сессии %s' % (own_order['order_id'], own_order['order_type'], own_order['pair'], own_order['session_id']), prefix)
