#coding=utf-8

import sqlite3
import time

class Storage:

    session_id = 0
    db_file = 'store.sqlite'
    init_sql = ['CREATE TABLE IF NOT EXISTS session_data (key, value, type, session_id INTEGER, utime INTEGER)']

    def __init__(self, session_id):
        self.session_id = session_id
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        for sql in self.init_sql:
            cur.execute(sql)
        cur.close()
        conn.close()

    def save(self, key, value, type='string'):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE key=? AND session_id=?', (key, self.session_id,))
        if len(cur.fetchall()) == 0:
            cur.execute('INSERT INTO session_data (key,value,type,session_id, utime) VALUES(?,?,?,?,?)',(key, value, type, self.session_id, int(time.time())))
        else:
            cur.execute('UPDATE session_data SET value=?, type=?, utime=? WHERE session_id=? AND key=?',(value, type, int(time.time()), self.session_id, key,))
        conn.commit()
        cur.close()
        conn.close()

    def load(self, key):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE key=? AND session_id=?', (key, self.session_id,))
        row = cur.fetchone()
        if row is not None:
            if row[2] == 'int':
                return int(row[1])
            elif row[2] == 'float':
                return float(row[1])
            else:
                return row[1]
        return None

    def get_utime(self, key):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute('SELECT * FROM session_data WHERE key=? AND session_id=?', (key, self.session_id,))
        row = cur.fetchone()
        if row is not None:
            return row[4]
        return None

    def delete(self, key):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute('DELETE FROM session_data WHERE key=? AND session_id=?', (key, self.session_id,))
        conn.commit()
        cur.close()
        conn.close()

