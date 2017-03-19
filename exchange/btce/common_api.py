#coding=utf-8

import exchange.exmo.config as config
from pprint import pprint
import time

class CommonAPI:
    name = 'btce'
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
        data = self.api.btce_public_api('info')['pairs']
        result = {}
        for pair, settings in data.items():
            result[pair.upper()] = settings
            for key in settings.keys():
                if key in ['decimal_places', 'hidden']:
                    result[pair.upper()][key] = int(result[pair.upper()][key])
                else:
                    result[pair.upper()][key] = float(result[pair.upper()][key])
                result[pair.upper()]['min_quantity'] = 0.0
                result[pair.upper()]['max_quantity'] = 10000000.0
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
    Проверка валютной пары и при необходимости
    изменение порядка валют в паре
    '''
    def check_pair(self, pair):
        valid_pairs = self.pair_settings.keys()
        if pair in valid_pairs:
            return pair
        elif '_'.join([pair.split('_')[1], pair.split('_')[0]]) in valid_pairs:
            return '_'.join([pair.split('_')[1], pair.split('_')[0]])
        else:
            raise Exception('pair expected in %s' % str(valid_pairs))

    '''
    получение минимальных балансов по валютам в паре
    необходимых для создания ордера
    @return (min_primary_balance, min_secondary_balance)
    '''
    def get_min_balance(self, pair, ticker=None):
        if ticker is None:
            ticker = self.ticker()
        price = max(ticker[pair]['buy_price'], ticker[pair]['sell_price'])
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
        for pair in pairs:
            if pair not in valid_pairs:
                raise Exception('pairs expected subset %s' % str(self.pair_settings.keys()))
        data = self.api.btce_public_api('trades', pairs='-'.join(pairs).lower(), limit=limit)
        trades = {}
        for pair, items in data.items():
            trades[pair.upper()] = []
            for item in items:
                date = int(item['timestamp'])
                trade_id = int(item['tid'])
                price = float(item['price'])
                quantity = float(item['amount'])
                amount = quantity * price
                ttype = {'ask':'sell', 'bid':'buy'}[item['type']]
                trades[pair.upper()].append({'date': date, 'trade_id': trade_id, 'price': price, 'amount': amount, 'quantity': quantity, 'type': ttype})
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
        data = self.api.btce_public_api('depth', pairs='-'.join(pairs).lower(), limit=limit)
        orders = {}
        for pair, orders_for_pair in data.items():
            orders[pair.upper()] = {}
            orders[pair.upper()]['ask'] = []
            orders[pair.upper()]['bid'] = []
            for order in orders_for_pair['asks']:
                orders[pair.upper()]['ask'].append([float(order[0]), float(order[1]), float(order[0])*float(order[1])])
            for order in orders_for_pair['bids']:
                orders[pair.upper()]['bid'].append([float(order[0]), float(order[1]), float(order[0])*float(order[1])])

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
        data = self.api.btce_public_api('ticker')
        tickers = {}
        for pair, params in data.items():
            tickers[pair.upper()] = {}
            tickers[pair.upper()]['high'] = float(params['high'])
            tickers[pair.upper()]['low'] = float(params['low'])
            tickers[pair.upper()]['avg'] = float(params['avg'])
            tickers[pair.upper()]['vol'] = float(params['vol'])
            tickers[pair.upper()]['vol_curr'] = float(params['vol_cur'])
            tickers[pair.upper()]['last_trade'] = float(params['last'])
            tickers[pair.upper()]['buy_price'] = float(params['buy'])
            tickers[pair.upper()]['sell_price'] = float(params['sell'])
            tickers[pair.upper()]['updated'] = int(params['updated'])

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
        try:
            data = self.api.btce_api('getInfo')
        except Exception, ex:
            return {'error': ex.message}
        if currency is not None and currency in self.currency:
            balances = float(data['funds'][currency.lower()])
        else:
            balances = {}
            for pair, amount in data['funds'].items():
                balances[pair.upper()] = float(amount)
        return balances

    '''
    получение баланса по выбранной валюте или по всем в ордерах
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def orders_balance(self, currency=None):
        user_orders = self.user_orders()
        balance = {}
        for currency in self.currency:
            balance[currency] = 0.0
        for pair, orders in user_orders.items():
            for order in orders:
                if order['type'] == 'sell':
                    curr = pair.split('_')[0]
                    sum = order['quantity']
                    balance[curr] += sum
                elif order['type'] == 'buy':
                    curr = pair.split('_')[1]
                    sum = order['amount']
                    balance[curr] += sum
                else:
                    pass

        return balance

    '''
    получение баланса по выбранной валюте или по всем
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def balance_full(self):
        balance = self.balance()
        orders_balance = self.orders_balance()
        for curr, amount in orders_balance.items():
            if curr in balance:
                balance[curr] += amount
            else:
                balance[curr] = amount
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
        try:
            data = self.api.btce_api('ActiveOrders')
        except Exception, ex:
            return {}
        orders = {}

        for order_id, order in data.items():
            if order['pair'].upper() not in orders:
                orders[order['pair'].upper()] = []
            new_order = {}
            new_order['order_id'] = int(order_id)
            new_order['created'] = int(order['timestamp_created'])
            new_order['type'] = order['type']
            new_order['pair'] = order['pair'].upper()
            new_order['price'] = float(order['rate'])
            new_order['quantity'] = float(order['amount'])
            new_order['amount'] = float(order['rate']) * float(order['amount'])
            orders[order['pair'].upper()].append(new_order)

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
    def user_trades(self, pairs=None, offset=0, limit=100):
        valid_pairs = self.pair_settings.keys()
        if pairs is not None:
            for pair in pairs:
                if pair not in valid_pairs:
                    raise Exception('pair expected in ' + str(valid_pairs))
        try:
            if type(pairs) is list and len(pairs) == 1:
                data = self.api.btce_api('TradeHistory', pair=pairs[0].lower(), order='DESC', count=limit)
            elif pairs is None:
                data = self.api.btce_api('TradeHistory', order='DESC', count=limit)
            else:
                data = self.api.btce_api('TradeHistory', order='DESC', count=limit)
        except Exception, ex:
            print ex
            return {}
        trades = {}
        for trade_id, trade in data.items():
           if int(trade['is_your_order']) != 1:
               continue
           if trade['pair'].upper() not in trades:
                trades[trade['pair'].upper()] = []
           new_trade = {}
           new_trade['order_id'] = int(trade['order_id'])
           new_trade['date'] = int(trade['timestamp'])
           new_trade['type'] = trade['type']
           new_trade['pair'] = trade['pair'].upper()
           new_trade['trade_id'] = int(trade_id)
           new_trade['price'] = float(trade['rate'])
           new_trade['quantity'] = float(trade['amount'])
           new_trade['amount'] = float(trade['rate']) * float(trade['amount'])
           trades[trade['pair'].upper()].append(new_trade)

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


    '''
    Подсчет на какое количество валюты currency_to можно
    обменять количество amount_from валюты currency_from
    '''
    def possable_amount(self, currency_from, currency_to, amount_from, orders=None):
        currencies = self._get_currency()
        if currency_from not in currencies or currency_to not in currencies:
            raise Exception('currencies expected in ' + str(currencies))
        valid_pairs = self.pair_settings.keys()
        if currency_from + '_' + currency_to in valid_pairs:
            pair = currency_from + '_' + currency_to
            order_type = 'bid'
        elif currency_to + '_' + currency_from in valid_pairs:
            pair = currency_to + '_' + currency_from
            order_type = 'ask'
        else:
            raise Exception('pair expected in ' + str(valid_pairs))

        if orders is None:
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

    def balance_full_usd(self, balance_full=None, ticker=None):
        if balance_full is None:
            balance_full = self.balance_full()
        if ticker is None:
            ticker = self.ticker()
        currency_ratio = {}
        currency_ratio_usd = {}
        for pair, data in ticker.items():
            currency_ratio[pair] = (data['sell_price'] + data['buy_price']) / 2

        for curr in self.currency:
            if curr + '_USD' in currency_ratio:
                currency_ratio_usd[curr] = currency_ratio[curr + '_USD']
                continue
            elif 'USD_' + curr in currency_ratio:
                currency_ratio_usd[curr] = 1 / currency_ratio['USD_' + curr]
                continue
            elif curr + '_BTC' in currency_ratio and 'BTC_USD' in currency_ratio:
                currency_ratio_usd[curr] = currency_ratio[curr + '_BTC'] * currency_ratio['BTC_USD']
                continue
            elif 'BTC_' + curr in currency_ratio and 'BTC_USD' in currency_ratio:
                currency_ratio_usd[curr] = currency_ratio['BTC_USD']/currency_ratio['BTC_' + curr]

        #pprint(currency_ratio_usd)
        balance_usd = 0.0
        for curr, amount in balance_full.items():
            if curr not in self.currency:
                continue
            balance_usd += amount * currency_ratio_usd[curr]

        return balance_usd


    '''
    определение полного баланса в BTC
    '''

    def balance_full_btc(self, balance_full=None, ticker=None):
        if balance_full is None:
            balance_full = self.balance_full()
        if ticker is None:
            ticker = self.ticker()
        currency_ratio = {}
        currency_ratio_btc = {}
        for pair, data in ticker.items():
            currency_ratio[pair] = (data['sell_price'] + data['buy_price']) / 2

        for curr in self.currency:
            if curr + '_BTC' in currency_ratio:
                currency_ratio_btc[curr] = currency_ratio[curr + '_BTC']
                continue
            elif 'BTC_' + curr in currency_ratio:
                currency_ratio_btc[curr] = 1 / currency_ratio['BTC_' + curr]
                continue
            elif curr + '_USD' in currency_ratio and 'BTC_USD' in currency_ratio:
                currency_ratio_btc[curr] = currency_ratio[curr + '_USD'] / currency_ratio['BTC_USD']
                continue
            elif 'USD_' + curr in currency_ratio and 'BTC_USD' in currency_ratio:
                currency_ratio_btc[curr] = currency_ratio['BTC_USD'] * currency_ratio['USD_' + curr]

        #pprint(currency_ratio_btc)
        balance_btc = 0.0
        for curr, amount in balance_full.items():
            if curr not in self.currency:
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
        tree = [{'id':0, 'parent':None, 'currency': currency_start, 'used':False, 'pair':None, 'order_type':None}]
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
            chains.append({'chain': chain, 'profit':0.0})
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
                adjacent.append({'currency': pair.split('_')[1], 'prev': start, 'order_type': 'sell', 'pair': pair})
            else:
                adjacent.append({'currency': pair.split('_')[0], 'prev': start, 'order_type': 'buy', 'pair': pair})
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
                tree.append({'id':len(tree), 'parent':tree[i]['id'], 'currency':item['currency'], 'used':False, 'pair':item['pair'], 'order_type': item['order_type']})
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
        fees = self._get_fee()
        for chain in chains:
            amount = 10.0
            amount_begin = amount
            for path in chain['chain']:
                if path['pair'] is not None:
                    fee = fees[path['pair']]
                if path['order_type'] == 'buy':
                    price = max(ticker[path['pair']]['buy_price'], ticker[path['pair']]['sell_price'])
                    amount = amount / price * (1 - fee)
                elif path['order_type'] == 'sell':
                    price = min(ticker[path['pair']]['buy_price'], ticker[path['pair']]['sell_price'])
                    amount = amount * price * (1 - fee)
                else:
                    continue

            chain['profit'] = (amount - amount_begin)/amount_begin
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
        fees = self._get_fee()
        for path in chain['chain']:
            if path['pair'] is None:
                currency_from = path['currency']
                continue
            fee = fees[path['pair']]
            currency_to = path['currency']
            amount = self.possable_amount(currency_from, currency_to, amount) * (1 - fee)
            currency_from = currency_to
        profit = (amount - amount_begin)/amount_begin
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
            try:
                amount_to = self._round(amount_to, 6)
                data = self.api.btce_api('Trade', pair=path['pair'].lower(), type=path['order_type'], rate=rate, amount=amount_to)
            except Exception, ex:
                print rate, amount_to
                return {'result': False, 'error': ex.message}
            else:
                if int(data['order_id']) == 0:
                    current_currency = path['currency']
                    current_quantity = float(data['funds'][current_currency.lower()])
                else:
                    return {'result': False, 'order_id': int(data['order_id'])}
        return {'result': True, 'amount': current_quantity}


    '''
    обмен по рынку всех валют на USD
    '''
    def exchange_all_to_usd(self):
        self.orders_cancel()
        time.sleep(1)
        balance = self.balance()
        for currency, amount in balance.items():
            if amount == 0 or currency in ['USD']:
                continue
            if currency + '_USD' in self.pair_settings.keys():
                try:
                    rate = self.pair_settings[currency + '_USD']['min_price']
                    amount_to = self._round(amount, 6)
                    data = self.api.btce_api('Trade', pair=(currency + '_USD').lower(), type='sell', rate=rate, amount=amount_to)
                except Exception, ex:
                    print ex
                else:
                    time.sleep(1)

            elif 'USD_' + currency in self.pair_settings.keys():
                try:
                    rate = self.pair_settings['USD_' + currency]['min_price']
                    amount_to = self._round(amount, 6)
                    data = self.api.btce_api('Trade', pair=('USD_' + currency).lower(), type='sell', rate=rate, amount=amount_to)
                except Exception, ex:
                    print ex
                else:
                    time.sleep(1)
            else:
                if currency +'_BTC' in self.pair_settings.keys():
                    try:
                        rate = self.pair_settings[currency + '_BTC']['min_price']
                        amount_to = self._round(amount, 6)
                        data = self.api.btce_api('Trade', pair=(currency + '_BTC').lower(), type='sell', rate=rate,amount=amount_to)
                    except Exception, ex:
                        print ex
                    else:
                        time.sleep(1)
                elif 'BTC_' + currency in self.pair_settings.keys():
                    try:
                        rate = self.pair_settings['BTC_' + currency]['min_price']
                        amount_to = self._round(amount, 6)
                        data = self.api.btce_api('Trade', pair=('BTC_' + currency).lower(), type='sell', rate=rate,amount=amount_to)
                    except Exception, ex:
                        print ex
                    else:
                        time.sleep(1)
                else:
                    pass
        return self.balance()

    '''
    вычисление на какую сумму в USD можно продать по рынку
    все имеющиеся на балансе криптовалюты
    '''
    def possable_amount_usd(self):
        balance_full = self.balance_full()
        total_amount = 0.0
        currencies = self._get_currency()
        valid_pairs = self.pair_settings.keys()
        for currency, amount in balance_full.items():
            if currency not in currencies:
                continue
            if currency == 'USD':
                total_amount += amount
                continue
            pair = None
            if '_'.join([currency, 'USD']) in valid_pairs:
                pair = '_'.join([currency, 'USD'])
            if '_'.join(['USD', currency]) in valid_pairs:
                pair = '_'.join(['USD', currency])
            if pair is None:
                continue
            if amount < self.pair_settings[pair]['min_quantity']:
                continue
            curr_amount = self.possable_amount(currency, 'USD', amount)
            total_amount += curr_amount
        return total_amount

    def fix_profit(self, session_id):
        # stop trading
        # cancel all orders
        # exchange_all_to_usd
        # clear balance history
        return {'status': 'Ok', 'amount': 100.0, 'session_id': session_id}
