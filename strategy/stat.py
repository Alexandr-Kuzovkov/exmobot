#coding=utf-8
import time
import math
import strategy.library.functions as Lib
from pprint import pprint

'''
Стратегия для сбора статистики
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'stat'
    session_id = 'stat'
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

        #время хранения данных статистики в сутках
        self.store_time = Lib.set_param(self, key='store_time', param_type='int', default_value='30')

        self.prefix = self.name

        self.pairs = Lib.set_param(self, key='pairs')
        self.pairs = self.pairs.split(',')

    '''
    функция реализующая торговую логику
    '''
    def run(self):
        if type(self.capi) is dict:
            for name, capi in self.capi.items():
                for pair in self.pairs:
                    if pair in capi.pair_settings.keys():
                        try:
                            orders = capi.orders([pair])
                            trades = capi.trades([pair])
                            low_sell = orders[pair]['ask'][0][0]
                            top_buy = orders[pair]['bid'][0][0]
                            order_qt_sell = 0.0
                            order_qt_buy = 0.0
                            for order in orders[pair]['ask']:
                                order_qt_sell += order[1]
                            for order in orders[pair]['bid']:
                                order_qt_buy += order[1]
                            trade_qt_sell = 0.0
                            trade_qt_buy = 0.0
                            for trade in trades[pair]:
                                if trade['type'] == 'sell':
                                    trade_qt_sell += trade['quantity']
                                elif trade['type'] == 'buy':
                                    trade_qt_buy += trade['quantity']
                            data = (name, pair, order_qt_sell, order_qt_buy, trade_qt_sell, trade_qt_buy, low_sell, top_buy)
                            self.logger.info('Received data: exchange: %s pair: %s %f %f %f %f %f %f' % data, self.prefix)
                            self.storage.save_stat(name, pair, order_qt_sell, order_qt_buy, trade_qt_sell, trade_qt_buy, low_sell, top_buy)
                            self.logger.info('Stat data from "%s" for pair %s has been saved' % (name, pair), self.prefix)
                        except Exception, ex:
                            self.logger.info('Error while get stat from %s for pair %s ' % (name, pair), self.prefix)

        else:
            for pair in self.pairs:
                if pair in self.capi.pair_settings.keys():
                    try:
                        orders = self.capi.orders([pair])
                        trades = self.capi.trades([pair])
                        low_sell = orders[pair]['ask'][0][0]
                        top_buy = orders[pair]['bid'][0][0]
                        order_qt_sell = 0.0
                        order_qt_buy = 0.0
                        for order in orders[pair]['ask']:
                            order_qt_sell += order[1]
                        for order in orders[pair]['bid']:
                            order_qt_buy += order[1]
                        trade_qt_sell = 0.0
                        trade_qt_buy = 0.0
                        for trade in trades[pair]:
                            if trade['type'] == 'sell':
                                trade_qt_sell += trade['quantity']
                            elif trade['type'] == 'buy':
                                trade_qt_buy += trade['quantity']
                        data = (self.capi.name, pair, order_qt_sell, order_qt_buy, trade_qt_sell, trade_qt_buy, low_sell, top_buy)
                        self.logger.info('Received data: exchange: %s pair: %s %f %f %f %f %f %f' % data, self.prefix)
                        self.storage.save_stat(self.capi.name, pair, order_qt_sell, order_qt_buy, trade_qt_sell, trade_qt_buy,
                                               low_sell, top_buy)
                        self.logger.info('Stat data from %s for pair %s saved' % (self.capi.name, pair), self.prefix)
                    except Exception, ex:
                        self.logger.info('Error while get stat from %s for pair %s ' % (self.capi.name, pair), self.prefix)

        #удаление старых данных
        utmost_update = time.time() - self.store_time * 86400
        self.storage.delete_old_stat(utmost_update)
