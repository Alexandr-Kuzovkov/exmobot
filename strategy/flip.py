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
    if 'pair' in params:
        pair = params['pair']
    elif conf.has_option('common', 'pair'):
        pair = conf.get('common', 'pair')
    else:
        pair = 'BTC_USD'

    #имя стратегии
    if 'name' in params:
        name = params['name']
    elif conf.has_option('common', 'name'):
        name = conf.get('common', 'name')
    else:
        name = 'FLIP_' + pair

    #режим обмена
    if 'mode' in params:
        mode = int(params['mode'])
    elif conf.has_option('common', 'mode'):
        mode = int(conf.get('common', 'mode'))
    else:
        mode = 0

    #минимальный профит при выставлении ордера не по верху стакана
    if 'min_profit' in params:
        min_profit = float(params['min_profit'])
    elif conf.has_option('common', 'min_profit'):
        min_profit = float(conf.get('common', 'min_profit'))
    else:
        min_profit = 0.005

    #id сессии
    if 'session_id' in params:
        session_id = params['session_id']
    elif conf.has_option('common', 'session_id'):
        session_id = conf.get('common', 'session_id')
    else:
        session_id = 0

    #лимит использования депозита по второй валюте в паре
    if 'limit' in params:
        limit = float(params['limit'])
    elif conf.has_option('common', 'limit'):
        limit = float(conf.get('common', 'limit'))
    else:
        limit = 1000000000.0


    #print mode, pair, session_id
    #return

    #префикс для логгера
    prefix = capi.name + ' ' + name

    logger.info('-'*40, prefix)
    logger.info('pair: %s  mode: %i' % (pair, mode), prefix)

    #удаляем неактуальные записи об ордерах
    user_orders = capi.user_orders()
    stored_orders = storage.orders(session_id=session_id)
    for stored_order in stored_orders:
        order_exists = False
        for user_order_for_pair in user_orders[stored_order['pair']]:
            if (user_order_for_pair['order_id'] == stored_order['order_id']) and (user_order_for_pair['type'] == stored_order['order_type']):
                order_exists = True
                break
        if not order_exists:
            storage.order_delete(pair=stored_order['pair'], order_id=stored_order['order_id'], session_id=session_id)

    #удаляем ордера по валютной паре, поставленные в своей сессии
    logger.info('Удаляем ордера по %s в сессии %s' % (pair, session_id), prefix)
    own_orders = storage.orders(pair, session_id)
    for own_order in own_orders:
        res = capi.order_cancel(own_order['order_id'])
        if res['result']:
            storage.order_delete(own_order['order_id'], pair, session_id)
        else:
            logger.info('Ошибка отмены ордера %i "%s" на паре %s в сессии %s' % (own_order['order_id'], own_order['order_type'], own_order['pair'], own_order['session_id']), prefix)

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
    primary_balance = balance[pair.split('_')[0]]
    secondary_balance = balance[pair.split('_')[1]]

    #print 'usd=%f   eth=%f' % (fiat_balance, coin_balance)
    logger.info('Balance: %s = %f; %s = %f' % (pair.split('_')[0], balance[pair.split('_')[0]], pair.split('_')[1], balance[pair.split('_')[1]]), prefix)

    #комиссия
    fee = capi.fee[pair]
    logger.info('fee=%f' % fee)

    #если наращиваем вторую валюту в паре(игра на повышении)
    if mode == 0:
        #получаем цену предыдущей покупки
        prev_price = storage.load(pair.split('_')[0] + '_buy_price', session_id)
        #logger.info('prev_price=%s' % str(prev_price), prefix)

        #если есть на балансе первая валюта
        if primary_balance > 0:
            #новые цены продажи и покупки
            new_ask = ask - 0.000001
            new_bid = bid + 0.000001
            if prev_price is not None:
                #если монеты уже покупались
                #вычисляем профит на основе верхней цены продажи и цены покупки
                profit = new_ask/prev_price*(1-fee)*(1-fee) - 1
                if profit <= 0:
                    #если профита нет, то цену ставим побольше (пониже по стакану) но с профитом
                    new_ask = prev_price * (1 + (2*fee + min_profit))
            else:
                #если монеты не покупались
                #вычисляем профит на основе верхней цены и нижней цены
                profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                if profit <= 0:
                    #вычисляем цену продажи исходя из текущей цены покупки и небольшого профита
                    new_ask = new_bid * (1 + (2*fee + min_profit))

            #ставим ордер на продажу
            try:
                quantity = min(limit/new_ask, primary_balance)
                res = capi.order_create(pair=pair, quantity=quantity, price=new_ask, order_type='sell')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "sell": %s: price=%f' % (pair, new_ask), prefix)
                    #сохраняем данные по поставленному ордеру
                    storage.order_add(res['order_id'], pair, quantity, new_ask, 'sell', session_id)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "sell": %s' % ex.message, prefix)

        else:
            #если первой валюты на балансе нет удаляем цену покупки
            storage.delete(pair.split('_')[0] + '_buy_price', session_id)

        time.sleep(2)

        #если есть на балансе вторая валюта
        if secondary_balance > 0:
            #новые цены продажи и покупки
            new_ask = ask - 0.000001
            new_bid = bid + 0.000001
            #вычисляем профит на основе верхней цены и нижней цены
            profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
            if profit <= 0:
                #если профита нет выставляем цену покупки ниже, на основе цены продажи и профита
                new_bid = new_ask * (1 - (2*fee + min_profit))
            #выставляем ордер на покупку и запоминаем цену покупки
            try:
                quantity = min(limit/new_bid, secondary_balance/new_bid)
                res = capi.order_create(pair=pair, quantity=quantity, price=new_bid, order_type='buy')
                if not res['result']:
                    logger.info('1.Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "buy": %s: price=%f' % (pair, new_bid), prefix)
                    storage.save(pair.split('_')[0] + '_buy_price', new_bid, 'float', session_id)
                    #сохраняем данные по поставленному ордеру
                    storage.order_add(res['order_id'], pair, quantity, new_bid, 'buy', session_id)
            except Exception, ex:
                logger.info('2.Ошибка выставления ордера "buy": %s' % ex.message, prefix)

    #если наращиваем первую валюту в паре (игра на понижении)
    elif mode == 1:
        #если есть на балансе первая валюта
        if primary_balance > 0:
            #новые цены продажи и покупки
            new_ask = ask - 0.000001
            new_bid = bid + 0.000001
            #вычисляем профит на основе лучшей цены продажи и покупки
            profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
            if profit <= 0:
                #если профита нет выставляем цену продажи выше, на основе цены покупки и профита
                new_ask = new_bid * (1 + (2*fee + min_profit))
            #ставим ордер на продажу и запоминаем цену продажи
            try:
                quantity = min(primary_balance, limit/new_ask)
                res = capi.order_create(pair=pair, quantity=quantity, price=new_ask, order_type='sell')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "sell": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "sell": %s: price=%f' % (pair, new_ask), prefix)
                    storage.save(pair.split('_')[0] + '_sell_price', new_ask, 'float', session_id)
                    #сохраняем данные по поставленному ордеру
                    storage.order_add(res['order_id'], pair, quantity, new_ask, 'sell', session_id)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "sell": %s' % ex.message, prefix)


        time.sleep(2)

        #если есть на балансе вторая валюта
        if secondary_balance > 0:
            #получаем цену предыдущей продажи
            prev_price = storage.load(pair.split('_')[0] + '_sell_price', session_id)
            #logger.info('prev_price=%s' % str(prev_price), prefix)

            #новые цены продажи и покупки
            new_ask = ask - 0.000001
            new_bid = bid + 0.000001

            if prev_price is not None:
                #если монеты уже продавались
                #вычисляем профит на основе верхней цены покупки и цены продажи
                profit = prev_price/new_bid*(1-fee)*(1-fee) - 1
                if profit <= 0:
                    #если профита нет, то цену ставим поменьше (пониже по стакану) но с профитом
                    new_bid = prev_price * (1 - (2*fee + min_profit))
            else:
                #если монеты не продавались
                #вычисляем профит на основе верхней цены и нижней цены
                profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                if profit <= 0:
                    #вычисляем цену покупки исходя из текущей цены продажи и небольшого профита
                    new_bid = new_ask * (1 - (2*fee + min_profit))

            #выставляем ордер на покупку
            try:
                quantity = min(secondary_balance/new_bid, limit/new_bid)
                res = capi.order_create(pair=pair, quantity=quantity, price=new_bid, order_type='buy')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "buy": %s: price=%f' % (pair, new_bid), prefix)
                    #сохраняем данные по поставленному ордеру
                    storage.order_add(res['order_id'], pair, quantity, new_bid, 'buy', session_id)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "buy": %s' % ex.message, prefix)

        else:
            #если второй валюты на балансе нет, то удаляем цену продажи
            storage.delete(pair.split('_')[0] + '_sell_price', session_id)

    else:
        #если неправильно задан mode
        raise Exception('incorrect mode value: expected 0 or 1!')
