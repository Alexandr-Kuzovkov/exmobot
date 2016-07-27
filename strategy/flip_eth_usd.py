#coding=utf-8

import strategy.flip as flip

def run(capi, logger, storage, conf=None, **params):
    flip.run(capi, logger, storage, conf, mode=0, pair='ETH_USD')
    flip.run(capi, logger, storage, conf, mode=1, pair='ETH_USD')
