#coding=utf-8
import random
from pprint import pprint
import time
from sms import smsru


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
        self.prefix = capi.name + ' ' + self.name

        #ввод параметров
        #id сессии
        self.session_id = self.set_param(key='session_id', default_value='0')
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации


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
    запись изменений баланса в базу
    '''
    def save_change_balance(self, currency, amount):
        last = self.storage.get_last_balance(currency, 1, self.session_id)
        if (len(last) > 0) and (last[0]['amount'] == amount):
            pass
        else:
            self.storage.save_balance(currency, amount, self.session_id)


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



        #user_trades = capi.user_trades(['ETH_USD'], limit=2)
        #pprint(user_trades)
        #storage.save_user_trades(user_trades['ETH_USD'])

        #storage.delete_old_values(['user_trades'], time.time()-3, False, 'test')
        #pprint(storage.get_last_user_trades(pair=None, limit=5, session_id='test'))

        #min_primary_balance, min_secondary_balance = capi.get_min_balance('ETH_USD', 11.1)
        #print min_primary_balance, min_secondary_balance

        #storage.clear_all()

        '''
        отправка СМС
        cli = smsru.Client()
        res = cli.send("+79877171421", u'miner fail')
        print res
        '''

        #pprint(capi.pair_settings.keys())
        #pprint(capi.get_min_balance('USDT_ETH', 11.2))
        #pprint(capi.trades(['USDT_ETH']))
        #pprint(capi._date2timestamp('2016-08-15 13:04:53'))
        #pprint(capi.orders(['USDT_ETH', 'BTC_ETH'], 5))
        #pprint(capi.ticker())
        #pprint(capi.balance('BTC'))
        #pprint(capi.orders_balance('ETH'))
        #pprint(capi.balance_full())
        #pprint(capi.required_amount('USDT_ETH', 10))
        #pprint(capi.user_trades(['USDT_ETH','BTC_ETH']))
        #self.session_id = 'poloniex-1'
        #pprint(capi.user_orders())
        #pprint(capi.orders_cancel(['BTC_ETH']))
        #pprint(capi.order_create('BTC_ETH',1.15863329, 0.01857750, 'buy'))
        #pprint(capi._check_pair('ETH_BTC'))

        #pprint(capi.possable_amount('USD','BTC', 600.0))
        #pprint(capi.possable_amount('BTC', 'USD', 1.0))
        #pprint(capi.possable_amount('ETH', 'USD', 34.85))

        #Для poloniex.com
        #pprint(capi.possable_amount('USDT','BTC', 600.0))
        #pprint(capi.possable_amount('BTC', 'USDT', 1.0))
        #pprint(capi.possable_amount('ETH', 'USDT', 34.13))

        #поиск пар для профитной торговли


        fees = capi._get_fee()
        ticker = capi.ticker()
        base_valute = {'exmo': 0, 'btce':1, 'poloniex':0}

        #pprint(ticker)
        profit_pairs = []
        currency_ratio = {}
        for pair, data in ticker.items():
            if data['buy_price'] < data['sell_price']:
                buy_price = data['buy_price']
                sell_price = data['sell_price']
            else:
                buy_price = data['sell_price']
                sell_price = data['buy_price']
            fee = fees[pair]
            profit = sell_price / buy_price * (1-fee) * (1-fee) - 1
            currency_ratio[pair] = (sell_price + buy_price)/2
            vol_currency = pair.split('_')[base_valute[capi.name]]
            pair_info = {'pair':pair, 'profit':profit, 'vol': data['vol'], 'vol_btc': 0.0, 'vol_currency': vol_currency, 'sell_price':sell_price, 'buy_price':buy_price}

            if profit > 0:
                profit_pairs.append(pair_info)

        profits_pair = sorted(profit_pairs, key=lambda row: 1/row['profit'])

        #pprint(currency_ratio)
        if capi.name == 'poloniex':
            for i in range(len(profit_pairs)):
                if profit_pairs[i]['vol_currency'] == 'BTC':
                    profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol']
                elif ('BTC_' + profit_pairs[i]['vol_currency']) in currency_ratio:
                    profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] * currency_ratio[('BTC_' + profit_pairs[i]['vol_currency'])]
                elif (profit_pairs[i]['vol_currency'] + '_BTC') in currency_ratio:
                    profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] / currency_ratio[(profit_pairs[i]['vol_currency'] + '_BTC')]
                else:
                    profit_pairs[i]['vol_btc'] = 0.0
        else:
            for i in range(len(profit_pairs)):
                if profit_pairs[i]['vol_currency'] == 'BTC':
                    profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol']
                elif ('BTC_' + profit_pairs[i]['vol_currency']) in currency_ratio:
                    profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] / currency_ratio[('BTC_' + profit_pairs[i]['vol_currency'])]
                elif (profit_pairs[i]['vol_currency'] + '_BTC') in currency_ratio:
                    profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] * currency_ratio[(profit_pairs[i]['vol_currency'] + '_BTC')]
                else:
                    profit_pairs[i]['vol_btc'] = 0.0

        print 'Биржа: %s всего пар: %i пар с профитом: %i' % (capi.name, len(ticker), len(profit_pairs))
        for item in profits_pair:
            print 'pair=%s   profit=%f   volume=%f(%s) = %f BTC   sell_price=%.10f   buy_price=%.10f' % (item['pair'], item['profit'], item['vol'], item['vol_currency'], item['vol_btc'], item['sell_price'], item['buy_price'])


        #pprint(capi.balance())
        #pprint(capi.orders_balance())
        #pprint(capi.balance_full())

        #pprint(capi.currency)
        #print '-' * 50
        #pprint(capi.balance_full_usd())
        #print '-' * 50
        #pprint(capi.balance_full_btc())


