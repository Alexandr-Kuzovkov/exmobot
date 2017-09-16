#!/usr/bin/env python

from pprint import pprint
import time
import os
import sys
from time import sleep
abspath = os.path.abspath(__file__)
rootpath = '/'.join(abspath.split('/')[0:len(abspath.split('/'))-2])
sys.path.append(rootpath)
os.chdir(rootpath)

import exchange.poloniex.api as poloniex_mod_api
import exchange.poloniex.common_api as poloniex_mod_capi
import exchange.exmo.api as exmo_mod_api
import exchange.exmo.common_api as exmo_mod_capi
import exchange.btce.api as btce_mod_api
import exchange.btce.common_api as btce_mod_capi


poloniex_capi = poloniex_mod_capi.CommonAPI(poloniex_mod_api.API())
exmo_capi = exmo_mod_capi.CommonAPI(exmo_mod_api.API())
btce_capi = btce_mod_capi.CommonAPI(btce_mod_api.API())


print '-'*80
print 'BEGIN Testing exchange...'

#capis = [poloniex_capi, exmo_capi, btce_capi]
capis = [btce_capi]
for capi in capis:
    pair = capi.check_pair('BTC_ETH')
    print 'Testing API %s' % capi.name
    sleep(2)
    print '----trades(["'+pair+'"])----'
    sleep(2)
    pprint(capi.trades([pair]))
    sleep(3)
    print '----orders(["BTC_ETH"])----'
    sleep(2)
    pprint(capi.orders([pair]))
    sleep(3)
    print '----ticker()----'
    sleep(2)
    pprint(capi.ticker())
    sleep(3)
    print '----balance()----'
    sleep(2)
    pprint(capi.balance())
    sleep(3)
    print '----user_orders()----'
    sleep(2)
    pprint(capi.user_orders())
    sleep(3)
    print '----user_trades()----'
    sleep(2)
    pprint(capi.user_trades())
    sleep(3)
    print '----possable_amount("ETH", "BTC", 100)----'
    sleep(2)
    pprint(capi.possable_amount('ETH', 'BTC', 100))

print 'END Testing exchange...'
print '-' * 80