#!/usr/bin/env python

import storage.sqlite.crud as crud



crud = crud.Crud()
crud.insert('session_data', [('key1', 'val1', 'str', 'sess1', 1234567890),('key1', 'val1', 'str', 'sess1', 1234567890),('key1', 'val1', 'str', 'sess1', 1234567890)])
