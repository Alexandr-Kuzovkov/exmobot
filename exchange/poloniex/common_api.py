#coding=utf-8

from pprint import pprint
from time import strptime
from time import mktime
from time import time

class CommonAPI:
    name = 'poloniex'
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
            result[pair]['fee_taker'] = 0.25
            result[pair]['min_quantity'] = 0.0
            result[pair]['max_quantity'] = 100000000.0
            result[pair]['min_price'] = 0.0001
            result[pair]['max_price'] = 4999.0
            result[pair]['min_amount'] = 0.0001
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
    Проверка валютной пары и при необходимости
    изменение порядка валют в паре
    '''
    def _check_pair(self, pair):
        valid_pairs = self.pair_settings.keys()
        if pair in valid_pairs:
            return pair
        elif '_'.join([pair.split('_')[1], pair.split('_')[0]]) in valid_pairs:
            return '_'.join([pair.split('_')[1], pair.split('_')[0]])
        else:
            raise Exception('pair expected in %s' % str(valid_pairs))


    '''
    Проверка валютной пары в списке и при необходимости
    изменение порядка валют в паре
    '''
    def _check_pairs(self, pairs):
        valid_pairs = self.pair_settings.keys()
        new_pairs = []
        for pair in pairs:
            new_pairs.append(self._check_pair(pair))
        return new_pairs


    '''
    получение минимальных балансов по валютам в паре
    необходимых для создания ордера
    @return (min_primary_balance, min_secondary_balance)
    '''
    def get_min_balance(self, pair, price):
        pair = self._check_pair(pair)
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
        pair = self._check_pair(pairs[0])
        data = self.api.public_api_query('returnTradeHistory', currencyPair=pair)
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
        pairs = self._check_pairs(pairs)
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
        pair = self._check_pair(pair)
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

        if order_type == 'buy':
            data = self.api.trade_api_query('buy', currencyPair=pair, rate=price, amount=quantity)
            if 'error' in data:
                return {'result': False, 'error': data['error']}
            else:
                return {'result': True, 'error': '', 'order_id': data['orderNumber']}
        else:
            data = self.api.trade_api_query('sell', currencyPair=pair, rate=price, amount=quantity)
            if 'error' in data:
                return {'result': False, 'error': data['error']}
            else:
                return {'result': True, 'error': '', 'order_id': data['orderNumber']}


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
        data = self.api.trade_api_query('cancelOrder', orderNumber=order_id)
        if 'error' in data:
            return {'result': False, 'error': data['error']}
        elif 'success' in data and data['success'] == 1:
            return {'result': True, 'error': ''}
        else:
            return {'result': False, 'error': 'unknown error'}

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
        balance = {}
        for currency, all_balances in data.items():
            balance[currency] = float(all_balances['available'])
            balance[currency] += float(all_balances['onOrders'])
        return balance


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
        pairs = self._check_pairs(pairs)
        trades = {}
        if len(pairs) == 1:
            data = self.api.trade_api_query('returnTradeHistory', currencyPair=pairs[0])
            if 'error' in data:
                raise Exception(data['error'])
            trades[pairs[0]] = []
            for trade in data:
                new_trade = {}
                new_trade['order_id'] = int(trade['orderNumber'])
                new_trade['date'] = self._date2timestamp(trade['date'])
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
        pair = self._check_pair(pair)
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


    '''
    Подсчет на какое количество валюты currency_to можно
    обменять количество amount_from валюты currency_from
    '''
    def possable_amount(self, currency_from, currency_to, amount_from):
        currencies = self._get_currency();
        if currency_from not in currencies or currency_to not in currencies:
            raise Exception('currencies expected in ' + str(currencies))
        valid_pairs = self.pair_settings.keys()
        if currency_from + '_' + currency_to in valid_pairs:
            pair = currency_from + '_' + currency_to
            order_type = 'ask'
        elif currency_to + '_' + currency_from in valid_pairs:
            pair = currency_to + '_' + currency_from
            order_type = 'bid'
        else:
            raise Exception('pair expected in ' + str(valid_pairs))

        orders = self.orders([pair], limit=1000)
        amount_to = 0.0
        if order_type == 'bid':
            quantity_curr = 0.0
            for order in orders[pair][order_type]:
                order_price = order[0]
                order_quantity = order[1]
                order_amount = order[2]
                if (order_quantity < (amount_from - quantity_curr)):
                    quantity_curr = quantity_curr + order_quantity
                    amount_to = amount_to + order_amount
                else:
                    amount_to = amount_to + (amount_from - quantity_curr) * order_price
                    break

        elif order_type == 'ask':
            amount_curr = 0.0
            for order in orders[pair][order_type]:
                order_price = order[0]
                order_quantity = order[1]
                order_amount = order[2]
                if (order_amount < (amount_from - amount_curr)):
                    amount_curr += order_amount
                    amount_to += order_quantity
                else:
                    amount_to += (amount_from - amount_curr) / order_price
                    break

        return amount_to


    '''
    определение полного баланса в USD
    '''
    def balance_full_usd(self):
        balance_full = self.balance_full()
        ticker = self.ticker()
        currency_ratio = {}
        currency_ratio_usd = {}
        for pair, data in ticker.items():
            if data['sell_price'] > data['buy_price']:
                currency_ratio[pair] = data['buy_price']
            else:
                currency_ratio[pair] = data['sell_price']

        for curr in self.currency:
            if curr + '_USDT' in currency_ratio:
                currency_ratio_usd[curr] = 1/currency_ratio[curr + '_USDT']
                continue
            elif 'USDT_' + curr in currency_ratio:
                currency_ratio_usd[curr] = currency_ratio['USDT_' + curr]
                continue
            elif curr + '_BTC' in currency_ratio and 'USDT_BTC' in currency_ratio:
                currency_ratio_usd[curr] = 1/currency_ratio[curr + '_BTC'] * currency_ratio['USDT_BTC']
                continue
            elif 'BTC_' + curr in currency_ratio and 'USDT_BTC' in currency_ratio:
                currency_ratio_usd[curr] = currency_ratio['USDT_BTC'] * currency_ratio['BTC_' + curr]

        # pprint(currency_ratio_usd)
        balance_usd = 0.0
        for curr, amount in balance_full.items():
            if curr not in self.currency or curr not in currency_ratio_usd:
                continue
            balance_usd += amount * currency_ratio_usd[curr]

        return balance_usd

    '''
    определение полного баланса в BTC
    '''
    def balance_full_btc(self):
        balance_full = self.balance_full()
        ticker = self.ticker()
        currency_ratio = {}
        currency_ratio_btc = {}
        for pair, data in ticker.items():
            if data['sell_price'] > data['buy_price']:
                currency_ratio[pair] = data['buy_price']
            else:
                currency_ratio[pair] = data['sell_price']

        for curr in self.currency:
            if curr + '_BTC' in currency_ratio:
                currency_ratio_btc[curr] = 1/currency_ratio[curr + '_BTC']
                continue
            elif 'BTC_' + curr in currency_ratio:
                currency_ratio_btc[curr] = currency_ratio['BTC_' + curr]
                continue
            elif curr + '_USDT' in currency_ratio and 'BTC_USDT' in currency_ratio:
                currency_ratio_btc[curr] = currency_ratio[curr + '_USDT'] / currency_ratio['BTC_USDT']
                continue
            elif 'USDT_' + curr in currency_ratio and 'BTC_USDT' in currency_ratio:
                currency_ratio_btc[curr] = currency_ratio['BTC_USDT'] * currency_ratio['USDT_' + curr]

        # pprint(currency_ratio_btc)
        balance_btc = 0.0
        for curr, amount in balance_full.items():
            if curr not in self.currency or curr not in currency_ratio_btc:
                continue
            balance_btc += amount * currency_ratio_btc[curr]

        return balance_btc


    '''
    поиск прибыльных цепочек обмена
    возвращает список циклических
    цепочек обмена начиная с валюты currency_start
    обмен по которым будет прибыльным
    @param currency_start начальная валюта
    @param chain_len длина цепочки обмена (количество обменов)
    @param profit_only возвращать только прибыльные цепочки
    @return chains список цепочек обмена вида
    [{'chain':chain, 'profit': profit},...], где
    chain - цепочка обмена в виде списка путей обмена, вида:
    [{'currency': 'USD',
             'id': 0,
             'order_type': None,
             'pair': None,
             'parent': None,
             'used': True},
            {'currency': u'RUR',
             'id': 9,
             'order_type': 'sell',
             'pair': u'USD_RUR',
             'parent': 0,
             'used': True},
            {'currency': u'LTC',
             'id': 45,
             'order_type': 'buy',
             'pair': u'LTC_RUR',
             'parent': 9,
             'used': True},
            {'currency': u'USD',
             'id': 206,
             'order_type': 'sell',
             'pair': u'LTC_USD',
             'parent': 45,
             'used': False}]
    '''
    def search_exchains(self, currency_start, chain_len=3, profit_only=True):
        currencies = self._get_currency()
        pairs = self._get_pair_settings().keys()
        if currency_start not in currencies:
            raise Exception('currency_start expected in ' + str(currencies))
        tree = [{'id': 0, 'parent': None, 'currency': currency_start, 'used': False, 'pair': None, 'order_type': None}]
        for i in range(chain_len):
            tree = self._next_step(tree, pairs)

        chains = []
        for node in filter(lambda node: not node['used'], tree):
            if node['currency'] != currency_start:
                continue
            chain = [node]
            parent_id = node['parent']
            while parent_id != 0:
                parent_node = tree[parent_id]
                parent_id = parent_node['parent']
                chain.append(parent_node)
            chain.append(tree[0])
            chain.reverse()
            chains.append({'chain': chain, 'profit': 0.0})
        if profit_only:
            return filter(lambda chain: chain['profit'] > 0, self._search_profit(chains))
        else:
            return self._search_profit(chains)


    '''
    возвращает список путей обмена заданной валюты start
    в виде списка словарей вида
    {'currency': currency, 'prev': prev_currency, 'order_type': 'sell/buy', 'pair': pair}
    @param start начальная валюта
    @param pairs список пар биржи
    @return adjacent список путей обмена
    '''
    def _get_adjacents(self, start, pairs):
        adjacent_pairs = filter(lambda pair: start in pair.split('_'), pairs)
        adjacent = []
        for pair in adjacent_pairs:
            if pair.split('_')[0] == start:
                adjacent.append({'currency': pair.split('_')[1], 'prev': start, 'order_type': 'buy', 'pair': pair})
            else:
                adjacent.append({'currency': pair.split('_')[0], 'prev': start, 'order_type': 'sell', 'pair': pair})
        return adjacent


    '''
    выполняет цикл построения дерева путей обмена
    @param tree дерево путей обмена
    @param pairs список пар биржи
    @return tree дерево путей обмена
    '''
    def _next_step(self, tree, pairs):
        start_currency = None
        for node in tree:
            if node['parent'] is None:
                start_currency = node['currency']
                break
        length = len(tree)
        for i in range(length):
            if tree[i]['used'] or (tree[i]['currency'] == start_currency and length > 1):
                continue
            adjacents = self._get_adjacents(tree[i]['currency'], pairs)
            for item in adjacents:
                tree.append({'id': len(tree), 'parent': tree[i]['id'], 'currency': item['currency'], 'used': False,
                             'pair': item['pair'], 'order_type': item['order_type']})
            tree[i]['used'] = True
        return tree


    '''
    просчет цепочек обмена с целью поиска цепочек с профитом
    @param chains список цепочек обмена вида:
     [{'chain': [{'currency': 'USD',
             'id': 0,
             'order_type': None,
             'pair': None,
             'parent': None,
             'used': True},
            {'currency': u'RUR',
             'id': 9,
             'order_type': 'sell',
             'pair': u'USD_RUR',
             'parent': 0,
             'used': True},
            {'currency': u'LTC',
             'id': 45,
             'order_type': 'buy',
             'pair': u'LTC_RUR',
             'parent': 9,
             'used': True},
            {'currency': u'USD',
             'id': 206,
             'order_type': 'sell',
             'pair': u'LTC_USD',
             'parent': 45,
             'used': False}],
    'profit': 0.0}, ...]
    @return список цепочек обмена c заполненным полем profit
    '''
    def _search_profit(self, chains):
        ticker = self.ticker()
        for chain in chains:
            amount = 1.0
            amount_begin = amount
            for path in chain['chain']:
                if path['pair'] is not None:
                    fee = self.pair_settings[path['pair']]['fee_taker'] / 100
                if path['order_type'] == 'buy':
                    price = max(ticker[path['pair']]['buy_price'], ticker[path['pair']]['sell_price'])
                    amount = amount / price * (1 - fee)
                elif path['order_type'] == 'sell':
                    price = min(ticker[path['pair']]['buy_price'], ticker[path['pair']]['sell_price'])
                    amount = amount * price * (1 - fee)
                else:
                    continue
            chain['profit'] = (amount - amount_begin) / amount_begin
        return chains


    '''
    более подробный просчет прибыльности обмена по цепочке с учетом
    реально существующих ордеров
    @param chain - цепочка обмена вида:
    {'chain': [{'currency': 'USD',
            'id': 0,
            'order_type': None,
            'pair': None,
            'parent': None,
            'used': True},
           {'currency': u'RUR',
            'id': 9,
            'order_type': 'sell',
            'pair': u'USD_RUR',
            'parent': 0,
            'used': True},
           {'currency': u'LTC',
            'id': 45,
            'order_type': 'buy',
            'pair': u'LTC_RUR',
            'parent': 9,
            'used': True},
           {'currency': u'USD',
            'id': 206,
            'order_type': 'sell',
            'pair': u'LTC_USD',
            'parent': 45,
            'used': False}],
    'profit': 0.0}
    @param amount сумма входной валюты
    @return  profit уточненный профит
    '''
    def calc_chain_profit_real(self, chain, amount):
        amount_begin = amount
        currency_from = None
        for path in chain['chain']:
            if path['pair'] is None:
                currency_from = path['currency']
                continue
            fee = self.pair_settings[path['pair']]['fee_taker'] /100
            currency_to = path['currency']
            amount = self.possable_amount(currency_from, currency_to, amount) * (1 - fee)
            currency_from = currency_to
        profit = (amount - amount_begin) / amount_begin
        return profit


    '''
    выполнение цепочки обменов
    @param chain - цепочка обмена вида:
    {'chain': [{'currency': 'USD',
            'id': 0,
            'order_type': None,
            'pair': None,
            'parent': None,
            'used': True},
           {'currency': u'RUR',
            'id': 9,
            'order_type': 'sell',
            'pair': u'USD_RUR',
            'parent': 0,
            'used': True},
           {'currency': u'LTC',
            'id': 45,
            'order_type': 'buy',
            'pair': u'LTC_RUR',
            'parent': 9,
            'used': True},
           {'currency': u'USD',
            'id': 206,
            'order_type': 'sell',
            'pair': u'LTC_USD',
            'parent': 45,
            'used': False}],
    'profit': 0.0}
    @param amount сумма входной валюты
    '''
    def execute_exchange_chain(self, chain, amount):
        current_quantity = amount
        pairs = []
        for path in chain['chain']:
            if path['pair'] is None:
                continue
            pairs.append(path['pair'])
        pairs = set(pairs)
        pairs = list(pairs)
        orders = self.orders(pairs, limit=1000)

        for path in chain['chain']:
            if path['pair'] is None:
                continue
            if path['order_type'] == 'sell':
                order_type = 'bid'
                rate = self.pair_settings[path['pair']]['min_price']
            elif path['order_type'] == 'buy':
                order_type = 'ask'
                rate = self.pair_settings[path['pair']]['max_price']
            amount_to = 0.0
            if order_type == 'bid':
                amount_to = current_quantity
                if rate * amount_to < self.pair_settings[path['pair']]['min_amount']:
                    rate = self.pair_settings[path['pair']]['min_amount']/amount_to * 2
            elif order_type == 'ask':
                amount_curr = 0.0
                for order in orders[path['pair']][order_type]:
                    order_price = order[0]
                    order_quantity = order[1]
                    order_amount = order[2]
                    if (order_amount < (current_quantity - amount_curr)):
                        amount_curr += order_amount
                        amount_to += order_quantity
                    else:
                        amount_to += (current_quantity - amount_curr) / order_price
                        break
            amount_to = self._round(amount_to, 6)
            #print 'before req order rate=%f amount_to=%f' % (rate, amount_to)
            data = self.api.trade_api_query(path['order_type'], currencyPair=path['pair'], rate=rate, amount=amount_to, immediateOrCancel=1)
            #pprint(data)
            if 'error' in data:
                #print 'rate=%f amount_to=%f' % (rate, amount_to)
                return {'result': False, 'error': data['error']}
            else:
                if float(data['amountUnfilled']) == 0.0:
                    current_currency = path['currency']
                    current_quantity = self.balance(current_currency)
                else:
                    return {'result': False, 'order_id': int(data['orderNumber'])}
        return {'result': True, 'amount': current_quantity}

