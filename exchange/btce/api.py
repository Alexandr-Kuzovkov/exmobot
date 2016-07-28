# coding=utf-8

import exchange.btce.btcelib as btcelib
import exchange.btce.config as config

'''
Contents
This api provides access to such information as tickers of currency pairs, active orders on different pairs, the latest trades for each pair etc.

All API requests are made from this address:
https://btc-e.com/api/3/<method name>/<pair listing>

Currency pairs are hyphen-separated (-), e.g.:
https://btc-e.nz/api/3/ticker/btc_usd-btc_rur

You can use as many pairs in the listing as you wish. Duplicates are not allowed. It is also possible to use only one pair:
https://btc-e.nz/api/3/ticker/btc_usd
A set of pairs works with all the methods presented in the public api except info.

All information is cached every 2 seconds, so there's no point in making more frequent requests.
All API responses have the following format JSON.

Important! API will display an error if we disable one of the pairs listed in your request. If you are not going to synchronize the state of pairs using the method info, you need to send the GET-parameter ignore_invalid equal to 1, e.g.:
https://btc-e.nz/api/3/ticker/btc_usd-btc_btc?ignore_invalid=1
Without the parameter ignore_invalid this request would have caused an error because of a non-existent pair.
'''


class API:
    papi = None
    tapi = None

    def __init__(self):
        self.papi = btcelib.PublicAPIv3()
        self.tapi = btcelib.TradeAPIv1(config.apikey, compr=True)


    '''
    Вызов метода PUBLIC API
    '''
    def btce_public_api(self, method, **params):
        return self.papi.call(method, **params)


    '''
    Вызов метода AUTH API
    '''
    def btce_api(self, method, **params):
        return self.tapi.call(method, params)

