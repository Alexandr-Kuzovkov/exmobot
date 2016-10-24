#coding=utf-8
from cgi import parse_qs, escape
# importing pyspatialite
#import sqlite3
import time
import os
import math
import json

import sys
abspath = os.path.dirname(__file__)
absbotpath = '/'.join(abspath.split('/')[0:len(abspath.split('/')) - 2])
sys.path.append(absbotpath)
os.chdir(absbotpath)
#storage_type = 'sqlite'
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

    #print post
    #пример POST параметров: {'par2': ['234'], 'par1': ['value1']}

    #print get
    #пример GET параметров: {'par2': ['123'], 'par1': ['val1']}

    #mod_storage = __import__('storage.' + storage_type, globals(), locals(), ['Storage'], -1)
    #storage = mod_storage.Storage(session_id, absbotpath)

    response = 'Test wsgi! <br>POST: ' + str(post) + '; <br>GET: ' + str(get)
    response += '<br>' + str(parseRequest(get))
    response_headers = [('Content-type', 'text/html; charset=utf-8'), ('Access-Control-Allow-Origin', '*')]
    start_response(status, response_headers)
    return [response]


def parseRequest(get):
    if 'exchange' in get:
        capi_name = get['exchange'][0]
        capi = __import__('exchange.' + capi_name + '.common_api', globals(), locals(), ['CommonAPI'], -1)
    else:
        capi = None

    if 'method' in get:
        method = get['method'][0]
    else:
        method = None

    params = []
    for key, val in get.items():
        if key not in ['exchange', 'method']:
            params.append(val[0])
    return (capi, method, params)
