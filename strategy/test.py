#coding=utf-8


def run(capi, logger):
    #print capi.delete_orders(['BTC_USD'])
    #print action.delete_orders_for_pair('ETH_USD')
    #print capi.get_orders_balance()

    '''
    user_info = exmo.user_info()
    eth_amount = user_info['balances']['ETH']

    price =11.29897
    pair = 'ETH_USD'
    order_type = 'sell'
    quantity = eth_amount

    print exmo.order_create(pair=pair, price=price, order_type= order_type, quantity=eth_amount)

    '''

    #print capi.get_user_orders()
    #print capi.get_ticker()
    #print capi.user_trades(['BTC_USD'])
    #print capi.user_cancelled_orders(100000, 1000)
    print capi.order_trades(48266008)
    #print capi.required_amount('BTC_USD', 1)


