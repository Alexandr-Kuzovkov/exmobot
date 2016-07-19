#coding=utf-8

def run(action, logger):
    res = action.get_balance()
    logger.info(res)
    print res

