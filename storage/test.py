#!/usr/bin/env python

import storage
import SQLite.crud
import MySQL.crud
from pprint import pprint
import time
import os
import sys
abspath = os.path.abspath(__file__)
rootpath = '/'.join(abspath.split('/')[0:len(abspath.split('/'))-2])
sys.path.append(rootpath)
os.chdir(rootpath)
import exchange.poloniex.api as mod_api
import exchange.poloniex.common_api as mod_capi
capi = mod_capi.CommonAPI(mod_api.API())



print '-'*80
print 'BEGIN Testing storage.storage...'

dbases = [SQLite.crud.Crud(), MySQL.crud.Crud()]
for dbase in dbases:
    strg = storage.Storage(dbase, 'sess-test')
    strg.save('key1', 'value1')
    strg.save('key2', 'value2')
    strg.save('key2', 'value3')
    strg.save('key4', 56)
    strg.save('key4', 78)
    pprint(strg.load('key1'))
    pprint(strg.get_utime('key1'))
    pprint(strg.get_utime('key11'))
    pprint(strg.delete('key1'))
    pprint(strg.load('key1'))

    strg.order_add(1727312, 'ETH_USD', 10.5, 12.45, 'sell')
    strg.order_add(1721727, 'BTC_USD', 1.1, 645.45, 'sell')
    strg.order_add(1721728, 'BTC_RUR', 1.1, 645.45, 'sell')

    pprint(strg.order_delete(order_id=1727312))
    pprint(strg.old_orders_delete(int(time.time())-10000))
    pprint(strg.order_add(1721729, 'BTC_LTC', 1.1, 645.45, 'sell'))

    pprint(strg.orders())

    pprint(strg.save_balance('ETH', 0.25))
    pprint(strg.save_balance('ETH', 0.34))

    pprint(strg.delete_old_values(['balance'], time.time()-3000, full=False))
    pprint(strg.get_last_balance('ETH', 3))

    user_trades = capi.user_trades(['ETH_USDT'], limit=10)
    pprint(user_trades)
    strg.save_user_trades(user_trades['USDT_ETH'])




print 'END Testing storage.storage...'
print '-'*80