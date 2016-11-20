#coding=utf-8

import sqlite3
import time
import os
from ConfigParser import *
from pprint import pprint


class Crud:

    session_id = '0'
    rel_path_db_file = 'db/store.sqlite' #относительный путь до файла базы данных относительно корня скрипта
    db_file = ''
    rel_path_schema = '/storage/schema.ini'
    schema_file = ''
    schema = {} #словарь в котором хранится схема БД

    #конструктор, создание таблиц
    def __init__(self):
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = '/'.join(self.curr_dir.split('/')[0:len(self.curr_dir.split('/')) - 2])
        self.db_file = '/'.join([root_dir, self.rel_path_db_file])
        self.schema_file = '/'.join([root_dir, self.rel_path_schema])
        self.create_tables()
        #pprint(self.schema)

    def _get_connection(self):
        return sqlite3.connect(self.db_file)

    '''
    выполнение запроса с возвратом результата
    @param query строка запроса с ? в месте вставки данных
    @param data кортеж с данными
    '''
    def query(self, query, data=None):
        conn = self._get_connection()
        cur = conn.cursor()
        success = True
        try:
            if data is not None:
                cur.execute(query, data)
            else:
                cur.execute(query)
            res = cur.fetchall()
        except sqlite3.OperationalError, ex:
            print ex
            success = False
        finally:
            cur.close()
            conn.close()
        if success:
            return res
        else:
            return success

    '''
    выполнение запроса без возврата результата
    @param query строка запроса с ? в месте вставки данных
    @param data кортеж с данными
    '''
    def execute(self, query, data=None):
        conn = self._get_connection()
        cur = conn.cursor()
        success = True
        try:
            if data is not None:
                cur.execute(query, data)
            else:
                cur.execute(query)
            conn.commit()
        except sqlite3.OperationalError, ex:
            success = False
            print ex
        finally:
            cur.close()
            conn.close()
        return success


    '''
    вставка данных в таблицу
    @param table имя таблицы
    @param data_rows список кортежей с данными
    '''
    def insert(self, table, data):
        conn = self._get_connection()
        cur = conn.cursor()
        success = True
        place_holders = []
        try:
            for i in range(len(self.schema[table])):
                place_holders.append('?')
            fln = []
            for field in self.schema[table]:
                fln.append(field['name'])
            query = ' '.join(['INSERT INTO', table, '(', ','.join(fln), ') VALUES (', ','.join(place_holders),')'])
        except Exception, ex:
            print ex
            success = False
            return success
        #print query
        try:
            for data_row in data:
                cur.execute(query, data_row)
            conn.commit()
        except sqlite3.OperationalError, ex:
            success = False
            print ex
        finally:
            cur.close()
            conn.close()
        return success


    '''
    получение данных из таблицы
    @param table имя таблицы
    @param conditions список словарей с условиями запроса (то что после where)
    '''
    def get(self, table, conditions=None):
        conn = self._get_connection()
        cur = conn.cursor()
        success = True
        q = ['SELECT * FROM', table, 'WHERE']
        tail = []
        if conditions is not None:
            if type(conditions) is list:
                for condition in conditions:
                    key, val = condition.items()[0]
                    tail.append(''.join([key,str(val)]))
            elif type(conditions) is dict:
                for key, val in conditions.items():
                    tail.append(''.join([key,str(val)]))
            q.append(' AND '.join(tail))
        else:
            q.append('1')
        query = ' '.join(q)
        #print query
        try:
            cur.execute(query)
            res = cur.fetchall()
        except sqlite3.OperationalError, ex:
            print ex
            success = False
        finally:
            cur.close()
            conn.close()
        if success:
            return res
        else:
            return None

    '''
    удаление данных из таблицы
    @param table имя таблицы
    @param conditions список словарей с условиями запроса (то что после where)
    '''
    def delete(self, table, conditions=None):
        conn = self._get_connection()
        cur = conn.cursor()
        success = True
        q = ['DELETE FROM', table, 'WHERE']
        tail = []
        if conditions is not None:
            if type(conditions) is list:
                for condition in conditions:
                    key, val = condition.items()[0]
                    tail.append(''.join([key, str(val)]))
            elif type(conditions) is dict:
                for key, val in conditions.items():
                    tail.append(''.join([key, str(val)]))
            q.append(' AND '.join(tail))
        else:
            q.append('1')
        query = ' '.join(q)
        #print query
        try:
            cur.execute(query)
            conn.commit()
        except sqlite3.OperationalError, ex:
            print ex
            success = False
        finally:
            cur.close()
            conn.close()
        return success


    '''
    обновление данных в таблице
    @param table имя таблицы
    @param data словарь с данными {field_name: value}
    @param conditions список словарей с условиями запроса (то что после where)
    '''
    def update(self, table, data, conditions=None):
        conn = self._get_connection()
        cur = conn.cursor()
        success = True
        values = data.values()
        sets = []
        for fld, val in data.items():
            sets.append(''.join([fld, '=?']))
        sets = ','.join(sets)
        q = ['UPDATE', table, 'SET', sets, 'WHERE']
        tail = []
        if conditions is not None:
            if type(conditions) is list:
                for condition in conditions:
                    key, val = condition.items()[0]
                    tail.append(''.join([key, str(val)]))
            elif type(conditions) is dict:
                for key, val in conditions.items():
                    tail.append(''.join([key, str(val)]))
            q.append(' AND '.join(tail))
        else:
            q.append('1')
        query = ' '.join(q)
        #print query
        try:
            cur.execute(query, values)
            conn.commit()
        except sqlite3.OperationalError, ex:
            success = False
            print ex
        finally:
            cur.close()
            conn.close()
        return success


    '''
    удаление таблиц БД
    '''
    def drop_tables(self):
        rows = self.query("SELECT * FROM sqlite_master WHERE type = 'table'")
        tables = []
        for row in rows:
            tables.append(row[1])
        for table in tables:
            query = ['DROP TABLE IF EXISTS', table]
            query = ' '.join(query)
            self.execute(query)
        return True


    '''
    создание таблиц базы данных
    '''
    def create_tables(self):
        root_dir = '/'.join(self.curr_dir.split('/')[0:len(self.curr_dir.split('/')) - 2])
        conf = ConfigParser()
        conf.read(self.schema_file)
        conn = self._get_connection()
        cur = conn.cursor()
        success = True
        for table in conf.sections():
            self.schema[table] = []
            fls = []
            for field in conf.options(table):
                fparams = conf.get(table, field).split('|')
                ftype = fparams[0]
                fsize = fparams[1]
                self.schema[table].append({'name':field, 'type':ftype})
                if len(fparams) > 2:
                    fdef = fparams[2].strip()
                    if fdef in ['null', 'NULL', 'None', 'NONE']:
                        fdef = ' DEFAULT NULL'
                    elif fdef:
                        fdef = ' DEFAULT ' + fparams[2]
                    else:
                        fdef = ' DEFAULT ' + "'" + fdef + "'"
                else:
                    fdef = ''
                if ftype == 'int':
                    fls.append(' '.join([field, ' INTEGER', fdef]))
                elif ftype == 'float':
                    fls.append(' '.join([field, ' REAL', fdef]))
                else:
                    fls.append(field)
            q = ' '.join(['CREATE TABLE IF NOT EXISTS ', table,'(', ','.join(fls), ')'])
            #print q
            try:
                cur.execute(q)
            except sqlite3.OperationalError, ex:
                success = False
                print ex
        cur.close()
        conn.close()
        return success

