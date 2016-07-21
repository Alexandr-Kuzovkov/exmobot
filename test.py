#!/usr/bin/env python

import getopt
import sys
from logger.logger import Logger

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:s:e:i:', ['log-file=','strategy=','exchange=','id='])
    if '-f' in map(lambda item: item[0], optlist):
        log_file = filter(lambda item: item[0]=='-f', optlist)[0][1]
        logger = Logger(log_file)
    elif '--log-file' in map(lambda item: item[0], optlist):
        log_file = filter(lambda item: item[0]=='--log-file', optlist)[0][1]
        logger = Logger(log_file)
    else:
        logger = Logger()

    if '-i' in map(lambda item: item[0], optlist):
        session_id = filter(lambda item: item[0]=='-i', optlist)[0][1]
    elif '--id' in map(lambda item: item[0], optlist):
        session_id = filter(lambda item: item[0]=='--id', optlist)[0][1]
    else:
        session_id = 0

    if '-e' in map(lambda item: item[0], optlist):
        exchange_name = filter(lambda item: item[0]=='-e', optlist)[0][1]
    else:
        exchange_name = filter(lambda item: item[0]=='--exchange', optlist)[0][1]

    if '-s' in map(lambda item: item[0], optlist):
        strategy_name = filter(lambda item: item[0]=='-s', optlist)[0][1]
    else:
        strategy_name = filter(lambda item: item[0]=='--strategy', optlist)[0][1]
except:
    print 'Usage: %s -e <exchange: (exmo|btc_e)> -s <strategy> [-f <log file>]' % sys.argv[0]
    print 'or %s --exchange=<exchange: (exmo|btc_e)> --strategy=<strategy> [--log-file <log file>]' % sys.argv[0]
    exit(1)

try:
    strategy = __import__('strategy.' + strategy_name, globals(), locals(), ['run'], -1)
    mod_api = __import__('exchange.' + exchange_name + '.api', globals(), locals(), ['API'], -1)
    mod_common_api = __import__('exchange.' + exchange_name + '.common_api', globals(), locals(), ['CommonAPI'], -1)
    api = mod_api.API()
    capi = mod_common_api.CommonAPI(api)
except Exception, e:
    print 'Error: %s' % e.strerror
    exit(1)


strategy.run(capi, logger, session_id)




