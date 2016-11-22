#!/usr/bin/env python

import getopt
import sys
from logger.logger import Logger
from ConfigParser import *
import os
import storage.storage as mod_storage


try:
    optlist, args = getopt.getopt(sys.argv[1:], 'c:', ['config-file='])
    if '-c' in map(lambda item: item[0], optlist):
        config_file = filter(lambda item: item[0]=='-c', optlist)[0][1]
    elif '--config-file' in map(lambda item: item[0], optlist):
        config_file = filter(lambda item: item[0]=='--config-file', optlist)[0][1]
    else:
        raise Exception('config file expected!')

    conf = ConfigParser()
    conf.read(config_file)

    if conf.has_option('common', 'exchange'):
        exchange_name = conf.get('common', 'exchange')
    else:
        raise Exception('"exchange" option expected in config file!')

    if conf.has_option('common', 'strategy'):
        strategy_name = conf.get('common', 'strategy')
    else:
        raise Exception('"strategy" option expected in config file!')

    if conf.has_option('common', 'session_id'):
        session_id = conf.get('common', 'session_id')
    else:
        session_id = 0

    if conf.has_option('common', 'log_file'):
        log_file = conf.get('common', 'log_file')
        logger = Logger(log_file)
    else:
        logger = Logger()

    if conf.has_option('common', 'storage'):
        storage_type = conf.get('common', 'storage')
    else:
        storage_type = 'SQLite'

    if conf.has_option('common', 'debug'):
        debug = int(conf.get('common', 'debug'))
    else:
        debug = 0

    if conf.has_option('account', 'key'):
        api_key = conf.get('account', 'key')
    else:
        api_key = None

    if conf.has_option('account', 'secret'):
        api_secret = conf.get('account', 'secret')
    else:
        api_secret = None

except Exception, ex:
    print '''
        Bot for cryptocurrency traiding
    '''
    print 'Usage: %s [options]' % sys.argv[0]
    print '''
            Options:
                 -c <exchange>  or --config-file=<filename>  - Filename config. Required.

            Example:
                crontab -e
                * * * * * /path/to/exmo_bot/bot.py --config-file=/path/to/exmo_bot/conf/flip_eth_usd.conf

    '''
    print ex.message
    exit(1)

exchange_name_list = exchange_name.split(',')
if len(exchange_name_list) == 1:
    mod_api = __import__('exchange.' + exchange_name + '.api', globals(), locals(), ['API'], -1)
    mod_common_api = __import__('exchange.' + exchange_name + '.common_api', globals(), locals(), ['CommonAPI'], -1)
    api = mod_api.API(api_key, api_secret)
    capi = mod_common_api.CommonAPI(api)
else:
    capi = {}
    for exchange_name in exchange_name_list:
        mod_api = __import__('exchange.' + exchange_name + '.api', globals(), locals(), ['API'], -1)
        mod_common_api = __import__('exchange.' + exchange_name + '.common_api', globals(), locals(), ['CommonAPI'], -1)
        api = mod_api.API(api_key, api_secret)
        capi[exchange_name] = mod_common_api.CommonAPI(api)

if debug:
    mod_strategy = __import__('strategy.' + strategy_name, globals(), locals(), ['run'], -1)
    mod_dbase = __import__('storage.' + storage_type + '.crud', globals(), locals(), ['Storage'], -1)
    dbase = mod_dbase.Crud()
    storage = mod_storage.Storage(dbase, session_id)
    strategy = mod_strategy.Strategy(capi, logger, storage, conf)
else:
    try:
        mod_strategy = __import__('strategy.' + strategy_name, globals(), locals(), ['run'], -1)
        mod_dbase = __import__('storage.' + storage_type + '.crud', globals(), locals(), ['Storage'], -1)
        dbase = mod_dbase.Crud()
        storage = mod_storage.Storage(dbase, session_id)
        strategy = mod_strategy.Strategy(capi, logger, storage, conf)
    except Exception, e:
        print 'Startup Error: %s' % e
        logger.info('Startup Error: %s' % e)
        exit(1)


if debug:
    strategy.run()
else:
    try:
        strategy.run()
    except Exception, ex:
        print 'Strategy.run: %s %s' % (ex, ex.message)
        logger.info('Strategy.run: %s %s' % (ex, ex.message))

