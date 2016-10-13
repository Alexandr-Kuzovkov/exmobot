#coding=utf-8
import time
import math

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
        self.pair = self.set_param(key='pair', default_value='BTC_USD')

        #id сессии
        self.session_id = self.set_param(key='session_id', default_value='0')

        # имя стратегии
        self.name = self.set_param(key='name', default_value=self.session_id + '->' + self.name)

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

        # минимальный баланс первой и второй валют в паре для создания ордера
        min_primary_balance, min_secondary_balance = capi.get_min_balance(pair, ask)

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
                new_ask = self.calc_price_sell(primary_balance, user_trades)
                if new_ask is None:
                    return False
                #ставим ордер на продажу
                self.order_create('sell', new_ask, primary_balance)

        #биржа с обратным название пар
        elif self.capi.name in ['poloniex']:

            #если есть на балансе первая валюта
            if secondary_balance > min_secondary_balance:
                new_ask = self.calc_price_sell(secondary_balance, user_trades)
                if new_ask is None:
                    return False
                #ставим ордер на продажу
                self.order_create('sell', new_ask, secondary_balance)

        else:
            #если неправильно задан mode
            raise Exception('incorrect capi.name value!')



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


    '''
    Округление числа
    '''
    def _round(self, number, prec):
        number = number * (10**prec)
        number = int(number)
        number = float(number) / (10**prec)
        return number


    '''
    создание ордера
    @param order_type ('sell'/'buy')
    @price цена
    @quantity количество
    '''
    def order_create(self, order_type, price, quantity):
        self.logger.info('Order create: pair=%s quantity=%f price=%f type=%s' % (self.pair, quantity, price, order_type),self.prefix)
        try:
            res = self.capi.order_create(pair=self.pair, quantity=quantity, price=price, order_type=order_type)
            if not res['result']:
                self.logger.info('Error order create "'+order_type+'": %s' % str(res['error']), self.prefix)
                return False
            else:
                self.logger.info('Order "'+order_type+'": %s: price=%f' % (self.pair, price), self.prefix)
                #сохраняем данные по поставленному ордеру
                self.storage.order_add(res['order_id'], self.pair, quantity, price, order_type, self.session_id)
                return True
        except Exception, ex:
            self.logger.info('Error order create "'+order_type+'": %s' % ex.message, self.prefix)
            return False


    '''
    получение минимальной цены продажи для обеспечения
    продажи не в убыток на основе истории сделок
    @param quantity количество первой валюты в паре
    '''
    def calc_price_sell(self, quantity, user_trades=None, limit=100):
        if user_trades is None:
            user_trades = self.capi.user_trades([self.pair], limit=limit)
        curr_quantity = 0.0
        curr_amount = 0.0
        if self.pair in user_trades:
            for trade in user_trades[self.pair]:
                if trade['type'] == 'sell' or trade['pair'] != self.pair:
                    continue
                curr_quantity += trade['quantity']
                curr_amount += trade['amount']
                if curr_quantity >= quantity:
                    break
            if curr_quantity == 0:
                return None
            price = curr_amount/curr_quantity * (1 + (2*self.fee + self.min_profit))
            return price
        else:
            return None
