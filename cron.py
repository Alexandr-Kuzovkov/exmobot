#!/usr/bin/env python

import getopt
import sys
from logger.logger import Logger
from storage.sqlite import Storage

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:s:e:i:', ['log-file=','strategy=','exchange=','session-id='])
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
    elif '--session-id' in map(lambda item: item[0], optlist):
        session_id = filter(lambda item: item[0]=='--session-id', optlist)[0][1]
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
    print '''
        Bot for cryptocurrency traiding
    '''
    print 'Usage: %s [options]' % sys.argv[0]
    print '''
            Options:
                 -e <exchange>  or --exchange=<exchange>  - Which exchange for trade. Required. (exmo|btc_e)
                 -s <strategy> or --strategy=<strategy> - Strategy of trade name. Required
                 -f <logfile> or --log-file=<logfile> - Filename for log write. Optional
                 -i <expression> or --session-id=<expression> - Session ID for differential storage data for other instances of bot

            Example:
                crontab -e
                * * * * * /path/to/exmo_bot/cron.py --exchange=exmo --strategy=flip_eth_usd --session-id=1 --log-file=/path/to/exmo_bot/flip_eth_usd.log

    '''
    exit(1)
try:
    strategy = __import__('strategy.' + strategy_name, globals(), locals(), ['run'], -1)
    mod_api = __import__('exchange.' + exchange_name + '.api', globals(), locals(), ['API'], -1)
    mod_common_api = __import__('exchange.' + exchange_name + '.common_api', globals(), locals(), ['CommonAPI'], -1)
    api = mod_api.API()
    capi = mod_common_api.CommonAPI(api)

except Exception, e:
    print 'Error: %s' % e
    exit(1)

storage = Storage(session_id)
strategy.run(capi, logger, storage)










