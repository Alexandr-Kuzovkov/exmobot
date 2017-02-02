#coding=utf-8
import time
import strategy.library.functions as Lib

'''
Циклический обмен одной валюты на другую
с целью увеличить количество одной из валют.
Модификация стратегии flip3.
Добавлена автоматическая смена порядка валют в паре при несоответствии
(актуально для Poloniex.com).
Работа на заданных парах.
Не продаем в убыток (ордера на продажу не отменяются)
Работа на паре если есть профит
'''

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pairs = []
    pair = None
    name = 'flip6'
    session_id = 'default'
    min_profit = 0.001
    limit = 1000000000.0
    #префикс для логгера
    prefix = ''
    stop_trade = 0

    def __init__(self, capi, logger, storage, conf=None, **params):
        self.storage = storage
        self.capi = capi
        self.conf = conf
        self.logger = logger
        self.params = params

        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации

        #список валютных пар для работы
        self.pairs = Lib.set_param(self, key='pairs', default_value='BTC_USD')
        self.pairs = map(lambda s: s.strip(), self.pairs.split(','))

        #минимальный профит при выставлении ордера не по верху стакана
        self.min_profit = Lib.set_param(self, key='min_profit', default_value=0.001, param_type='float')

        #id сессии
        self.session_id = Lib.set_param(self, key='session_id', default_value='0')

        # имя стратегии
        self.name = Lib.set_param(self, key='name', default_value=self.session_id + '->' + self.name)

        #лимит использования депозита по второй валюте в паре
        self.limit = Lib.set_param(self, key='limit', default_value=1000000000.0, param_type='float')

        self.prefix = capi.name + ' ' + self.name

        # флаг остановки торгов
        self.stop_trade = Lib.set_param(self, key='stop_trade', default_value=0, param_type='int')

    '''
    функция реализующая торговую логику
    '''
    def run(self):

        #print mode, pair, session_id
        #return

        self.logger.info('-'*40, self.prefix)
        self.logger.info('Run strategy %s, pairs: %s' % (self.name, str(self.pairs)), self.prefix)

        #получаем свои ордера
        user_orders = self.capi.user_orders()

        #удаляем неактуальные записи об ордерах в базе
        Lib.delete_orders_not_actual(self, user_orders)

        #получаем ticker
        ticker = self.capi.ticker()

        #удаляем ордера "BUY"
        for pair, user_orders_for_pair in user_orders.items():
            for user_order_for_pair in user_orders_for_pair:
                if user_order_for_pair['type'] == 'buy':
                    order_id = int(user_order_for_pair['order_id'])
                    res = self.capi.order_cancel(order_id)
                    if 'result' in res and res['result'] == True:
                        self.logger.info('order "BUY" id=%i removed succesfully' % order_id, self.prefix)
                    else:
                        self.logger.info('ERROR while removing order "BUY" id=%i' % order_id, self.prefix)

        if self.stop_trade > 0:
            self.logger.info('Stopping trade...')
            return

        #перебираем пары с которыми работаем
        for pair in self.pairs:
            self.pair = pair
            # получаем наличие своих средств
            balance = self.capi.balance()
            ask = max(ticker[pair]['sell_price'], ticker[pair]['buy_price'])
            bid = min(ticker[pair]['sell_price'], ticker[pair]['buy_price'])
            primary_balance = min(balance[pair.split('_')[0]], self.limit / ask)
            secondary_balance = min(balance[pair.split('_')[1]], self.limit)

            self.logger.info('pair %s, ask = %f, bid = %f' %(pair, ask, bid), self.prefix)
            self.logger.info('Balance: %s = %f; %s = %f' % (pair.split('_')[0], balance[pair.split('_')[0]], pair.split('_')[1], balance[pair.split('_')[1]]), self.prefix)
            self.logger.info('Balance with limit: %s = %f; %s = %f' % (pair.split('_')[0], primary_balance, pair.split('_')[1], secondary_balance), self.prefix)

            #комиссия
            try:
                fee = self.capi.fee[pair]
            except KeyError:
                fee = self.capi.fee['_'.join([pair.split('_')[1], pair.split('_')[0]])]

            self.logger.info('fee=%f' % fee, self.prefix)

            #минимальный шаг
            try:
                if 'decimal_places' in self.capi.pair_settings[pair]:
                    min_price_step = 1.0/(10**(self.capi.pair_settings[pair]['decimal_places']))
                else:
                    min_price_step = 0.000001
            except KeyError:
                if 'decimal_places' in self.capi.pair_settings['_'.join([pair.split('_')[1], pair.split('_')[0]])]:
                    min_price_step = 1.0/(10**(self.capi.pair_settings['_'.join([pair.split('_')[1], pair.split('_')[0]])]['decimal_places']))
                else:
                    min_price_step = 0.000001

            #logger.info(min_price_step)

            #минимальный баланс первой и второй валют в паре для создания ордера
            min_primary_balance, min_secondary_balance = self.capi.get_min_balance(pair, ticker)
            profit = (ask - min_price_step) / (bid + min_price_step) * (1-fee) * (1-fee) - 1.0
            self.logger.info('Profit on pair %s = %f' % (pair, profit), self.prefix)

            #logger.info(min_primary_balance)
            #logger.info(min_secondary_balance)

            #биржа с нормальным названием пар
            if self.capi.name not in ['poloniex']:
                # если разбег цен обеспечивает профит и вторая валюта есть
                if secondary_balance >= min_secondary_balance and profit >= self.min_profit:
                    #новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step
                    # выставляем ордер на покупку
                    Lib.order_create(self, 'buy', new_bid, secondary_balance / new_bid)
                    #сохраняем данные по цене
                    self.storage.save(pair + '_ask', new_ask, 'float')
                    self.storage.save(pair + '_bid', new_bid, 'float')
                else:
                    self.logger.info('No profit or no balance, no action required...', self.prefix)

                time.sleep(2)

                # если есть на балансе первая валюта
                if primary_balance >= min_primary_balance:
                    saved_ask = self.storage.load(pair + '_ask')
                    if saved_ask is None:
                        saved_ask = 0.0
                    sell_price = max(saved_ask, ask - min_price_step)
                    # ставим ордер на продажу
                    Lib.order_create(self, 'sell', sell_price, primary_balance)


            #биржа с обратным названием пар
            elif self.capi.name in ['poloniex']:
                # если есть на балансе первая валюта
                if primary_balance >= min_primary_balance and profit >= self.min_profit:
                    # новые цены продажи и покупки
                    new_ask = ask - min_price_step
                    new_bid = bid + min_price_step
                    # выставляем ордер на покупку
                    Lib.order_create(self, 'buy', new_bid, primary_balance / new_bid)
                    # сохраняем данные по цене
                    self.storage.save(pair + '_ask', new_ask, 'float')
                    self.storage.save(pair + '_bid', new_bid, 'float')
                else:
                    self.logger.info('No profit or no balance, no action required...', self.prefix)

                time.sleep(2)

                if secondary_balance >= min_secondary_balance:
                    saved_ask = self.storage.load(pair + '_ask')
                    if saved_ask is None:
                        saved_ask = 0.0
                    sell_price = max(saved_ask, ask - min_price_step)
                    # ставим ордер на продажу
                    Lib.order_create(self, 'sell', sell_price, secondary_balance)

        #сохраняем последние сделки
        Lib.save_last_user_trades2(self)

        #сохраняем балансы для статистики
        balance_full = self.capi.balance_full()
        full_usd_balance = self.capi.balance_full_usd(balance_full, ticker)
        full_btc_balance = self.capi.balance_full_btc(balance_full, ticker)
        Lib.save_change_balance(self, 'USD', full_usd_balance)
        Lib.save_change_balance(self, 'BTC', full_btc_balance)

