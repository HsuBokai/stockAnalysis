#coding=utf-8

import sys
import pandas as pd
import requests
from io import StringIO
import time
import numpy as np
from datetime import datetime, timedelta


def crawl_price(date_str):
	r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_str + '&type=ALL')
	ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
					for i in r.text.split('\n') 
					if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	time.sleep(10)
	return pd.to_numeric(ret.set_index('證券代號')['收盤價'], errors='coerce')

def getClose(date_str):
	close_dict = { date_str[0:6] : crawl_price(date_str) }
	return pd.DataFrame(close_dict).transpose()
