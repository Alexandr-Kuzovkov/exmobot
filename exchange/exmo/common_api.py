#coding=utf-8

import exchange.exmo.config as config


class CommonAPI:
    api = None
    name = 'EXMO'
    pair_settings = None
    currency = None
    fee = None

    def __init__(self, api):
        self.api = api
        self.pair_settings = self._get_pair_settings()
        self.currency = self._get_currency()
        self.fee = config.fee

    '''
    Настройки валютных пар
    Входящие параметры:	Отсутствуют
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
    def _get_pair_settings(self):
        data = self.api.exmo_public_api('pair_settings')
        for pair, settings in data.items():
            settings['max_amount'] = float(settings['max_amount'])
            settings['max_quantity'] = float(settings['max_quantity'])
            settings['min_amount'] = float(settings['min_amount'])
            settings['min_price'] = float(settings['min_price'])
            settings['min_quantity'] = float(settings['min_quantity'])
            settings['max_price'] = float(settings['max_price'])

        return data

    '''
    Cписок валют биржи
    Входящие параметры:	Отсутствуют
    Возращаемое значение:
    ["USD","EUR","RUB","BTC","DOGE","LTC"] 
    '''
    def _get_currency(self):
        return self.api.exmo_public_api('currency')


    '''
    Список сделок по валютной паре
    pair - одна или несколько валютных пар в виде списка (пример ['BTC_USD','BTC_EUR'])
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
        valid_pairs = self.pair_settings.keys()
        for pair in pairs:
            if pair not in valid_pairs:
                return False
        data = self.api.exmo_public_api('trades', {'pair': ','.join(pairs)})
        for pair, items in data.items():
            for order in items:
                order['date'] = int(order['date'])
                order['trade_id'] = int(order['trade_id'])
                order['price'] = float(order['price'])
                order['amount'] = float(order['amount'])
                order['quantity'] = float(order['quantity'])
        return data

    '''
    Книга ордеров по валютной паре
    Входящие параметры:
    pair - одна или несколько валютных пар разделенных в виде списка (пример ['BTC_USD','BTC_EUR'])
    limit - кол-во отображаемых позиций (по умолчанию 100, максимум 1000)
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
    def orders(self, pairs=[], limit=100):
        valid_pairs = self.pair_settings.keys()
        for pair in pairs:
            if pair not in valid_pairs:
                raise Exception('pair expected in ' + str(valid_pairs))
        orders = self.api.exmo_public_api('order_book', {'pair': ','.join(pairs), 'limit': limit})
        for pair, data in orders.items():
            data['ask_quantity'] = float(data['ask_quantity'])
            data['ask_amount'] = float(data['ask_amount'])
            data['ask_top'] = float(data['ask_top'])
            data['bid_quantity'] = float(data['bid_quantity'])
            data['bid_amount'] = float(data['bid_amount'])
            data['bid_top'] = float(data['bid_top'])
            for row in data['bid']:
                for i in range(len(row)):
                    row[i] = float(row[i])
            for row in data['ask']:
                for i in range(len(row)):
                    row[i] = float(row[i])

        return orders


    '''
    Cтатистика цен и объемов торгов по валютным парам
    Входящие параметры:	Отсутствуют
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
        ticker = self.api.exmo_public_api('ticker')
        for pair, data in ticker.items():
            data['high'] = float(data['high'])
            data['low'] = float(data['low'])
            data['avg'] = float(data['avg'])
            data['vol'] = float(data['vol'])
            data['vol_curr'] = float(data['vol_curr'])
            data['last_trade'] = float(data['last_trade'])
            data['buy_price'] = float(data['buy_price'])
            data['sell_price'] = float(data['sell_price'])
            data['updated'] = int(data['updated'])

        return ticker





    '''
    Создание ордера
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
        valid_types = ['buy', 'sell', 'market_buy', 'market_sell', 'market_buy_total', 'market_sell_total']
        valid_pairs = self.pair_settings.keys()
        min_quantity = self.pair_settings[pair]['min_quantity']
        max_quantity = self.pair_settings[pair]['max_quantity']
        min_price = self.pair_settings[pair]['min_price']
        max_price = self.pair_settings[pair]['max_price']
        if pair is None or pair not in valid_pairs:
            raise Exception('pair expected in ' + str(valid_pairs))
        if quantity is None or quantity < min_quantity or quantity > max_quantity:
            raise Exception('quantity expected in range %f - %f!' % (min_quantity, max_quantity))
        if price is None or price < min_price or price > max_price:
            raise Exception('price expected in range %f - %f!' % (min_price, max_price))
        if order_type is None or order_type not in valid_types:
            raise Exception('type expected in ' + str(valid_types))
        params = {'pair': pair, 'quantity': quantity, 'price': price, 'type': order_type}
        return self.api.exmo_api('order_create', params)

    '''
    Отмена ордера
    Входящие параметры:
    order_id - идентификатор ордера
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
        return self.api.exmo_api('order_cancel', params)

    '''
    отмена всех ордеров по валютным парам(задаются в виде списка), если не задана то по всем парам
    @param pair  - валютная пара
    @return {order_id:True/False, ...}
    '''
    def orders_cancel(self, pairs=None):
        open_orders = self.api.exmo_api('user_open_orders')
        results = {}
        for cur_pair, orders_for_pair in open_orders.items():
            if pairs is not None and cur_pair not in pairs:
                continue
            for order in orders_for_pair:
                res = self.api.exmo_api('order_cancel', {'order_id': order['order_id']})
                results[order['order_id']] = res['result']
        return results


    '''
    получение баланса по выбранной валюте или по всем
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def balance(self, currency=None):
        user_info = self.api.exmo_api('user_info')
        if currency is not None and currency in self.currency:
            return float(user_info['balances'][currency])
        else:
            balances = {}
            for k,v in user_info['balances'].items():
                balances[k] = float(v)
            return balances

    '''
    получение баланса по выбранной валюте или по всем в ордерах
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def orders_balance(self, currency=None):
        user_info = self.api.exmo_api('user_info')
        if currency is not None and currency in self.currency:
            return float(user_info['reserved'][currency])
        else:
            balances = {}
            for k,v in user_info['reserved'].items():
                balances[k] = float(v)
            return balances


    '''
    получение баланса по выбранной валюте или по всем
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def balance_full(self):
        user_info = self.api.exmo_api('user_info')
        balances = {'balances': user_info['balances'], 'orders': user_info['reserved']}
        for currency, amount in balances['balances'].items():
            balances['balances'][currency] = float(balances['balances'][currency])
        for currency, amount in balances['orders'].items():
            balances['orders'][currency] = float(balances['orders'][currency])
        return balances


    '''
    Получение списока открытых ордеров пользователя
    Входящие параметры:	отсутствуют
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
    def user_orders(self):
        orders = self.api.user_open_orders()
        for pair,list_orders in orders.items():
            for order in list_orders:
                order['created'] = int(order['created'])
                order['order_id'] = int(order['order_id'])
                order['price'] = float(order['price'])
                order['amount'] = float(order['amount'])
                order['quantity'] = float(order['quantity'])
        return orders


    '''
    Получение сделок пользователя
    Входящие параметры:
    pair - одна или несколько валютных пар в виде списка (пример ['BTC_USD','BTC_EUR'])
    offset - смещение от последней сделки (по умолчанию 0)
    limit - кол-во возвращаемых сделок (по умолчанию 100, максимум 10 000)
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
        valid_pairs = self.pair_settings.keys()
        for pair in pairs:
            if pair not in valid_pairs:
                raise Exception('pair expected in ' + str(valid_pairs))
        params = {'pair': ','.join(pairs), 'offset': offset, 'limit': limit}
        data = self.api.exmo_api('user_trades', params)
        for pair, trades in data.items():
            for trade in trades:
                trade['price'] = float(trade['price'])
                trade['amount'] = float(trade['amount'])
                trade['quantity'] = float(trade['quantity'])
        return data


    '''
    Получение отмененных ордеров пользователя
    Входящие параметры:
    offset - смещение от последней сделки (по умолчанию 0)
    limit - кол-во возвращаемых сделок (по умолчанию 100, максимум 10 000)
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
        return self.api.exmo_api('user_cancelled_orders', params)


    '''
    Получение истории сделок ордера

    Входящие параметры:
    order_id - идентификатор ордера
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
        data = self.api.exmo_api('order_trades', params)
        data['in_amount'] = float(data['in_amount'])
        data['out_amount'] = float(data['out_amount'])
        for trade in data['trades']:
            trade['price'] = float(trade['price'])
            trade['amount'] = float(trade['amount'])
            trade['quantity'] = float(trade['quantity'])
        return data


    '''
    Подсчет в какую сумму обойдется покупка определенного кол-ва валюты по конкретной валютной паре
    Входящие параметры:
    pair - валютная пара
    quantity - кол-во которое необходимо купить
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
        valid_pairs = self.pair_settings.keys()
        if pair not in valid_pairs:
            raise Exception('pair expected in ' + str(valid_pairs))
        params = {'pair': pair, 'quantity': quantity}
        data = self.api.exmo_api('required_amount', params)
        data['quantity'] = float(data['quantity'])
        data['amount'] = float(data['amount'])
        data['avg_price'] = float(data['avg_price'])
        return data
