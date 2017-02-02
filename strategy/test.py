#coding=utf-8
import random
from pprint import pprint
import time
from sms import smsru
import strategy.library.functions as Lib


class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'unknown'
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
        self.prefix = self.name

        #ввод параметров
        #id сессии
        self.session_id = Lib.set_param(self, key='session_id', default_value='0')
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации


    def run(self):

        capi = self.capi
        storage = self.storage
        logger = self.logger

        #print capi.delete_orders(['BTC_USD'])
        #print action.delete_orders_for_pair('ETH_USD')
        #print capi.orders_balance()

        '''
        user_info = exmo.user_info()
        eth_amount = user_info['balances']['ETH']

        price =11.29897
        pair = 'ETH_USD'
        order_type = 'sell'
        quantity = eth_amount

        print exmo.order_create(pair=pair, price=price, order_type= order_type, quantity=eth_amount)

        '''

        #print capi.user_orders()
        #print capi.ticker()
        #print capi.user_trades(['BTC_USD'])
        #print capi.user_cancelled_orders(100000, 1000)
        #print capi.order_trades(48267083)
        #print capi.required_amount('BTC_USD', 1)
        #logger.info(res)
        #print res
        #print capi.
        #print capi.order_trades()
        '''
        storage.save('key1', 'value1')
        storage.save('key2', 'value1')
        print storage.load('key2')
        print storage.get_utime('key2')
        storage.delete('key2')

        #print capi.balance_full()

        ids = random.randrange(100000, 200000, 1)
        storage.order_add(ids, 'ETH_USD', 10.5, 12.45, 'sell', '123')
        storage.order_add(ids+1, 'BTC_USD', 1.1, 645.45, 'sell', '123')
        print storage.orders(session_id='123')
        print '-' * 40
        print storage.orders(pair='LTC_USD', session_id='123')
        storage.order_delete(pair='BTC_USD', session_id='123')
        storage.old_orders_delete(utime=1469620306, pair='ETH_USD', session_id='123')
        '''
        #print capi.order_cancel(123)
        #удаляем неактуальные записи об ордерах
        '''
        session_id='123'
        user_orders = capi.user_orders()
        print user_orders
        stored_orders = storage.orders(session_id='123')
        print stored_orders
        for stored_order in stored_orders:
            order_exists = False
            for user_order_for_pair in user_orders[stored_order['pair']]:
                if user_order_for_pair['order_id'] == stored_order['order_id'] and user_order_for_pair['type'] == stored_order['order_type']:
                    order_exists = True
            print order_exists
            if not order_exists:
                storage.order_delete(pair=stored_order['pair'], order_id=stored_order['order_id'], session_id=session_id)
        '''

        #pprint(capi.trades(['BTC_USD', 'ETH_USD'], limit=10))
        #pprint(capi.orders(['BTC_USD', 'ETH_USD'], limit=5))
        #pprint(capi.ticker())
        #pprint(capi.balance())
        #pprint(capi.user_orders())
        #pprint(capi.order_create(pair='USD_RUR', quantity=1, price=63.25, order_type='buy'))
        #pprint(capi.order_cancel(1166872879))
        #pprint(capi.orders_cancel())
        #pprint(capi.orders_cancel())
        #pprint(capi.required_amount('USD_RUR', 10000))
        #pprint(capi.order_create(pair='ETH_USD', quantity=capi.balance('ETH'), price=11.499, order_type='sell'))
        #print capi.balance()
        #pprint(capi.user_orders())
        #pprint(capi.user_trades(['ETH_USD'],limit=3))


        #storage.save_balance('ETH', 0.25)
        #self.save_change_balance('ETH', 0.26)
        #time.sleep(2)
        #storage.save_balance('ETH', 0.34)

        #storage.delete_old_values(['balance'], time.time()-3, True)
        #pprint(storage.get_last_balance('USD', 3, 'test'))



        #user_trades = capi.user_trades(['BTC_USD'])
        #pprint(user_trades)
        #storage.save_user_trades(user_trades['BTC_USD'])

        #storage.delete_old_values(['user_trades'], time.time()-3, False, 'test')
        #pprint(storage.get_last_user_trades(pair=None, limit=5))

        #min_primary_balance, min_secondary_balance = capi.get_min_balance('ETH_USD', 11.1)
        #print min_primary_balance, min_secondary_balance

        #storage.clear_all()

        '''
        отправка СМС
        cli = smsru.Client()
        res = cli.send("+79877171421", u'miner fail')
        print res0
        '''

        #pprint(capi.pair_settings.keys())
        #pprint(capi.get_min_balance('USDT_ETH', 11.2))
        #pprint(capi.trades(['USDT_ETH']))
        #pprint(capi._date2timestamp('2016-08-15 13:04:53'))
        #pprint(capi.orders(['BTC_USD']))
        #pprint(capi.ticker())
        #pprint(capi.balance('BTC'))
        #pprint(capi.orders_balance('ETH'))
        #pprint(capi.balance_full())
        #pprint(capi.required_amount('USDT_ETH', 10))
        #pprint(capi.user_trades(['USDT_ETH','BTC_ETH']))
        #pprint(capi.user_trades(['BTC_USD']))
        #pprint(capi.user_trades())
        #self.session_id = 'poloniex-1'
        #pprint(capi.user_orders())
        #pprint(capi.orders_cancel(['BTC_ETH']))
        #pprint(capi.order_create('BTC_ETH',1.15863329, 0.01857750, 'buy'))
        #pprint(capi._check_pair('ETH_BTC'))

        '''
        if capi.name in ['poloniex']:
            # Для poloniex.com
            pprint(capi.possable_amount('USDT','BTC', 600.0))
            pprint(capi.possable_amount('BTC', 'USDT', 1.0))
            pprint(capi.possable_amount('ETH', 'USDT', 42.085))
        else:
            pprint(capi.possable_amount('USD','BTC', 600.0))
            pprint(capi.possable_amount('BTC', 'USD', 1.0))
            pprint(capi.possable_amount('ETH', 'USD', 42.085))

        '''



        #pprint(capi.balance())
        #time.sleep(3)
        #pprint(capi.ticker())
        #pprint(capi.ticker())
        #pprint(capi.orders_balance())
        #pprint(capi.balance_full())

        #pprint(capi.currency)
        #print '-' * 50
        #pprint(capi.balance_full_usd())
        #print '-' * 50
        #pprint(capi.balance_full_btc())

        '''
        if capi.name in ['poloniex']:
            # Для poloniex.com
            pprint(capi.search_exchains('USDT', 4))
        else:
            pprint(capi.search_exchains('USD', 4))

        '''

        #тестирование подробного просчета цепочек
        #и выполнения обмена по цепочке
        '''
        if capi.name in ['poloniex']:
            # Для poloniex.com
            chains = sorted(capi.search_exchains('USDT', 4, False), key=lambda item: 1/item['profit'])
            chain = chains[0]
            pprint(chain)
            chain['profit'] = capi.calc_chain_profit_real(chain, 10.0)
            pprint(chain)
        else:
            chains = sorted(capi.search_exchains('USD', 4, False), key=lambda item: 1/item['profit'])
            chain = chains[0]
            pprint(chain)
            chain['profit'] = capi.calc_chain_profit_real(chain, 10.0)
            pprint(chain)

        res = raw_input('Execute chain: (y/n)')
        if res == 'y':
            pprint(capi.execute_exchange_chain(chain, 8.0))
        else:
            print 'you has canceled execute chain'

        '''

        '''
        ticker = self.capi.ticker()
        self.print_profit_pairs(ticker)
        profit_pairs = self.get_profit_pairs(ticker)
        for pair in profit_pairs:
            print '%s ' % pair['pair']
        print 'всего: %i' % len(profit_pairs)
        pprint(profit_pairs)
        '''

        '''
        #тестирование функции возвращающей минимальные балансы
        ticker = self.capi.ticker()
        for pair, data in ticker.items():
            min_primary_balance, min_secondary_balance = self.capi.get_min_balance(pair, ticker)
            print 'pair=%s min_primary_balance=%f min_secondary_balance=%f' % (pair, min_primary_balance, min_secondary_balance)
        '''


        #тестирование функции вычисления цены безубыточной продажи
        '''
        quantity = 1.0
        if self.capi.name not in ['poloniex']:
            self.pair = 'ETH_USD'
        else:
            self.pair = 'USDT_ETH'

        try:
            self.fee = capi.fee[self.pair]
        except KeyError:
            self.fee = capi.fee['_'.join([self.pair.split('_')[1], self.pair.split('_')[0]])]
        pprint(Lib.calc_price_sell(self, quantity))
        '''

        #тестирование использования нескольких capi в одной стратегии
        '''
        if type(self.capi) is dict:
            pprint(str(self.capi))
            for ca in self.capi.values():
                pprint(ca.name)
        else:
            pprint(self.capi.name)
            pprint(self.capi.balance())
        '''
        #pprint(self.capi.exchange_all_to_usd())
        #pprint(capi.user_trades(['ETH_BTC']))

        '''
        if self.capi.name in ['poloniex']:
            pprint(self.capi.orders(['USDT_BTC'], 20))
        else:
            pprint(self.capi.orders(['BTC_USD'], 20))
        '''

        '''
        if self.capi.name in ['poloniex']:
            pprint(self.capi.trades(['USDT_BTC']))
        else:
            pprint(self.capi.trades(['BTC_USD']))

        self.pair = 'BTC_USD'
        Lib.save_statistic_data(self)
        pprint(Lib.detect_marker_direct(self, 'BTC_USD', 30))



        #получаем наличие своих средств
        balance = self.capi.balance()

        self.pair = 'BTC_USD'
        pprint(balance)
        primary_balance = balance[self.pair.split('_')[0]]
        secondary_balance = balance[self.pair.split('_')[1]]
        Lib.save_change_balance(self, self.pair.split('_')[0], primary_balance)
        Lib.save_change_balance(self, self.pair.split('_')[1], secondary_balance)
        '''

        # сохраняем последние сделки
        if self.capi.name == 'exmo':
            self.pairs = ['BTC_USD', 'ETH_USD', 'DASH_USD']
        elif self.capi.name == 'btce':
            self.pairs = ['BTC_USD','ETH_USD','DSH_USD','LTC_USD']
            #self.pairs = ['LTC_USD']
        elif self.capi.name == 'poloniex':
            self.pairs = ['USDT_BTC','USDT_REP','USDT_ETC','USDT_DASH']
            #self.pairs = ['BTC_ETC']
        Lib.save_last_user_trades2(self)

