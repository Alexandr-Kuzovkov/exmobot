import httplib
import urllib
import json
import hashlib
import hmac
import time
from re import search as research

class APIError(Exception):
    "Raise exception when the BTC-E API returned an error."
    pass

class PublicAPIv3:
    host = "btc-e.com"
    headers = {}
    conn = None
    req = None

    def __init__(self):
        pass

    def call(self, method, **params):
        if method == 'info':
            url = '/api/3/{}'.format(method)
        else:    # method: ticker, depth, trades
            if 'pairs' in params:
                url = '/api/3/{}/{}'.format(method, params['pairs'])
            else:
                url = '/api/3/{}/{}'.format(method, self.pairs)
        if params:
            url = '{}?{}'.format(url, urllib.urlencode(params))
        body = None
        conn = httplib.HTTPSConnection(self.host)
        conn.request('GET', url, body, self.headers)
        response = conn.getresponse()
        return json.load(response)

class TradeAPIv1:

    host = "btc-e.com"
    _nonce = 0
    apikey = None

    def __init__(self, apikey, compr=False):
        self.apikey = apikey
        # Get nonce value from BTC-E API.
        res = self.call('getInfo')
        if res['success'] == 0:
            if 'invalid nonce' in res['error']:
                self._nonce = int(research(r'\d+', res['error']).group())


    def _nextnonce(self):
        """Increase the nonce POST parameter.
        @return: next nonce parameter <type 'int'>"""
        self._nonce += 1
        return self._nonce

    def call(self, method, **params):
        params['method'] = method
        params["nonce"] = self._nextnonce()
        if params:
            params = urllib.urlencode(params)
        H = hmac.new(self.apikey['Secret'], digestmod=hashlib.sha512)
        H.update(params)
        sign = H.hexdigest()

        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Key": self.apikey['Key'],
                   "Sign": sign}
        conn = httplib.HTTPSConnection(self.host)
        conn.request("POST", "/tapi", params, headers)
        response = conn.getresponse()
        status = response.status
        reason = response.reason
        res = json.load(response)
        conn.close()
        if status == 200:
            if res['success'] == 1:
                return res['return']
            else:
                return res
        else:
            raise Exception(reason)
