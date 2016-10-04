#coding=utf-8

from pprint import pprint
import time

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'arbitrage'
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
        self.session_id = capi.name + '-' + self.name
        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации


    '''
    Округление числа
    '''
    def _round(self, number, prec):
        number = number * (10 ** prec)
        number = int(number)
        number = float(number) / (10 ** prec)
        return number

    '''
    функция реализующая торговую логику
    '''
    def run(self):
        #максимальная длина цепочки
        max_chain_len = self.set_param(key='max_chain_len', default_value=4, param_type='int')
        #сумма на входе цепочки
        start_amount = self.set_param(key='start_amount', default_value=10.0, param_type='float')
        #валюта на входе цепочки
        start_currency = self.set_param(key='start_currency', default_value='USD')

        try:
            chains = self.capi.search_exchains(start_currency, max_chain_len)
        except Exception, ex:
            self.logger.info('Error while search_exchains: %s' % ex)
        else:
            if len(chains) > 0:
                self.logger.info('%i profitable chains found, begin complete checking...' % len(chains), self.prefix)
                for i in range(len(chains)):
                    chains[i]['profit'] = self.capi.calc_chain_profit_real(chains[i], start_amount)
                str_chains = str(filter(chains, lambda chain: chain['profit'] > 0))
                str_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
                self.storage.save(str_time, str_chains)
                self.logger('Profitable chains: %s' % str_chains)
            else:
                self.logger.info('Profitable chains not found...', self.prefix)


    '''
    установка значения параметра
    @param key имя параметра
    @param default_value значение по умолчанию
    @param param_type тип
    @return значение параметра
    '''
    def set_param(self, key, default_value, param_type=None):
        if key in self.params:
            param = self.params[key]
        elif self.conf.has_option('common', key):
            param = self.conf.get('common', key)
        else:
            param = default_value
        if param_type is not None:
            if param_type == 'int':
                param = int(param)
            elif param_type == 'float':
                param = float(param)
            else:
                param = str(param)
        return param

