#coding=utf-8
import time
import math

pair = 'BTC_USD'
name = 'FLIP_BTC_USD'

def run(capi, logger, storage):
    #префикс для логгера
    prefix = capi.name + ' ' + name

    #удаляем ордера по валютной паре
    capi.orders_cancel([pair])
    logger.info('Удаляем ордера по %s' % pair)

    #получаем существующие ордера по валютной паре
    orders = capi.orders([pair])
    #print orders

    #получаем лучшие цены покупки и продажи
    ask = orders[pair]['ask'][0][0]
    bid = orders[pair]['bid'][0][0]
    logger.info('ask=%f  bid=%f' % (ask, bid), prefix)

    #получаем наличие своих средств
    balance = capi.balance()
    coin_balance = balance['BTC']
    fiat_balance = balance['USD']
    #print 'usd=%f   eth=%f' % (fiat_balance, coin_balance)
    logger.info('Balance: %s = %f; %s = %f' % (pair.split('_')[0], balance[pair.split('_')[0]], pair.split('_')[1], balance[pair.split('_')[1]]), prefix)

    #получаем цену предыдущей покупки coin
    prev_price = storage.load(pair.split('_')[0] + '_buy_price')
    #logger.info('prev_price=%s' % str(prev_price), prefix)

    #комиссия
    fee = capi.fee['sell']

    #если есть на балансе coin
    if coin_balance > 0:
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
            res = capi.order_create(pair=pair, quantity=coin_balance, price=new_ask, order_type='sell')
            if not res['result']:
                logger.info('Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
            else:
                logger.info('Ордер "sell": %s: price=%f' % (pair, new_ask), prefix)
        except Exception, ex:
            logger.info('Ошибка выставления ордера "sell": %s' % ex.message, prefix)

    else:
        #если coin на балансе нет удаляем цену покупки
        storage.delete(pair.split('_')[0] + '_buy_price')

    time.sleep(2)

    #если есть на балансе fiat
    if fiat_balance > 0:
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
            res = capi.order_create(pair=pair, quantity=(fiat_balance/new_bid), price=new_bid, order_type='buy')
            if not res['result']:
                logger.info('Ошибка выставления ордера "buy": %s' % str(res['error']), prefix)
            else:
                logger.info('Ордер "buy": %s: price=%f' % (pair, new_bid), prefix)
                storage.save(pair.split('_')[0] + '_buy_price', new_bid, 'float')
        except Exception, ex:
            logger.info('Ошибка выставления ордера "buy": %s' % ex.message, prefix)