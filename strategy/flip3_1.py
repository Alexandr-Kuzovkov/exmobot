#coding=utf-8
import time
import math
import strategy.library.functions as Lib

'''
Циклический обмен одной валюты на другую
с целью увеличить количество одной из валют (как правило обоих).
Модификация стратегии flip3.
Добавлена возможность настраивать запрет продажи в убыток
Отмена снятия ордеров на продажу при малом количестве валюты на нем
для предотвращения скопления малых количеств валют на балансах
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    fee = 0.002
    name = 'flip3_1'
    #флаг что не продавать в убыток
    not_loss = 1
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

        #флаг что не продавать в убыток
        self.not_loss = Lib.set_param(self, key='not_loss', default_value=1, param_type='int')

        #валюта которую нельзя выставлять на продажу (hold), может быть не одна
        self.hold_currency = Lib.set_param(self, key='hold_currency', default_value=None)
        if self.hold_currency is not None:
            self.hold_currency = map(lambda s: s.strip(), self.hold_currency.split(','))

        self.prefix = capi.name + ' ' + self.name

    '''
    функция реализующая торговую логику
    '''
    def run(self):

        #print mode, pair, session_id
        #return

        self.logger.info('-'*40, self.prefix)
        self.logger.info('Run strategy %s, pair: %s hold_currency %s' % (self.name, self.pair, str(self.hold_currency)), self.prefix)

        #удаляем неактуальные записи об ордерах
        Lib.delete_orders_not_actual(self)

        #удаляем все ордера по паре
        #self.capi.orders_cancel([pair])

        #получаем существующие ордера по валютной паре
        orders = self.capi.orders([self.pair])
        #print orders

        #получаем лучшие цены покупки и продажи
        try:
            ask = orders[self.pair]['ask'][0][0]
            bid = orders[self.pair]['bid'][0][0]
        except KeyError:
            ask = orders['_'.join([self.pair.split('_')[1], self.pair.split('_')[0]])]['ask'][0][0]
            bid = orders['_'.join([self.pair.split('_')[1], self.pair.split('_')[0]])]['bid'][0][0]

        self.logger.info('pair %s: ask=%f  bid=%f' % (self.pair, ask, bid), self.prefix)

        # минимальный баланс первой и второй валют в паре для создания ордера
        min_primary_balance, min_secondary_balance = self.capi.get_min_balance(self.pair)
        print min_primary_balance, min_secondary_balance

        # удаляем ордера по валютной паре, поставленные в своей сессии
        self.logger.info('Remove orders for pair %s in session %s' % (self.pair, self.session_id), self.prefix)
        Lib.delete_own_orders(self, min_primary_balance)
        time.sleep(3)

        #получаем наличие своих средств
        balance = self.capi.balance()
        primary_balance = min(balance[self.pair.split('_')[0]], self.limit/ask)
        secondary_balance = min(balance[self.pair.split('_')[1]], self.limit)

        # сохраняем в базу последние сделки
        user_trades = self.capi.user_trades([self.pair], limit=100)
        Lib.save_last_user_trades(self, user_trades)

        self.logger.info('Balance: %s = %f; %s = %f' % (self.pair.split('_')[0], balance[self.pair.split('_')[0]], self.pair.split('_')[1], balance[self.pair.split('_')[1]]), self.prefix)
        self.logger.info('Balance with limit: %s = %f; %s = %f' % (self.pair.split('_')[0], primary_balance, self.pair.split('_')[1], secondary_balance), self.prefix)

        #комиссия
        try:
            self.fee = self.capi.fee[self.pair]
        except KeyError:
            self.fee = self.capi.fee['_'.join([self.pair.split('_')[1], self.pair.split('_')[0]])]

        self.logger.info('fee=%f' % self.fee, self.prefix)

        #минимальный шаг
        try:
            if 'decimal_places' in self.capi.pair_settings[self.pair]:
                min_price_step = 1.0/(10**(self.capi.pair_settings[self.pair]['decimal_places']))
            else:
                min_price_step = 0.000001
        except KeyError:
            if 'decimal_places' in self.capi.pair_settings['_'.join([self.pair.split('_')[1], self.pair.split('_')[0]])]:
                min_price_step = 1.0/(10**(self.capi.pair_settings['_'.join([self.pair.split('_')[1], self.pair.split('_')[0]])]['decimal_places']))
            else:
                min_price_step = 0.000001

        #logger.info(min_price_step)



        #logger.info(min_primary_balance)
        #logger.info(min_secondary_balance)

        #биржа с нормальным названием пар
        if self.capi.name not in ['poloniex']:
            #если есть на балансе первая валюта
            if primary_balance > min_primary_balance:
                #новые цены продажи и покупки
                new_ask = ask - min_price_step
                new_bid = bid + min_price_step

                #еcли разрешено продавать в убыток
                if self.not_loss == 0:
                    #вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask/new_bid*(1-self.fee)*(1-self.fee) - 1
                    if profit <= self.min_profit:
                        #вычисляем цену продажи исходя из текущей цены покупки и небольшого профита
                        new_ask = new_bid * (1 + (2*self.fee + self.min_profit))
                #иначе ставим цену чтоб была прибыль
                else:
                    new_ask = self.calc_price_sell(primary_balance, user_trades)

                if new_ask is None:
                    new_ask = new_bid * (1 + (2*self.fee + self.min_profit))

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
                profit = new_ask/new_bid*(1-self.fee)*(1-self.fee) - 1
                if profit <= self.min_profit:
                    #если профита нет выставляем цену покупки ниже, на основе цены продажи и профита
                    new_bid = new_ask * (1 - (2*self.fee + self.min_profit))

                #если вторая валюта не является hold
                if (self.hold_currency is not None) and (self.pair.split('_')[1] in self.hold_currency):
                    self.logger.info('Currency %s is hold!' % self.pair.split('_')[1], self.prefix)
                else:
                    #выставляем ордер на покупку
                    Lib.order_create(self, 'buy', new_bid, secondary_balance/new_bid)


        #биржа с обратным название пар
        elif self.capi.name in ['poloniex']:
             #если есть на балансе вторая валюта
            if primary_balance > min_primary_balance:

                #новые цены продажи и покупки
                new_ask = ask - min_price_step
                new_bid = bid + min_price_step

                #вычисляем профит на основе верхней цены и нижней цены
                profit = new_ask/new_bid*(1-self.fee)*(1-self.fee) - 1
                if profit <= self.min_profit:
                    #вычисляем цену покупки исходя из текущей цены продажи и небольшого профита
                    new_bid = new_ask * (1 - (2*self.fee + self.min_profit))

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

                #еcли разрешено продавать в убыток
                if self.not_loss == 0:
                    #вычисляем профит на основе лучшей цены продажи и покупки
                    profit = new_ask/new_bid*(1-self.fee)*(1-self.fee) - 1
                    if profit <= self.min_profit:
                        #если профита нет выставляем цену продажи выше, на основе цены покупки и профита
                        new_ask = new_bid * (1 + (2*self.fee + self.min_profit))
                #иначе ставим цену чтоб была прибыль
                else:
                    new_ask = self.calc_price_sell(secondary_balance, user_trades)

                if new_ask is None:
                    new_ask = new_bid * (1 + (2*self.fee + self.min_profit))

                #если вторая валюта не является hold
                if (self.hold_currency is not None) and (self.pair.split('_')[1] in self.hold_currency):
                    self.logger.info('Currency %s is hold!' % self.pair.split('_')[1], self.prefix)
                else:
                    #ставим ордер на продажу
                    Lib.order_create(self, 'sell', new_ask, secondary_balance)

        else:
            #если неправильно задан mode
            raise Exception('incorrect capi.name value!')

