#coding=utf-8
import time
import math
import strategy.library.functions as Lib

'''
Алгоритм коридор2
Если есть валюта в паре, то ставим ордер на продажу по верхней границе
и ордер на покупку по нижней границе
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'corridor2'
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

        #флаг остановки торгов
        self.stop_trade = Lib.set_param(self, key='stop_trade', default_value=0, param_type='int')

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

        #если задан флаг остановки торгов удаляем все ордера по паре и выходим
        if self.stop_trade > 0:
            capi.orders_cancel(self.pair)
            logger.info('stopping trading...', self.prefix)
            return

        #получаем существующие ордера по валютной паре
        orders = capi.orders([pair])
        #print orders

        #получаем свои ордера
        user_orders = capi.user_orders()
        #проверяем цены ордеров текущим установкам, при несоответствии удаляем ордер
        if pair in user_orders: #если есть ордера
            logger.info('current orders: ', self.prefix)
            for user_order in user_orders[pair]:
                if user_order['type'] == 'sell':
                    logger.info('order type: %s, order price: %f, top_price: %f' % (user_order['type'], user_order['price'], self.top_price), self.prefix)
                    if user_order['price'] != self.top_price:
                        logger.info('order %i will removed' % user_order['order_id'], self.prefix)
                        capi.order_cancel(user_order['order_id'])
                        time.sleep(1)
                    else:
                        logger.info('order price match, keep it', self.prefix)


                else:
                    logger.info('order type: %s, order price: %f, low_price: %f' % (user_order['type'], user_order['price'], self.low_price), self.prefix)
                    if user_order['price'] != self.low_price:
                        logger.info('order %i will removed' % user_order['order_id'], self.prefix)
                        capi.order_cancel(user_order['order_id'])
                        time.sleep(1)
                    else:
                        logger.info('order price match, keep it', self.prefix)

        else: #если ордеров нет сохраняем сделки
            Lib.save_last_user_trades(self)


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
                res = Lib.order_create(self, 'buy', self.low_price, secondary_balance / self.low_price)
                if not res:
                    logger.info('Error create order %s for pair %s' % ('"BUY"', self.pair), self.prefix)

            if primary_balance > min_primary_balance: #если есть первая валюта
                res = Lib.order_create(self, 'sell', self.top_price, primary_balance)
                if not res:
                    logger.info('Error create order %s for pair %s' % ('"SELL"', self.pair), self.prefix)


        else:#если биржа с обратным названием пар

            if secondary_balance > min_secondary_balance: #если есть вторая валюта
                res = Lib.order_create(self, 'sell', self.top_price, secondary_balance)
                if not res:
                    logger.info('Error create order %s for pair %s' % ('"SELL"', self.pair), self.prefix)

            if primary_balance > min_primary_balance: #если есть первая валюта
                res = Lib.order_create(self, 'buy', self.low_price, primary_balance / self.low_price)
                if not res:
                    logger.info('Error create order %s for pair %s' % ('"BUY"', self.pair), self.prefix)