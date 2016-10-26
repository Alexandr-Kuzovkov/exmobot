#coding=utf-8

import sqlite3
import time
import os
from ConfigParser import *
from pprint import pprint


class Crud:

    session_id = '0'
    rel_path_db_file = 'db/store_test.sqlite' #относительный путь до файла базы данных относительно корня скрипта
    db_file = ''
    rel_path_schema = '/storage/schema.ini'
    schema = {} #словарь в котором хранится схема БД

    #конструктор, создание таблиц
    def __init__(self):
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = '/'.join(self.curr_dir.split('/')[0:len(self.curr_dir.split('/')) - 2])
        self.db_file = '/'.join([root_dir, self.rel_path_db_file])
        schema_file = '/'.join([root_dir, self.rel_path_schema])
        conf = ConfigParser()
        conf.read(schema_file)
        conn = self._get_connection()
        cur = conn.cursor()
        for table in conf.sections():
            self.schema[table] = {}
            fls = []
            for field in conf.options(table):
                ftype = conf.get(table, field).split('|')[0]
                fsize = conf.get(table, field).split('|')[1]
                self.schema[table][field] = ftype
                if ftype == 'int':
                    fls.append(field + ' INTEGER')
                elif ftype == 'float':
                    fls.append(field + ' REAL')
                else:
                     fls.append(field)
            q = ' '.join(['CREATE TABLE IF NOT EXISTS ', table,'(', ','.join(fls), ')'])
            #print q
            cur.execute(q)
        cur.close()
        conn.close()
        pprint(self.schema)

    def _get_connection(self):
        return sqlite3.connect(self.db_file)

    '''
    выполнение запроса на выборку
    '''
    def query(self, query, data):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(query, data)
        res = cur.fetchall()
        cur.close()
        conn.close()
        return res

    '''
    выполнение запроса на модификацию
    '''
    def execute(self, query, data):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(query, data)
        cur.commit()
        cur.close()
        conn.close()


    def insert(self, table, data_rows):
        conn = self._get_connection()
        cur = conn.cursor()
        place_holders = []
        for field in self.schema[table].keys():
            place_holders.append('?')
        query = ' '.join(['INSERT INTO', table, '(', ','.join(self.schema[table].keys()), ') VALUES (', ','.join(place_holders),')'])
        print query
        for data in data_rows:
            cur.execute(query, data)
        conn.commit()
        cur.close()
        conn.close()
