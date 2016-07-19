#!/usr/bin/env python

import getopt
import sys

try:
    optlist, args = getopt.getopt(sys.argv[1:], 's:e:')
    exchange = filter(lambda item: item[0]=='-e', optlist)[0][1]
    strategy = filter(lambda item: item[0]=='-s', optlist)[0][1]
except:
	print 'Usage: %s -e <exchange: (exmo|btc_e)> -s <strategy>' % sys.argv[0]
	exit(1)

test = __import__('exchange.' + exchange + '.test', globals(), locals(), ['test_api', 'test_action'], -1)

#from exchange.exmo import test as exmo_test
from logger.logger import Logger

test.test_api()
test.test_action()




