#coding=utf-8

'''
Стратегия поиска валютных пар на которых есть профитный спред
и запуск на них стратегии циклического обмена flip3_1
На непрофитных парах создаем ордера на продажу ранее купленной валюты
'''

import strategy.flip3_1 as flip3
import strategy.sell as sell3
from pprint import pprint

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'multiflip2'
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
        self.session_id = capi.name + '-' + self.name
        #ввод параметров
        #параметры передаваемые при вызове функции имеют приоритет
        #перед параметрами заданными в файле конфигурации


    '''
    Округление числа
    '''
    def _round(self, number, prec):
        number = number * (10 ** prec)
        number = int(number)
        number = float(number) / (10 ** prec)
        return number

    '''
    функция реализующая торговую логику
    '''
    def run(self):
        self.logger.info('-' * 40, self.prefix)
        self.logger.info('Run strategy %s' % self.name, self.prefix)
        ticker = self.capi.ticker()
        balance = self.capi.balance()
        #минимальный объем торгов криптовалюты
        profit_pairs = self.get_profit_pairs(ticker, balance)
        self.logger.info('Pairs for trading: %s' % str(map(lambda e: e['pair'], profit_pairs)), self.prefix)
        #pprint(profit_pairs)

        # сохраняем балансы в базу для сбора статистики
        balance_usd = self.capi.balance_full_usd(ticker)
        if self.capi.name == 'poloniex':
            self.save_change_balance('USDT', balance_usd)
        else:
            self.save_change_balance('USD', balance_usd)

        #запускаем торговлю для всех профитных пар
        pairs_with_profit = []
        for pair in profit_pairs:
            pairs_with_profit.append(pair['pair'])
            flip = flip3.Strategy(self.capi, self.logger, self.storage, self.conf, pair=pair['pair'])
            flip.run()

        #ставим ордера на продажу на непрофитных парах
        balance = self.capi.balance()
        pairs_with_balance = filter(lambda pair: balance[pair.split('_')[0]] > self.capi.get_min_balance(pair, ticker)[0] or balance[pair.split('_')[1]] > self.capi.get_min_balance(pair, ticker)[1], self.capi.pair_settings.keys())
        for pair in pairs_with_balance:
            if pair in pairs_with_profit:
                continue
            sell = sell3.Strategy(self.capi, self.logger, self.storage, self.conf, pair=pair['pair'])
            sell.run()

    '''
    поиск пар для профитной торговли
    выбираем пары с наличием баланса валюты в паре и с профитом, сортируем по произведению величины спреда и объема торгов
    @return profit_pairs список пар вида: [{'pair':pair, 'profit':profit, 'vol': data['vol'], 'vol_btc': 0.0, 'vol_currency': vol_currency, 'sell_price':sell_price, 'buy_price':buy_price}, ...]
    '''
    def get_profit_pairs(self, ticker=None, balance=None):
        fees = self.capi._get_fee()
        if ticker is None:
            ticker = self.capi.ticker()
        if balance is None:
            balance = self.capi.balance()
        pairs_with_balance = filter(lambda pair: balance[pair.split('_')[0]] > self.capi.get_min_balance(pair, ticker)[0] or balance[pair.split('_')[1]] > self.capi.get_min_balance(pair, ticker)[1], self.capi.pair_settings.keys())

        black_list = ['USD_RUR', 'EUR_USD', 'EUR_RUR']
        base_valute = {'exmo': 0, 'btce':1, 'poloniex':0}
        #pprint(ticker)
        profit_pairs = []
        currency_ratio = {}
        for pair, data in ticker.items():
            buy_price = min(data['buy_price'], data['sell_price'])
            sell_price = max(data['buy_price'], data['sell_price'])
            fee = fees[pair]
            profit = sell_price / buy_price * (1-fee) * (1-fee) - 1
            currency_ratio[pair] = (sell_price + buy_price)/2
            vol_currency = pair.split('_')[base_valute[self.capi.name]]
            pair_info = {'pair':pair, 'profit':profit, 'vol': data['vol'], 'vol_btc': 0.0, 'vol_currency': vol_currency, 'sell_price':sell_price, 'buy_price':buy_price}
            if profit > 0 and pair in pairs_with_balance and pair not in black_list:
                profit_pairs.append(pair_info)

        profits_pair = sorted(profit_pairs, key=lambda row: 1/row['profit'])

        #pprint(currency_ratio)
        if self.capi.name == 'poloniex':
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

        return sorted(profit_pairs, key=lambda row: 1/(row['profit'] * row['vol_btc']))


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
        curr_amount = self._round(amount, 6)
        if len(last) > 0:
            last_amount = self._round(last[0]['amount'], 6)
            if abs(curr_amount - last_amount) / last_amount > 0.001:
                self.storage.save_balance(currency, curr_amount, self.session_id)
        else:
            self.storage.save_balance(currency, curr_amount, self.session_id)

