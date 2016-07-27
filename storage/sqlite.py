#coding=utf-8

import sqlite3
import time
import os


class Storage:

    session_id = 0
    db_file = 'store.sqlite'
    root_dir = '/'
    init_sql = ['CREATE TABLE IF NOT EXISTS session_data (key, value, type, session_id, utime INTEGER)']

    def __init__(self, session_id, root_dir):
        self.session_id = session_id
        self.root_dir = root_dir
        conn = self._get_connection()
        cur = conn.cursor()
        for sql in self.init_sql:
            cur.execute(sql)
        cur.close()
        conn.close()

    def _get_connection(self):
        return sqlite3.connect(self.root_dir + '/db/' + self.db_file)

    def save(self, key, value, type='string', session_id=None):
        conn = conn = self._get_connection()
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
        conn = conn = self._get_connection()
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
        conn = conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE key=? AND session_id=?', (key, session_id,))
        row = cur.fetchone()
        if row is not None:
            return row[4]
        return None

    def delete(self, key, session_id=None):
        conn = conn = self._get_connection()
        if session_id is None:
            session_id = self.session_id
        cur = conn.cursor()
        cur.execute('DELETE FROM session_data WHERE key=? AND session_id=?', (key, session_id,))
        conn.commit()
        cur.close()
        conn.close()

