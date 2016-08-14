import urllib
import urllib2
import json
import time
import hmac,hashlib
import exchange.poloniex.config as config

def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))

class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))

        return after

    def api_query(self, command, req={}):

        if(command == "returnTicker" or command == "return24Volume"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif(command == "returnOrderBook"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif(command == "returnMarketTradeHistory"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
            post_data = urllib.urlencode(req)

            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers))
            jsonRet = json.loads(ret.read())
            return self.post_process(jsonRet)


    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24Volume(self):
        return self.api_query("return24Volume")

    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})


    # Returns all of your balances.
    # Outputs:
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')

    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})


    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
    # If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
    # If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs:
    # succes        1 or 0
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method,
    # the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount",
    # and "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})


'''
-----------------------------------------------------------------------------------------------------------------------
PUBLIC API Methods

Please note that making more than 6 calls per second to the public API, or repeatedly and needlessly fetching
excessive amounts of data, can result in your IP being banned.
There are six public methods, all of which take HTTP GET requests and return output in JSON format:
-----------------------------------------------------------------------------------------------------------------------
returnTicker
Returns the ticker for all markets. Sample output:

{"BTC_LTC":{"last":"0.0251","lowestAsk":"0.02589999","highestBid":"0.0251","percentChange":"0.02390438",
"baseVolume":"6.16485315","quoteVolume":"245.82513926"},"BTC_NXT":{"last":"0.00005730","lowestAsk":"0.00005710",
"highestBid":"0.00004903","percentChange":"0.16701570","baseVolume":"0.45347489","quoteVolume":"9094"}, ... }

Call: https://poloniex.com/public?command=returnTicker

-----------------------------------------------------------------------------------------------------------------------
return24Volume
Returns the 24-hour volume for all markets, plus totals for primary currencies. Sample output:

{"BTC_LTC":{"BTC":"2.23248854","LTC":"87.10381314"},"BTC_NXT":{"BTC":"0.981616","NXT":"14145"}, ...
"totalBTC":"81.89657704","totalLTC":"78.52083806"}

Call: https://poloniex.com/public?command=return24hVolume

-----------------------------------------------------------------------------------------------------------------------
returnOrderBook
Returns the order book for a given market, as well as a sequence number for use with the Push API and an indicator
specifying whether the market is frozen. You may set currencyPair to "all" to get the order books of all markets.
Sample output:

{"asks":[[0.00007600,1164],[0.00007620,1300], ... ], "bids":[[0.00006901,200],[0.00006900,408], ... ], "isFrozen": 0,
"seq": 18849}

Or, for all markets:

{"BTC_NXT":{"asks":[[0.00007600,1164],[0.00007620,1300], ... ], "bids":[[0.00006901,200],[0.00006900,408], ... ],
"isFrozen": 0, "seq": 149},"BTC_XMR":...}

Call: https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=10

-----------------------------------------------------------------------------------------------------------------------
returnTradeHistory
Returns the past 200 trades for a given market, or up to 50,000 trades between a range specified in UNIX timestamps by
the "start" and "end" GET parameters. Sample output:

[{"date":"2014-02-10 04:23:23","type":"buy","rate":"0.00007600","amount":"140","total":"0.01064"},
{"date":"2014-02-10 01:19:37","type":"buy","rate":"0.00007600","amount":"655","total":"0.04978"}, ... ]

Call: https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1410158341&end=1410499372

-----------------------------------------------------------------------------------------------------------------------
returnChartData
Returns candlestick chart data. Required GET parameters are "currencyPair", "period" (candlestick period in seconds;
valid values are 300, 900, 1800, 7200, 14400, and 86400), "start", and "end". "Start" and "end" are given in UNIX
timestamp format and used to specify the date range for the data returned. Sample output:

[{"date":1405699200,"high":0.0045388,"low":0.00403001,"open":0.00404545,"close":0.00427592,"volume":44.11655644,
"quoteVolume":10259.29079097,"weightedAverage":0.00430015}, ...]

Call: https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400

-----------------------------------------------------------------------------------------------------------------------
returnCurrencies
Returns information about currencies. Sample output:

{"1CR":{"maxDailyWithdrawal":10000,"txFee":0.01,"minConf":3,"disabled":0},"ABY":{"maxDailyWithdrawal":10000000,
"txFee":0.01,"minConf":8,"disabled":0}, ... }

Call: https://poloniex.com/public?command=returnCurrencies

-----------------------------------------------------------------------------------------------------------------------
returnLoanOrders
Returns the list of loan offers and demands for a given currency, specified by the "currency" GET parameter.
Sample output:

{"offers":[{"rate":"0.00200000","amount":"64.66305732","rangeMin":2,"rangeMax":8}, ... ],"demands":[{"rate":"0.00170000",
"amount":"26.54848841","rangeMin":2,"rangeMax":2}, ... ]}

Call: https://poloniex.com/public?command=returnLoanOrders&currency=BTC
-----------------------------------------------------------------------------------------------------------------------
TRADING API Methods

To use the trading API, you will need to create an API key.

Please note that there is a default limit of 6 calls per second. If you require more than this, please consider
optimizing your application using the push API, the "moveOrder" command, or the "all" parameter where appropriate.
If this is still insufficient, please contact support to discuss a limit raise.

All calls to the trading API are sent via HTTP POST to https://poloniex.com/tradingApi and must contain the following
headers:

Key - Your API key.
Sign - The query's POST data signed by your key's "secret" according to the HMAC-SHA512 method.
Additionally, all queries must include a "nonce" POST parameter. The nonce parameter is an integer which must always
be greater than the previous nonce used.

All responses from the trading API are in JSON format. In the event of an error, the response will always be of the
following format:

{"error":"<error message>"}

There are several methods accepted by the trading API, each of which is specified by the "command" POST parameter:

-----------------------------------------------------------------------------------------------------------------------
returnBalances
Returns all of your available balances. Sample output:

{"BTC":"0.59098578","LTC":"3.31117268", ... }

-----------------------------------------------------------------------------------------------------------------------
returnCompleteBalances
Returns all of your balances, including available balance, balance on orders, and the estimated BTC value of your balance.
By default, this call is limited to your exchange account; set the "account" POST parameter to "all" to include your
margin and lending accounts. Sample output:

{"LTC":{"available":"5.015","onOrders":"1.0025","btcValue":"0.078"},"NXT:{...} ... }

-----------------------------------------------------------------------------------------------------------------------
returnDepositAddresses
Returns all of your deposit addresses. Sample output:

{"BTC":"19YqztHmspv2egyD6jQM3yn81x5t5krVdJ","LTC":"LPgf9kjv9H1Vuh4XSaKhzBe8JHdou1WgUB", ... "ITC":"Press Generate.." ... }

-----------------------------------------------------------------------------------------------------------------------
generateNewAddress
Generates a new deposit address for the currency specified by the "currency" POST parameter. Sample output:

{"success":1,"response":"CKXbbs8FAVbtEa397gJHSutmrdrBrhUMxe"}

Only one address per currency per day may be generated, and a new address may not be generated before the
previously-generated one has been used.

-----------------------------------------------------------------------------------------------------------------------
returnDepositsWithdrawals
Returns your deposit and withdrawal history within a range, specified by the "start" and "end" POST parameters, both of
which should be given as UNIX timestamps. Sample output:

{"deposits":
[{"currency":"BTC","address":"...","amount":"0.01006132","confirmations":10,
"txid":"17f819a91369a9ff6c4a34216d434597cfc1b4a3d0489b46bd6f924137a47701","timestamp":1399305798,"status":"COMPLETE"},
{"currency":"BTC","address":"...","amount":"0.00404104","confirmations":10,
"txid":"7acb90965b252e55a894b535ef0b0b65f45821f2899e4a379d3e43799604695c","timestamp":1399245916,"status":"COMPLETE"}],
"withdrawals":[{"withdrawalNumber":134933,"currency":"BTC","address":"1N2i5n8DwTGzUq2Vmn9TUL8J1vdr1XBDFg","amount":"5.00010000",
"timestamp":1399267904,"status":"COMPLETE: 36e483efa6aff9fd53a235177579d98451c4eb237c210e66cd2b9a2d4a988f8e","ipAddress":"..."}]}

-----------------------------------------------------------------------------------------------------------------------
returnOpenOrders
Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP".
Set "currencyPair" to "all" to return open orders for all markets. Sample output for single market:

[{"orderNumber":"120466","type":"sell","rate":"0.025","amount":"100","total":"2.5"},{"orderNumber":"120467",
"type":"sell","rate":"0.04","amount":"100","total":"4"}, ... ]

Or, for all markets:

{"BTC_1CR":[],"BTC_AC":[{"orderNumber":"120466","type":"sell","rate":"0.025","amount":"100","total":"2.5"},
{"orderNumber":"120467","type":"sell","rate":"0.04","amount":"100","total":"4"}], ... }

-----------------------------------------------------------------------------------------------------------------------
returnTradeHistory
Returns your trade history for a given market, specified by the "currencyPair" POST parameter. You may specify "all" as
the currencyPair to receive your trade history for all markets. You may optionally specify a range via "start" and/or
"end" POST parameters, given in UNIX timestamp format; if you do not specify a range, it will be limited to one day.
Sample output:

[{ "globalTradeID": 25129732, "tradeID": "6325758", "date": "2016-04-05 08:08:40", "rate": "0.02565498",
"amount": "0.10000000", "total": "0.00256549", "fee": "0.00200000", "orderNumber": "34225313575", "type": "sell",
"category": "exchange" }, { "globalTradeID": 25129628, "tradeID": "6325741", "date": "2016-04-05 08:07:55",
"rate": "0.02565499", "amount": "0.10000000", "total": "0.00256549", "fee": "0.00200000", "orderNumber": "34225195693",
 "type": "buy", "category": "exchange" }, ... ]

Or, for all markets:

{"BTC_MAID": [ { "globalTradeID": 29251512, "tradeID": "1385888", "date": "2016-05-03 01:29:55", "rate": "0.00014243",
 "amount": "353.74692925", "total": "0.05038417", "fee": "0.00200000", "orderNumber": "12603322113", "type": "buy",
 "category": "settlement" }, { "globalTradeID": 29251511, "tradeID": "1385887", "date": "2016-05-03 01:29:55",
 "rate": "0.00014111", "amount": "311.24262497", "total": "0.04391944", "fee": "0.00200000",
"orderNumber": "12603319116", "type": "sell", "category": "marginTrade" }, ... ],"BTC_LTC":[ ... ] ... }

-----------------------------------------------------------------------------------------------------------------------
returnOrderTrades
Returns all trades involving a given order, specified by the "orderNumber" POST parameter. If no trades for the order
have occurred or you specify an order that does not belong to you, you will receive an error. Sample output:

[{"globalTradeID": 20825863, "tradeID": 147142, "currencyPair": "BTC_XVC", "type": "buy", "rate": "0.00018500",
"amount": "455.34206390", "total": "0.08423828", "fee": "0.00200000", "date": "2016-03-14 01:04:36"}, ...]

-----------------------------------------------------------------------------------------------------------------------
buy
Places a limit buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
If successful, the method will return the order number. Sample output:

{"orderNumber":31226040,"resultingTrades":[{"amount":"338.8732","date":"2014-10-18 23:03:21","rate":"0.00000173",
"total":"0.00058625","tradeID":"16164","type":"buy"}]}

You may optionally set "fillOrKill", "immediateOrCancel", "postOnly" to 1. A fill-or-kill order will either fill in its
entirety or be completely aborted. An immediate-or-cancel order can be partially or completely filled, but any portion
of the order that cannot be filled immediately will be canceled rather than left on the order book. A post-only order
will only be placed if no portion of it fills immediately; this guarantees you will never pay the taker fee on any
part of the order that fills.

-----------------------------------------------------------------------------------------------------------------------
sell
Places a sell order in a given market. Parameters and output are the same as for the buy method.

-----------------------------------------------------------------------------------------------------------------------
cancelOrder
Cancels an order you have placed in a given market. Required POST parameter is "orderNumber". If successful, the method
will return:

{"success":1}

-----------------------------------------------------------------------------------------------------------------------
moveOrder
Cancels an order and places a new one of the same type in a single atomic transaction, meaning either both operations
will succeed or both will fail. Required POST parameters are "orderNumber" and "rate"; you may optionally specify
 "amount" if you wish to change the amount of the new order. Sample output:

{"success":1,"orderNumber":"239574176","resultingTrades":{"BTC_BTS":[]}}

-----------------------------------------------------------------------------------------------------------------------
withdraw
Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the
withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address".
For XMR withdrawals, you may optionally specify "paymentId". Sample output:

{"response":"Withdrew 2398 NXT."}

-----------------------------------------------------------------------------------------------------------------------
returnFeeInfo
If you are enrolled in the maker-taker fee schedule, returns your current trading fees and trailing 30-day volume in BTC.
This information is updated once every 24 hours.

{"makerFee": "0.00140000", "takerFee": "0.00240000", "thirtyDayVolume": "612.00248891", "nextTier": "1200.00000000"}

-----------------------------------------------------------------------------------------------------------------------
returnAvailableAccountBalances
Returns your balances sorted by account. You may optionally specify the "account" POST parameter if you wish to fetch
only the balances of one account. Please note that balances in your margin account may not be accessible if you have
any open margin positions or orders. Sample output:

{"exchange":{"BTC":"1.19042859","BTM":"386.52379392","CHA":"0.50000000","DASH":"120.00000000","STR":"3205.32958001",
"VNL":"9673.22570147"},"margin":{"BTC":"3.90015637","DASH":"250.00238240","XMR":"497.12028113"},
"lending":{"DASH":"0.01174765","LTC":"11.99936230"}}

-----------------------------------------------------------------------------------------------------------------------
returnTradableBalances
Returns your current tradable balances for each currency in each market for which margin trading is enabled.
Please note that these balances may vary continually with market conditions. Sample output:

{"BTC_DASH":{"BTC":"8.50274777","DASH":"654.05752077"},"BTC_LTC":{"BTC":"8.50274777","LTC":"1214.67825290"},
"BTC_XMR":{"BTC":"8.50274777","XMR":"3696.84685650"}}

-----------------------------------------------------------------------------------------------------------------------
transferBalance
Transfers funds from one account to another (e.g. from your exchange account to your margin account). Required POST
parameters are "currency", "amount", "fromAccount", and "toAccount". Sample output:

{"success":1,"message":"Transferred 2 BTC from exchange to margin account."}

-----------------------------------------------------------------------------------------------------------------------
returnMarginAccountSummary
Returns a summary of your entire margin account. This is the same information you will find in the Margin Account
section of the Margin Trading page, under the Markets list. Sample output:

{"totalValue": "0.00346561","pl": "-0.00001220","lendingFees": "0.00000000","netValue": "0.00345341",
"totalBorrowedValue": "0.00123220","currentMargin": "2.80263755"}

-----------------------------------------------------------------------------------------------------------------------
marginBuy
Places a margin buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
You may optionally specify a maximum lending rate using the "lendingRate" parameter. If successful, the method will
 return the order number and any trades immediately resulting from your order. Sample output:

{"success":1,"message":"Margin order placed.","orderNumber":"154407998","resultingTrades":
{"BTC_DASH":[{"amount":"1.00000000","date":"2015-05-10 22:47:05","rate":"0.01383692",
"total":"0.01383692","tradeID":"1213556","type":"buy"}]}}

-----------------------------------------------------------------------------------------------------------------------
marginSell
Places a margin sell order in a given market. Parameters and output are the same as for the marginBuy method.

-----------------------------------------------------------------------------------------------------------------------
getMarginPosition
Returns information about your margin position in a given market, specified by the "currencyPair" POST parameter.
You may set "currencyPair" to "all" if you wish to fetch all of your margin positions at once. If you have no margin
position in the specified market, "type" will be set to "none". "liquidationPrice" is an estimate, and does not
necessarily represent the price at which an actual forced liquidation will occur. If you have no liquidation price,
the value will be -1. Sample output:

{"amount":"40.94717831","total":"-0.09671314",""basePrice":"0.00236190","liquidationPrice":-1,"pl":"-0.00058655",
"lendingFees":"-0.00000038","type":"long"}

-----------------------------------------------------------------------------------------------------------------------
closeMarginPosition
Closes your margin position in a given market (specified by the "currencyPair" POST parameter) using a market order.
This call will also return success if you do not have an open position in the specified market. Sample output:

{"success":1,"message":"Successfully closed margin position.","resultingTrades":{"BTC_XMR":[{"amount":"7.09215901",
"date":"2015-05-10 22:38:49","rate":"0.00235337","total":"0.01669047","tradeID":"1213346","type":"sell"},
{"amount":"24.00289920","date":"2015-05-10 22:38:49","rate":"0.00235321","total":"0.05648386","tradeID":"1213347",
"type":"sell"}]}}

-----------------------------------------------------------------------------------------------------------------------
createLoanOffer
Creates a loan offer for a given currency. Required POST parameters are "currency", "amount", "duration", "autoRenew"
(0 or 1), and "lendingRate". Sample output:

{"success":1,"message":"Loan order placed.","orderID":10590}

-----------------------------------------------------------------------------------------------------------------------
cancelLoanOffer
Cancels a loan offer specified by the "orderNumber" POST parameter. Sample output:

{"success":1,"message":"Loan offer canceled."}

-----------------------------------------------------------------------------------------------------------------------
returnOpenLoanOffers
Returns your open loan offers for each currency. Sample output:

{"BTC":[{"id":10595,"rate":"0.00020000","amount":"3.00000000","duration":2,"autoRenew":1,"date":"2015-05-10 23:33:50"}],
"LTC":[{"id":10598,"rate":"0.00002100","amount":"10.00000000","duration":2,"autoRenew":1,"date":"2015-05-10 23:34:35"}]}

-----------------------------------------------------------------------------------------------------------------------
returnActiveLoans
Returns your active loans for each currency. Sample output:

{"provided":[{"id":75073,"currency":"LTC","rate":"0.00020000","amount":"0.72234880","range":2,"autoRenew":0,
"date":"2015-05-10 23:45:05","fees":"0.00006000"},{"id":74961,"currency":"LTC","rate":"0.00002000",
"amount":"4.43860711","range":2,"autoRenew":0,"date":"2015-05-10 23:45:05","fees":"0.00006000"}],
"used":[{"id":75238,"currency":"BTC","rate":"0.00020000","amount":"0.04843834","range":2,
"date":"2015-05-10 23:51:12","fees":"-0.00000001"}]}

-----------------------------------------------------------------------------------------------------------------------
toggleAutoRenew
Toggles the autoRenew setting on an active loan, specified by the "orderNumber" POST parameter. If successful,
"message" will indicate the new autoRenew setting. Sample output:

{"success":1,"message":0}
-----------------------------------------------------------------------------------------------------------------------
'''
