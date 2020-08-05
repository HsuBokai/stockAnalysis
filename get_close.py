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
	time.sleep(10)
	return ret.set_index('證券代號')
