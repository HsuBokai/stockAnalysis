#coding=utf-8

import sys
import pandas as pd
import requests
from io import StringIO
import time
import datetime as dt
import buy

def crawl_price(date_str):
	print(date_str)
	r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_str + '&type=ALL')
	ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
					for i in r.text.split('\n') 
					if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	ret = ret.set_index('證券名稱')
	ret['成交金額'] = ret['成交金額'].str.replace(',','')
	ret['成交股數'] = ret['成交股數'].str.replace(',','')
	return pd.to_numeric(ret['收盤價'], errors='coerce')

def main(argv):
	if 2 <= len(argv):
		date_str = argv[1]
		now=dt.datetime(int(date_str[0:4]),int(date_str[4:6]),int(date_str[6:8]))
	else:
		now=dt.datetime.now()
		date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
	close = crawl_price(date_str)
	results_dict = {}
	for year,month,date,stock,cost in buy.BUY:
		if now < dt.datetime(year,month,date):
			continue
		price = close[stock]*1000
		diff = price - cost
		if stock not in results_dict:
			results_dict[stock] = [price , cost, diff]
		else:
			results_dict[stock][0] += price
			results_dict[stock][1] += cost
			results_dict[stock][2] += diff
	results = pd.DataFrame(data=results_dict.values(), index=results_dict.keys(), columns = ['price','cost','diff'])
	print(results)
	print('===== ToTal Sum =====')
	print(results.sum())
	time.sleep(10)

if __name__ == "__main__":
    main(sys.argv)
