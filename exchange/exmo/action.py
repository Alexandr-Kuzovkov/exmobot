# coding=utf-8

class Action:
    api = None

    def __init__(self, api):
        self.api = api

    #удаление всех ордеров
    def delete_all_orders(self):
        res = self.api.user_open_orders()
        if res['status'] == 200:
            for orders_for_pair in res['result'].values():
                for order in orders_for_pair:
                    return self.api.order_cancel(order['order_id'])

        else:
            return False

