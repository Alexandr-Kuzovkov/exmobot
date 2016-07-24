#coding=utf-8

import strategy.flip_btc_usd as flip_btc_usd
import strategy.flip_eth_usd as flip_eth_usd

def run(capi, logger, storage):
    flip_btc_usd.run(capi, logger, storage)
    flip_eth_usd.run(capi, logger, storage)