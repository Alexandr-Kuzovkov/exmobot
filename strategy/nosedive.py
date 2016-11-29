#coding=utf-8
import time
import math
import strategy.library.functions as Lib
from pprint import pprint

'''
Стратегия основанная на поиске резких провалов цены,
покупке и последующей продаже когда цена восстановится
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'nosedive'
    session_id = 'default'
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

        #id сессии
        self.session_id = Lib.set_param(self, key='session_id', default_value='0')
        self.session_id += ('-' + self.pair)

        #лимит использования депозита
        self.limit = Lib.set_param(self, key='limit', default_value=1000000000.0, param_type='float')

        self.prefix = capi.name + ' ' + self.name

        #отступ цены вниз от верха стакана в процентах
        self.margin_down_percent = Lib.set_param(self, key='margin_down_percent', default_value=3, param_type='float')

        #объем ордеров от верха стакана в единицах второй валюты, после которого будем ставитить ордер
        self.margin_down_volume = Lib.set_param(self, key='margin_down_volume', default_value=10, param_type='float')


    '''
    функция реализующая торговую логику
    '''
    def run(self):

        self.logger.info('-'*40, self.prefix)
        self.logger.info('Run strategy %s, pair: %s' % (self.name, self.pair), self.prefix)

        # удаляем неактуальные записи об ордерах
        Lib.delete_orders_not_actual(self)

        #Получаем ордера на покупку
        orders = self.capi.orders([self.pair])
        try:
            buy_orders = orders[self.pair]['bid']
        except KeyError:
             buy_orders = orders[Lib.reverse_pair(self.pair)]['bid']

        #минимальный баланс первой и второй валют в паре для создания ордера
        ticker = self.capi.ticker()
        min_primary_balance, min_secondary_balance = self.capi.get_min_balance(self.pair, ticker)

        #получаем комиссию
        self.fee = self.capi.fee[self.capi.check_pair(self.pair)]

        #удаляем все ордера по паре
        self.capi.orders_cancel([self.pair])

        #получаем наличие своих средств
        balance = self.capi.balance()
        primary_balance = balance[self.pair.split('_')[0]]
        secondary_balance = min(balance[self.pair.split('_')[1]], self.limit)

        #сохраняем в базу последние сделки
        Lib.save_last_user_trades(self)

        # сохраняем балансы в базу для сбора статистики
        if primary_balance < min_primary_balance:
            Lib.save_change_balance(self, self.pair.split('_')[1], balance[self.pair.split('_')[1]])
        if secondary_balance < min_secondary_balance:
            Lib.save_change_balance(self, self.pair.split('_')[0], balance[self.pair.split('_')[0]])

        self.logger.info('balance: %s=%f; %s=%f' % (self.pair.split('_')[0], primary_balance, self.pair.split('_')[1], secondary_balance), self.prefix)

        #если баланс по 2 валюте достаточен
        if secondary_balance >= min_secondary_balance:
            self.logger.info('buing %s' % self.pair.split('_')[0], self.prefix)
            #цена покупки по процентам
            buy_price_percent = buy_orders[0][0]*(1 - self.margin_down_percent/100.0)

            #цена покупки по сумме
            temp_amount = 0.0
            for row in buy_orders:
                order_price = row[0]
                order_quantity = row[1]
                order_amount = row[2]
                temp_amount += order_amount
                if temp_amount >= self.margin_down_volume:
                    buy_price_amount = order_price
                    break
            buy_price = min(buy_price_percent, buy_price_amount)

            self.logger.info('top_buy_price=%f; buy_price_percent=%f; buy_price_amount=%f' % (buy_orders[0][0], buy_price_percent, buy_price_amount), self.prefix)
            Lib.order_create(self, 'buy', buy_price, secondary_balance/buy_price)
            self.storage.save(self.session_id + 'buy_price', buy_price, 'float', self.session_id) #сохраняем закупочную цену

        #если баланс по первой валюте достаточен
        if primary_balance >= min_primary_balance:
            self.logger.info('checking selling %s profitness' % self.pair.split('_')[0], self.prefix)
            #получаем историю торгов по паре и сортируем по времени
            user_trades = self.capi.user_trades([self.pair])
            user_trades = sorted(user_trades[self.capi.check_pair(self.pair)], key=lambda row: -row['date'])
            #вычисляем сколько мы потратили  второй валюты на покупку имеющегося количества первой валюты (amount1)
            curr_quantity = 0.0
            amount1 = 0.0
            trades_data_valid = False
            for trade in user_trades:
                if trade['type'] == 'sell' or trade['pair'] != self.capi.check_pair(self.pair):
                    continue
                print 'quantity=%f; amount=%f' % (trade['quantity'], trade['amount'])
                curr_quantity += trade['quantity']
                amount1 += trade['amount']
                #print 'q=%f a=%f time=%s' % (trade['quantity'], trade['amount'], time.ctime(trade['date']))
                if Lib._round(curr_quantity * (1 - self.fee), 5) >= Lib._round(primary_balance, 5):
                    trades_data_valid = True
                    break
            #обрабатываем когда нет данных о сделках
            if not trades_data_valid:
                amount1 = self.storage.load(self.session_id + 'buy_price', self.session_id) * primary_balance
            #вычисляем из ордеров на покупку за сколько можно продать по рынку имеющееся количество первой валюты (amount2)
            amount2 = self.capi.possable_amount(self.pair.split('_')[0], self.pair.split('_')[1], primary_balance, orders)
            self.logger.info('amount1=%f; amount2=%f' % (amount1, amount2), self.prefix)
            if amount2 * (1 - self.fee) > amount1: #если цена восстановилась
                self.logger.info('selling %s by market' % self.pair.split('_')[0], self.prefix)
                #продаем по рынку первую валюту
                pair = self.capi.check_pair(self.pair)
                chain = {'chain': [{'pair': pair, 'currency': self.pair.split('_')[0], 'order_type': 'sell'}]}
                res = self.capi.execute_exchange_chain(chain, primary_balance)
                self.logger.info(str(res), self.prefix)

