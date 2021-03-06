#coding=utf-8

import sys
import pandas as pd
import requests
from io import StringIO
import time
import numpy as np
from datetime import datetime, timedelta


def crawlPrice(date_str):
	r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_str + '&type=ALL')
	ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
					for i in r.text.split('\n') 
					if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	ret['成交金額'] = ret['成交金額'].str.replace(',','')
	ret['成交股數'] = ret['成交股數'].str.replace(',','')
	ret['成交筆數'] = ret['成交筆數'].str.replace(',','')
	ret['開盤價'] = ret['開盤價'].str.replace(',','')
	ret['最高價'] = ret['最高價'].str.replace(',','')
	ret['最低價'] = ret['最低價'].str.replace(',','')
	ret['收盤價'] = ret['收盤價'].str.replace(',','')
	time.sleep(10)
	return ret.set_index('證券代號')
