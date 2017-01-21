#coding=utf-8
import time
import math
import strategy.library.functions as Lib

'''
Циклический обмен одной валюты на другую
с целью увеличить количество одной из валют.
Модификация стратегии flip3.
Добавлена автоматическая смена порядка валют в паре при несоответствии
(актуально для Poloniex.com)
добавлено hold_currency
добавлено определение и учет тренда
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'flip5'
    session_id = 'default'
    min_profit = 0.005
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

        #минимальный профит при выставлении ордера не по верху стакана
        self.min_profit = Lib.set_param(self, key='min_profit', default_value=0.005, param_type='float')

        #id сессии
        self.session_id = Lib.set_param(self, key='session_id', default_value='0')

        # имя стратегии
        self.name = Lib.set_param(self, key='name', default_value=self.session_id + '->' + self.name)

        #лимит использования депозита по второй валюте в паре
        self.limit = Lib.set_param(self, key='limit', default_value=1000000000.0, param_type='float')

        #валюта которую нельзя выставлять на продажу (hold), может быть не одна
        self.hold_currency = Lib.set_param(self, key='hold_currency', default_value=None)
        if self.hold_currency is not None:
            self.hold_currency = map(lambda s: s.strip(), self.hold_currency.split(','))

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
        logger.info('Run strategy %s, pair: %s  mode: %i hold_currency %s' % (self.name, pair, mode, str(self.hold_currency)), prefix)

        #удаляем неактуальные записи об ордерах
        Lib.delete_orders_not_actual(self)

        #удаляем ордера по валютной паре, поставленные в своей сессии
        logger.info('Remove orders for pair %s in session %s' % (pair, session_id), prefix)
        Lib.delete_own_orders(self)
        time.sleep(3)

        #удаляем все ордера по паре
        #capi.orders_cancel([pair])

        #получаем существующие ордера по валютной паре
        orders = capi.orders([pair])
        #print orders

        #получаем историю торгов
        trades = capi.trades([pair])

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

        logger.info('fee=%f' % fee, prefix)

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

        logger.info('min_price_step %f' % min_price_step, prefix)

        #минимальный баланс первой и второй валют в паре для создания ордера
        min_primary_balance, min_secondary_balance = capi.get_min_balance(pair)

        logger.info('min_primary_balance %f' % min_primary_balance, prefix)
        logger.info('min_secondary_balance' % min_secondary_balance, prefix)

        #сохраняем балансы в базу для сбора статистики
        if primary_balance < min_primary_balance:
            Lib.save_change_balance(self, pair.split('_')[1], balance[pair.split('_')[1]])
        if secondary_balance < min_secondary_balance:
            Lib.save_change_balance(self, pair.split('_')[0], balance[pair.split('_')[0]])

        Lib.save_statistic_data(self, orders=orders, trades=trades, store_time=5)
        price_trend = Lib.detect_marker_direct(self, pair=pair, time_interval=30)


        if price_trend is not None and price_trend >= 0: #тренд восходящий
            logger.info('trend is bull(up)', prefix)
            #биржа с нормальным названием пар
            if self.capi.name not in ['poloniex']:
                #если есть на балансе первая валюта
                if primary_balance > min_primary_balance:
                    #новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step

                    #вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                    if profit <= min_profit:
                        #вычисляем цену продажи исходя из текущей цены покупки и небольшого профита
                        new_ask = new_bid * (1 + (2*fee + min_profit))

                    #если первая валюта не является hold
                    if (self.hold_currency is not None) and (self.pair.split('_')[0] in self.hold_currency):
                        self.logger.info('Currency %s is hold!' % self.pair.split('_')[0], self.prefix)
                    else:
                        #ставим ордер на продажу
                        Lib.order_create(self, 'sell', new_ask, primary_balance)

                time.sleep(2)

                #если есть на балансе вторая валюта
                if secondary_balance > min_secondary_balance:
                    #новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step
                    #вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                    # выставляем цену покупки по верху стакана
                    #если вторая валюта не является hold
                    if (self.hold_currency is not None) and (self.pair.split('_')[1] in self.hold_currency):
                        self.logger.info('Currency %s is hold!' % self.pair.split('_')[1], self.prefix)
                    else:
                        #выставляем ордер на покупку
                        Lib.order_create(self, 'buy', new_bid, secondary_balance/new_bid)


            #биржа с обратным название пар
            else:
                 #если есть на балансе вторая валюта
                if primary_balance > min_primary_balance:

                    #новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step

                    #вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask/new_bid*(1-fee)*(1-fee) - 1

                    #ставим цену покупки по верху стакана

                    # если первая валюта не является hold
                    if (self.hold_currency is not None) and (self.pair.split('_')[0] in self.hold_currency):
                        self.logger.info('Currency %s is hold!' % self.pair.split('_')[0], self.prefix)
                    else:
                        #выставляем ордер на покупку
                        Lib.order_create(self, 'buy', new_bid, primary_balance/new_bid)

                time.sleep(2)

                #если есть на балансе первая валюта
                if secondary_balance > min_secondary_balance:
                    #новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step
                    #вычисляем профит на основе лучшей цены продажи и покупки
                    profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                    if profit <= min_profit:
                        #если профита нет выставляем цену продажи выше, на основе цены покупки и профита
                        new_ask = new_bid * (1 + (2*fee + min_profit))

                    #если вторая валюта не является hold
                    if (self.hold_currency is not None) and (self.pair.split('_')[1] in self.hold_currency):
                        self.logger.info('Currency %s is hold!' % self.pair.split('_')[1], self.prefix)
                    else:
                        #ставим ордер на продажу
                        Lib.order_create(self, 'sell', new_ask, secondary_balance)
        elif price_trend is not None and price_trend < 0: #тренд нисходящий
            logger.info('trend is bear(down)', prefix)
            # биржа с нормальным названием пар
            if self.capi.name not in ['poloniex']:
                # если есть на балансе первая валюта
                if primary_balance > min_primary_balance:
                    # новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step

                    # вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask / new_bid * (1 - fee) * (1 - fee) - 1

                    #ставим цену продажи по верху стакана

                    # если первая валюта не является hold
                    if (self.hold_currency is not None) and (self.pair.split('_')[0] in self.hold_currency):
                        self.logger.info('Currency %s is hold!' % self.pair.split('_')[0], self.prefix)
                    else:
                        # ставим ордер на продажу
                        Lib.order_create(self, 'sell', new_ask, primary_balance)

                time.sleep(2)

                # если есть на балансе вторая валюта
                if secondary_balance > min_secondary_balance:
                    # новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step
                    # вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask / new_bid * (1 - fee) * (1 - fee) - 1
                    if profit <= min_profit:
                        # если профита нет выставляем цену покупки ниже, на основе цены продажи и профита
                        new_bid = new_ask * (1 - (2 * fee + min_profit))

                    # если вторая валюта не является hold
                    if (self.hold_currency is not None) and (self.pair.split('_')[1] in self.hold_currency):
                        self.logger.info('Currency %s is hold!' % self.pair.split('_')[1], self.prefix)
                    else:
                        # выставляем ордер на покупку
                        Lib.order_create(self, 'buy', new_bid, secondary_balance / new_bid)


            # биржа с обратным название пар
            else:
                # если есть на балансе вторая валюта
                if primary_balance > min_primary_balance:

                    # новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step

                    # вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask / new_bid * (1 - fee) * (1 - fee) - 1
                    if profit <= min_profit:
                        # вычисляем цену покупки исходя из текущей цены продажи и небольшого профита
                        new_bid = new_ask * (1 - (2 * fee + min_profit))

                    # если первая валюта не является hold
                    if (self.hold_currency is not None) and (self.pair.split('_')[0] in self.hold_currency):
                        self.logger.info('Currency %s is hold!' % self.pair.split('_')[0], self.prefix)
                    else:
                        # выставляем ордер на покупку
                        Lib.order_create(self, 'buy', new_bid, primary_balance / new_bid)

                time.sleep(2)

                # если есть на балансе первая валюта
                if secondary_balance > min_secondary_balance:
                    # новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step
                    # вычисляем профит на основе лучшей цены продажи и покупки
                    profit = new_ask / new_bid * (1 - fee) * (1 - fee) - 1

                    #ставим цену продажи по верху стакана

                    # если вторая валюта не является hold
                    if (self.hold_currency is not None) and (self.pair.split('_')[1] in self.hold_currency):
                        self.logger.info('Currency %s is hold!' % self.pair.split('_')[1], self.prefix)
                    else:
                        # ставим ордер на продажу
                        Lib.order_create(self, 'sell', new_ask, secondary_balance)


        else: #тренд не определен
            logger.info('trend not defined', prefix)
            #вычисляем цены покупки и продажи
            prices = Lib.calc_prices(self, orders, min_price_step, fee)
            new_ask = prices['ask']
            new_bid = prices['bid']
            logger.info('new_ask=%f  new_bid=%f' % (new_ask, new_bid), prefix)

            #если есть на балансе первая валюта
            if primary_balance > min_primary_balance:
                #ставим ордер на продажу
                Lib.order_create(self, 'sell', new_ask, primary_balance)

            time.sleep(2)

            #если есть на балансе вторая валюта
            if secondary_balance > min_secondary_balance:
                #выставляем ордер на покупку
                Lib.order_create(self, 'buy', new_bid, secondary_balance/new_bid)
