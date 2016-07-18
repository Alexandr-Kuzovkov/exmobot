# coding=utf-8

import httplib
import urllib
import json
import hashlib
import hmac
import time


class EXMO:
    api_key = ''
    api_secret = ''

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    '''
    Вызов метода API
    '''
    def _exmo_api(self, method, params={}):
        nonce = int(round(time.time() * 1000))
        params["nonce"] = nonce
        params = urllib.urlencode(params)

        H = hmac.new(self.api_secret, digestmod=hashlib.sha512)
        H.update(params)
        sign = H.hexdigest()

        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Key": self.api_key,
                   "Sign": sign}
        conn = httplib.HTTPSConnection("api.exmo.com")
        conn.request("POST", "/v1/" + method, params, headers)
        response = conn.getresponse()
        status = response.status
        reason = response.reason
        res = json.load(response)
        conn.close()
        return {'status': status, 'reson': reason, 'result': res}

    '''
    Вызов метода PUBLIC API
    '''
    def _exmo_public_api(self, method, params={}):
        nonce = int(round(time.time() * 1000))
        params["nonce"] = nonce
        params = urllib.urlencode(params)

        headers = {"Content-type": "application/x-www-form-urlencoded"}
        conn = httplib.HTTPSConnection("api.exmo.com")
        conn.request("POST", "/v1/" + method, params, headers)
        response = conn.getresponse()
        status = response.status
        reason = response.reason
        res = json.load(response)
        conn.close()
        return {'status': status, 'reson': reason, 'result': res}


    #PUBLIC API
    '''
    Список сделок по валютной паре
    Наименование метода:	trades
    pair - одна или несколько валютных пар разделенных запятой (пример BTC_USD,BTC_EUR)
    Пример использования:	https://api.exmo.com/v1/trades/?pair=BTC_USD
    Возращаемое значение:
    {
      "BTC_USD": [
        {
          "trade_id": 3,
          "type": "sell",
          "price": "100",
          "quantity": "1",
          "amount": "100",
          "date": 1435488248
        }
      ]
    }
    Описание полей:
    trade_id - идентификатор сделки
    type - тип сделки
    price - цена сделки
    quantity - кол-во по сделке
    amount - сумма сделки
    date - дата и время сделки в формате Unix
    '''
    def trades(self, pairs = ['BTC_USD']):
        return self._exmo_public_api('trades', {'pair': ','.join(pairs)})

    '''
    Книга ордеров по валютной паре
    Наименование метода:	order_book
    Тип запроса:	POST или GET
    Входящие параметры:
    pair - одна или несколько валютных пар разделенных запятой (пример BTC_USD,BTC_EUR)
    limit - кол-во отображаемых позиций (по умолчанию 100, максимум 1000)
    Пример использования:	https://api.exmo.com/v1/order_book/?pair=BTC_USD
    Возращаемое значение:
    {
      "BTC_USD": {
        "ask_quantity": "3",
        "ask_amount": "500",
        "ask_top": "100",
        "bid_quantity": "1",
        "bid_amount": "99",
        "bid_top": "99",
        "ask": [
          [
            100,
            1,
            100
          ],
          [
            200,
            2,
            400
          ]
        ],
        "bid": [
          [
            99,
            1,
            99
          ]
        ]
      }
    }
    Описание полей:
    ask_quantity - объем всех ордеров на продажу
    ask_amount - сумма всех ордеров на продажу
    ask_top - минимальная цена продажи
    bid_quantity - объем всех ордеров на покупку
    bid_amount - сумма всех ордеров на покупку
    bid_top - максимальная цена покупки
    bid - список ордеров на покупку, где каждая строка это цена, количество и сумма
    ask - список ордеров на продажу, где каждая строка это цена, количество и сумма
    '''
    def order_book(self, pairs = ['BTC_USD']):
        return self._exmo_public_api('order_book', {'pair': ','.join(pairs)})

    '''
    Cтатистика цен и объемов торгов по валютным парам
    Наименование метода:	ticker
    Тип запроса:	POST или GET
    Входящие параметры:	Отсутствуют
    Пример использования:	https://api.exmo.com/v1/ticker/
    Возращаемое значение:
    {
      "BTC_USD": {
        "high": 120,
        "low": 100,
        "avg": 110,
        "vol": 1020,
        "vol_curr": 1043420,
        "last_trade": 111,
        "buy_price": 110,
        "sell_price": 111,
        "updated": 1435517311
      }
    }
    Описание полей:
    high - максимальная цена сделки за 24 часа
    low - минимальная цена сделки за 24 часа
    avg - средняя цена сделки за 24 часа
    vol - объем всех сделок за 24 часа
    vol_curr - сумма всех сделок за 24 часа
    last_trade - цена последней сделки
    buy_price - текущая максимальная цена покупки
    sell_price - текущая минимальная цена продажи
    updated - дата и время обновления данных
    '''
    def ticker(self):
        return self._exmo_public_api('ticker')

    '''
    Настройки валютных пар
    Наименование метода:	pair_settings
    Тип запроса:	POST или GET
    Входящие параметры:	Отсутствуют
    Пример использования:	https://api.exmo.com/v1/pair_settings/
    Возращаемое значение:
    {
      "BTC_USD": {
        "min_quantity": 0.01,
        "max_quantity": 1000,
        "min_price": 1,
        "max_price": 2000,
        "max_amount": 100000,
        "min_amount": 1
      }
    }
    Описание полей:
    min_quantity - минимальное кол-во по ордеру
    max_quantity - максимальное кол-во по ордеру
    min_price - минимальная цена по ордеру
    max_price - максимальная цена по ордеру
    min_amount - минимальная сумма по ордеру
    max_amount - максимальная сумма по ордеру
    '''
    def pair_settings(self):
        return self._exmo_public_api('pair_settings')









    '''
    Получение информации об аккаунте пользователя
    Наименование метода:	user_info
    Тип запроса:	POST
    Входящие параметры:	Отсутствуют
    Пример использования:	api_query("user_info", Array());
    Возращаемое значение:
    {
      "uid": 10542,
      "server_date": 1435518576,
      "balances": {
        "BTC": "970.994",
        "USD": "949.47"
      },
      "reserved": {
        "BTC": "3",
        "USD": "0.5"
      }
    }
    Описание полей:
    uid - идентификатор пользоватля
    server_date - дата и время сервера
    balances - доступный баланс пользователя
    reserved - баланс пользователя в ордерах
    '''
    def user_info(self):
        return self._exmo_api('user_info')