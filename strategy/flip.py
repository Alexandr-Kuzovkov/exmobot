#coding=utf-8
import time
import math
import strategy.library.functions as Lib

'''
Циклический обмен одной валюты на другую
с целью увеличить количество одной из валют,
названной базовой. Базовая определяется параметром
mode.
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
    name = 'flip'
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
        logger.info('Run strategy %s, pair: %s  mode: %i hold_currency %s' % (self.name, pair, mode, str(self.hold_currency)), prefix)

        #удаляем неактуальные записи об ордерах
        Lib.delete_orders_not_actual(self)

        #удаляем ордера по валютной паре, поставленные в своей сессии
        logger.info('Удаляем ордера по %s в сессии %s' % (pair, session_id), prefix)
        Lib.delete_own_orders(self)

        #удаляем все ордера по паре
        #capi.orders_cancel([pair])

        #получаем существующие ордера по валютной паре
        orders = capi.orders([pair])
        #print orders

        #получаем лучшие цены покупки и продажи
        ask = orders[pair]['ask'][0][0]
        bid = orders[pair]['bid'][0][0]
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
        fee = capi.fee[pair]

        #минимальный шаг
        if 'decimal_places' in capi.pair_settings[pair]:
            min_price_step = 1.0/(10**(capi.pair_settings[pair]['decimal_places']))
        else:
            min_price_step = 0.000001

        #logger.info(min_price_step)

        #минимальный баланс первой и второй валют в паре для создания ордера
        min_primary_balance, min_secondary_balance = capi.get_min_balance(pair)

        #logger.info(min_primary_balance)
        #logger.info(min_secondary_balance)

        #если наращиваем вторую валюту в паре(игра на повышении)
        if mode == 0:
            #получаем цену предыдущей покупки
            prev_price = storage.load(pair.split('_')[0] + '_buy_price', session_id)
            #logger.info('prev_price=%s' % str(prev_price), prefix)

            #если есть на балансе первая валюта
            if primary_balance > min_primary_balance:
                #новые цены продажи и покупки
                new_ask = ask - min_price_step
                new_bid = bid + min_price_step
                if prev_price is not None:
                    #если монеты уже покупались
                    #вычисляем профит на основе верхней цены продажи и цены покупки
                    profit = new_ask/prev_price*(1-fee)*(1-fee) - 1
                    if profit <= min_profit:
                        #если профита нет, то цену ставим побольше (пониже по стакану) но с профитом
                        new_ask = prev_price * (1 + (2*fee + min_profit))
                else:
                    #если монеты не покупались
                    #вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                    if profit <= min_profit:
                        #вычисляем цену продажи исходя из текущей цены покупки и небольшого профита
                        new_ask = new_bid * (1 + (2*fee + min_profit))

                #ставим ордер на продажу
                Lib.order_create(self,'sell', new_ask, primary_balance)
            else:
                #если первой валюты на балансе нет удаляем цену покупки
                storage.delete(pair.split('_')[0] + '_buy_price', session_id)
                #сохраняем баланс по второй валюте в базу
                Lib.save_change_balance(self, pair.split('_')[1], balance[pair.split('_')[1]])

            time.sleep(2)

            #если есть на балансе вторая валюта
            if secondary_balance > min_secondary_balance:
                #новые цены продажи и покупки
                new_ask = ask - min_price_step
                new_bid = bid + min_price_step
                #вычисляем профит на основе верхней цены и нижней цены
                profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                if profit <= min_profit:
                    #если профита нет выставляем цену покупки ниже, на основе цены продажи и профита
                    new_bid = new_ask * (1 - (2*fee + min_profit))
                #выставляем ордер на покупку и запоминаем цену покупки
                if Lib.order_create(self, 'buy', new_bid, secondary_balance/new_bid):
                    storage.save(pair.split('_')[0] + '_buy_price', new_bid, 'float', session_id)

            else:
                #сохраняем баланс по первой валюте в базу
                Lib.save_change_balance(self, pair.split('_')[0], balance[pair.split('_')[0]])

        #если наращиваем первую валюту в паре (игра на понижении)
        elif mode == 1:
             #если есть на балансе вторая валюта
            if secondary_balance > min_secondary_balance:
                #получаем цену предыдущей продажи
                prev_price = storage.load(pair.split('_')[0] + '_sell_price', session_id)
                #logger.info('prev_price=%s' % str(prev_price), prefix)

                #новые цены продажи и покупки
                new_ask = ask - min_price_step
                new_bid = bid + min_price_step

                if prev_price is not None:
                    #если монеты уже продавались
                    #вычисляем профит на основе верхней цены покупки и цены продажи
                    profit = prev_price/new_bid*(1-fee)*(1-fee) - 1
                    if profit <= min_profit:
                        #если профита нет, то цену ставим поменьше (пониже по стакану) но с профитом
                        new_bid = prev_price * (1 - (2*fee + min_profit))
                else:
                    #если монеты не продавались
                    #вычисляем профит на основе верхней цены и нижней цены
                    profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                    if profit <= min_profit:
                        #вычисляем цену покупки исходя из текущей цены продажи и небольшого профита
                        new_bid = new_ask * (1 - (2*fee + min_profit))

                #выставляем ордер на покупку
                Lib.order_create(self, 'buy', new_bid, secondary_balance/new_bid)

            else:
                #если второй валюты на балансе нет, то удаляем цену продажи
                storage.delete(pair.split('_')[0] + '_sell_price', session_id)
                #сохраняем баланс по первой валюте в базу
                Lib.save_change_balance(self, pair.split('_')[0], balance[pair.split('_')[0]])

            time.sleep(2)

            #если есть на балансе первая валюта
            if primary_balance > min_primary_balance:
                #новые цены продажи и покупки
                new_ask = ask - min_price_step
                new_bid = bid + min_price_step
                #вычисляем профит на основе лучшей цены продажи и покупки
                profit = new_ask/new_bid*(1-fee)*(1-fee) - 1
                if profit <= min_profit:
                    #если профита нет выставляем цену продажи выше, на основе цены покупки и профита
                    new_ask = new_bid * (1 + (2*fee + min_profit))
                #ставим ордер на продажу и запоминаем цену продажи
                if Lib.order_create(self, 'sell', new_ask, primary_balance):
                    storage.save(pair.split('_')[0] + '_sell_price', new_ask, 'float', session_id)
            else:
                #сохраняем баланс по второй валюте в базу
                Lib.save_change_balance(self, pair.split('_')[1], balance[pair.split('_')[1]])

        else:
            #если неправильно задан mode
            raise Exception('incorrect mode value: expected 0 or 1!')
