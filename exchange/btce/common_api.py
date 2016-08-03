#coding=utf-8

import exchange.exmo.config as config
from pprint import pprint


class CommonAPI:
    name = 'BTC-E'
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
        raise Exception('"orders_balance" now not realise!')


    '''
    получение баланса по выбранной валюте или по всем
    @currency валюта
    return словарь вида {u'DASH': 0.0, u'USD': 6e-08, u'RUB': 0.0, u'DOGE': 0.0, u'LTC': 0.0, u'BTC': 0.0, u'ETH': 0.0, u'EUR': 0.0}
    или число
    '''
    def balance_full(self):
        raise Exception('"balance_full" now not realise!')


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
    def user_trades(self, pairs, offset=0, limit=100):
        valid_pairs = self.pair_settings.keys()
        for pair in pairs:
            if pair not in valid_pairs:
                raise Exception('pair expected in ' + str(valid_pairs))
        try:
            data = self.api.btce_api('TradeHistory', pair='-'.join(pairs).lower(), count=limit)
        except Exception, ex:
            return {}

        trades = {}
        for trade_id, trade in data.items():
           if trade['is_you_order'] == 0: continue
           if trade['pair'].upper() not in trades:
                trades[trade['pair'].upper()] = []
                new_trade = {}
                new_trade['order_id'] = int(trade_id)
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