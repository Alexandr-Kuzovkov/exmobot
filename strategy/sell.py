#coding=utf-8
import time
import math
import strategy.library.functions as Lib

'''
Продажа валюты если она есть на балансе и ранее покупалась
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    fee = 0.002
    name = 'sell'
    #флаг что не продавать в убыток
    session_id = 'default'
    limit = 1000000000.0
    #префикс для логгера
    prefix = ''
    #валюта которую нельзя выставлять на продажу
    hold_currency = None

    def __init__(self, capi, logger, storage, conf=None, **params):
        self.storage = storage
        self.capi = capi
        self.conf = conf
        self.logger = logger
        self.params = params

        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации

        #с какой валютной парой работаем
        self.pair = Lib.set_param(self, key='pair', default_value='BTC_USD')

        #id сессии
        self.session_id = Lib.set_param(self, key='session_id', default_value='0')

        # имя стратегии
        self.name = Lib.set_param(self, key='name', default_value=self.session_id + '->' + self.name)

        self.prefix = capi.name + ' ' + self.name

    '''
    функция реализующая торговую логику
    '''
    def run(self):

        logger = self.logger
        prefix = self.prefix
        pair = self.pair
        capi = self.capi

        #print mode, pair, session_id
        #return

        logger.info('-'*40, prefix)
        logger.info('Run strategy %s, pair: %s' % (self.name, pair), prefix)


        user_trades = self.capi.user_trades([self.pair])

        # минимальный баланс первой и второй валют в паре для создания ордера
        min_primary_balance, min_secondary_balance = capi.get_min_balance(pair)

        #получаем наличие своих средств
        balance = capi.balance()
        primary_balance = balance[pair.split('_')[0]]
        secondary_balance = balance[pair.split('_')[1]]

        logger.info('Balance with limit: %s = %f; %s = %f' % (pair.split('_')[0], primary_balance, pair.split('_')[1], secondary_balance), prefix)

        #комиссия
        try:
            self.fee = capi.fee[pair]
        except KeyError:
            self.fee = capi.fee['_'.join([pair.split('_')[1], pair.split('_')[0]])]

        logger.info('fee=%f' % self.fee, prefix)

        #logger.info(min_price_step)

        #logger.info(min_primary_balance)
        #logger.info(min_secondary_balance)

        #биржа с нормальным названием пар
        if self.capi.name not in ['poloniex']:
            #если есть на балансе первая валюта
            if primary_balance > min_primary_balance:
                new_ask = Lib.calc_price_sell(self, primary_balance, user_trades)
                if new_ask is None:
                    return False
                #ставим ордер на продажу
                Lib.order_create(self, 'sell', new_ask, primary_balance)

        #биржа с обратным название пар
        elif self.capi.name in ['poloniex']:

            #если есть на балансе первая валюта
            if secondary_balance > min_secondary_balance:
                new_ask = Lib.calc_price_sell(self, secondary_balance, user_trades)
                if new_ask is None:
                    return False
                #ставим ордер на продажу
                Lib.order_create(self, 'sell', new_ask, secondary_balance)

        else:
            #если неправильно задан mode
            raise Exception('incorrect capi.name value!')


