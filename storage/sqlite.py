#coding=utf-8

import sqlite3
import time
import os


class Storage:

    session_id = 0
    db_file = 'store.sqlite'
    root_dir = '/'

    def __init__(self, session_id, root_dir):
        self.session_id = session_id
        self.root_dir = root_dir
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS session_data (key, value, type, session_id, utime INTEGER)')
        cur.execute('CREATE TABLE IF NOT EXISTS orders (order_id, pair, quantity REAL, price REAL, order_type, session_id, utime INTEGER)')
        cur.close()
        conn.close()

    def _get_connection(self):
        return sqlite3.connect(self.root_dir + '/db/' + self.db_file)

    def save(self, key, value, type='string', session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE key=? AND session_id=?', (key, session_id,))
        if len(cur.fetchall()) == 0:
            cur.execute('INSERT INTO session_data (key,value,type,session_id, utime) VALUES(?,?,?,?,?)',(key, value, type, session_id, int(time.time())))
        else:
            cur.execute('UPDATE session_data SET value=?, type=?, utime=? WHERE session_id=? AND key=?',(value, type, int(time.time()), session_id, key,))
        conn.commit()
        cur.close()
        conn.close()

    def load(self, key, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE key=? AND session_id=?', (key, session_id,))
        row = cur.fetchone()
        if row is not None:
            if row[2] == 'int':
                return int(row[1])
            elif row[2] == 'float':
                return float(row[1])
            else:
                return row[1]
        return None

    def get_utime(self, key, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE key=? AND session_id=?', (key, session_id,))
        row = cur.fetchone()
        if row is not None:
            return row[4]
        return None

    def delete(self, key, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('DELETE FROM session_data WHERE key=? AND session_id=?', (key, session_id,))
        conn.commit()
        cur.close()
        conn.close()

    def order_add(self, order_id, pair, quantity, price, order_type, session_id=None):
        conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM orders WHERE order_id=? AND session_id=?', (order_id, session_id,))
        if len(cur.fetchall()) == 0:
            cur.execute('INSERT INTO orders (order_id, pair, quantity, price, order_type, session_id, utime) VALUES (?,?,?,?,?,?,?)',(order_id, pair, quantity, price, order_type, session_id, int(time.time())))
        else:
            cur.execute('UPDATE orders SET order_id=?, pair=?, quantity=?, price=?, order_type=?, utime=? WHERE session_id=? AND order_id=?',(order_id, pair, quantity, price, order_type, int(time.time()), session_id, order_id,))
        conn.commit()
        cur.close()
        conn.close()

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
        return result
