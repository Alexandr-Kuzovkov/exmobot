#coding=utf-8

import time
from pprint import pprint
import os


class Storage:

    session_id = 'default'
    dbase = None #объект crud базы данных

    def __init__(self, dbase, session_id=None):
        if session_id is not None:
            self.session_id = session_id
        self.dbase = dbase

    def _quote(self, s):
        return ''.join(["'", s, "'"])

    '''
    запись значения в сессию
    '''
    def save(self, key, value, value_type='string', session_id=None):
        if session_id is None:
            session_id = self.session_id
        res = self.dbase.get('session_data', {'`key`=':self._quote(key), '`session_id`=':self._quote(session_id)})
        if len(res) == 0:
            self.dbase.insert('session_data',[(key, value, value_type, session_id, int(time.time()))])
        else:
            self.dbase.update('session_data', {'value':value, 'type':value_type, 'utime':int(time.time())}, {'session_id=':self._quote(session_id), '`key`=':self._quote(key)})

    '''
    чтение значения из сессии по ключу
    '''
    def load(self, key, session_id=None):
        if session_id is None:
            session_id = self.session_id
        rows = self.dbase.get('session_data', {'`key`=':self._quote(key), '`session_id`=':self._quote(session_id)})
        if len(rows) > 0:
            if rows[0][2] == 'int':
                return int(rows[0][1])
            elif rows[0][2] == 'float':
                return float(rows[0][1])
            else:
                return rows[0][1]
        return None

    '''
    получение времени обновления значения с заданным ключом
    '''
    def get_utime(self, key, session_id=None):
        if session_id is None:
            session_id = self.session_id
        rows = self.dbase.get('session_data', {'`key`=':self._quote(key), '`session_id`=':self._quote(session_id)})
        if rows is not None and len(rows) > 0:
            return rows[0][4]
        return None

    '''
    удаление значения в сессии
    '''
    def delete(self, key, session_id=None):
        if session_id is None:
            session_id = self.session_id
        return self.dbase.delete('session_data', {'`key`=':self._quote(key), '`session_id`=':self._quote(session_id)})


    '''
    запись данных ордера в таблицу
    '''
    def order_add(self, order_id, pair, quantity, price, order_type, session_id=None):
        if session_id is None:
            session_id = self.session_id
        rows = self.dbase.get('orders', {'`order_id`=':order_id, '`session_id`=':self._quote(session_id)})
        if len(rows) == 0:
            res = self.dbase.insert('orders', [(order_id, pair, quantity, price, order_type, session_id, int(time.time()))])
        else:
            res = self.dbase.update('orders', {'order_id':order_id, 'pair':pair, 'quantity':quantity, 'price':price, 'order_type':order_type, 'utime': int(time.time())}, {'`order_id`=':order_id, '`session_id`=':self._quote(session_id)})
        return res


    '''
    удаление данных ордера из таблицы
    '''
    def order_delete(self, order_id=None, pair=None, session_id=None):
        if session_id is None:
            session_id = self.session_id
        if (order_id is not None) and (pair is not None):
            res = self.dbase.delete('orders', {'pair=':self._quote(pair), 'order_id=':order_id, 'session_id=':self._quote(session_id)})
        elif pair is not None:
            res = self.dbase.delete('orders', {'pair=': self._quote(pair), 'session_id=': self._quote(session_id)})
        elif order_id is not None:
            res = self.dbase.delete('orders', {'order_id=': order_id, 'session_id=': self._quote(session_id)})
        else:
            res = self.dbase.delete('orders', {'session_id=': self._quote(session_id)})
        return res

    '''
    удаление записей об ордерах с utime менее заданного
    '''
    def old_orders_delete(self, utime, pair=None, session_id=None):
        if session_id is None:
            session_id = self.session_id
        if pair is not None:
            res = self.dbase.delete('orders', {'pair=': self._quote(pair), 'session_id=': self._quote(session_id), 'utime<': utime})
        else:
            res = self.dbase.delete('orders', {'session_id=': self._quote(session_id), 'utime<': utime})
        return res

    '''
    получение записей об ордерах из таблицы
    '''
    def orders(self, pair=None, session_id=None):
        if session_id is None:
            session_id = self.session_id
        if pair is None:
            rows = self.dbase.get('orders', {'session_id=':self._quote(session_id)})
        else:
            rows = self.dbase.get('orders', {'session_id=':self._quote(session_id), 'pair=':self._quote(pair)})
        result = []
        for row in rows:
            result.append({'order_id': row[0], 'pair': row[1], 'quantity': row[2], 'price': row[3], 'order_type': row[4], 'session_id': row[5], 'utime': row[6]})
        return result

    '''
    запись величины баланса в таблицу
    '''
    def save_balance(self, currency, amount, session_id=None):
        if session_id is None:
            session_id = self.session_id
        res = self.dbase.insert('balance', [(currency, amount, session_id, int(time.time()))])
        return res

    '''
    получение последних записей о балансе из таблицы
    '''
    def get_last_balance(self, currency, limit=1, session_id=None):
        if session_id is None:
            session_id = self.session_id
        rows = self.dbase.get('balance', [{'session_id=':self._quote(session_id)}, {'currency=':self._quote(currency) + ' ORDER BY utime DESC LIMIT ' + str(limit)}])
        result = []
        for row in rows:
            result.append({'currency': row[0], 'amount': row[1], 'session_id': row[2], 'utime': row[3]})
        return result

    '''
    удаление записей из таблиц с utime менее заданного
    @param tables список имен таблиц
    @param full при равном True удаляются записи для всех сессий
    '''
    def delete_old_values(self, tables, utime, full=False, session_id=None):
        if session_id is None:
            session_id = self.session_id
        if full:
            for table in tables:
                self.dbase.delete(table, {'utime<': utime})
        else:
            for table in tables:
                self.dbase.delete(table, {'utime<': utime, 'session_id=':self._quote(session_id)})
        return True

    '''
    запись в таблицу сделок пользователя
    @param trades список словарей  вида
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
    '''
    def save_user_trades(self, trades, session_id=None):
        if session_id is None:
            session_id = self.session_id
        rows = self.dbase.get('user_trades', {'session_id=':self._quote(session_id)})
        data_to_write = []
        now = int(time.time())
        for trade in trades:
            if trade['date'] < now * 3600 * 24: #не добавляем сделки старше суток
                continue
            if len(rows) > 0:
                record_exists = False
                for row in rows:
                    if (row[0] == trade['trade_id']) and (row[1] == trade['order_id']) and(row[8] == trade['date']):
                        record_exists = True
                        break
                if record_exists:
                    continue
            data = (trade['trade_id'], trade['order_id'], trade['pair'], trade['quantity'], trade['price'], trade['amount'], trade['type'], session_id, trade['date'], int(time.time()),)
            data_to_write.append(data)
        res = self.dbase.insert('user_trades', data_to_write)
        return res

    '''
    получение последних сделок limit пользователя по паре pair
    '''
    def get_last_user_trades(self, pair=None, limit=100, session_id=None):
        if session_id is None:
            session_id = self.session_id
        if pair is None:
            rows = self.dbase.get('user_trades', [{'session_id=':self._quote(session_id) + ' ORDER BY trade_date DESC limit ' + str(limit)}])
        else:
            rows = self.dbase.get('user_trades', [{'session_id=':self._quote(session_id)}, {'pair=':self._quote(pair) +' ORDER BY trade_date DESC limit ' + str(limit)}])
        result = []
        for row in rows:
            result.append({'trade_id':row[0], 'order_id':row[1], 'pair':row[2], 'quantity':row[3], 'price':row[4], 'amount':row[5], 'type':row[6], 'session_id':row[7], 'date':row[8], 'utime':row[9]})
        return result


    '''
    запись данных тикера
    @param ticker словарь вида:
    {
        "btce": {
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
    def save_ticker(self, ticker):
        data_to_write = []
        for exchange, exchange_ticker in ticker.items():
            for pair, pair_ticker in exchange_ticker.items():
                data = (exchange, pair, pair_ticker['high'], pair_ticker['low'], pair_ticker['avg'], pair_ticker['vol'], pair_ticker['vol_curr'], pair_ticker['last_trade'], pair_ticker['buy_price'], pair_ticker['sell_price'], pair_ticker['updated'])
                data_to_write.append(data)
        self.dbase.insert('ticker', data_to_write)


    '''
    получение данных тикера из базы
    @param exchange имя биржи
    @param pair валютная пара
    @param start временная метка начала интервала данных
    @param end временная метка конца интервала данных
    @return словарь вида:
    {
        "btce": {
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
    def load_ticker(self, exchange=None, pair=None, start=None, end=None):
        condition = []
        if exchange is not None:
            condition.append({'exchange=': self._quote(exchange)})
        if pair is not None:
             condition.append({'pair=': self._quote(pair)})
        if start is not None:
            condition.append({'updated>=': start})
        if end is not None:
            condition.append({'updated<=': end})
        if len(condition) == 0:
            condition = None
        data = self.dbase.get('ticker', condition)
        ticker = {}
        for row in data:
            exchange, pair, high, low, avg, vol, vol_curr, last_trade, buy_price, sell_price, updated = row
            if exchange not in ticker:
                ticker[exchange] = {}
            if pair not in ticker[exchange]:
                ticker[exchange][pair] = {}
            ticker[exchange][pair]['high'] = high
            ticker[exchange][pair]['low'] = low
            ticker[exchange][pair]['avg'] = avg
            ticker[exchange][pair]['vol'] = vol
            ticker[exchange][pair]['vol_curr'] = vol_curr
            ticker[exchange][pair]['last_trade'] = last_trade
            ticker[exchange][pair]['buy_price'] = buy_price
            ticker[exchange][pair]['sell_price'] = sell_price
            ticker[exchange][pair]['updated'] = updated
        return ticker


    '''
    удаление старых данных по тикерам
    @param utmost_update крайняя временная метка, ранее которой записи подлежат удалению
    '''
    def delete_old_tickers(self, utmost_update):
        self.dbase.delete('ticker', {'updated<': utmost_update})


    '''
    запись данных статистики
    @param exchange имя биржи
    @param pair валютная пара
    @param order_qt_sell
    @param order_qt_buy
    @param trade_qt_sell
    @param trade_qt_buy
    @param top_buy
    @param low_sell
    '''
    def save_stat(self, exchange, pair, order_qt_sell, order_qt_buy, trade_qt_sell, trade_qt_buy, low_sell, top_buy):
        data_to_write = []
        row = (int(time.time()), exchange, pair, order_qt_sell, order_qt_buy, trade_qt_sell, trade_qt_buy, low_sell, top_buy)
        data_to_write.append(row)
        self.dbase.insert('stat', data_to_write)


    '''
    удаление старых данных статистики
    @param utmost_update крайняя временная метка, ранее которой записи подлежат удалению
    '''
    def delete_old_stat(self, utmost_update):
        self.dbase.delete('stat', {'utime<': utmost_update})
