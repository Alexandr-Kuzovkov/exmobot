#!/usr/bin/env python

import crud
from pprint import pprint

print '-'*80
print 'BEGIN Testing storage.MySQL.crud...'


crud = crud.Crud('store_test')

crud.query('SELECT * FROM session_data')
crud.insert('session_data', [('key1', 'val1', 'str', 'sess1', 1234567890), ('key1', 'val1', 'str', 'sess1', 1234567890), ('key1', 'val1', 'str', 'sess1', 1234567890)])
crud.insert('session_data2', [('key1', 'val1', 'str', 'sess1', 1234567890), ('key1', 'val1', 'str', 'sess1', 1234567890), ('key1', 'val1', 'str', 'sess1', 1234567890)])
pprint(crud.get('session_data', {'session_id2=': "'sess1'", '`key`=': "'key2'"}))
pprint(crud.get('session_data', {'session_id=': "'sess1'", '`key`=': "'key2'"}))
crud.delete('session_data2')
crud.delete('session_data')

crud.insert('session_data', data=[('key2', 'val1', 'str', 'sess1', 1234567890)])


crud.drop_tables()
crud.create_tables()
crud.insert('session_data', data=[('key2', 'val1', 'str', 'sess1', 1234567890)])
crud.update('session_data2', data={'value': 'val3'}, conditions=[{'session_id=': "'sess1'"}, {'utime=':str(1234567890)}])
crud.update('session_data', data={'value': 'val3'}, conditions=[{'session_id=': "'sess1'"}, {'utime=':str(1234567890)}])



print 'END Testing storage.MySQL.crud...'
print '-'*80