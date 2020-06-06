#coding=utf-8

import sys
import pandas as pd
import requests
from io import StringIO
import time

def monthly_report(year, month):
	if year > 1990:
		year -= 1911
	url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'_0.html'
	if year <= 98:
		url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'.html'
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	r = requests.get(url, headers=headers)
	r.encoding = 'big5'
	dfs = pd.read_html(StringIO(r.text), encoding='big-5')
	df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
	time.sleep(10)
	return df

def main(argv):
	return
	#y=int(argv[1])
	#m=int(argv[2])
	y=2017
	for m in range(1,13):
		date_str = '{:04d}{:02d}'.format(y,m)
		print(date_str)
		monthly_report(y,m).to_csv('/mnt/monthly/' + date_str)
	#df = pd.read_csv('monthly/108_7')
	#print(df.head(5))

if __name__ == "__main__":
    main(sys.argv)
