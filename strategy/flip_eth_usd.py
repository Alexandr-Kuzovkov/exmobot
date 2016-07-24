#coding=utf-8
import time

pair = 'ETH_USD'
name = 'FLIP_ETH_USD'

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
    coin_balance = balance['ETH']
    fiat_balance = balance['USD']
    #print 'usd=%f   eth=%f' % (fiat_balance, coin_balance)
    logger.info(balance, prefix)

    #получаем цену предыдущей покупки coin
    prev_price = storage.load('btc_buy_price')

    #комиссия
    fee = capi.fee['sell']

    #если есть на балансе coin
    if coin_balance > 0:
        #новые цены продажи и покупки
        new_ask = ask - 0.000001
        new_bid = bid + 0.000001
        if prev_price is not None:
            #если монеты уже покупались
            #вычисляем профит на основе верхней цены и цены покупки
            profit = new_ask/prev_price*(1-fee)*(1-fee) - 1
            if profit <= 0:
                #если профита нет, то цену ставим пониже но с профитом
                new_ask = prev_price * (1 + (2*fee + 0.001))
        else:
            #если монеты не покупались
            #вычисляем профит на основе верхней цены и нижней цены
            profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
            if profit <= 0:
                new_ask = None

        #если нужно ставим ордер на продажу
        if new_ask is not None:
            try:
                capi.order_create(pair=pair, quantity=coin_balance, price=new_ask, order_type='sell')
                logger.info('Ордер "sell": %s: price=%f' % (pair, new_ask), prefix)
            except Exception, ex:
                logger.info('Ошибка выставления ордера "sell": %s' % ex.message, prefix)
        else:
            logger.info('Профита для ордера "sell" нет', prefix)

    else:
        #если coin на балансе нет удаляем цену покупки
        storage.delete('btc_buy_price')

    time.sleep(2)

    #если есть на балансе fiat
    if fiat_balance > 0:
        #новые цены продажи и покупки
        new_ask = ask - 0.000001
        new_bid = bid + 0.000001
        #вычисляем профит на основе верхней цены и нижней цены
        profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
        if profit >= 0:
            #если профит есть выставляем ордер на покупку и запоминаем цену покупки
            try:
                capi.order_create(pair=pair, quantity=fiat_balance, price=new_bid, order_type='buy')
                logger.info('Ордер "buy": %s: price=%f' % (pair, new_bid), prefix)
                storage.save('btc_buy_price', new_bid, 'float')
            except Exception, ex:
                logger.info('Ошибка выставления ордера "buy": %s' % ex.message, prefix)
        else:
            logger.info('Профита для ордера "buy" нет', prefix)