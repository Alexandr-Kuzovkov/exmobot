# coding=utf-8

from exchange.exmo.api import EXMO
from exchange.exmo.action import Action
from exchange.exmo.config import *

exmo = EXMO(api_key, api_secret)
action = Action(exmo)


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

    #print exmo.user_open_orders()
    #print exmo.user_trades(pairs=['BTC_USD','ETH_USD'])
    #print exmo.user_cancelled_orders(offset=100)
    #print exmo.required_amount('BTC_USD',1)
    #print exmo.wallet_history()






def test_action():
    print action.delete_all_orders()

    '''
    user_info = exmo.user_info()
    eth_amount = user_info['result']['balances']['ETH']

    price =11.29897
    pair = 'ETH_USD'
    order_type = 'sell'
    quantity = eth_amount

    print exmo.order_create(pair=pair, price=price, order_type= order_type, quantity=eth_amount)

    '''