#coding=utf-8
import time
import math
import strategy.library.functions as Lib

'''
Алгоритм коридор
Покупаем если цена ниже заданного порога, продаем если цена выше заданного порога
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'corridor'
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

        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации

        #с какой валютной парой работаем
        self.pair = Lib.set_param(self, key='pair', default_value='BTC_USD')

        #минимальный профит при выставлении ордера не по верху стакана
        self.min_profit = Lib.set_param(self, key='min_profit', default_value=0.005, param_type='float')

        #id сессии
        self.session_id = Lib.set_param(self, key='session_id', default_value='0')

        # имя стратегии
        self.name = Lib.set_param(self, key='name', default_value=self.session_id + '->' + self.name)

        #лимит использования депозита по второй валюте в паре
        self.limit = Lib.set_param(self, key='limit', default_value=1000000000.0, param_type='float')

        #нижняя граница
        self.low_price = Lib.set_param(self, key='low_price', default_value=1000000000.0, param_type='float')

        #верхняя граница
        self.top_price = Lib.set_param(self, key='top_price', default_value=1000000000.0, param_type='float')

    '''
    функция реализующая торговую логику
    '''
    def run(self):

        logger = self.logger
        prefix = self.prefix
        pair = self.pair
        session_id = self.session_id
        capi = self.capi
        storage = self.storage
        limit = self.limit
        min_profit = self.min_profit

        #print mode, pair, session_id
        #return

        logger.info('-'*40, prefix)
        logger.info('Run strategy %s, pair: %s' % (self.name, pair), prefix)

        #удаляем все ордера по паре
        logger.info('Remove orders for pair %s' % pair, prefix)
        capi.orders_cancel([pair])


        #получаем существующие ордера по валютной паре
        orders = capi.orders([pair])
        #print orders

        #получаем лучшие цены покупки и продажи
        try:
            ask = orders[pair]['ask'][0][0]
            bid = orders[pair]['bid'][0][0]
        except KeyError:
            ask = orders['_'.join([pair.split('_')[1], pair.split('_')[0]])]['ask'][0][0]
            bid = orders['_'.join([pair.split('_')[1], pair.split('_')[0]])]['bid'][0][0]

        logger.info('pair %s: ask=%f  bid=%f' % (pair, ask, bid), prefix)
        logger.info('pair %s: low_price=%f  top_price=%f' % (pair, self.low_price, self.top_price), prefix)

        #получаем наличие своих средств
        balance = capi.balance()
        primary_balance = min(balance[pair.split('_')[0]], limit/ask)
        secondary_balance = min(balance[pair.split('_')[1]], limit)

        #сохраняем в базу последние сделки
        Lib.save_last_user_trades(self)

        logger.info('Balance: %s = %f; %s = %f' % (pair.split('_')[0], balance[pair.split('_')[0]], pair.split('_')[1], balance[pair.split('_')[1]]), prefix)
        logger.info('Balance with limit: %s = %f; %s = %f' % (pair.split('_')[0], primary_balance, pair.split('_')[1], secondary_balance), prefix)

        #комиссия
        try:
            fee = capi.fee[pair]
        except KeyError:
            fee = capi.fee['_'.join([pair.split('_')[1], pair.split('_')[0]])]

        logger.info('fee=%f' % fee, prefix)

        ticker = capi.ticker()
        #минимальный баланс первой и второй валют в паре для создания ордера
        min_primary_balance, min_secondary_balance = capi.get_min_balance(pair, ticker)
        logger.info('min_primary_balance %f' % min_primary_balance, prefix)
        logger.info('min_secondary_balance %f' % min_secondary_balance, prefix)

        # сохраняем балансы в базу для сбора статистики
        if primary_balance < min_primary_balance:
            Lib.save_change_balance(self, pair.split('_')[1], balance[pair.split('_')[1]])
        if secondary_balance < min_secondary_balance:
            Lib.save_change_balance(self, pair.split('_')[0], balance[pair.split('_')[0]])


        if capi.name not in ['poloniex']: #если биржа с нормальным названием пар

            if secondary_balance > min_secondary_balance: #если есть вторая валюта
                possable_amount = capi.possable_amount(pair.split('_')[1], pair.split('_')[0], secondary_balance, orders) #сколько можно купить на нее первой
                avg_price = secondary_balance / possable_amount #средняя цена будет
                logger.info('buy_avg_price=%f;  low_price=%f' % (avg_price, self.low_price), prefix)
                if avg_price <= self.low_price: #если средняя цена меньше нижней границы, то покупаем по рынку
                    chain = {'chain': [{'currency': pair.split('_')[0], 'order_type':'buy', 'pair': pair, 'parent':0, 'user':True}], 'profit': 0.0}
                    res = capi.execute_exchange_chain(chain, secondary_balance)
                    #если все успешно записываем в лог
                    if type(res) is dict and 'result' in res and res.result:
                        logger.info('%s was bought, balance %s=%f' % (pair.split('_')[0], pair.split('_')[0], res.amount), prefix)
                        #сохраняем в базу последние сделки
                        Lib.save_last_user_trades(self)
                    else:
                         logger.info('%error while exchange %s -> %s' % (pair.split('_')[1], pair.split('_')[0]), prefix)


            if primary_balance > min_primary_balance: #если есть первая валюта
                possable_amount = capi.possable_amount(pair.split('_')[0], pair.split('_')[1], primary_balance, orders) #сколько можно за нее получить второй
                avg_price = primary_balance / possable_amount #средняя цена будет
                logger.info('sell_avg_price=%f;  top_price=%f' % (avg_price, self.top_price), prefix)
                if avg_price >= self.top_price: #если средняя цена выше верхней границы, то продаем по рынку
                    chain = {'chain': [{'currency': pair.split('_')[1], 'order_type':'sell', 'pair': pair, 'parent':0, 'user':True}], 'profit': 0.0}
                    res = capi.execute_exchange_chain(chain, primary_balance)
                    #если все успешно записываем в лог
                    if type(res) is dict and 'result' in res and res.result:
                        logger.info('%s was sold, balance %s=%f' % (pair.split('_')[0], pair.split('_')[0], res.amount), prefix)
                        #сохраняем в базу последние сделки
                        Lib.save_last_user_trades(self)
                    else:
                        logger.info('%error while exchange %s -> %s' % (pair.split('_')[0], pair.split('_')[1]), prefix)


        else:#если биржа с обратным названием пар

            if primary_balance > min_primary_balance: #если есть вторая валюта
                possable_amount = capi.possable_amount(pair.split('_')[0], pair.split('_')[1], primary_balance, orders) #сколько можно купить на нее первой
                avg_price = primary_balance / possable_amount #средняя цена будет
                logger.info('buy_avg_price=%f;  low_price=%f' % (avg_price, self.low_price), prefix)
                if avg_price <= self.low_price: #если средняя цена меньше нижней границы, то покупаем по рынку
                    chain = {'chain': [{'currency': pair.split('_')[1], 'order_type':'buy', 'pair': pair, 'parent':0, 'user':True}], 'profit': 0.0}
                    res = capi.execute_exchange_chain(chain, primary_balance)
                    #если все успешно записываем в лог
                    if type(res) is dict and 'result' in res and res.result:
                        logger.info('%s was bought, balance %s=%f' % (pair.split('_')[1], pair.split('_')[1], res.amount), prefix)
                        #сохраняем в базу последние сделки
                        Lib.save_last_user_trades(self)
                    else:
                         logger.info('%error while exchange %s -> %s' % (pair.split('_')[0], pair.split('_')[1]), prefix)


            if secondary_balance > min_secondary_balance: #если есть первая валюта
                possable_amount = capi.possable_amount(pair.split('_')[1], pair.split('_')[0], secondary_balance, orders) #сколько можно за нее получить второй
                avg_price = secondary_balance / possable_amount #средняя цена будет
                logger.info('sell_avg_price=%f;  top_price=%f' % (avg_price, self.top_price), prefix)
                if avg_price >= self.top_price: #если средняя цена выше верхней границы, то продаем по рынку
                    chain = {'chain': [{'currency': pair.split('_')[0], 'order_type':'sell', 'pair': pair, 'parent':0, 'user':True}], 'profit': 0.0}
                    res = capi.execute_exchange_chain(chain, secondary_balance)
                    #если все успешно записываем в лог
                    if type(res) is dict and 'result' in res and res.result:
                        logger.info('%s was sold, balance %s=%f' % (pair.split('_')[1], pair.split('_')[1], res.amount), prefix)
                        #сохраняем в базу последние сделки
                        Lib.save_last_user_trades(self)
                    else:
                        logger.info('%error while exchange %s -> %s' % (pair.split('_')[1], pair.split('_')[0]), prefix)
