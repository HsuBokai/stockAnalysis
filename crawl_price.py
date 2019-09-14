#coding=utf-8

import sys
import pandas as pd
import requests
from io import StringIO
import time
import numpy as np

def crawl_price(date_str):
	print(date_str)
	r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_str + '&type=ALL')
	ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
					for i in r.text.split('\n') 
					if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	ret = ret.set_index('證券代號')
	ret['成交金額'] = ret['成交金額'].str.replace(',','')
	ret['成交股數'] = ret['成交股數'].str.replace(',','')
	time.sleep(10)
	return ret

def main(argv):
	return
	#date_str = argv[1]
	y=2017
	for m in range(1,13):
		try:
			date_str = '{:04d}{:02d}{:02d}'.format(y,m,5)
			crawl_price(date_str).to_csv('./price/' + date_str)
		except:
			date_str = '{:04d}{:02d}{:02d}'.format(y,m,7)
			crawl_price(date_str).to_csv('./price/' + date_str)

if __name__ == "__main__":
    main(sys.argv)
