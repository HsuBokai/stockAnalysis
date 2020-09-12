#coding=utf-8

import sys
import pandas as pd
import glob as gb
import functools as ft
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from re import sub
import re
from decimal import Decimal

def readData(f, index_str, column_str_list):
	df = pd.read_csv(f)
	df['4number_str'] = df[index_str].astype(str)
	valid4number = re.compile(r'[a-zA-Z0-9]+')
	validindex = list(filter(valid4number.match, df['4number_str']))
	df = df.set_index('4number_str').loc[validindex, :]
	df['value'] = np.nan
	for c in column_str_list:
		if c in df.columns:
			null_index = df['value'].isnull()
			df.loc[null_index, 'value'] = df.loc[null_index, c]
	df['value'] = df['value'].apply(lambda x: '--' if '--' == x else Decimal(sub(r'[^\d.]', '', x)))
	return pd.to_numeric(df['value'], errors='coerce')

def regression_slope(df):
	regression = pd.DataFrame({})
	regression['mean_y'] = df.mean(axis=1,skipna=True)
	day = len(df.columns)
	xx = np.arange(0, day)
	regression['slope'] = regression['mean_y']-regression['mean_y']
	for idx,x in enumerate(xx - xx.mean()):
		regression['slope'] += (df.iloc[:,idx]-regression['mean_y']) * x
	return regression['slope']

def ma_direct(file_list, day_list):
	close_dict = {}
	high_dict = {}
	low_dict = {}
	rsv_dict = {}
	width_dict = {}
	volume_dict = {}
	name_dict = {}
	vma_dict = {}
	for f in file_list:
		today = pd.read_csv(f).set_index('證券代號')
		close_dict[f[-8:]] = pd.to_numeric(today['收盤價'], errors='coerce')
		high_dict[f[-8:]] = pd.to_numeric(today['最高價'], errors='coerce')
		low_dict[f[-8:]] = pd.to_numeric(today['最低價'], errors='coerce')
		rsv_dict[f[-8:]] = (close_dict[f[-8:]]-low_dict[f[-8:]]) / (high_dict[f[-8:]]-low_dict[f[-8:]])
		width_dict[f[-8:]] = (high_dict[f[-8:]]-low_dict[f[-8:]]) / close_dict[f[-8:]]
		volume_dict[f[-8:]] = pd.to_numeric(today['成交股數'], errors='coerce') / 1000
		name_dict[f[-8:]] = today['證券名稱']
		vma_dict[f[-8:]] = close_dict[f[-8:]] * volume_dict[f[-8:]]
	close = pd.DataFrame(close_dict)
	high = pd.DataFrame(high_dict)
	low = pd.DataFrame(low_dict)
	rsv = pd.DataFrame(rsv_dict)
	width = pd.DataFrame(width_dict)
	volume = pd.DataFrame(volume_dict)
	name = pd.DataFrame(name_dict)
	vma = pd.DataFrame(vma_dict)
	d2 = {}
	d2['name'] = name.iloc[:,0-1]
	for day in day_list:
		d2['v'+str(day)] = volume.iloc[:,0-day:].mean(axis=1,skipna=True)
		d2['vS'+str(day)] = regression_slope(volume.iloc[:,0-day:])
		d2['ma'+str(day)] = close.iloc[:,0-day:].mean(axis=1,skipna=True)
		d2['maS'+str(day)] = regression_slope(close.iloc[:,0-day:])
		d2['h'+str(day)] = high.iloc[:,0-day:].max(axis=1,skipna=True)
		d2['l'+str(day)] = low.iloc[:,0-day:].min(axis=1,skipna=True)
		d2['rsv'+str(day)] = rsv.iloc[:,0-day:].mean(axis=1,skipna=True)
		d2['rsvS'+str(day)] = regression_slope(rsv.iloc[:,0-day:])
		d2['vma'+str(day)] = vma.iloc[:,0-day:].mean(axis=1,skipna=True)
		d2['w'+str(day)] = width.iloc[:,0-day:].mean(axis=1,skipna=True)
		d2['wS'+str(day)] = regression_slope(width.iloc[:,0-day:])
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

def moving_average(date_str):
	folder = 'price_daily/'
	file_list = [ f for f in sorted(gb.glob(folder + '2*')) ]
	try:
		date_index = file_list.index(folder+date_str) + 1
	except:
		print('missing today price')
		return
	day_list = [1,2,3,4,5,10,20,30,40,50,60,120,240]
	scope = max(day_list)
	ma = ma_direct(file_list[date_index-scope-1:date_index], day_list)
	#ma = ma_recursive(file_list[date_index-scope-1:date_index], day_list)
	#print(ma)
	print(date_str)
	ma.to_csv('./price_ma/' + date_str)

def crawl_week(friday):
	today = friday
	for i in list(range(0,5)):
		date_str = '{:04d}{:02d}{:02d}'.format(today.year,today.month,today.day)
		moving_average(date_str)
		today = today - timedelta(days=1)

def main(argv):
	#friday = datetime(2020, 3, 20, 0, 0)
	#for i in list(range(0,20)):
	#	crawl_week(friday)
	#	friday = friday - timedelta(days=7)
	#return
	if 2 <= len(argv):
		date_str = argv[1]
	else:
		now=datetime.now()
		date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
	moving_average(date_str)

if __name__ == "__main__":
    main(sys.argv)
