#coding=utf-8

def run(capi, logger):
    res = capi.get_balance()
    logger.info(res)
    print res

