#coding=utf-8

import strategy.flip as flip

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'unknown'
    mode = 0
    session_id = 'default'
    min_profit = 0.005
    limit = 1000000000.0
    #префикс для логгера
    prefix = ''


    def __init__(self, capi, logger, storage, conf=None, **params):
        self.storage = storage
        self.capi = capi
        self.conf = conf
        self.logger = logger
        self.params = params
        self.prefix = capi.name + ' ' + self.name
        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации


    def run(self):
        flip1 = flip.Strategy(self.capi, self.logger, self.storage, self.conf)
        flip1.run()
        #flip2 = flip.Strategy(self.capi, self.logger, self.storage, self.conf, mode=1)
        #flip2.run()
