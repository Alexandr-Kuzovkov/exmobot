#coding=utf-8
import time
import math
import strategy.library.functions as Lib
from pprint import pprint

'''
Стратегия для сбора данных тикеров
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'ticker'
    session_id = 'ticker'
    #префикс для логгера
    prefix = ''

    def __init__(self, capi, logger, storage, conf=None, **params):
        self.storage = storage
        self.capi = capi
        self.conf = conf
        self.logger = logger
        self.params = params

        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации

        #имя стратегии
        self.name = Lib.set_param(self, key='name', default_value=self.name)

        #id сессии
        self.session_id = Lib.set_param(self, key='session_id', default_value='0')

        #время хранения данных тикера в сутках
        self.store_time = Lib.set_param(self, key='store_time', param_type='int', default_value='30')

        self.prefix = self.name


    '''
    функция реализующая торговую логику
    '''
    def run(self):
        ticker = {}
        if type(self.capi) is dict:
            for name, capi in self.capi.items():
                try:
                    ticker[name] = capi.ticker()
                except Exception, ex:
                    self.logger.info('Error while get ticker from %s' % name, self.prefix)
            self.storage.save_ticker(ticker)
            self.logger.info('All tickers succesfully saved', self.prefix)
        else:
            try:
                ticker[self.capi.name] = self.capi.ticker()
            except Exception, ex:
                 self.logger.info('Error while get ticker from %s' % self.capi.name, self.prefix)
            self.storage.save_ticker(ticker)
            self.logger.info('Ticker from %s successfully saved', self.prefix)

        #удаление старых данных
        utmost_update = time.time() - self.store_time * 86400
        self.storage.delete_old_tickers(utmost_update)
