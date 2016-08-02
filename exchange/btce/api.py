# coding=utf-8

import exchange.btce.btcelib as btcelib
import exchange.btce.btcelib2 as btcelib2
import exchange.btce.config as config


class API:
    papi = None
    tapi = None

    def __init__(self):
        self.papi = btcelib2.PublicAPIv3()
        self.tapi = btcelib2.TradeAPIv1(config.apikey, compr=True)

    '''
    Вызов метода PUBLIC API
    '''

    def btce_public_api(self, method, **params):
        return self.papi.call(method, **params)

    '''
    Вызов метода AUTH API
    '''

    def btce_api(self, method, **params):
        return self.tapi.call(method, **params)



'''
------------------------------------------------------------------------------------------------------------------------
PUBLIC API

Contents
This api provides access to such information as tickers of currency pairs, active orders on different pairs, the latest trades for each pair etc.

All API requests are made from this address:
https://btc-e.com/api/3/<method name>/<pair listing>

Currency pairs are hyphen-separated (-), e.g.:
https://btc-e.nz/api/3/ticker/btc_usd-btc_rur

You can use as many pairs in the listing as you wish. Duplicates are not allowed. It is also possible to use only one pair:
https://btc-e.nz/api/3/ticker/btc_usd
A set of pairs works with all the methods presented in the public api except info.

All information is cached every 2 seconds, so there's no point in making more frequent requests.
All API responses have the following format JSON.

Important! API will display an error if we disable one of the pairs listed in your request. If you are not going to synchronize the state of pairs using the method info, you need to send the GET-parameter ignore_invalid equal to 1, e.g.:
https://btc-e.nz/api/3/ticker/btc_usd-btc_btc?ignore_invalid=1
Without the parameter ignore_invalid this request would have caused an error because of a non-existent pair.


------------------------------------------------------------------------------------------------------------------------
Method info
This method provides all the information about currently active pairs, such as the maximum number of digits after the decimal point, the minimum price, the maximum price, the minimum transaction size, whether the pair is hidden, the commission for each pair.

Sample request:
https://btc-e.nz/api/3/info

Sample response:
{
	"server_time":1370814956,
	"pairs":{
		"btc_usd":{
			"decimal_places":3,
			"min_price":0.1,
			"max_price":400,
			"min_amount":0.01,
			"hidden":0,
			"fee":0.2
		}
		...
	}
}

decimal_places: number of decimals allowed during trading.
min_price: minimum price allowed during trading.
max_price: maximum price allowed during trading.
min_amount: minimum sell / buy transaction size.
hidden: whether the pair is hidden, 0 or 1.
fee: commission for this pair.

A hidden pair (hidden=1) remains active but is not displayed in the list of pairs on the main page.
The Commission is displayed for all users, it will not change even if it was reduced on your account in case of promotional pricing.
If one of the pairs is disabled, it will simply disappear from the list.
------------------------------------------------------------------------------------------------------------------------
Method ticker
This method provides all the information about currently active pairs, such as: the maximum price, the minimum price, average price, trade volume, trade volume in currency, the last trade, Buy and Sell price.
All information is provided over the past 24 hours.

Sample request:
https://btc-e.nz/api/3/ticker/btc_usd

Sample response:
{
	"btc_usd":{
		"high":109.88,
		"low":91.14,
		"avg":100.51,
		"vol":1632898.2249,
		"vol_cur":16541.51969,
		"last":101.773,
		"buy":101.9,
		"sell":101.773,
		"updated":1370816308
	}
	...
}

high: maximum price.
low: minimum price.
avg: average price.
vol: trade volume.
vol_cur: trade volume in currency.
last: the price of the last trade.
buy: buy price.
sell: sell price.
updated: last update of cache.
------------------------------------------------------------------------------------------------------------------------
Method depth
This method provides the information about active orders on the pair.

Additionally it accepts an optional GET-parameter limit, which indicates how many orders should be displayed (150 by default).
Is set to less than 2000.

Sample request:
https://btc-e.nz/api/3/depth/btc_usd

Sample response:
{
	"btc_usd":{
		"asks":[
			[103.426,0.01],
			[103.5,15],
			[103.504,0.425],
			[103.505,0.1],
			...
		],
		"bids":[
			[103.2,2.48502251],
			[103.082,0.46540304],
			[102.91,0.99007913],
			[102.83,0.07832332],
			...
		]
	}
	...
}

asks: Sell orders.
bids: Buy orders.
------------------------------------------------------------------------------------------------------------------------
Method trades
This method provides the information about the last trades.

Additionally it accepts an optional GET-parameter limit, which indicates how many orders should be displayed (150 by default).
The maximum allowable value is 2000.

Sample request:
https://btc-e.nz/api/3/trades/btc_usd

Sample response:
{
	"btc_usd":[
		{
			"type":"ask",
			"price":103.6,
			"amount":0.101,
			"tid":4861261,
			"timestamp":1370818007
		},
		{
			"type":"bid",
			"price":103.989,
			"amount":1.51414,
			"tid":4861254,
			"timestamp":1370817960
		},
		...
	]
	...
}

type: ask – Sell, bid – Buy.
price: Buy price/Sell price.
amount: the amount of asset bought/sold.
tid: trade ID.
timestamp: UNIX time of the trade.
------------------------------------------------------------------------------------------------------------------------
TRADE API

Contents
This API allows to trade on the exchange and receive information about the account.

To use this API, you need to create an API key.
An API key can be created in your Profile in the API Keys section. After creating an API key you’ll receive a key and a secret.
Note that the Secret can be received only during the first hour after the creation of the Key.
API key information is used for authentication.

All requests to Trade API come from the following URL: https://btc-e.com/tapi
The method name is sent via the POST-parameter method.
All method parameters are sent via the POST-parameters.
All server responses are received in the JSON format.
Each request needs an authentication. You can find out more on authentication in the relevant section of this documentation.

In the case of successful request, the response will be of the following type:
{
	"success":1,
	"return":{<response>}
}
Response in the case of error:
{
	"success":0,
	"error":"<error>"
}

In the case of error you may also receive a response not in the JSON format. It usually happens if API limits are exceeded or in the case of unknown errors.
------------------------------------------------------------------------------------------------------------------------
Method getInfo
Returns information about the user’s current balance, API-key privileges, the number of open orders and Server Time.
To use this method you need a privilege of the key info.
Parameters:
None.
Sample response:
{
	"success":1,
	"return":{
		"funds":{
			"usd":325,
			"btc":23.998,
			"ltc":0,
			...
		},
		"rights":{
			"info":1,
			"trade":0,
			"withdraw":0
		},
		"transaction_count":0,
		"open_orders":1,
		"server_time":1342123547
	}
}

funds: Your account balance available for trading. Doesn’t include funds on your open orders.
rights: The privileges of the current API key. At this time the privilege to withdraw is not used anywhere.
transaction_count: Deprecated, is equal to 0.
open_orders: The number of your open orders.
server_time: Server time (MSK).
------------------------------------------------------------------------------------------------------------------------
Method Trade
The basic method that can be used for creating orders and trading on the exchange.
To use this method you need an API key privilege to trade.

You can only create limit orders using this method, but you can emulate market orders using rate parameters. E.g. using rate=0.1 you can sell at the best market price.
Each pair has a different limit on the minimum / maximum amounts, the minimum amount and the number of digits after the decimal point. All limitations can be obtained using the info method in PublicAPI v3.
Parameters:
Parameter	description	assumes value
pair	pair	btc_usd (example)
type	order type	buy or sell
rate	the rate at which you need to buy/sell	numerical
amount	the amount you need to buy / sell	numerical

You can get the list of pairs using the info method in PublicAPI v3.
Sample response:
{
	"success":1,
	"return":{
		"received":0.1,
		"remains":0,
		"order_id":0,
		"funds":{
			"usd":325,
			"btc":2.498,
			"ltc":0,
			...
		}
	}
}

received: The amount of currency bought/sold.
remains: The remaining amount of currency to be bought/sold (and the initial order amount).
order_id: Is equal to 0 if the request was fully “matched” by the opposite orders, otherwise the ID of the executed order will be returned.
funds: Balance after the request.
------------------------------------------------------------------------------------------------------------------------
Method ActiveOrders
Returns the list of your active orders.
To use this method you need a privilege of the info key.

If the order disappears from the list, it was either executed or canceled.
Optional parameters:
Parameter	description	assumes value	standard value
pair	pair	btc_usd (example)	all pairs

You can get the list of pairs using the info method in PublicAPI v3.
Sample response:
{
	"success":1,
	"return":{
		"343152":{
			"pair":"btc_usd",
			"type":"sell",
			"amount":12.345,
			"rate":485,
			"timestamp_created":1342448420,
			"status":0
		},
		...
	}
}

Array key : Order ID.
pair: The pair on which the order was created.
type: Order type, buy/sell.
amount: The amount of currency to be bought/sold.
rate: Sell/Buy price.
timestamp_created: The time when the order was created.
status: Deprecated, is always equal to 0.
------------------------------------------------------------------------------------------------------------------------
Method OrderInfo
Returns the information on particular order.
To use this method you need a privilege of the info key.
Parameters:
Parameter	description	assumes value
order_id	order ID	numerical
Sample response:
{
	"success":1,
	"return":{
		"343152":{
			"pair":"btc_usd",
			"type":"sell",
			"start_amount":13.345,
			"amount":12.345,
			"rate":485,
			"timestamp_created":1342448420,
			"status":0
		}
	}
}

Array key: Order ID.
pair: The pair on which the order was created
type: Order type, buy/sell.
start_amount: The initial amount at the time of order creation.
amount: The remaining amount of currency to be bought/sold.
rate: Sell/Buy price.
timestamp_created: The time when the order was created.
status: 0 - active, 1 – executed order, 2 - canceled, 3 – canceled, but was partially executed.
------------------------------------------------------------------------------------------------------------------------
Method CancelOrder
This method is used for order cancelation.
To use this method you need a privilege of the trade key.
Parameters:
Parameter	description	assumes value
order_id	order ID	numerical
Sample response:
{
	"success":1,
	"return":{
		"order_id":343154,
		"funds":{
			"usd":325,
			"btc":24.998,
			"ltc":0,
			...
		}
	}
}

order_id: The ID of canceled order.
funds: Balance upon request.
------------------------------------------------------------------------------------------------------------------------
Method TradeHistory
Returns trade history.
To use this method you need a privilege of the info key.
Optional parameters:
Parameter	description	assumes value	standard value
from	trade ID, from which the display starts	numerical	0
count	the number of trades for display	numerical	1000
from_id	trade ID, from which the display starts	numerical	0
end_id	trade ID on which the display ends	numerical	∞
order	Sorting	ASC or DESC	DESC
since	the time to start the display	UNIX time	0
end	the time to end the display	UNIX time	∞
pair	pair to be displayed	btc_usd (example)	all pairs

When using parameters since or end, the order parameter automatically assumes the value ASC.
When using the since parameter the maximum time that can displayed is 1 week.
Sample response:
{
	"success":1,
	"return":{
		"166830":{
			"pair":"btc_usd",
			"type":"sell",
			"amount":1,
			"rate":450,
			"order_id":343148,
			"is_your_order":1,
			"timestamp":1342445793
		}
	}
}

Array keys: Trade ID.
pair: The pair on which the trade was executed.
type: Trade type, buy/sell.
amount: The amount of currency was bought/sold.
rate: Sell/Buy price.
order_id: Order ID.
is_your_order: Is equal to 1 if order_id is your order, otherwise is equal to 0.
timestamp: Trade execution time.
------------------------------------------------------------------------------------------------------------------------
Method TransHistory
Returns the history of transactions.
To use this method you need a privilege of the info key.
Optional parameters:
Parameter	description	assumes value	standard value
from	transaction ID, from which the display starts	numerical	0
count	number of transaction to be displayed	numerical	1000
from_id	transaction ID, from which the display starts	numerical	0
end_id	transaction ID on which the display ends	numerical	∞
order	sorting	ASC or DESC	DESC
since	the time to start the display	UNIX time	0
end	the time to end the display	UNIX time	∞

When using the parameters since or end, the order parameter automatically assumes the value ASC.
Sample response:
{
	"success":1,
	"return":{
		"1081672":{
			"type":1,
			"amount":1.00000000,
			"currency":"BTC",
			"desc":"BTC Payment",
			"status":2,
			"timestamp":1342448420
		}
	}
}

Array keys: Transaction ID.
type: Transaction type. 1/2 - deposit/withdrawal, 4/5 - credit/debit.
amount: Transaction amount.
currency: Transaction currency.
desc: Transaction description.
status: Transaction status. 0 - canceled/failed, 1 - waiting for acceptance, 2 - successful, 3 – not confirmed
timestamp: Transaction time.
------------------------------------------------------------------------------------------------------------------------
WithdrawCoin Method
The method is designed for cryptocurrency withdrawals.
Please note: You need to have the privilege of the Withdraw key to be able to use this method. You can make a request for enabling this privilege by submitting a ticket to Support.
You need to create the API key that you are going to use for this method in advance. Please provide the first 8 characters of the key (e.g. HKG82W66) in your ticket to support. We'll enable the Withdraw privilege for this key.
When using this method, there will be no additional confirmations of withdrawal. Please note that you are fully responsible for keeping the secret of the API key safe after we have enabled the Withdraw privilege for it.
Parameters:
Parameter	Description	Assumes value
coinName	currency	BTC, LTC (example)
amount	withdrawal amount	numeric
address	withdrawal address	address
Sample response:
{
	"success":1,
	"return":{
		"tId":37832629,
		"amountSent":0.009,
		"funds":{
			"usd":325,
			"btc":24.998,
			"ltc":0,
			...
		}
	}
}

tId: Transaction ID.
amountSent: The amount sent including commission.
funds: Balance after the request.
------------------------------------------------------------------------------------------------------------------------
CreateCoupon Method
This method allows you to create Coupons.
Please, note: In order to use this method, you need the Coupon key privilege. You can make a request to enable it by submitting a ticket to Support..
You need to create the API key that you are going to use for this method in advance. Please provide the first 8 characters of the key (e.g. HKG82W66) in your ticket to support. We'll enable the Coupon privilege for this key.
You must also provide us the IP-addresses from which you will be accessing the API.
When using this method, there will be no additional confirmations of transactions. Please note that you are fully responsible for keeping the secret of the API key safe after we have enabled the Withdraw privilege for it.
Parameters:
parameter	description	assumes value
currency	currency	USD, BTC (example)
amount	withdrawal amount	numeric
Sample response:
{
	"success":1,
	"return":{
		"coupon":"BTCE-USD-69AA4BBX-1UAZ32BP-LKBR0QZT-X5AENVNF-WNZHNQDZ",
		"transID":37832629,
		"funds":{
			"usd":325,
			"btc":24.998,
			"ltc":0,
			...
		}
	}
}

coupon: Generated coupon.
transID: Transaction ID.
funds: Balance after the request.
------------------------------------------------------------------------------------------------------------------------
RedeemCoupon Method
This method is used to redeem coupons.
Please, note: In order to use this method, you need the Coupon key privilege. You can make a request to enable it by submitting a ticket to Support..
You need to create the API key that you are going to use for this method in advance. Please provide the first 8 characters of the key (e.g. HKG82W66) in your ticket to support. We'll enable the Coupon privilege for this key.
You must also provide us the IP-addresses from which you will be accessing the API.
When using this method, there will be no additional confirmations of transactions. Please note that you are fully responsible for keeping the secret of the API key safe after we have enabled the Withdraw privilege for it.
Parameters:
parameter	description	assumes value
coupon	coupon	BTCE-USD... (example)
Sample response:
{
	"success":1,
	"return":{
		"couponAmount":"1",
		"couponCurrency":"USD",
		"transID":37832629,
		"funds":{
			"usd":325,
			"btc":24.998,
			"ltc":0,
			...
		}
	}
}

couponAmount: The amount that has been redeemed.
couponCurrency: The currency of the coupon that has been redeemed.
transID: Transaction ID.
funds: Balance after the request.
------------------------------------------------------------------------------------------------------------------------
'''