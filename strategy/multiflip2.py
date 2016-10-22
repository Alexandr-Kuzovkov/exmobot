#coding=utf-8

'''
Стратегия поиска валютных пар на которых есть профитный спред
и запуск на них стратегии циклического обмена flip3_1
На непрофитных парах создаем ордера на продажу ранее купленной валюты
'''

import strategy.flip3_1 as flip3
import strategy.sell as sell1
import strategy.library.functions as Lib
from pprint import pprint

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'multiflip2'
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
        self.session_id = capi.name + '-' + self.name
        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации


    '''
    функция реализующая торговую логику
    '''
    def run(self):
        self.logger.info('-' * 40, self.prefix)
        self.logger.info('Run strategy %s' % self.name, self.prefix)
        ticker = self.capi.ticker()

        balance = self.capi.balance()
        #получаем профитные пары
        profit_pairs = Lib.get_profit_pairs(self, ticker, balance)
        self.logger.info('Pairs for trading: %s' % str(map(lambda e: e['pair'], profit_pairs)), self.prefix)
        #pprint(profit_pairs)

        # сохраняем балансы в базу для сбора статистики
        balance_usd = self.capi.balance_full_usd(ticker)
        if self.capi.name == 'poloniex':
            Lib.save_change_balance2(self, 'USDT', balance_usd)
        else:
            Lib.save_change_balance2(self, 'USD', balance_usd)

        #запускаем торговлю для всех профитных пар
        pairs_with_profit = []
        for pair in profit_pairs:
            pairs_with_profit.append(pair['pair'])
            flip = flip3.Strategy(self.capi, self.logger, self.storage, self.conf, pair=pair['pair'])
            flip.run()

        #ставим ордера на продажу на непрофитных парах
        balance = self.capi.balance()
        pairs_with_balance = filter(lambda pair: balance[pair.split('_')[0]] > self.capi.get_min_balance(pair, ticker)[0] or balance[pair.split('_')[1]] > self.capi.get_min_balance(pair, ticker)[1], self.capi.pair_settings.keys())
        for pair in pairs_with_balance:
            if pair in pairs_with_profit:
                continue
            sell = sell1.Strategy(self.capi, self.logger, self.storage, self.conf, pair=pair)
            sell.run()





