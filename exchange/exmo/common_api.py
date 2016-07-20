#coding=utf-8

import exchange.exmo.config as Config

class CommonAPI:
    api = None
    name = 'EXMO'
    pair_settings = None
    currency = None

    def __init__(self, api):
        self.api = api
        self.pair_settings = self._get_pair_settings()
        self.currency = self._get_currrency()

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
        data = self.api._exmo_public_api('pair_settings')
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
    def _get_currrency(self):
        return self.api._exmo_public_api('currency')


    '''
    Получение комиссии
    '''
    def get_fee(self, pair=None, order_type='sell'):
        return Config.fee[order_type]



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
    def get_trades(self, pairs=[]):
        valid_pairs = self.pair_settings.keys()
        for pair in pairs:
            if pair not in valid_pairs:
                return False
        data = self.api._exmo_public_api('trades', {'pair': ','.join(pairs)})
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
    def get_orders(self, pairs=[], limit=100):
        valid_pairs = self.pair_settings.keys()
        for pair in pairs:
            if pair not in valid_pairs:
                raise Exception('pair expected in ' + str(valid_pairs))
        orders = self.api._exmo_public_api('order_book', {'pair': ','.join(pairs), 'limit': limit})
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
    def get_ticker(self):
        ticker = self.api._exmo_public_api('ticker')
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
    удаление всех ордеров
    @return True/False
    '''
    def delete_all_orders(self):
        open_orders = self.api.user_open_orders()
        for orders_for_pair in open_orders.values():
            for order in orders_for_pair:
                res = self.api.order_cancel(order['order_id'])
                if res['result']:
                    return True
                else:
                    return False
    '''
    удаление ордеров по валютной паре
    @param pair  - валютная пара
    @return True/False
    '''
    def delete_orders_for_pair(self, pair):
        if not self.api.isPairValid(pair):
            raise Exception('Pair not valid')
        open_orders = self.api.user_open_orders()
        orders_for_pair = open_orders[pair]
        for order in orders_for_pair:
            res = self.api.order_cancel(order['order_id'])
            if res['result']:
                return True
            else:
                return False

    '''
    получение баланса по выбранной валюте или по всем
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    '''
    def get_balance(self, currency=None):
        user_info = self.api.user_info()
        if currency is not None and currency in self.currency:
            return float(user_info['balances'][currency])
        else:
            balances = {}
            for k,v in user_info['balances'].items():
                balances[k] = float(v)
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
    def get_user_orders(self):
        orders = self.api.user_open_orders()
        for pair,list_orders in orders.items():
            for order in list_orders:
                order['created'] = int(order['created'])
                order['order_id'] = int(order['order_id'])
                order['price'] = float(order['price'])
                order['amount'] = float(order['amount'])
                order['quantity'] = float(order['quantity'])
        return orders






