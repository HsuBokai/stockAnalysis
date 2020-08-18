#coding=utf-8

import sys
import pandas as pd
import requests
import numpy as np
import time
import math
from datetime import datetime, timedelta

def financial_statement(year, season, type='綜合損益彙總表'):
	if year >= 1000:
		year -= 1911
	if type == '綜合損益彙總表':
		url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'
	elif type == '資產負債彙總表':
		url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'
	elif type == '營益分析彙總表':
		url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb06'
	else:
		print('type does not match')
	r = requests.post(url, {
			'encodeURIComponent':1,
			'step':1,
			'firstin':1,
			'off':1,
			'TYPEK':'sii',
			'year':str(year),
			'season':str(season),
			})
	r.encoding = 'utf8'
	dfs = pd.read_html(r.text, header=None)
	df = pd.concat(dfs[1:], axis=0, sort=False)
	time.sleep(10)
	return df

def main(argv):
	#return
	if 2 <= len(argv):
		date_str = argv[1]
		year = int(date_str[0:4])
		m = int(date_str[4:6])
	else:
		now=datetime.now()
		year=now.year
		m = now.month
		if 5 <= now.month:
			m -= 4
		else:
			year -= 1
			m += 12
			m -= 4
		if 1 != m % 3:
			return
		date_str = '{:04d}{:02d}'.format(year, m)
	print(date_str)
	season = math.floor((m-1)/3)+1
	financial_statement(year, season, '綜合損益彙總表').to_csv('/mnt/income/' + date_str)
	financial_statement(year, season, '資產負債彙總表').to_csv('/mnt/balance/' + date_str)

if __name__ == "__main__":
    main(sys.argv)
