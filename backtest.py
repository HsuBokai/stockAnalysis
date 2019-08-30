#coding=utf-8

from twstock import Stock
from functools import partial
import numpy as np

STOCKS = [ \
	'2801', \
	'2809', \
	'2812', \
	'2834', \
	'2836', \
	'2845', \
	'2849', \
	'2880', \
	'2883', \
	'2884', \
	'2885', \
	'2886', \
	'2888', \
	'2889', \
	'2890', \
	'2892', \
	'5820', \
	#'5876', \
	'5880', \
	]

YEAR_COLUMN_MAP = { \
	2018: 0, \
	2017: 12, \
	2016: 24, \
	2015: 36, \
	}

def backtest(year):
	end = YEAR_COLUMN_MAP[year]
	start = end + 10
	my_load = partial(np.loadtxt, dtype=np.str, delimiter=',')
	price_file = [ './' + s + '/price.csv' for s in STOCKS ]
	price_list = [ my_load(f)[start:end:-1, 2].astype(np.float) for f in price_file ]
	price_dict = dict(zip(STOCKS, price_list))
	#print(price_dict)
	return_list = [ np.reciprocal(price_dict[s]) * price_dict[s][-1] for s in STOCKS ]
	#print(return_list)
	AVG = np.mean(return_list)
	return_dict = dict(zip(STOCKS, return_list))
	#print(return_dict)
	invest = ['2880','2888','2801']
	INV = np.mean([ return_dict[stock_id][idx] for idx, stock_id in enumerate(invest) ])
	print('=============== ' + str(year) + ' ===============')
	print('AVG ReturnOfRate : ' + str(AVG))
	print('INV ReturnOfRate : ' + str(INV))
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
