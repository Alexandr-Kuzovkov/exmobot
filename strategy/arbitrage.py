#coding=utf-8

from pprint import pprint
import time

class Strategy:

    capi = None
    logger = None
    storage = None
    conf = None
    params = None

    pair = None
    name = 'arbitrage'
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
        #флаг что поиск цепочки и обмен нужно повторять в случае успешного поиска
        do_repeat = self.set_param(key='do_repeat', default_value=0, param_type='int')
        repeat = True
        while repeat:
            try:
                repeat = False
                result = self.search_profit_chains_and_exchange()
            except Exception, ex:
                self.logger.info('Error in search_profit_chains_and_exchange(): %s' % ex)
                break
            else:
                if result and do_repeat > 0:
                    self.logger.info('Repeat search profit chains and exchange', self.prefix)
                    repeat = True



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
            if abs(curr_amount - last_amount) / last_amount > 0.0001:
                self.storage.save_balance(currency, curr_amount, self.session_id)
        else:
            self.storage.save_balance(currency, curr_amount, self.session_id)

    '''
    поиск профитноных цепочек и выполнение обмена
    '''
    def search_profit_chains_and_exchange(self):
        # максимальная длина цепочки
        max_chain_len = self.set_param(key='max_chain_len', default_value=4, param_type='int')
        # лимит использования средств для обмена
        limit = self.set_param(key='limit', default_value=10.0, param_type='float')
        # валюта на входе цепочки
        start_currency = self.set_param(key='start_currency', default_value='USD')
        # производить ли обмен
        do_exchange = self.set_param(key='do_exchange', default_value=0, param_type='int')

        # получаем текущий баланс по стартовой валюте
        current_balance = self.capi.balance(start_currency)
        # записываем изменения баланса в базу
        self.save_change_balance(start_currency, current_balance)
        start_amount = min(limit, current_balance)

        try:
            chains = self.capi.search_exchains(start_currency, max_chain_len)
        except Exception, ex:
            self.logger.info('Error while search_exchains: %s' % ex)
            raise Exception('Error while search_exchains: %s' % ex)
        else:
            if len(chains) > 0:
                self.logger.info('%i profitable chains found, begin complete checking...' % len(chains), self.prefix)
                for i in range(len(chains)):
                    #просчитываем реальный профит по цепочке
                    chains[i]['profit'] = self.capi.calc_chain_profit_real(chains[i], start_amount)
                    # если задано проводить обмен, то проводим
                    if do_exchange > 0 and chains[i]['profit'] > 0:
                        self.logger.info('begin exchange by chain %i, balance=%f' % (i, current_balance))
                        result = self.capi.execute_exchange_chain(chains[i], start_amount)
                        if result['result']:
                            self.logger.info(
                                'Exchange by chain %i executed succesfully! balance=%f' % (i, result['amount']))
                            start_amount = min(limit, result['amount'])
                        else:
                            self.logger.info('Exchange by chain %i fail' % i)
                            start_amount = min(limit, self.capi.balance(start_currency))

                # записываем результаты в лог
                profitable_chains = filter(lambda chain: chain['profit'] > 0, chains)
                str_profitable_chains = str(profitable_chains)
                self.logger.info('Profitable chains: %s' % str_profitable_chains)

                # записываем результаты в базу
                if len(profitable_chains) > 0:
                    str_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
                    self.storage.save(str_time, str_profitable_chains)
                    if do_exchange > 0:
                        return True
            else:
                # записываем результаты в лог
                self.logger.info('Profitable chains not found...', self.prefix)
            return False
