#coding=utf-8

import time
from pprint import pprint

'''
получение минимальной цены продажи для обеспечения
продажи не в убыток на основе истории сделок
@param quantity количество первой валюты (ранее купленной а сейчас продаваемой)в паре
'''
def calc_price_sell(strategy, quantity, user_trades=None, limit=100):
    if user_trades is None:
        user_trades = strategy.capi.user_trades([strategy.pair], limit=limit)
    if strategy.pair not in user_trades:
        return None
    user_trades = sorted(user_trades[strategy.pair], key=lambda row: -row['date'])
    #pprint(user_trades[0:6])
    curr_quantity = 0.0
    curr_amount = 0.0
    for trade in user_trades:
        if trade['type'] == 'sell' or trade['pair'] != strategy.pair:
            continue
        curr_quantity += trade['quantity']
        curr_amount += trade['amount']
        #print 'q=%f a=%f time=%s' % (trade['quantity'], trade['amount'], time.ctime(trade['date']))
        if curr_quantity >= quantity:
            break
    if curr_quantity == 0:
        return None
    price = curr_amount / curr_quantity * (1 + (2 * strategy.fee + strategy.min_profit))
    return price


'''
установка значения параметра
@param key имя параметра
@param default_value значение по умолчанию
@param param_type тип
@return значение параметра
'''
def set_param(strategy, key, default_value=None, param_type=None):
    if key in strategy.params:
        param = strategy.params[key]
    elif strategy.conf.has_option('common', key):
        param = strategy.conf.get('common', key)
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
def save_change_balance(strategy, currency, amount):
    last = strategy.storage.get_last_balance(currency, 1, strategy.session_id)
    if (len(last) > 0) and (round(last[0]['amount'], 6) == round(amount, 6)):
        pass
    else:
        strategy.storage.save_balance(currency, amount, strategy.session_id)


'''
запись изменений баланса в базу (вариант 2)
'''
def save_change_balance2(strategy, currency, amount):
    last = strategy.storage.get_last_balance(currency, 1, strategy.session_id)
    curr_amount = round(amount, 6)
    if len(last) > 0:
        last_amount = round(last[0]['amount'], 6)
        if abs(curr_amount - last_amount) > 0.0001:
            strategy.storage.save_balance(currency, curr_amount, strategy.session_id)
    else:
        strategy.storage.save_balance(currency, curr_amount, strategy.session_id)


# поиск пар для профитной торговли
def print_profit_pairs(strategy, ticker=None):
    fees = strategy.capi._get_fee()
    if ticker is None:
        ticker = strategy.capi.ticker()
    base_valute = {'exmo': 0, 'btce': 1, 'poloniex': 0}

    # pprint(ticker)
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
        profit = sell_price / buy_price * (1 - fee) * (1 - fee) - 1
        currency_ratio[pair] = (sell_price + buy_price) / 2
        vol_currency = pair.split('_')[base_valute[strategy.capi.name]]
        pair_info = {'pair': pair, 'profit': profit, 'vol': data['vol'], 'vol_btc': 0.0, 'vol_currency': vol_currency,'sell_price': sell_price, 'buy_price': buy_price}

        if profit > 0:
            profit_pairs.append(pair_info)

    profit_pairs = sorted(profit_pairs, key=lambda row: 1 / row['profit'])

    # pprint(currency_ratio)
    if strategy.capi.name == 'poloniex':
        for i in range(len(profit_pairs)):
            if profit_pairs[i]['vol_currency'] == 'BTC':
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol']
            elif ('BTC_' + profit_pairs[i]['vol_currency']) in currency_ratio:
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] * currency_ratio[
                    ('BTC_' + profit_pairs[i]['vol_currency'])]
            elif (profit_pairs[i]['vol_currency'] + '_BTC') in currency_ratio:
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] / currency_ratio[
                    (profit_pairs[i]['vol_currency'] + '_BTC')]
            else:
                profit_pairs[i]['vol_btc'] = 0.0
    else:
        for i in range(len(profit_pairs)):
            if profit_pairs[i]['vol_currency'] == 'BTC':
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol']
            elif ('BTC_' + profit_pairs[i]['vol_currency']) in currency_ratio:
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] / currency_ratio[
                    ('BTC_' + profit_pairs[i]['vol_currency'])]
            elif (profit_pairs[i]['vol_currency'] + '_BTC') in currency_ratio:
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] * currency_ratio[
                    (profit_pairs[i]['vol_currency'] + '_BTC')]
            else:
                profit_pairs[i]['vol_btc'] = 0.0

    print 'Биржа: %s всего пар: %i пар с профитом: %i' % (strategy.capi.name, len(ticker), len(profit_pairs))
    for item in profit_pairs:
        print 'pair=%s   profit=%f   volume=%f(%s) = %f BTC   sell_price=%.10f   buy_price=%.10f' % (item['pair'], item['profit'], item['vol'], item['vol_currency'], item['vol_btc'], item['sell_price'],item['buy_price'])


'''
поиск пар для профитной торговли
выбираем пары с наличием баланса валюты в паре и с профитом, сортируем по произведению величины спреда и объема торгов
@return profit_pairs список пар вида: [{'pair':pair, 'profit':profit, 'vol': data['vol'], 'vol_btc': 0.0, 'vol_currency': vol_currency, 'sell_price':sell_price, 'buy_price':buy_price}, ...]
'''
def get_profit_pairs(strategy, ticker=None, balance=None):
    fees = strategy.capi._get_fee()
    if ticker is None:
        ticker = strategy.capi.ticker()
    if balance is None:
        balance = strategy.capi.balance()

    #pairs_with_balance = filter(lambda pair: balance[pair.split('_')[0]] > strategy.capi.get_min_balance(pair, ticker)[0] or balance[pair.split('_')[1]] > strategy.capi.get_min_balance(pair, ticker)[1], strategy.capi.pair_settings.keys())
    #print 'pair_with_balance %s' % str(pairs_with_balance)
    black_list = ['USD_RUR', 'EUR_USD', 'EUR_RUR']
    base_valute = {'exmo': 0, 'btce': 1, 'poloniex': 0}
    # pprint(ticker)
    profit_pairs = []
    currency_ratio = {}
    for pair, data in ticker.items():
        buy_price = min(data['buy_price'], data['sell_price'])
        sell_price = max(data['buy_price'], data['sell_price'])
        fee = fees[pair]
        profit = sell_price / buy_price * (1 - fee) * (1 - fee) - 1
        currency_ratio[pair] = (sell_price + buy_price) / 2
        vol_currency = pair.split('_')[base_valute[strategy.capi.name]]
        pair_info = {'pair': pair, 'profit': profit, 'vol': data['vol'], 'vol_btc': 0.0,
                     'vol_currency': vol_currency, 'sell_price': sell_price, 'buy_price': buy_price}
        #if profit > 0 and pair in pairs_with_balance and pair not in black_list:
        if profit > 0 and pair not in black_list:
            profit_pairs.append(pair_info)

    profit_pairs = sorted(profit_pairs, key=lambda row: 1 / row['profit'])

    # pprint(currency_ratio)
    if strategy.capi.name == 'poloniex':
        for i in range(len(profit_pairs)):
            if profit_pairs[i]['vol_currency'] == 'BTC':
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol']
            elif ('BTC_' + profit_pairs[i]['vol_currency']) in currency_ratio:
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] * currency_ratio[
                    ('BTC_' + profit_pairs[i]['vol_currency'])]
            elif (profit_pairs[i]['vol_currency'] + '_BTC') in currency_ratio:
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] / currency_ratio[
                    (profit_pairs[i]['vol_currency'] + '_BTC')]
            else:
                profit_pairs[i]['vol_btc'] = 0.0
    else:
        for i in range(len(profit_pairs)):
            if profit_pairs[i]['vol_currency'] == 'BTC':
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol']
            elif ('BTC_' + profit_pairs[i]['vol_currency']) in currency_ratio:
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] / currency_ratio[
                    ('BTC_' + profit_pairs[i]['vol_currency'])]
            elif (profit_pairs[i]['vol_currency'] + '_BTC') in currency_ratio:
                profit_pairs[i]['vol_btc'] = profit_pairs[i]['vol'] * currency_ratio[
                    (profit_pairs[i]['vol_currency'] + '_BTC')]
            else:
                profit_pairs[i]['vol_btc'] = 0.0

    return sorted(profit_pairs, key=lambda row: 1 / (row['profit'] * row['vol_btc']))


'''
Округление числа
'''
def _round(number, prec):
    number = number * (10 ** prec)
    number = int(number)
    number = float(number) / (10 ** prec)
    return number

'''
удаляем неактуальные записи об ордерах в базе данных
'''
def delete_orders_not_actual(strategy, user_orders = None):
    if user_orders is None:
        user_orders = strategy.capi.user_orders()
    stored_orders = strategy.storage.orders(session_id=strategy.session_id)
    for stored_order in stored_orders:
        order_exists = False
        for curr_pair, user_orders_for_pair in user_orders.items():
            for user_order_for_pair in user_orders_for_pair:
                if (user_order_for_pair['order_id'] == int(stored_order['order_id'])) and (user_order_for_pair['type'] == stored_order['order_type']):
                    order_exists = True
                    break
        if not order_exists:
            strategy.storage.order_delete(pair=stored_order['pair'], order_id=stored_order['order_id'], session_id=strategy.session_id)


'''
отменяем ордера поставленные в своей сессии по заданной валютной паре
если в ордере на продажу валюты меньше чем нужно на ордер, то
такой ордер не отменяем
@param min_balance мимнимальное количество валюты на ордер
'''
def delete_own_orders(strategy, min_balance=0):
    own_orders = strategy.storage.orders(strategy.pair, strategy.session_id)
    for own_order in own_orders:
        if own_order['order_type'] == 'sell' and own_order['quantity'] <= min_balance:
            continue
        res = strategy.capi.order_cancel(own_order['order_id'])
        if res['result']:
            strategy.storage.order_delete(own_order['order_id'], strategy.pair, strategy.session_id)
        else:
            strategy.logger.info('Error order cancelling %i "%s" for pair %s in session %s' % (own_order['order_id'], own_order['order_type'], own_order['pair'], own_order['session_id']), strategy.prefix)



'''
создание ордера
@param order_type ('sell'/'buy')
@price цена
@quantity количество
'''
def order_create(strategy, order_type, price, quantity):
    strategy.logger.info('Order create: pair=%s quantity=%f price=%f type=%s' % (strategy.pair, quantity, price, order_type), strategy.prefix)
    try:
        res = strategy.capi.order_create(pair=strategy.pair, quantity=quantity, price=price, order_type=order_type)
        if not res['result']:
            strategy.logger.info('Error order create "' + order_type + '": %s' % str(res['error']), strategy.prefix)
            return False
        else:
            strategy.logger.info('Order "' + order_type + '": %s: price=%f' % (strategy.pair, price), strategy.prefix)
            #сохраняем данные по поставленному ордеру
            strategy.storage.order_add(res['order_id'], strategy.pair, quantity, price, order_type, strategy.session_id)
            return True
    except Exception, ex:
        strategy.logger.info('Error order create "' + order_type + '": %s' % ex.message, strategy.prefix)
        return False


'''
запись последних сделок пользователя в базу
'''
def save_last_user_trades(strategy, user_trades=None, limit=100):
    if user_trades is None:
        user_trades = strategy.capi.user_trades([strategy.pair], limit=limit)
    if strategy.pair in user_trades or '_'.join([strategy.pair.split('_')[1], strategy.pair.split('_')[0]]) in user_trades:
        try:
            strategy.storage.save_user_trades(user_trades[strategy.pair], strategy.session_id)
        except KeyError:
            strategy.storage.save_user_trades(user_trades['_'.join([strategy.pair.split('_')[1], strategy.pair.split('_')[0]])], strategy.session_id)

'''
запись последних сделок пользователя в базу по всем списку пар, используемых в стратегии
'''
def save_last_user_trades2(strategy, user_trades=None, limit=100):
    if user_trades is None:
        user_trades = strategy.capi.user_trades(strategy.pairs, limit=limit)
        #pprint(user_trades)
    for pair in strategy.pairs:
        if pair in user_trades or '_'.join([pair.split('_')[1], pair.split('_')[0]]) in user_trades:
            try:
                strategy.storage.save_user_trades(user_trades[pair], strategy.session_id)
            except KeyError:
                strategy.storage.save_user_trades(user_trades['_'.join([pair.split('_')[1], pair.split('_')[0]])], strategy.session_id)


'''
вычисление профита на основе цены покупки, продажи и комиссии
'''
def _calc_profit(ask, bid, fee):
    return ask / bid * (1 - fee) * (1 - fee) - 1


'''
Рассчет цен ордеров на обмен
@param orders ордера на прямой обмен
@param min_profit минимальный профит
@param fee комиссия
@param price_step шаг изменения цены
@return {'ask':ask, 'bid': bid} словарь содержащий цены
'''
def calc_prices(strategy, orders, price_step, fee=0.002):
    try:
        ask = orders[strategy.pair]['ask'][0][0] - price_step
        bid = orders[strategy.pair]['bid'][0][0] + price_step
    except KeyError:
        ask = orders['_'.join([strategy.pair.split('_')[1], strategy.pair.split('_')[0]])]['ask'][0][0]
        bid = orders['_'.join([strategy.pair.split('_')[1], strategy.pair.split('_')[0]])]['bid'][0][0]

    profit = _calc_profit(ask, bid, fee)
    while (profit < strategy.min_profit):
        ask += price_step
        bid -= price_step
        profit = _calc_profit(ask, bid, fee)

    return {'ask': ask, 'bid': bid}



'''
возвращает название пары с обратным порядком валют
@param pair пара
'''
def reverse_pair(pair):
    return '_'.join([pair.split('_')[1], pair.split('_')[0]])


'''
определение направления рынка
@param pair пара
@param time_interval временной интервал окна в минутах
'''
def detect_marker_direct(strategy, pair, time_interval):
    time_interval = time_interval * 60
    exchange = strategy.capi.name
    if strategy.storage.dbase.name == 'MySQL':
        q = "select (select avg((top_buy+low_sell)/2) as avg from stat where exchange=? and pair=? and utime > unix_timestamp() - ?) - (select avg((top_buy+low_sell)/2) as avg from stat where exchange=? and pair=? and utime > unix_timestamp() - ? and utime < unix_timestamp() - ?) as result"
        data = (exchange, pair, time_interval, exchange, pair, time_interval * 2, time_interval)
        res = strategy.storage.dbase.query(q, data)
    elif strategy.storage.dbase.name == 'SQLite':
        q = "select (select avg((top_buy+low_sell)/2) as avg from stat where exchange=? and pair=? and utime > strftime('%s', 'now') - ?) - (select avg((top_buy+low_sell)/2) as avg from stat where exchange=? and pair=? and utime > strftime('%s', 'now') - ? and utime < strftime('%s', 'now') - ?) as result"
        data = (exchange, pair, time_interval, exchange, pair, time_interval * 2, time_interval)
        res = strategy.storage.dbase.query(q, data)
        print res
    else:
        raise Exception('Incorrect DB name')
        res = None
    if type(res) is list:
        return res[0][0]
    else:
        return None


'''
запись в базу статистики по текущей паре для текущей биржи
@param orders книга ордеров (результат запроса API)
@param trades история торгов (результат запроса API)
@param store_time время хранения данных в сутках
'''
def save_statistic_data(strategy, orders=None, trades=None, store_time=None):
    if store_time is None:
        store_time = 1
    pair = strategy.pair
    if pair in strategy.capi.pair_settings.keys():
        try:
            if orders is None:
                orders = strategy.capi.orders([pair])
            if trades is None:
                trades = strategy.capi.trades([pair])
            low_sell = orders[pair]['ask'][0][0]
            top_buy = orders[pair]['bid'][0][0]
            order_qt_sell = 0.0
            order_qt_buy = 0.0
            for order in orders[pair]['ask']:
                order_qt_sell += order[1]
            for order in orders[pair]['bid']:
                order_qt_buy += order[1]
            trade_qt_sell = 0.0
            trade_qt_buy = 0.0
            for trade in trades[pair]:
                if trade['type'] == 'sell':
                    trade_qt_sell += trade['quantity']
                elif trade['type'] == 'buy':
                    trade_qt_buy += trade['quantity']
            data = (strategy.capi.name, pair, order_qt_sell, order_qt_buy, trade_qt_sell, trade_qt_buy, low_sell, top_buy)
            strategy.logger.info('Received data: exchange: %s pair: %s %f %f %f %f %f %f' % data, strategy.prefix)
            strategy.storage.save_stat(strategy.capi.name, pair, order_qt_sell, order_qt_buy, trade_qt_sell, trade_qt_buy,
                                   low_sell, top_buy)
            strategy.logger.info('Stat data from %s for pair %s saved' % (strategy.capi.name, pair), strategy.prefix)
        except Exception, ex:
            strategy.logger.info('Error while get stat from %s for pair %s ' % (strategy.capi.name, pair), strategy.prefix)

    #удаление старых данных
    utmost_update = time.time() - store_time * 86400
    strategy.storage.delete_old_stat(utmost_update)
