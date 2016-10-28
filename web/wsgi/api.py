#coding=utf-8
from cgi import parse_qs, escape
# importing pyspatialite
#import sqlite3
import time
import os
import math
import json
from ConfigParser import *

import sys
abspath = os.path.dirname(__file__)
ABSBOTPATH = '/'.join(abspath.split('/')[0:len(abspath.split('/')) - 2])
config_file = ABSBOTPATH + '/web/wsgi/accounts.conf'
sys.path.append(ABSBOTPATH)
os.chdir(ABSBOTPATH)
#storage_type = 'SQLIte'
#session_id = 'test'


def application(environ, start_response):
    status = '200 OK'
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    post = parse_qs(request_body)
    get = parse_qs(environ['QUERY_STRING'])

    #mod_storage = __import__('storage.' + storage_type, globals(), locals(), ['Storage'], -1)
    #storage = mod_storage.Storage(session_id, ABSBOTPATH)

    params = parseRequest(get)
    capi = params['capi']
    method = getattr(capi, params['method'])
    if len(params['params']) == 0:
        result = method()
    else:
        result = callMethod(params)
    response = json.dumps(result)
    response_headers = [('Content-type', 'text/html; charset=utf-8'), ('Access-Control-Allow-Origin', '*')]
    start_response(status, response_headers)
    return [response]

'''
Парсинг GET параметров запроса и возвращение словаря вида:
{'capi': capi, 'method': method, 'params': params}, где
capi - объект CommonAPI, method - имя запрашиваемого метода
params - словарь с параметрами
'''
def parseRequest(get):
    if 'exchange' in get:
        exchange_name = get['exchange'][0]
        mod_api = __import__('exchange.' + exchange_name + '.api', globals(), locals(), ['API'], -1)
        mod_common_api = __import__('exchange.' + exchange_name + '.common_api', globals(), locals(), ['CommonAPI'], -1)
        conf = ConfigParser()
        conf.read(config_file)
        if conf.has_option(exchange_name, 'key'):
            api_key = conf.get(exchange_name, 'key')
        else:
            api_key = None

        if conf.has_option(exchange_name, 'secret'):
            api_secret = conf.get(exchange_name, 'secret')
        else:
            api_secret = None
        api = mod_api.API(api_key, api_secret)
        capi = mod_common_api.CommonAPI(api)
    else:
        capi = None

    if 'method' in get:
        method = get['method'][0]
    else:
        method = None

    if 'storage' in get:
        storage = get['storage'][0]
    else:
        storage = None

    params = {}
    for key, val in get.items():
        if key not in ['exchange', 'method']:
            params[key] = val[0]
    return {'capi': capi, 'method': method, 'params': params}


'''
Возвращает результат вызова метода
объекта CommonAPI с параметрами
'''
def callMethod(params):
    capi = params['capi']
    method = getattr(capi, params['method'])

    if params['method'] == 'balance':
        if 'currency' in params['params']:
            return method(params['params']['currency'])

    return method()
