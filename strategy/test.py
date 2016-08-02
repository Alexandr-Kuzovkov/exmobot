#coding=utf-8
import random
from pprint import pprint


def run(capi, logger, storage, conf=None, **params):
    #print capi.delete_orders(['BTC_USD'])
    #print action.delete_orders_for_pair('ETH_USD')
    #print capi.orders_balance()

    '''
    user_info = exmo.user_info()
    eth_amount = user_info['balances']['ETH']

    price =11.29897
    pair = 'ETH_USD'
    order_type = 'sell'
    quantity = eth_amount

    print exmo.order_create(pair=pair, price=price, order_type= order_type, quantity=eth_amount)

    '''

    #print capi.user_orders()
    #print capi.ticker()
    #print capi.user_trades(['BTC_USD'])
    #print capi.user_cancelled_orders(100000, 1000)
    #print capi.order_trades(48267083)
    #print capi.required_amount('BTC_USD', 1)
    #logger.info(res)
    #print res
    #print capi.
    #print capi.order_trades()
    #storage.save('key1', 'value1')
    #storage.save('key2', 'value1')
    #print storage.load('key2')
    #print storage.get_utime('key2')
    #storage.delete('key2')
    #print capi.balance_full()
    '''
    ids = random.randrange(100000, 200000, 1)
    storage.order_add(ids, 'ETH_USD', 10.5, 12.45, 'sell', '123')
    storage.order_add(ids+1, 'BTC_USD', 1.1, 645.45, 'sell', '123')
    print storage.orders(session_id='123')
    print '-' * 40
    print storage.orders(pair='LTC_USD', session_id='123')
    storage.order_delete(pair='BTC_USD', session_id='123')
    storage.old_orders_delete(utime=1469620306, pair='ETH_USD', session_id='123')
    '''
    #print capi.order_cancel(123)
    #удаляем неактуальные записи об ордерах
    '''
    session_id='123'
    user_orders = capi.user_orders()
    print user_orders
    stored_orders = storage.orders(session_id='123')
    print stored_orders
    for stored_order in stored_orders:
        order_exists = False
        for user_order_for_pair in user_orders[stored_order['pair']]:
            if user_order_for_pair['order_id'] == stored_order['order_id'] and user_order_for_pair['type'] == stored_order['order_type']:
                order_exists = True
        print order_exists
        if not order_exists:
            storage.order_delete(pair=stored_order['pair'], order_id=stored_order['order_id'], session_id=session_id)
    '''

    #pprint(capi.trades(['BTC_USD', 'ETH_USD'], limit=10))
    pprint(capi.orders(['BTC_USD', 'ETH_USD'], limit=5))
    #pprint(capi.ticker())
    #pprint(capi.balance())
    #pprint(capi.user_orders())
    #pprint(capi.order_create(pair='USD_RUR', quantity=1, price=63.25, order_type='buy'))
    #pprint(capi.order_cancel(1166872879))
    #pprint(capi.orders_cancel())
    #pprint(capi.orders_cancel())
    #pprint(capi.required_amount('USD_RUR', 10000))
    #pprint(capi.order_create(pair='ETH_USD', quantity=capi.balance('ETH'), price=11.499, order_type='sell'))
    print capi.balance()

