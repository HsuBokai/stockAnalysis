import sys
import pandas as pd
import requests
from io import StringIO
import time
import datetime as dt
import notice

def crawl_monthly(year, month):
	date_str = '{:04d}{:02d}'.format(year, month)
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
	df.to_csv('/mnt/monthly/' + date_str)
	df = pd.read_csv('/mnt/monthly/' + date_str)
	df.columns = df.iloc[0]
	df = df.set_index('公司名稱')
	yoy = pd.to_numeric(df['去年同月增減(%)'], errors='coerce')
	mom = pd.to_numeric(df['上月比較增減(%)'], errors='coerce')
	mm = pd.concat([yoy, mom], axis=1)
	mm.columns = ['yoy','mom']
	time.sleep(10)
	return mm

def crawl_this_monthly():
	now = dt.datetime.now()
	if 1 == now.month:
		mm = crawl_monthly(now.year, 12)
	else:
		mm = crawl_monthly(now.year, now.month-1)
	key_list_new = [ x[1] for x in notice.WATCHDOG if x[2] == 'O' and x[1] in list(mm.index.values) ]
	new_data = mm.loc[key_list_new,:]
	return new_data

def monthly_info():
	this_file = '/mnt/monthly/this_monthly'
	old_data = pd.read_csv(this_file)
	key_list_old = old_data['公司名稱'].tolist()
	new_data = crawl_this_monthly()
	new_data.to_csv(this_file)
	key_list_new = list(new_data.index.values)
	key_list_addition = [ x for x in key_list_new if x not in key_list_old ]
	if 0 == len(key_list_addition):
		return ''
	else:
		return str(new_data.loc[key_list_addition,:])
