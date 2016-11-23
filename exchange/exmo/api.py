# coding=utf-8

import httplib
import urllib
import urllib2
import json
import hashlib
import hmac
import time
import exchange.exmo.config as config
from pprint import pprint


class API:
    api_key = ''
    api_secret = ''
    proxy_address = None
    proxy_account = None
    pairs = []
    host = "http://api.exmo.com"

    def __init__(self, key=None, secret=None, proxy_address=None, proxy_account=None):
        if (key is None) or (secret is None):
            self.api_key = config.api_key
            self.api_secret = config.api_secret
        else:
            self.api_key = key
            self.api_secret = secret
        self.proxy_address = proxy_address
        self.proxy_account = proxy_account

    '''
    Вызов метода AUTH API
    '''
    def exmo_api(self, method, params={}):
        nonce = int(round(time.time() * 1000))
        params["nonce"] = nonce
        params = urllib.urlencode(params)

        H = hmac.new(self.api_secret, digestmod=hashlib.sha512)
        H.update(params)
        sign = H.hexdigest()

        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Key": self.api_key,
                   "Sign": sign}
        url = self.host + "/v1/" + method
        req = urllib2.Request(url)
        for key, val in headers.items():
            req.add_header(key, val)
        req.add_data(params)
        self.add_proxy({'address': self.proxy_address, 'account': self.proxy_account})
        res = urllib2.urlopen(req)
        status = res.getcode()
        reason = res.info()
        response = res.read()
        result = json.loads(response)
        if status == 200:
            return result
        else:
            raise Exception(reason)

    '''
    Вызов метода PUBLIC API
    '''
    def exmo_public_api(self, method, params={}):
        nonce = int(round(time.time() * 1000))
        params["nonce"] = nonce
        params = urllib.urlencode(params)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        url = self.host + "/v1/" + method
        req = urllib2.Request(url)
        for key, val in headers.items():
            req.add_header(key, val)
        req.add_data(params)
        self.add_proxy({'address': self.proxy_address, 'account': self.proxy_account})
        res = urllib2.urlopen(req)
        response = res.read()
        status = res.getcode()
        reason = res.info()
        result = json.loads(response)
        if status == 200:
            return result
        else:
            raise Exception(reason)

    '''
    реализация запроса через прокси
    @param proxy словарь вида {'address': 'protocol://ip_address:port', 'account': 'user:password'}
    '''
    def add_proxy(self, proxy):
        if type(proxy) is not dict:
            raise Exception('proxy parameter type must be dict')
        proxy_address = proxy.get('address', None)
        proxy_account = proxy.get('account', None)
        if proxy_address is None and proxy_account is None:
            return
        protocol = proxy_address.split(':')[0]
        ip_port = proxy_address.split('//')[1]
        if proxy_account is None:
            print str({protocol: ''.join([protocol + '://', ip_port])})
            proxy_handler = urllib2.ProxyHandler({protocol: ''.join([protocol + '://', ip_port])})
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
        else:
            print str({protocol: ''.join([protocol + '://', proxy_account, '@', ip_port])})
            proxy_handler = urllib2.ProxyHandler({protocol: ''.join([protocol + '://', proxy_account, '@', ip_port])})
            proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
            opener = urllib2.build_opener(proxy_handler, proxy_auth_handler, urllib2.HTTPHandler)
        urllib2.install_opener(opener)

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
    def trades(self, pairs=[]):
        self._getCurrencyPairs()
        for pair in pairs:
            if pair not in self.pairs:
                raise Exception('pair expected in ' + str(self.pairs))
        return self.exmo_public_api('trades', {'pair': ','.join(pairs)})

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
    def order_book(self, pairs=[], limit=100):
        self._getCurrencyPairs()
        for pair in pairs:
            if pair not in self.pairs:
                raise Exception('pair expected in ' + str(self.pairs))
        return self.exmo_public_api('order_book', {'pair': ','.join(pairs), 'limit': limit})

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
        return self.exmo_public_api('ticker')

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
        return self.exmo_public_api('pair_settings')

    '''
    Cписок валют биржи
    Наименование метода:	currency
    Тип запроса:	POST или GET
    Входящие параметры:	Отсутствуют
    Пример использования:	https://api.exmo.com/v1/currency/
    Возращаемое значение:
    ["USD","EUR","RUB","BTC","DOGE","LTC"] 
    '''
    def currency(self):
        return self.exmo_public_api('currency')


    #AUTHENTICATED API

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
        return self.exmo_api('user_info')

    '''
    Создание ордера
    Наименование метода:	order_create
    Тип запроса:	POST
    Входящие параметры:
    pair - валютная пара
    quantity - кол-во по ордеру
    price - цена по ордеру
    type - тип ордера, может принимать следующие значения:
    buy - ордер на покупку
    sell - ордер на продажу
    market_buy - ордера на покупку по рынку
    market_sell - ордер на продажу по рынку
    market_buy_total - ордер на покупку по рынку на определенную сумму
    market_sell_total - ордер на продажу по рынку на определенную сумму
    Возращаемое значение:
    {
      "result": true,
      "error": "",
      "order_id": 123456
    }
    Описание полей:
    result - true в случае успешного создания и false в случае ошибки
    error - содержит текст ошибки
    order_id - идентификатор ордера
    '''
    def order_create(self, pair, quantity, price, order_type):
        self._getCurrencyPairs()
        valid_types = ['buy', 'sell', 'market_buy', 'market_sell', 'market_buy_total', 'market_sell_total']
        if pair is None or pair not in self.pairs:
            raise Exception('pair expected in ' + str(self.pairs))
        if quantity is None or quantity <= 0:
            raise Exception('quantity expected!')
        if price is None or price <= 0:
            raise Exception('price expected!')
        if order_type is None or order_type not in valid_types:
            raise Exception('type expected in ' + str(valid_types))
        params = {'pair': pair, 'quantity': quantity, 'price': price, 'type': order_type}
        return self.exmo_api('order_create', params)

    '''
    Отмена ордера
    Наименование метода:	order_cancel
    Тип запроса:	POST
    Входящие параметры:
    order_id - идентификатор ордера
    Пример использования:
    api_query("order_cancel", Array(
        "order_id"=>104235
    ));
    Возращаемое значение:

    {
      "result": true,
      "error": ""
    }
    Описание полей:
    result - true в случае успешного создания задачи на отмену ордера и false в случае ошибки
    error - содержит текст ошибки
    '''
    def order_cancel(self, order_id):
        params = {'order_id': order_id}
        return self.exmo_api('order_cancel', params)

    '''
    Получение списока открытых ордеров пользователя
    Наименование метода:	user_open_orders
    Тип запроса:	POST
    Входящие параметры:	отсутствуют
    Пример использования:
    api_query("user_open_orders", Array());
    Возращаемое значение:

    {
      "BTC_USD": [
        {
          "order_id": "14",
          "created": "1435517311",
          "type": "buy",
          "pair": "BTC_USD",
          "price": "100",
          "quantity": "1",
          "amount": "100"
        }
      ]
    }
    Описание полей:
    order_id - идентификатор ордера
    created - дата и время создания ордера
    type - тип ордера
    pair - валютная пара
    price - цена по ордеру
    quantity - кол-во по ордеру
    amount - сумма по ордеру
    '''
    def user_open_orders(self):
        return self.exmo_api('user_open_orders')

    '''
    Получение сделок пользователя
    Наименование метода:	user_trades
    Тип запроса:	POST
    Входящие параметры:
    pair - одна или несколько валютных пар разделенных запятой (пример BTC_USD,BTC_EUR)
    offset - смещение от последней сделки (по умолчанию 0)
    limit - кол-во возвращаемых сделок (по умолчанию 100, максимум 10 000)
    Пример использования:
    api_query("user_trades", Array(
        "pair"=>"BTC_USD",
        "limit"=>100,
        "offset"=>0
    ));
    Возращаемое значение:

    {
      "BTC_USD": [
        {
          "trade_id": 3,
          "date": 1435488248,
          "type": "buy",
          "pair": "BTC_USD",
          "order_id": 7,
          "quantity": 1,
          "price": 100,
          "amount": 100
        }
      ]
    }
    Описание полей:
    trade_id - идентификатор сделки
    date - дата и время сделки
    type - тип сделки
    pair - валютная пара
    order_id - идентификатор ордера пользователя
    quantity - кол-во по сделке
    price - цена сделки
    amount - сумма сделки
    '''
    def user_trades(self, pairs, offset=0, limit=100):
        self._getCurrencyPairs()
        for pair in pairs:
            if pair not in self.pairs:
                raise Exception('pair expected in ' + str(self.pairs))
        params = {'pair': ','.join(pairs), 'offset': offset, 'limit': limit}
        return self.exmo_api('user_trades', params)

    '''
    Получение отмененных ордеров пользователя
    Наименование метода:	user_cancelled_orders
    Тип запроса:	POST
    Входящие параметры:
    offset - смещение от последней сделки (по умолчанию 0)
    limit - кол-во возвращаемых сделок (по умолчанию 100, максимум 10 000)
    Пример использования:
    api_query("user_cancelled_orders", Array(
        "limit"=>100,
        "offset"=>0
    ));
    Возращаемое значение:
    [
      {
        "date": 1435519742,
        "order_id": 15,
        "order_type": "sell",
        "pair": "BTC_USD",
        "price": 100,
        "quantity": 3,
        "amount": 300
      }
    ]
    Описание полей:
    date - дата и время отмены ордера
    order_id - идентификатор ордера
    order_type - тип ордера
    pair - валютная пара
    price - цена по ордеру
    quantity - кол-во по ордеру
    amount - сумма по ордеру
    '''
    def user_cancelled_orders(self, offset=0, limit=0):
        params = {'offset': offset, 'limit': limit}
        return self.exmo_api('user_cancelled_orders', params)


    '''
    Получение истории сделок ордера
    Наименование метода:	order_trades
    Тип запроса:	POST
    Входящие параметры:
    order_id - идентификатор ордера
    Пример использования:
    api_query("order_trades", Array(
        "order_id"=>12345
    ));
    Возращаемое значение:
    {
      "type": "buy",
      "in_currency": "BTC",
      "in_amount": "1",
      "out_currency": "USD",
      "out_amount": "100",
      "trades": [
        {
          "trade_id": 3,
          "date": 1435488248,
          "type": "buy",
          "pair": "BTC_USD",
          "order_id": 12345,
          "quantity": 1,
          "price": 100,
          "amount": 100
        }
      ]
    }
    Описание полей:
    type - тип ордера
    in_currency - валюта входящая
    in_amount - кол-во входящей валюты
    out_currency - валюта исходящая
    out_amount - кол-во исходящей валюты
    trades - массив сделок, где:
    trade_id - идентификатор сделки
    date - дата сделки
    type - тип сделки
    pair - валютная пара
    order_id - идентификатор ордера
    quantity - кол-во по сделке
    price - цена по сделке
    amount - сумма по сделке
    '''
    def order_trades(self, order_id):
        params = {'order_id': order_id}
        return self.exmo_api('order_trades', params)

    '''
    Подсчет в какую сумму обойдется покупка определенного кол-ва валюты по конкретной валютной паре
    Наименование метода:	required_amount
    Тип запроса:	POST
    Входящие параметры:
    pair - валютная пара
    quantity - кол-во которое необходимо купить
    Пример использования:
    api_query("required_amount", Array(
        "pair"=>"BTC_USD",
        "quantity"=>"11"
    ));
    Возращаемое значение:
    {
      "quantity": 3,
      "amount": 5,
      "avg_price": 3.66666666
    }
    Описание полей:
    quantity - кол-во которое вы сможете купить
    amount - сумма на которую вы потратите на покупку
    avg_price - средняя цена покупки
    '''
    def required_amount(self, pair, quantity):
        self._getCurrencyPairs()
        if pair not in self.pairs:
            raise Exception('pair expected in ' + str(self.pairs))
        params = {'pair': pair, 'quantity': quantity}
        return self.exmo_api('required_amount', params)

    '''
    Получнение списка адресов для депозита криптовалют
    Наименование метода:	deposit_address
    Тип запроса:	POST
    Входящие параметры:	отсутствуют
    Пример использования:
    api_query("deposit_address", Array());
    Возращаемое значение:
    {
      "BTC": "16UM5DoeHkV7Eb7tMfXSuQ2ueir1yj4P7d",
      "DOGE": "DEVfhgKErG5Nzas2FZJJH8Y8pjoLfVfWq4",
      "LTC": "LSJFhsVJM6GCFtSgRj5hHuK9gReLhNuKFb"
    }
    '''
    def deposit_address(self):
        return self.exmo_api('deposit_address')


    '''
    Создание задачи на вывод криптовалют. ВНИМАНИЕ!!! Эта API функция включается пользователю после запроса в техподдержку
    Наименование метода:	withdraw_crypt
    Тип запроса:	POST
    Входящие параметры:
    amount - кол-во выводимой валюты
    currency - наименование выводимой валюты
    address - адрес вывода
    Пример использования:
    api_query("withdraw_crypt", Array(
        "amount"=>10,
        "currency"=>"BTC",
        "address"=>"16UM5DoeHkV7Eb7tMfXSu..."
    ));
    Возращаемое значение:
    {
      "result": true,
      "error": "",
      "task_id": "467756"
    }
    Описание полей:
    result - true в случае успешного создания задачи на вывод, и false в случае ошибки
    error - содержит описание ошибки
    task_id - идентификатор задачи на вывод
    '''
    def withdraw_crypt(self, amount, currency, address):
        all_currency = self.currency()
        if currency not in all_currency:
            raise ApiError('Currency expected in ' + str(all_currency))
        params = {'amount': amount, 'currency': currency, 'address': address}
        return self.exmo_api('withdraw_crypt', params)

    '''
    Получение ИД транзакции криптовалюты для отслеживания на blockchain
    Наименование метода:	withdraw_get_txid
    Тип запроса:	POST
    Входящие параметры:
    task_id - идентификатор задания на вывод
    Пример использования:
    api_query("withdraw_get_txid", Array(
        "task_id"=>467756
    ));
    Возращаемое значение:
    {
      "result": true,
      "error": "",
      "status": true,
      "txid": "ec46f784ad976fd7f7539089d1a129fe46..."
    }
    Описание полей:
    result - true в случае успешного создания задачи на вывод, и false в случае ошибки
    error - содержит описание ошибки
    status - true если вывод уже осуществлен
    txid - идентификатор транзакции по которому можно её найти в blockchain
    '''
    def withdraw_get_txid(self, task_id):
        params = {'task_id': task_id}
        return self.exmo_api('withdraw_get_txid', params)



    #WALLET API

    '''
    Количество API вызовов ограничено 10 запросами в минуту с одного IP адреса.
    Получение истории wallet
    Наименование метода:	wallet_history
    Тип запроса:	POST
    Входящие параметры:	date - дата timestamp за которую нужно получить историю (если не указан берется текущий день)
    Пример использования
    api_query("wallet_history", Array(
        "date"=>1493998000
    ));
    Пример ответа:
    {
      "result": true,
      "error": "",
      "begin": "1493942400",
      "end": "1494028800",
      "history": [{
           "dt": 1461841192,
           "type": "deposit",
           "curr": "RUB",
           "status": "processing",
           "provider": "Qiwi (LA) [12345]",
           "amount": "1",
           "account": "",
         },
         {
           "dt": 1463414785,
           "type": "withdrawal",
           "curr": "USD",
           "status": "paid",
           "provider": "EXCODE",
           "amount": "-1",
           "account": "EX-CODE_19371_USDda...",
         }
      ]
    }
    Описание полей:
    result - true в случае успешного получения истории, и false в случае ошибки
    error - содержит описание ошибки
    begin - начало периода
    end - конец периода
    history - массив операций пользователя (история кошелька), где
    dt - дата операции
    type - тип
    curr - валюта
    status - статус
    provider - провайдер
    amount - сумма
    account - счет
    '''
    def wallet_history(self, date=0):
        if date == 0:
            date = time.time()
        params = {'date': date}
        return self.exmo_api('wallet_history', params)

#Количество API вызовов ограничено 180 запросами в минуту с одного IP адреса либо от одного пользователя.