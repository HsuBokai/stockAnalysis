#coding=utf-8

from twstock import Stock
from functools import partial
import numpy as np

STOCKS = { \
	'2801' : '彰銀', \
	'2809' : '京城銀', \
	'2812' : '台中銀', \
	'2834' : '台企銀', \
	'2836' : '高雄銀', \
	'2845' : '遠東銀', \
	'2849' : '安泰銀', \
	'2880' : '華南金', \
	#'2883' : '開發金', \
	'2884' : '玉山金', \
	'2885' : '元大金', \
	'2886' : '兆豐金', \
	'2888' : '新光金', \
	'2889' : '國票金', \
	'2890' : '永豐金', \
	'2892' : '第一金', \
	'5820' : '日盛金', \
	#'5876' : '上海商銀', \
	'5880' : '合庫金', \
	}

YEAR_COLUMN_MAP = { \
	2018: 0, \
	2017: 12, \
	2016: 24, \
	2015: 36, \
	}

def decide(history):
	#print(history)
	yoy = [ np.sum(h[0:3]) / np.sum(h[12:15]) for h in history ]
	#print(yoy)
	yoy_dict = dict(zip(STOCKS.keys(), yoy))
	#print(yoy_dict)
	advise = [ k for k in sorted(yoy_dict, key=yoy_dict.get, reverse=True) ]
	#print(advise)
	#print([ yoy_dict[k] for k in sorted(yoy_dict, key=yoy_dict.get, reverse=True) ])
	return advise[0]

def analyze(year):
	my_load = partial(np.loadtxt, dtype=np.str, delimiter=',')
	sale_file = [ './' + s + '/SaleMonDetail.csv' for s in STOCKS.keys() ]
	sale_list = [ my_load(f)[:0:-1, 7].astype(np.float) for f in sale_file ]
	#sale_dict = dict(zip(STOCKS.keys(), sale_list))
	#print(sale_dict)
	end_month = YEAR_COLUMN_MAP[year]
	start_month = end_month + 10
	return [ decide([ l[0-m::-1] for l in sale_list ]) for m in range(start_month, end_month, -1) ]

def backtest(year):
	end = YEAR_COLUMN_MAP[year]
	start = end + 10
	my_load = partial(np.loadtxt, dtype=np.str, delimiter=',')
	price_file = [ './' + s + '/price.csv' for s in STOCKS.keys() ]
	price_list = [ my_load(f)[start:end:-1, 2].astype(np.float) for f in price_file ]
	price_dict = dict(zip(STOCKS.keys(), price_list))
	#print(price_dict)
	return_list = [ np.reciprocal(price_dict[s]) * price_dict[s][-1] for s in STOCKS.keys() ]
	#print(return_list)
	AVG = np.mean(return_list)
	return_dict = dict(zip(STOCKS.keys(), return_list))
	#print(return_dict)
	invest = analyze(year)
	INV = [ return_dict[stock_id][idx] for idx, stock_id in enumerate(invest) ]
	print('=============== ' + str(year) + ' ===============')
	print('AVG ReturnOfRate : ' + str(AVG))
	print('invest : ' + str([ STOCKS[i] for i in invest ]))
	print('INV ReturnOfRate : ' + str(INV))
	print('INV ReturnOfRate : ' + str(np.mean(INV)))
	print('===============' + '======' + '===============')

def main():
	#s = Stock('2330')
	#s.fetch(2016,8)
	#print(s.close)
	#print(np.mean(s.close))
	for year in YEAR_COLUMN_MAP.keys():
		backtest(year)

if __name__ == "__main__":
    main()
