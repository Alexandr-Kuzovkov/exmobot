#coding=utf-8

import strategy.flip as flip

def run(capi, logger, storage, conf=None, **params):
    flip.run(capi, logger, storage, conf)
    #flip.run(capi, logger, storage, conf)
