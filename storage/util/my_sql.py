#coding=utf-8

import time
import os
import MySQL.connector

class Storage:

    session_id = '0'
    root_dir = '/'

    def __init__(self, session_id, root_dir):
        self.session_id = session_id
        self.root_dir = root_dir
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS session_data (`key` varchar(255), `value` varchar(255), `type` varchar(255), session_id varchar(255), utime INT(11))ENGINE=InnoDB DEFAULT CHARSET=utf8;')
        cur.execute('CREATE TABLE IF NOT EXISTS `orders` (order_id varchar(30), pair varchar(20), quantity REAL(20,6), price REAL(20,6), order_type varchar(10), session_id varchar(255), utime INT(11))ENGINE=InnoDB DEFAULT CHARSET=utf8;')
        cur.execute('CREATE TABLE IF NOT EXISTS balance (currency varchar(30), amount REAL(20,6), session_id varchar(255), utime INT(11))ENGINE=InnoDB DEFAULT CHARSET=utf8;')
        cur.execute('CREATE TABLE IF NOT EXISTS user_trades (trade_id varchar(255), order_id varchar(30), pair varchar(20), quantity REAL(20,6), price REAL(20,6), amount REAL(20,6), trade_type varchar(10), session_id varchar(255), trade_date INT(11), utime INT(11))ENGINE=InnoDB DEFAULT CHARSET=utf8;')
        cur.close()
        conn.close()

    def _get_connection(self):
        return MySQL.connector.connect(host='localhost', database='exmobot', user='root', password='rootroot', charset='utf8')

    '''
    запись значения в сессию
    '''
    def save(self, key, value, value_type='string', session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE `key`=%s AND session_id=%s', (key, session_id))
        if len(cur.fetchall()) == 0:
            cur.execute('INSERT INTO session_data (`key`,`value`,`type`,session_id, utime) VALUES(%s,%s,%s,%s,%s)', (key, value, value_type, session_id, int(time.time())))
        else:
            cur.execute('UPDATE session_data SET `value`=%s, `type`=%s, utime=%s WHERE session_id=%s AND `key`=%s', (value, value_type, int(time.time()), session_id, key))
        conn.commit()
        cur.close()
        conn.close()

    '''
    чтение значения из сессии по ключу
    '''
    def load(self, key, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE `key`=%s AND session_id=%s', (key, session_id))
        row = cur.fetchone()
        if row is not None:
            if row[2] == 'int':
                return int(row[1])
            elif row[2] == 'float':
                return float(row[1])
            else:
                return row[1]
        return None

    '''
    получение времени обновления значения с заданным ключом
    '''
    def get_utime(self, key, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE `key`=%s AND session_id=%s', (key, session_id))
        row = cur.fetchone()
        if row is not None:
            return row[4]
        return None

    '''
    удаление значения в сессии
    '''
    def delete(self, key, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('DELETE FROM session_data WHERE `key`=%s AND session_id=%s', (key, session_id))
        conn.commit()
        cur.close()
        conn.close()

    '''
    запись данных ордера в таблицу
    '''
    def order_add(self, order_id, pair, quantity, price, order_type, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM orders WHERE order_id=%s AND session_id=%s', (order_id, session_id,))
        if len(cur.fetchall()) == 0:
            cur.execute('INSERT INTO orders (order_id, pair, quantity, price, order_type, session_id, utime) VALUES (%s,%s,%s,%s,%s,%s,%s)',(order_id, pair, quantity, price, order_type, session_id, int(time.time())))
        else:
            cur.execute('UPDATE orders SET order_id=%s, pair=%s, quantity=%s, price=%s, order_type=%s, utime=%s WHERE session_id=%s AND order_id=%s',(order_id, pair, quantity, price, order_type, int(time.time()), session_id, order_id,))
        conn.commit()
        cur.close()
        conn.close()

    '''
    удаление данных ордера из таблицы
    '''
    def order_delete(self, order_id=None, pair=None, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        if (order_id is not None) and (pair is not None):
            cur.execute('DELETE FROM orders WHERE pair=%s AND order_id=%s AND session_id=%s', (pair, order_id, session_id,))
        elif pair is not None:
            cur.execute('DELETE FROM orders WHERE pair=%s AND session_id=%s', (pair, session_id,))
        elif order_id is not None:
            cur.execute('DELETE FROM orders WHERE order_id=%s AND session_id=%s', (order_id, session_id,))
        else:
            cur.execute('DELETE FROM orders WHERE session_id=%s', (session_id,))
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
            cur.execute('DELETE FROM orders WHERE pair=%s AND session_id=%s AND utime<%s', (pair, session_id, utime))
        else:
            cur.execute('DELETE FROM orders WHERE session_id=%s AND utime<%s', (session_id, utime))
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
            cur.execute('SELECT * FROM orders WHERE session_id=%s', (session_id,))
        else:
            cur.execute('SELECT * FROM orders WHERE pair=%s AND session_id=%s', (pair, session_id,))
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
        cur.execute('INSERT INTO balance (currency, amount, session_id, utime) VALUES (%s,%s,%s,%s)', (currency, amount, session_id, int(time.time())))
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
        cur.execute('SELECT * FROM balance WHERE session_id=%s AND currency=%s ORDER BY utime DESC LIMIT %s', (session_id, currency, limit))
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
                cur.execute('DELETE FROM '+table+' WHERE utime<%s', (utime,))
        else:
            for table in tables:
                cur.execute('DELETE FROM '+table+' WHERE session_id=%s AND utime < %s', (session_id, utime))
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
        cur.execute('SELECT * FROM user_trades WHERE session_id=%s', (session_id,))
        rows = cur.fetchall()
        for trade in trades:
            if rows:
                record_exists = False
                for row in rows:
                    if (int(row[0]) == trade['trade_id']) and (int(row[1]) == trade['order_id']) and(row[8] == trade['date']):
                        record_exists = True
                        break
                if record_exists:
                    continue
            data = (trade['trade_id'], trade['order_id'], trade['pair'], trade['quantity'], trade['price'], trade['amount'], trade['type'], session_id, trade['date'], int(time.time()),)
            cur.execute('INSERT INTO user_trades (trade_id, order_id, pair, quantity, price, amount, trade_type, session_id, trade_date, utime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', data)
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
            cur.execute('SELECT * FROM user_trades WHERE session_id=%s ORDER BY trade_date DESC limit %s', (session_id, limit,))
        else:
            cur.execute('SELECT * FROM user_trades WHERE session_id=%s AND pair=%s ORDER BY trade_date DESC limit %s', (session_id, pair, limit,))
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


