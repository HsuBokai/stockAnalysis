#coding=utf-8

import sys
import pandas as pd
import glob as gb
import functools as ft
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from re import sub
from decimal import Decimal

def readData(f, index_str, column_str_list):
	df = pd.read_csv(f)
	df['4number'] = pd.to_numeric(df[index_str], errors='coerce')
	df = df[df['4number'].notnull()]
	df['4number_str'] = df[index_str].astype(str)
	df = df.set_index('4number_str')
	df['value'] = np.nan
	for c in column_str_list:
		if c in df.columns:
			null_index = df['value'].isnull()
			df.loc[null_index, 'value'] = df.loc[null_index, c]
	df['value'] = df['value'].apply(lambda x: '--' if '--' == x else Decimal(sub(r'[^\d.]', '', x)))
	return pd.to_numeric(df['value'], errors='coerce')

def ma_direct(file_list, day_list):
	close_dict = {}
	volume_dict = {}
	name_dict = {}
	for f in file_list:
		today = pd.read_csv(f).set_index('證券代號')
		close_dict[f[-8:]] = pd.to_numeric(today['收盤價'], errors='coerce')
		volume_dict[f[-8:]] = pd.to_numeric(today['成交股數'], errors='coerce') / 1000
		name_dict[f[-8:]] = today['證券名稱']
	close = pd.DataFrame(close_dict)
	volume = pd.DataFrame(volume_dict)
	name = pd.DataFrame(name_dict)
	d2 = {}
	d2['name'] = name.iloc[:,0-1]
	for day in day_list:
		d2['v'+str(day)] = volume.iloc[:,0-day:].mean(axis=1,skipna=True)
		d2['ma'+str(day)] = close.iloc[:,0-day:].mean(axis=1,skipna=True)
	ma = pd.DataFrame(d2)
	ma.index.name = '4number_str'
	return ma.round(5)

def ma_recursive(file_list, day_list):
	today_value = readData(file_list[-1],'證券代號',['收盤價'])
	yesterday_ma = pd.read_csv('price_ma/' + file_list[-2][-8:])
	yesterday_ma['4number_str'] = yesterday_ma['4number_str'].astype(str)
	yesterday_ma = yesterday_ma.set_index('4number_str')
	ma = pd.DataFrame({})
	for day in day_list:
		prev_value = readData(file_list[-1-day],'證券代號',['收盤價'])
		ma['ma'+str(day)] = yesterday_ma['ma'+str(day)] + ((today_value - prev_value).fillna(0) / day)
	return ma.round(5)

def main(argv):
	if 2 <= len(argv):
		date_str = argv[1]
	else:
		now=dt.datetime.now()
		date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
	folder = 'price_daily/'
	file_list = [ f for f in sorted(gb.glob(folder + '2*')) ]
	try:
		date_index = file_list.index(folder+date_str) + 1
	except:
		print('missing today price')
		return
	day_list = [1,2,3,4,5,10,20,40,60,120,240]
	scope = max(day_list)
	ma = ma_direct(file_list[date_index-scope-1:date_index], day_list)
	#ma = ma_recursive(file_list[date_index-scope-1:date_index], day_list)
	print(ma)
	ma.to_csv('./price_ma/' + date_str)

if __name__ == "__main__":
    main(sys.argv)
