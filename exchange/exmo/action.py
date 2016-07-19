# coding=utf-8

class Action:
    api = None
    name = 'EXMO'

    def __init__(self, api):
        self.api = api

    #удаление всех ордеров
    def delete_all_orders(self):
        open_orders = self.api.user_open_orders()
        for orders_for_pair in open_orders.values():
            for order in orders_for_pair:
                res = self.api.order_cancel(order['order_id'])
                if res['result']:
                    return True
                else:
                    return False

    #удаление ордеров по валютной паре
    def delete_orders_for_pair(self, pair):
        if not self.api.isPairValid(pair):
            raise Exception('Pair not valid')
        open_orders = self.api.user_open_orders()
        orders_for_pair = open_orders[pair]
        for order in orders_for_pair:
            res = self.api.order_cancel(order['order_id'])
            if res['result']:
                return True
            else:
                return False

    #получение баланса по выбранной валюте или по всем
    def get_balance(self, currency=None):
        list_currency = self.api.currency()
        user_info = self.api.user_info()
        if currency is not None and currency in list_currency:
            return float(user_info['balances'][currency])
        else:
            balances = {}
            for k,v in user_info['balances'].items():
                balances[k] = float(v)
            return balances



