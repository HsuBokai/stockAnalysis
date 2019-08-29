#coding=utf-8

from twstock import Stock
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

def get_price(stock_id):
	tmp = np.loadtxt('./' + stock_id + '/price.csv', dtype=np.str, delimiter=',')
	#return tmp[10:0:-1,2].astype(np.float)
	#return tmp[22:12:-1,2].astype(np.float)
	#return tmp[34:24:-1,2].astype(np.float)
	return tmp[46:36:-1,2].astype(np.float)

def return_of_rate(stock_id):
	tmp = get_price(stock_id)
	return np.mean(np.reciprocal(tmp) * tmp[-1])

def main():
	#s = Stock('2330')
	#s.fetch(2016,8)
	#print(s.close)
	#print(np.mean(s.close))
	
	data = { stock_id: get_price(stock_id) for stock_id in STOCKS }
	print(data)
	
	print(np.mean(list(map(return_of_rate, STOCKS))))

if __name__ == "__main__":
    main()
