# coding: utf-8
# python: 2.7.9
# module: btcelib.py <http://pastebin.com/kABSEyYB>


import errno
import warnings
import time

from zlib import MAX_WBITS as _MAX_WBITS
from Cookie import SimpleCookie
from decimal import Decimal
from hashlib import sha512 as _sha512
from hmac import new as hmacnew
from httplib import HTTPSConnection
from json import loads as jsonloads
from re import search as research
from urllib import urlencode
from zlib import decompress as _zdecompress

from Cookie import CookieError
from httplib import BadStatusLine, HTTPException
from socket import error as SocketError

"""BTC-E Trade API v1 and BTC-E Public API v3

The MIT License (MIT) <http://opensource.org/licenses/MIT>.
Copyright (c) 2014, 2015, 2016, John Saturday <stozher@gmail.com>.

THE BTC-E IS NOT AFFILIATED WITH THIS PROJECT. THIS IS A COMPLETELY
INDEPENDENT IMPLEMENTATION BASED ON THE ONLINE BTC-E API DESCRIPTION:

BTC-E Trade API v1 <https://btc-e.com/tapi/docs>
BTC-E Public API v3 <https://btc-e.com/api/3/docs>

EXAMPLE:
    >>> import btcelib
    >>> from pprint import pprint
    >>> papi = btcelib.PublicAPIv3('btc_usd-ltc_xxx')
    >>> data = papi.call('ticker', ignore_invalid=1)
    >>> pprint(data)
    >>> # The next instance use the same connection...
    >>> apikey = {    # Replace with your API key/secret!
    ...     'Key': 'YOUR-KEY',
    ...     'Secret': 'YOUR-SECRET',
    ...     }
    >>> tapi = btcelib.TradeAPIv1(apikey, compr=True)
    >>> data = tapi.call('TradeHistory', pair='btc_usd', count=2)
    >>> pprint(data)

CLASSES:
    __builtin__.object
        BTCEConnection
            PublicAPIv3
            TradeAPIv1
    exceptions.Exception(exceptions.BaseException)
        APIError
    httplib.HTTPException(exceptions.Exception)
        CloudFlare

class btcelib.BTCEConnection([compr=None[, timeout=60]]):
    BTC-E Public/Trade API persistent HTTPS connection.
    BTCEConnection.jsonrequest(url[, apikey=None[, **params]]):
        Create query to the BTC-E API (JSON response).
    BTCEConnection.apirequest(url[, apikey=None[, **params]]):
        Create query to the BTC-E API (decoded response).
    BTCEConnection.conn - shared connection between class instances
    BTCEConnection.resp - response to the latest connection request

class btcelib.PublicAPIv3([*pairs[, **connkw]]):
    BTC-E Public API v3 (see: online documentation).
    PublicAPIv3.call(method[, **params]):
        Create query to the BTC-E Public API v3.
        method: info | ticker | depth | trades
        params: limit=150 (max: 2000), ignore_invalid=1

class btcelib.TradeAPIv1(apikey[, **connkw]):
    BTC-E Trade API v1 (see: online documentation).
    TradeAPIv1.call(method[, **params]):
        Create query to the BTC-E Trade API v1.
        method: getInfo | Trade | ActiveOrders | OrderInfo |
            CancelOrder | TradeHistory (max: 2000) |
            TransHistory (max: 2000)
        method*: WithdrawCoin | CreateCoupon | RedeemCoupon
        params: param1=value1, param2=value2, ..., paramN=valueN

EXCEPTIONS:
    btcelib.APIError, btcelib.CloudFlare
    also raise: httplib.HTTPException, socket.error

exception btcelib.APIError(exceptions.Exception):
    Raise exception when the BTC-E API returned an error.

exception btcelib.CloudFlare(httplib.HTTPException):
    Raise exception when the CloudFlare returned an error."""

__date__ = "2016-06-26 00:52:33 +0300"
__author__ = """John Saturday <stozher@gmail.com>
BTC: 13buUVsVXG5YwhmP6g6Bgd35WZ7bKjJzwM
LTC: Le3yV8mA3a7TrpQVHzpSSkBmKcd2Vw3NiR"""
__credits__ = "Alan McIntyre <https://github.com/alanmcintyre>"


API_REFRESH = 2            # time [sec]
BTCE_HOST = 'btc-e.nz'    # BTC-E host (SSL)
CF_COOKIE = '__cfduid'     # CloudFlare security

FloatParser = Decimal      # Parser for JSON values
IntegerParser = Decimal    # Parser for JSON values


class APIError(Exception):
    "Raise exception when the BTC-E API returned an error."
    pass

class CloudFlare(HTTPException):
    "Raise exception when the CloudFlare returned an error."
    pass


class BTCEConnection(object):
    """BTC-E Public/Trade API persistent HTTPS connection.
    @cvar conn: shared connection between class instances
    @cvar resp: response to the latest connection request"""
    _headers = {    # common HTTPS headers
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8',
        'Accept-Encoding': 'identity',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        }
    _post_headers = {    # common and POST headers
        'Content-Type': 'application/x-www-form-urlencoded',
        }
    conn = None    # type 'httplib.HTTPSConnection'
    resp = None    # type 'httplib.HTTPResponse'

    @classmethod
    def __init__(cls, compr=None, timeout=60):
        """Initialization of shared HTTPS connection.
        @param compr: HTTPS compression (default: identity)
        @param timeout: connection timeout (max: 60 sec)"""
        if compr is False:
            compr = 'identity'
        elif compr is True:
            compr = 'gzip, deflate'

        if not cls.conn:
            # Create new connection.
            cls.conn = HTTPSConnection(BTCE_HOST, strict=True, timeout=timeout)
            cls._post_headers.update(cls._headers)
        elif timeout != cls.conn.timeout:
            # update: connection timeout
            cls.conn.timeout = timeout
            cls.conn.close()

        if compr and compr != cls._headers['Accept-Encoding']:
            # update: connection compression
            cls._headers['Accept-Encoding'] = compr
            cls._post_headers.update(cls._headers)
            cls.conn.close()

    @classmethod
    def _signature(cls, apikey, msg):
        """Calculation of SHA-512 authentication signature.
        @param apikey: Trade API-Key {'Key': 'KEY', 'Secret': 'SECRET'}
        @param msg: Trade API method and parameters"""
        signature = hmacnew(apikey['Secret'], msg=msg, digestmod=_sha512)
        cls._post_headers['Key'] = apikey['Key']
        cls._post_headers['Sign'] = signature.hexdigest()

    @classmethod
    def _setcookie(cls):
        """Get the CloudFlare cookie and update security.
        @raise RuntimeWarning: where no CloudFlare cookie"""
        cookie_header = cls.resp.getheader('Set-Cookie')
        try:
            cf_cookie = SimpleCookie(cookie_header)[CF_COOKIE]
        except (CookieError, KeyError):
            # warn/failback: use the previous cookie
            if 'Cookie' not in cls._headers.iterkeys():
                warnings.warn("Missing CloudFlare security cookie",
                              category=RuntimeWarning, stacklevel=2)
        else:
            cls._post_headers['Cookie'] = \
                cls._headers['Cookie'] = cf_cookie.OutputString('value')

    @classmethod
    def _decompress(cls, data):
        """Decompress connection response.
        @return: decompressed data <type 'str'>"""
        encoding = cls.resp.getheader('Content-Encoding')
        if encoding == 'gzip':
            data = _zdecompress(data, _MAX_WBITS+16)
        elif encoding == 'deflate':
            data = _zdecompress(data, -_MAX_WBITS)
        # else/failback: the 'identity' encoding
        return data

    @classmethod
    def jsonrequest(cls, url, apikey=None, **params):
        """Create query to the BTC-E API (JSON response).
        @raise httplib.HTTPException, socket.error: connection errors
        @param url: Public/Trade API plain URL without parameters
        @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
        @param **params: Public/Trade API method and/or parameters
        @return: BTC-E API response (JSON data) <type 'str'>"""
        if apikey:
            # args: Trade API
            method = 'POST'
            body = urlencode(params)
            cls._signature(apikey, body)
            headers = cls._post_headers
        else:
            # args: Public API
            method = 'GET'
            if params:
                url = '{}?{}'.format(url, urlencode(params))
            body = None
            headers = cls._headers

        while True:
            try:
                # Make HTTPS request.
                cls.conn.request(method, url, body=body, headers=headers)
                cls.resp = cls.conn.getresponse()
            except HTTPException as error:
                cls.conn.close()
                if not isinstance(error, BadStatusLine):
                    raise
            except SocketError as error:
                cls.conn.close()
                if error.errno != errno.ECONNRESET:
                    raise
            else:
                cls._setcookie()
                break    # Connection succeeded.
        return cls._decompress(cls.resp.read())

    @classmethod
    def apirequest(cls, url, apikey=None, **params):
        """Create query to the BTC-E API (decoded response).
        @raise APIError, CloudFlare: BTC-E and CloudFlare errors
        @param url: Public/Trade API plain URL without parameters
        @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
        @param **params: Public/Trade API method and/or parameters
        @return: BTC-E API response (decoded data) <type 'dict'>"""
        jsondata = cls.jsonrequest(url, apikey, **params)
        try:
            data = jsonloads(jsondata,
                             parse_float=FloatParser,
                             parse_int=IntegerParser)
        except ValueError:
            if cls.resp.status != 200:
                # CloudFlare proxy errors
                raise CloudFlare("{} {}".format(
                    cls.resp.status, cls.resp.reason))
            else:
                # BTC-E API unknown errors
                raise APIError(jsondata)
        else:
            if 'error' in data:
                # BTC-E API standard errors
                raise APIError(data['error'])
        return data


class PublicAPIv3(BTCEConnection):
    "BTC-E Public API v3 <https://btc-e.com/api/3/docs>."
    def __init__(self, *pairs, **connkw):
        """Initialization of the BTC-E Public API v3.
        @param *pairs: [btc_usd[-btc_rur[-...]]] or arguments
        @param **connkw: ... (see: 'BTCEConnection' class)"""
        super(PublicAPIv3, self).__init__(**connkw)
        self.pairs = pairs    # type 'str' (delimiter: '-')

        if not self.pairs:
            # Get all pairs from BTC-E API.
            self.pairs = self.call('info')['pairs'].iterkeys()
        if not isinstance(self.pairs, str):
            self.pairs = '-'.join(self.pairs)

    def call(self, method, **params):
        """Create query to the BTC-E Public API v3.
        @param method: info | ticker | depth | trades
        @param **params: limit=150 (max: 2000), ignore_invalid=1
        @return: ... <type 'dict'> (see: online documentation)"""
        if method == 'info':
            url = '/api/3/{}'.format(method)
        else:    # method: ticker, depth, trades
            if 'pairs' in params:
                url = '/api/3/{}/{}'.format(method, params['pairs'])
            else:
                url = '/api/3/{}/{}'.format(method, self.pairs)
        return self.apirequest(url, **params)


class TradeAPIv1(BTCEConnection):
    "BTC-E Trade API v1 <https://btc-e.com/tapi/docs>."

    __wait_for_nonce = False

    def __init__(self, apikey, **connkw):
        """Initialization of the BTC-E Trade API v1.
        @raise APIError: where no 'invalid nonce' in error
        @param apikey: Trade API Key {'Key': 'KEY', 'Secret': 'SECRET'}
        @param **connkw: ... (see: 'BTCEConnection' class)"""
        super(TradeAPIv1, self).__init__(**connkw)
        self._apikey = apikey    # type 'dict' (keys: 'Key', 'Secret')
        self._nonce = None       # type 'int' (min/max: 1 to 4294967294)

        try:
            # Get nonce value from BTC-E API.
            self.apirequest('/tapi', self._apikey, nonce=None)
        except APIError as error:
            if 'invalid nonce' not in error.message:
                raise
            self._nonce = int(research(r'\d+', error.message).group())

    def _nextnonce(self):
        """Increase the nonce POST parameter.
        @return: next nonce parameter <type 'int'>"""
        self._nonce += 1
        return self._nonce

    def __nonce(self):
        if self.__wait_for_nonce:
            time.sleep(1)
        return str(time.time()).split('.')[0]

    def call(self, method, **params):
        """Create query to the BTC-E Trade API v1.
        @param method: getInfo | Trade | ActiveOrders | OrderInfo |
            CancelOrder | TradeHistory (max: 2000) | TransHistory (max: 2000)
        @param method*: WithdrawCoin | CreateCoupon | RedeemCoupon
        @param **params: param1=value1, param2=value2, ..., paramN=valueN
        @return: ... <type 'dict'> (see: online documentation)"""
        params['method'] = method
        params['nonce'] = self._nextnonce()
        return self.apirequest('/tapi', self._apikey, **params)['return']