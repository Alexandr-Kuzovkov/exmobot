#!/usr/bin/env python
# coding=utf-8

from exmo import EXMO

api_key = "K-5141d67a058280ff3d3d850ea229a73dee00ed52"
api_secret = "S-9f38e73e3cd387356a64eae3ad312ec962703ca4"
exmo = EXMO(api_key, api_secret)


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


#print exmo.trades(pairs=['BTS_USD'])


