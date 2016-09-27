#coding=utf-8

import strategy.flip3 as flip3
from pprint import pprint

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'flip5'
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
        #минимальный объем торгов криптовалюты
        min_volume = self.set_param(key='min_volume', default_value=10.0, param_type='float')
        profit_pairs = self.get_profit_pairs()
        pairs = self.select_pairs(profit_pairs, min_volume)
        #pprint(pairs)

        # сохраняем балансы в базу для сбора статистики
        balance_usd = self.capi.balance_full_usd()
        if self.capi.name == 'poloniex':
            self.save_change_balance('USDT', balance_usd)
        else:
            self.save_change_balance('USD', balance_usd)

        for pair in pairs:
            flip = flip3.Strategy(self.capi, self.logger, self.storage, self.conf, pair=pair['pair'])
            flip.run()


        #flip2 = flip.Strategy(self.capi, self.logger, self.storage, self.conf, mode=1)
        #flip2.run()

    '''
    поиск пар для профитной торговли
    '''
    def get_profit_pairs(self):
        fees = self.capi._get_fee()
        ticker = self.capi.ticker()
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
            vol_currency = pair.split('_')[base_valute[self.capi.name]]
            pair_info = {'pair':pair, 'profit':profit, 'vol': data['vol'], 'vol_btc': 0.0, 'vol_currency': vol_currency, 'sell_price':sell_price, 'buy_price':buy_price}
            if profit > 0:
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

        return profit_pairs


    '''
    выбор пар для торговли из массива заданных пар
    @param profit_pairs список пар вида: [{'pair':pair, 'profit':profit, 'vol': data['vol'], 'vol_btc': 0.0, 'vol_currency': vol_currency, 'sell_price':sell_price, 'buy_price':buy_price}, ...]
    @param  vol_min минимальный объем торгов в BTC
    '''
    def select_pairs(self, profit_pairs, vol_min):
        result = []
        black_list = ['USD_RUR', 'EUR_USD', 'EUR_RUR']
        for pair_info in profit_pairs:
            if pair_info['vol_btc'] >= vol_min and pair_info['pair'] not in black_list:
                result.append(pair_info)
        result = sorted(result, key=lambda row: 1/row['profit'])
        return result


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
        if (len(last) > 0) and (self._round(last[0]['amount'], 6) == self._round(amount, 6)):
            pass
        else:
            self.storage.save_balance(currency, amount, self.session_id)
