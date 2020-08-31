#coding=utf-8

import sys
import glob as gb
import pandas as pd
from io import StringIO
import time
import datetime as dt
import re

from get_finance import getFinance

def getETF():
	folder = './ETF'
	file_list = [ f for f in sorted(gb.glob(folder+'/2*')) ]
	file_1 = file_list[-1]
	print(file_1)
	with open(file_1, 'r', encoding='UTF-8') as f:
		text = f.read()
		df_list = pd.read_html(text)
	return df_list

def getMarket(year, m, close, finance):
	mining = pd.DataFrame({})
	now = '{:04d}{:02d}'.format(year,m)
	halfYear = '{:04d}{:02d}'.format(year,m-4)
	price = close.transpose()
	mining['Price'] = price[now]
	mining['Market'] = finance['shares'][halfYear] * price[now]
	mining['Total'] = mining['Market']
	mining['Total_Rank'] = mining['Total'].rank(ascending=0)
	return mining.sort_values(by='Total_Rank')

def main(argv):
	#ETF = getETF()
	#ETF0050 = ETF[1].set_index('股票代號')
	#print(ETF0050.index)
	#sys.exit(-1)
	if 2 <= len(argv):
		date_str = argv[1]
	else:
		now=dt.datetime.now()
		date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
	year = int(date_str[0:4])
	month = int(date_str[4:6])
	try:
		today = pd.read_csv('./price_daily/'+ date_str).set_index('證券代號')
	except:
		print('Fail to crawl today price!')
		sys.exit(-1)
	print(date_str)
	finance = getFinance()
	close_dict = {}
	close_dict[date_str[0:6]] = pd.to_numeric(today['收盤價'], errors='coerce')
	close = pd.DataFrame(close_dict).transpose()
	mining = getMarket(year, month, close, finance)
	mining['Name'] = today['證券名稱']
	pd.set_option('display.max_rows', None)
	ETF = getETF()
	valid4number = re.compile(r'[a-zA-Z0-9]+')
	ETF0050 = ETF[1].set_index('股票代號')
	ETF0050composition = list(filter(valid4number.match, ETF0050.index))
	mining.loc[ETF0050composition,'0050'] = ETF0050['持股比率']
	ETF0100 = ETF[3].set_index('股票代號')
	ETF0100composition = list(filter(valid4number.match, ETF0100.index))
	mining.loc[ETF0100composition,'0100'] = ETF0100['持股比率']
	stocks_sorted = mining.head(200)
	print(mining['Total'].describe())
	print(stocks_sorted[['Name','Total_Rank','0050','0100']])

if __name__ == "__main__":
	main(sys.argv)
