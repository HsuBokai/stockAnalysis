#coding=utf-8

import sys
import pandas as pd
import glob as gb
import functools as ft
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

def readData(f, index_str, column_str_list):
	df = pd.read_csv(f)
	df['4number'] = pd.to_numeric(df[index_str], errors='coerce')
	df = df[df['4number'].notnull()]
	df['4number_str'] = df[index_str].astype(str)
	df = df.set_index('4number_str')
	df['value'] = np.nan
	for c in column_str_list:
		if c in df.columns:
			df.loc[df['value'].isnull(), 'value'] = df.loc[df['value'].isnull(), c]
	return pd.to_numeric(df['value'], errors='coerce')

def ma_direct(file_list, day_list):
	d = { f[-8:] : readData(f,'證券代號',['收盤價']) for f in file_list }
	close = pd.DataFrame(d)
	d2 = { 'ma'+str(day) : close.iloc[:,0-day:].mean(axis=1) for day in day_list }
	return pd.DataFrame(d2)

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
	day_list = [1,2,5,10,20]
	scope = max(day_list)
	ma = ma_direct(file_list[date_index-scope:date_index], day_list)
	print(ma)
	ma.to_csv('./price_ma/' + date_str)

if __name__ == "__main__":
    main(sys.argv)
