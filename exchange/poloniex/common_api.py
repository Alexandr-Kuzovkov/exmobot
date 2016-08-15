#coding=utf-8

from pprint import pprint
from time import strptime
from time import mktime
from time import time

class CommonAPI:
    name = 'Poloniex'
    pair_settings = None
    currency = None
    fee = None

    def __init__(self, api):
        self.api = api
        self.pair_settings = self._get_pair_settings()
        self.currency = self._get_currency()
        self.fee = self._get_fee()

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
        data = self.api.public_api_query('returnTicker')
        result = {}
        for pair, settings in data.items():
            result[pair.upper()] = {}
        for pair in result.keys():
            result[pair]['fee'] = 0.15
            result[pair]['min_quantity'] = 0.0
            result[pair]['max_quantity'] = 100000000.0
            result[pair]['min_price'] = 0.0
            result[pair]['max_price'] = 100000000.0
            result[pair]['min_amount'] = 0.0
            result[pair]['max_amount'] = 100000000.0
        return result

    '''
    Cписок валют биржи
    Входящие параметры:	Отсутствуют
    Возращаемое значение:
    ["USD","EUR","RUB","BTC","DOGE","LTC"] 
    '''
    def _get_currency(self):
        currency = []
        for pair in self.pair_settings.keys():
            currency.append(pair.split('_')[0].upper())
            currency.append(pair.split('_')[1].upper())
        currency = set(currency)
        currency = list(currency)
        return currency


    '''
    Получение комиссий по парам
    '''
    def _get_fee(self):
        fee = {}
        for pair, settings in self.pair_settings.items():
            fee[pair] = settings['fee']/100.0
        return fee


    '''
    Округление числа
    '''
    def _round(self, number, prec):
        number = number * (10**prec)
        number = int(number)
        number = float(number) / (10**prec)
        return number

    '''
    преобразование строки вида 2016-08-15 13:04:52 в timestamp
    '''
    def _date2timestamp(self, date):
        try:
            timestamp = int(mktime(strptime(date, '%Y-%m-%d %H:%M:%S')))
        except ValueError, ex:
            print ex
            return 0
        else:
            return timestamp



    '''
    получение минимальных балансов по валютам в паре
    необходимых для создания ордера
    @return (min_primary_balance, min_secondary_balance)
    '''
    def get_min_balance(self, pair, price):
        if 'min_quantity' in self.pair_settings[pair] and self.pair_settings[pair]['min_quantity'] != 0:
            min_primary_balance = self.pair_settings[pair]['min_quantity']
        elif 'min_amount' in self.pair_settings[pair]:
            min_primary_balance = self.pair_settings[pair]['min_amount']
        else:
            min_primary_balance = 0.0001

        if 'min_quantity' in self.pair_settings[pair] and self.pair_settings[pair]['min_quantity'] != 0:
            min_secondary_balance = self.pair_settings[pair]['min_quantity'] * price
        elif 'min_amount' in self.pair_settings[pair]:
            min_secondary_balance = self.pair_settings[pair]['min_amount'] * price
        else:
            min_secondary_balance = 0.0001

        return (min_primary_balance, min_secondary_balance)



    #PUBLIC API

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
    def trades(self, pairs=[], limit=150):
        valid_pairs = self.pair_settings.keys()
        if len(pairs) > 1:
            raise Exception('Poloniex API support one pair only')
        for pair in pairs:
            if pair not in valid_pairs:
                raise Exception('pairs expected subset %s' % str(self.pair_settings.keys()))
        data = self.api.public_api_query('returnTradeHistory', currencyPair=pairs[0])
        pair = pairs[0]
        trades = {}
        trades[pair] = []
        for trade in data:
            date = self._date2timestamp(trade['date'])
            trade_id = int(trade['globalTradeID'])
            price = float(trade['rate'])
            quantity = float(trade['amount'])
            amount = float(trade['total'])
            ttype = trade['type']
            trades[pair].append({'date': date, 'trade_id': trade_id, 'price': price, 'amount': amount, 'quantity': quantity, 'type': ttype})
        return trades


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
    def orders(self, pairs=[], limit=150):
        valid_pairs = self.pair_settings.keys()
        for pair in pairs:
            if pair not in valid_pairs:
                raise Exception('pairs expected subset %s' % str(self.pair_settings.keys()))
        orders = {}

        if len(pairs) == 1:
            orders[pairs[0]] = {}
            orders[pairs[0]]['ask'] = []
            orders[pairs[0]]['bid'] = []
            data = self.api.public_api_query('returnOrderBook', currencyPair=pairs[0], depth=limit)

            for order in data['asks']:
                orders[pairs[0]]['ask'].append([float(order[0]), float(order[1]), float(order[0]) * float(order[1])])
            for order in data['bids']:
                orders[pairs[0]]['bid'].append([float(order[0]), float(order[1]), float(order[0]) * float(order[1])])

        else:
            data = self.api.public_api_query('returnOrderBook', currencyPair='all', depth=limit)
            for pair, orders_for_pair in data.items():
                if pair not in pairs:
                    continue
                orders[pair] = {}
                orders[pair]['ask'] = []
                orders[pair]['bid'] = []
                for order in orders_for_pair['asks']:
                    orders[pair]['ask'].append([float(order[0]), float(order[1]), float(order[0])*float(order[1])])
                for order in orders_for_pair['bids']:
                    orders[pair]['bid'].append([float(order[0]), float(order[1]), float(order[0])*float(order[1])])

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
        data = self.api.public_api_query('returnTicker')
        tickers = {}
        for pair, params in data.items():
            tickers[pair] = {}
            tickers[pair]['high'] = float(params['high24hr'])
            tickers[pair]['low'] = float(params['low24hr'])
            tickers[pair]['vol'] = float(params['baseVolume'])
            tickers[pair]['vol_curr'] = float(params['quoteVolume'])
            tickers[pair]['last_trade'] = float(params['last'])
            tickers[pair]['buy_price'] = float(params['highestBid'])
            tickers[pair]['sell_price'] = float(params['lowestAsk'])
            tickers[pair]['updated'] = int(time())
            if tickers[pair]['vol_curr'] > 0:
                tickers[pair]['avg'] = tickers[pair]['vol']/tickers[pair]['vol_curr']
            else:
                tickers[pair]['avg'] = 0.0
        return tickers


    #AUTH API


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
        valid_types = ['buy', 'sell']
        valid_pairs = self.pair_settings.keys()
        min_quantity = self.pair_settings[pair]['min_quantity']
        max_quantity = self.pair_settings[pair]['max_quantity']
        min_price = self.pair_settings[pair]['min_price']
        max_price = self.pair_settings[pair]['max_price']
        min_amount = self.pair_settings[pair]['min_amount']

        amount = price * quantity
        if amount < min_amount:
            raise Exception('amount expected greater %f!' % min_amount)
        if pair is None or pair not in valid_pairs:
            raise Exception('pair expected in ' + str(valid_pairs))
        if quantity is None or quantity < min_quantity or quantity > max_quantity:
            raise Exception('quantity expected in range %f - %f!' % (min_quantity, max_quantity))
        if price is None or price < min_price or price > max_price:
            raise Exception('price expected in range %f - %f!' % (min_price, max_price))
        if order_type is None or order_type not in valid_types:
            raise Exception('type expected in ' + str(valid_types))

        quantity = self._round(quantity, 6)
        price = self._round(price, self.pair_settings[pair]['decimal_places'])

        try:
            data = self.api.btce_api('Trade', pair=pair.lower(), type=order_type, rate=price, amount=quantity)
        except Exception, ex:
            return {'result': False, 'error': ex.message}
        else:
            return {'result': True, 'error': '', 'order_id': int(data['order_id'])}

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
        try:
            data = self.api.btce_api('CancelOrder', order_id=order_id)
        except Exception, ex:
            return {'result': False, 'error': ex.message}
        else:
            return {'result': True, 'error': ''}

    '''
    отмена всех ордеров по валютным парам(задаются в виде списка), если не задана то по всем парам
    @param pair  - валютная пара
    @return {order_id:True/False, ...}
    '''
    def orders_cancel(self, pairs=None):
        open_orders = self.user_orders()
        results = {}
        for pair, orders_for_pair in open_orders.items():
            if pairs is not None and pair not in pairs:
                continue
            for order in orders_for_pair:
                res = self.order_cancel(order['order_id'])
                results[order['order_id']] = res['result']
        return results


    '''
    получение баланса по выбранной валюте или по всем
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def balance(self, currency=None):
        data = self.api.trade_api_query('returnBalances')
        if 'error' in data:
            raise Exception(data['error'])
        if currency is not None and currency in self.currency:
            balances = float(data[currency])
        else:
            balances = {}
            for currency, amount in data.items():
                balances[currency] = float(amount)
        return balances

    '''
    получение баланса по выбранной валюте или по всем в ордерах
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def orders_balance(self, currency=None):
        data = self.api.trade_api_query('returnCompleteBalances')
        if 'error' in data:
            raise Exception(data['error'])
        if currency is not None and currency in self.currency:
            balances = float(data[currency]['onOrders'])
        else:
            balances = {}
            for currency, all_balances in data.items():
                balances[currency] = float(all_balances['onOrders'])
        return balances


    '''
    получение баланса по выбранной валюте или по всем
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def balance_full(self):
        data = self.api.trade_api_query('returnCompleteBalances')
        if 'error' in data:
            raise Exception(data['error'])
        balances = {}
        balances['balances'] = {}
        balances['orders'] = {}
        for currency, all_balances in data.items():
            balances['balances'][currency] = all_balances['available']
            balances['orders'][currency] = all_balances['onOrders']
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
        data = self.api.trade_api_query('returnOpenOrders', currencyPair='all')
        if 'error' in data:
            raise Exception(data['error'])
        orders = {}
        for pair, orders_for_pair in data.items():
            if pair not in orders:
                orders[pair] = []
            for order in orders_for_pair:
                new_order = {}
                new_order['order_id'] = int(order['orderNumber'])
                new_order['created'] = 0
                new_order['type'] = order['type']
                new_order['pair'] = pair
                new_order['price'] = float(order['rate'])
                new_order['quantity'] = float(order['amount'])
                new_order['amount'] = float(order['total'])
                orders[pair].append(new_order)
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
        trades = {}
        if len(pairs) == 1:
            data = self.api.trade_api_query('returnTradeHistory', currencyPair=pairs[0])
            if 'error' in data:
                raise Exception(data['error'])
            trades[pairs[0]] = []
            for trade in data:
                new_trade = {}
                new_trade['order_id'] = int(trade['orderNumber'])
                new_trade['date'] = self._date2timestamp(trade['globalTradeID'])
                new_trade['type'] = trade['type']
                new_trade['pair'] = pairs[0]
                new_trade['trade_id'] = int(trade['globalTradeID'])
                new_trade['price'] = float(trade['rate'])
                new_trade['quantity'] = float(trade['amount'])
                new_trade['amount'] = float(trade['total'])
                trades[pairs[0]].append(new_trade)

        elif len(pairs) > 1:
            data = self.api.trade_api_query('returnTradeHistory', currencyPair='all')
            if 'error' in data:
                raise Exception(data['error'])
            if isinstance(data, list) and len(data) == 0:
                for pair in pairs:
                    trades[pair] = []
                return trades
            for pair, trades_for_pair in data.items():
                if pair not in pairs:
                   continue
                if pair not in trades:
                    trades[pair] = []
                for trade in trades_for_pair:
                    new_trade = {}
                    new_trade['order_id'] = int(trade['orderNumber'])
                    new_trade['date'] = self._date2timestamp(trade['globalTradeID'])
                    new_trade['type'] = trade['type']
                    new_trade['pair'] = pairs[0]
                    new_trade['trade_id'] = int(trade['globalTradeID'])
                    new_trade['price'] = float(trade['rate'])
                    new_trade['quantity'] = float(trade['amount'])
                    new_trade['amount'] = float(trade['total'])
                    trades[pair].append(new_trade)
        else:
            pass
        return trades


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
        raise Exception('"user_cancelled_orders" not realised now!')


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
        raise Exception('"order_trades" not realised now!')


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
        orders = self.orders([pair], limit=1000)
        amount = 0.0
        curr_quantity = 0.0
        for order in orders[pair]['ask']:
            order_price = order[0]
            order_quantity = order[1]
            order_amount = order[2]
            if order_quantity >= (quantity - curr_quantity):
                amount = amount + (quantity - curr_quantity) * order_price
                curr_quantity = quantity
                break
            else:
                amount = amount + order_quantity * order_price
                curr_quantity = curr_quantity + order_quantity
        if curr_quantity == quantity:
            return {'quantity': quantity, 'amount': amount, 'avg_price': amount/quantity}
        else:
            raise Exception('Еhe requested quantity can not be bought!')