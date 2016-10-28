#!/usr/bin/env python

import storage
import SQLite.crud
import MySQL.crud
from pprint import pprint


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

print 'END Testing storage.storage...'
print '-'*80