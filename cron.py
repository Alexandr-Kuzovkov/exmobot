#!/usr/bin/env python

import getopt
import sys
from logger.logger import Logger

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'fs:e:')
    if '-f' in map(lambda item: item[0], optlist):
        log_file = filter(lambda item: item[0]=='-f', optlist)[0][1]
        logger = Logger(log_file)
    else:
        logger = Logger()
    exchange_name = filter(lambda item: item[0]=='-e', optlist)[0][1]
    strategy_name = filter(lambda item: item[0]=='-s', optlist)[0][1]
except:
	print 'Usage: %s -e <exchange name: (exmo|btc_e)> -s <strategy name> [-f <log file>]' % sys.argv[0]
	exit(1)

try:
    strategy = __import__('strategy.' + strategy_name, globals(), locals(), ['run'], -1)
    mod_api = __import__('exchange.' + exchange_name + '.api', globals(), locals(), ['API'], -1)
    mod_common_api = __import__('exchange.' + exchange_name + '.common_api', globals(), locals(), ['Action'], -1)
    api = mod_api.API()
    capi = mod_common_api.CommonAPI(api)
except:
    print 'Usage: %s -e <exchange name: (exmo|btc_e)> -s <strategy name>' % sys.argv[0]
    exit(1)


strategy.run(capi, logger)










