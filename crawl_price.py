#coding=utf-8

import sys
import pandas as pd
import requests
from io import StringIO
import time
import numpy as np
from datetime import datetime, timedelta

def crawl_price(date_str):
	time.sleep(60)
	r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_str + '&type=ALL')
	ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
					for i in r.text.split('\n') 
					if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	ret = ret.set_index('證券代號')
	ret['成交金額'] = ret['成交金額'].str.replace(',','')
	ret['成交股數'] = ret['成交股數'].str.replace(',','')
	ret['成交筆數'] = ret['成交筆數'].str.replace(',','')
	ret['開盤價'] = ret['開盤價'].str.replace(',','')
	ret['最高價'] = ret['最高價'].str.replace(',','')
	ret['最低價'] = ret['最低價'].str.replace(',','')
	ret['收盤價'] = ret['收盤價'].str.replace(',','')
	return ret

def crawl_day(now):
	folder = './price_daily/'
	date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
	try:
		crawl_price(date_str).to_csv(folder + date_str)
		print(date_str)
	except:
		try:
			crawl_price(date_str).to_csv(folder + date_str)
			print(date_str)
		except:
			try:
				crawl_price(date_str).to_csv(folder + date_str)
				print(date_str)
			except:
				print(date_str + ' FAIL!')
				pass

def crawl_week(friday):
	day = friday
	for i in list(range(0,5)):
		crawl_day(day)
		day = day - timedelta(days=1)

def main(argv):
	#friday = datetime.now() - timedelta(days=27)
	#for i in list(range(0,3)):
	#	crawl_week(friday)
	#	friday = friday - timedelta(days=7)
	#return
	folder = './price_daily/'
	if 2 <= len(argv):
		date_str = argv[1]
		crawl_price(date_str).to_csv(folder + date_str)
	else:
		now=datetime.now()
		yesterday = now - timedelta(days=1)
		try:
			date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
			crawl_price(date_str).to_csv(folder + date_str)
		except:
			date_str = '{:04d}{:02d}{:02d}'.format(yesterday.year, yesterday.month, yesterday.day)
			crawl_price(date_str).to_csv(folder + date_str)

if __name__ == "__main__":
    main(sys.argv)
