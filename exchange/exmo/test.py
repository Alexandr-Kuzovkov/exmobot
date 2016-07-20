# coding=utf-8

from exchange.exmo.api import API
from exchange.exmo.common_api import CommonAPI
from logger.logger import Logger
from exchange.exmo.config import *

api = API()
capi = CommonAPI(api)


def test_api():
    #print exmo.trades(['BTC_USD'])
    #print exmo.order_book(['BTC_USD'])
    #print exmo.ticker()
    #print exmo.pair_settings()
    #print exmo.currency()
    #print exmo.user_info()

    '''
    pairs = exmo.pair_settings()['result'].keys()
    pair = 'ETH_USD'
    if pair in pairs:
        print 'pair %s in pairs' % pair
    else:
        print 'pair %s is not in pairs' % pair
    '''

    #print api.user_open_orders()
    #print exmo.user_trades(pairs=['BTC_USD','ETH_USD'])
    #print exmo.user_cancelled_orders(offset=100)
    #print exmo.required_amount('BTC_USD',1)
    #print exmo.wallet_history()






def test_common_api():
    #print action.delete_all_orders()
    #print action.delete_orders_for_pair('ETH_USD')

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
    print capi.get_ticker()