#coding=utf-8
import time
import math
import strategy.library.functions as Lib

'''
Циклический обмен одной валюты на другую
с целью увеличить количество одной из валют,
названной базовой. Базовая определяется параметром
mode.
Модификация стратегии flip3. Изменен алгоритм расчета цен ордеров на покупку и продажу
Добавлена автоматическая смена порядка валют в паре при несооответсвии
0 - увеличиваем вторую валюту в паре: покупаем дешевле, продаем дороже
1 - увеличиваем первую валюту в паре: продаем дороже, покупаем дешевле
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'flip4'
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

        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации

        #с какой валютной парой работаем
        self.pair = Lib.set_param(self, key='pair', default_value='BTC_USD')

        #имя стратегии
        self.name = Lib.set_param(self, key='name', default_value=self.name)

        #режим обмена
        self.mode = Lib.set_param(self, key='mode', default_value=0, param_type='int')

        #минимальный профит при выставлении ордера не по верху стакана
        self.min_profit = Lib.set_param(self, key='min_profit', default_value=0.005, param_type='float')

        #id сессии
        self.session_id = Lib.set_param(self, key='session_id', default_value='0')

        #лимит использования депозита по второй валюте в паре
        self.limit = Lib.set_param(self, key='limit', default_value=1000000000.0, param_type='float')

        self.prefix = capi.name + ' ' + self.name

    '''
    функция реализующая торговую логику
    '''
    def run(self):

        logger = self.logger
        prefix = self.prefix
        pair = self.pair
        mode = self.mode
        session_id = self.session_id
        capi = self.capi
        storage = self.storage
        limit = self.limit
        min_profit = self.min_profit

        #print mode, pair, session_id
        #return

        logger.info('-'*40, prefix)
        logger.info('Run strategy %s, pair: %s  mode: %i' % (self.name, pair, mode), prefix)

        #удаляем неактуальные записи об ордерах
        Lib.delete_orders_not_actual(self)

        #удаляем ордера по валютной паре, поставленные в своей сессии
        logger.info('Удаляем ордера по %s в сессии %s' % (pair, session_id), prefix)
        Lib.delete_own_orders(self)
        time.sleep(3)

        #удаляем все ордера по паре
        #capi.orders_cancel([pair])

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

        #минимальный шаг
        try:
            if 'decimal_places' in capi.pair_settings[pair]:
                min_price_step = 1.0/(10**(capi.pair_settings[pair]['decimal_places']))
            else:
                min_price_step = 0.000001
        except KeyError:
            if 'decimal_places' in capi.pair_settings['_'.join([pair.split('_')[1], pair.split('_')[0]])]:
                min_price_step = 1.0/(10**(capi.pair_settings['_'.join([pair.split('_')[1], pair.split('_')[0]])]['decimal_places']))
            else:
                min_price_step = 0.000001

        #logger.info(min_price_step)

        #минимальный баланс первой и второй валют в паре для создания ордера
        min_primary_balance, min_secondary_balance = capi.get_min_balance(pair)

        #logger.info(min_primary_balance)
        #logger.info(min_secondary_balance)

        #сохраняем балансы в базу для сбора статистики
        if primary_balance < min_primary_balance:
            Lib.save_change_balance(self, pair.split('_')[1], balance[pair.split('_')[1]])
        if secondary_balance < min_secondary_balance:
            Lib.save_change_balance(self, pair.split('_')[0], balance[pair.split('_')[0]])

        #вычисляем цены покупки и продажи
        prices = Lib.calc_prices(self, orders, min_price_step, fee)
        new_ask = prices['ask']
        new_bid = prices['bid']
        logger.info('new_ask=%f  new_bid=%f' % (new_ask, new_bid), prefix)

        #если наращиваем вторую валюту в паре(игра на повышении)
        if mode == 0:
            #если есть на балансе первая валюта
            if primary_balance > min_primary_balance:
                #ставим ордер на продажу
                Lib.order_create(self, 'sell', new_ask, primary_balance)

            time.sleep(2)

            #если есть на балансе вторая валюта
            if secondary_balance > min_secondary_balance:
                #выставляем ордер на покупку
                Lib.order_create(self, 'buy', new_bid, secondary_balance/new_bid)


        #если наращиваем первую валюту в паре (игра на понижении)
        elif mode == 1:
             #если есть на балансе вторая валюта
            if secondary_balance > min_secondary_balance:
                #выставляем ордер на покупку
                Lib.order_create(self, 'buy', new_bid, secondary_balance/new_bid)

            time.sleep(2)

            #если есть на балансе первая валюта
            if primary_balance > min_primary_balance:
                #ставим ордер на продажу
                Lib.order_create(self, 'sell', new_ask, primary_balance)

        else:
            #если неправильно задан mode
            raise Exception('incorrect mode value: expected 0 or 1!')

