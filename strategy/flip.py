#coding=utf-8
import time
import math

'''
Циклический обмен одной валюты на другую
с целью увеличить количество одной из валют,
названной базовой
'''

def run(capi, logger, storage, conf=None):
    #ввод параметров
    if conf.has_option('common', 'pair'):
        pair = conf.get('common', 'pair')
    else:
        pair = 'BTC_USD'

    if conf.has_option('common', 'name'):
        name = conf.get('common', 'name')
    else:
        name = 'FLIP_' + pair

    if conf.has_option('common', 'mode'):
        mode = int(conf.get('common', 'mode'))
    else:
        mode = 0

    if conf.has_option('common', 'min-profit'):
        min_profit = float(conf.get('common', 'min-profit'))
    else:
        min_profit = 0.005


    #префикс для логгера
    prefix = capi.name + ' ' + name

    logger.info('pair: %s  mode: %i' % (pair, mode), prefix)

    #удаляем ордера по валютной паре
    capi.orders_cancel([pair])
    logger.info('Удаляем ордера по %s' % pair, prefix)

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
    fee = capi.fee['sell']

    #если наращиваем вторую валюту в паре(игра на повышении)
    if mode == 0:
        #получаем цену предыдущей покупки
        prev_price = storage.load(pair.split('_')[0] + '_buy_price')
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
                    new_ask = prev_price * (1 + (2*fee + 0.003))
            else:
                #если монеты не покупались
                #вычисляем профит на основе верхней цены и нижней цены
                profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                if profit <= 0:
                    #вычисляем цену продажи исходя из текущей цены покупки и небольшого профита
                    new_ask = new_bid * (1 + (2*fee + 0.003))

            #ставим ордер на продажу
            try:
                res = capi.order_create(pair=pair, quantity=primary_balance, price=new_ask, order_type='sell')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "sell": %s: price=%f' % (pair, new_ask), prefix)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "sell": %s' % ex.message, prefix)

        else:
            #если первой валюты на балансе нет удаляем цену покупки
            storage.delete(pair.split('_')[0] + '_buy_price')

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
                new_bid = new_ask * (1 - (2*fee + 0.005))
            #выставляем ордер на покупку и запоминаем цену покупки
            try:
                res = capi.order_create(pair=pair, quantity=(secondary_balance/new_bid), price=new_bid, order_type='buy')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "buy": %s: price=%f' % (pair, new_bid), prefix)
                    storage.save(pair.split('_')[0] + '_buy_price', new_bid, 'float')
            except Exception, ex:
                logger.info('Ошибка выставления ордера "buy": %s' % ex.message, prefix)

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
                new_ask = new_bid * (1 + (2*fee + 0.005))
            #ставим ордер на продажу и запоминаем цену продажи
            try:
                res = capi.order_create(pair=pair, quantity=primary_balance, price=new_ask, order_type='sell')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "sell": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "sell": %s: price=%f' % (pair, new_ask), prefix)
                    storage.save(pair.split('_')[0] + '_sell_price', new_ask, 'float')
            except Exception, ex:
                logger.info('Ошибка выставления ордера "sell": %s' % ex.message, prefix)


        time.sleep(2)

        #если есть на балансе вторая валюта
        if secondary_balance > 0:
            #получаем цену предыдущей продажи
            prev_price = storage.load(pair.split('_')[0] + '_sell_price')
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
                    new_bid = prev_price * (1 - (2*fee + 0.003))
            else:
                #если монеты не продавались
                #вычисляем профит на основе верхней цены и нижней цены
                profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                if profit <= 0:
                    #вычисляем цену покупки исходя из текущей цены продажи и небольшого профита
                    new_bid = new_ask * (1 - (2*fee + 0.003))

            #выставляем ордер на покупку
            try:
                res = capi.order_create(pair=pair, quantity=(secondary_balance/new_bid), price=new_bid, order_type='buy')
                if not res['result']:
                    logger.info('Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
                else:
                    logger.info('Ордер "buy": %s: price=%f' % (pair, new_bid), prefix)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "buy": %s' % ex.message, prefix)

        else:
            #если второй валюты на балансе нет, то удаляем цену продажи
            storage.delete(pair.split('_')[0] + '_sell_price')

    else:
        #если неправильно задан mode
        raise Exception('incorrect mode value: expected 0 or 1!')
