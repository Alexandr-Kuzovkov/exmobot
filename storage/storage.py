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
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        if (order_id is not None) and (pair is not None):
            cur.execute('DELETE FROM orders WHERE pair=? AND order_id=? AND session_id=?', (pair, order_id, session_id,))
        elif pair is not None:
            cur.execute('DELETE FROM orders WHERE pair=? AND session_id=?', (pair, session_id,))
        elif order_id is not None:
            cur.execute('DELETE FROM orders WHERE order_id=? AND session_id=?', (order_id, session_id,))
        else:
            cur.execute('DELETE FROM orders WHERE session_id=?', (session_id,))
        conn.commit()
        cur.close()
        conn.close()

    '''
    удаление записей об ордерах с utime менее заданного
    '''
    def old_orders_delete(self, utime, pair=None, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        if pair is not None:
            cur.execute('DELETE FROM orders WHERE pair=? AND session_id=? AND utime<?', (pair, session_id, utime))
        else:
            cur.execute('DELETE FROM orders WHERE session_id=? AND utime<?', (session_id, utime))
        conn.commit()
        cur.close()
        conn.close()

    '''
    получение записей об ордерах из таблицы
    '''
    def orders(self, pair=None, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        if pair is None:
            cur.execute('SELECT * FROM orders WHERE session_id=?', (session_id,))
        else:
            cur.execute('SELECT * FROM orders WHERE pair=? AND session_id=?', (pair, session_id,))
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({'order_id': row[0], 'pair': row[1], 'quantity': row[2], 'price': row[3], 'order_type': row[4], 'session_id': row[5], 'utime': row[6]})
        cur.close()
        conn.close()
        return result

    '''
    запись величины баланса в таблицу
    '''
    def save_balance(self, currency, amount, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('INSERT INTO balance (currency, amount, session_id, utime) VALUES (?,?,?,?)', (currency, amount, session_id, int(time.time())))
        conn.commit()
        cur.close()
        conn.close()

    '''
    получение последних записей о балансе из таблицы
    '''
    def get_last_balance(self, currency, limit=1, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM balance WHERE session_id=? AND currency=? ORDER BY utime DESC LIMIT ?', (session_id, currency, limit))
        rows = cur.fetchall()
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
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        if full:
            for table in tables:
                cur.execute('DELETE FROM '+table+' WHERE utime<?', (utime,))
        else:
            for table in tables:
                cur.execute('DELETE FROM '+table+' WHERE session_id=? AND utime < ?', (session_id, utime))
        conn.commit()
        cur.close()
        conn.close()

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
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM user_trades WHERE session_id=?', (session_id,))
        rows = cur.fetchall()
        for trade in trades:
            if rows:
                record_exists = False
                for row in rows:
                    if (row[0] == trade['trade_id']) and (row[1] == trade['order_id']) and(row[8] == trade['date']):
                        record_exists = True
                        break
                if record_exists:
                    continue
            data = (trade['trade_id'], trade['order_id'], trade['pair'], trade['quantity'], trade['price'], trade['amount'], trade['type'], session_id, trade['date'], int(time.time()),)
            cur.execute('INSERT INTO user_trades (trade_id, order_id, pair, quantity, price, amount, trade_type, session_id, trade_date, utime) VALUES (?,?,?,?,?,?,?,?,?,?)', data)
        conn.commit()
        cur.close()
        conn.close()

    '''
    получение последних сделок limit пользователя по паре pair
    '''
    def get_last_user_trades(self, pair=None, limit=100, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        if pair is None:
            cur.execute('SELECT * FROM user_trades WHERE session_id=? ORDER BY trade_date DESC limit ?', (session_id, limit,))
        else:
            cur.execute('SELECT * FROM user_trades WHERE session_id=? AND pair=? ORDER BY trade_date DESC limit ?', (session_id, pair, limit,))
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({'trade_id':row[0], 'order_id':row[1], 'pair':row[2], 'quantity':row[3], 'price':row[4], 'amount':row[5], 'type':row[6], 'session_id':row[7], 'date':row[8], 'utime':row[9]})
        cur.close()
        conn.close()
        return result


    '''
    очистка всех таблиц
    '''
    def clear_all(self):
        conn = self._get_connection()
        cur = conn.cursor()
        tables = ['orders', 'balance', 'session_data', 'user_trades']
        for table in tables:
            cur.execute('DELETE FROM ' + table)
        conn.commit()
        cur.close()
        conn.close()


