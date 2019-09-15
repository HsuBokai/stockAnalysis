#coding=utf-8

import pandas as pd
import glob as gb
import functools as ft
import numpy as np
import matplotlib.pyplot as plt

STOCKS = { \
	'2801' : '彰銀', \
	'2809' : '京城銀', \
	'2812' : '台中銀', \
	'2834' : '台企銀', \
	'2836' : '高雄銀', \
	'2845' : '遠東銀', \
	'2849' : '安泰銀', \
	'2880' : '華南金', \
	'2883' : '開發金', \
	'2884' : '玉山金', \
	'2885' : '元大金', \
	'2886' : '兆豐金', \
	'2888' : '新光金', \
	'2889' : '國票金', \
	'2890' : '永豐金', \
	'2892' : '第一金', \
	'5820' : '日盛金', \
	#'5876' : '上海商銀', \
	'5880' : '合庫金', \
	}

YEAR_COLUMN_MAP = { \
	2018: 0, \
	2017: 12, \
	#2016: 24, \
	#2015: 36, \
	}

def getClose(date_str):
	files = [ f for f in gb.glob('price/' + date_str + '*') ]
	df = pd.read_csv(files[0])
	#cond1 = pd.to_numeric(df['收盤價'], errors='coerce') < 10
	conds = [ df['證券名稱'] == s for s in STOCKS.values() ]
	cond2 = ft.reduce(lambda c1, c2: c1 | c2, conds[1:], conds[0])
	df = df[cond2]
	return pd.to_numeric(df.set_index('證券名稱')['收盤價'], errors='coerce')

def getIndex(close):
	equality = close.dropna(axis=1).mean(axis=1)
	#print(equality)
	return equality * range(1,equality.shape[0]+1) / equality.cumsum()

def getReturn(close, choose):
	cost_list = np.cumsum([ c.iloc[idx].sum()  for idx, c in enumerate(choose) ])
	#print(cost_list)
	cost = pd.DataFrame(data=cost_list, index=close.index).sum(axis=1)
	#print(cost)
	equality_list = [ c.sum(axis=1) for idx, c in enumerate(choose) ]
	for idx in range(0,close.shape[0]):
		equality_list[idx].iloc[:idx] = 0
	#print(equality_list[0])
	equality = pd.concat(equality_list,axis=1).sum(axis=1)
	#print(equality)
	return equality / cost

def getRate(year):
	close_dict = {}
	for m in range(10,13):
		date_str = '{:04d}{:02d}'.format(year,m)
		close_dict['{:02d}'.format(m)] = getClose(date_str)
	year+=1
	for m in range(1,8):
		date_str = '{:04d}{:02d}'.format(year,m)
		close_dict['{:02d}'.format(m)] = getClose(date_str)
	close = pd.DataFrame(close_dict).transpose()
	#print(close)
	#print((close.iloc[-1,:] / close).mean(axis=1).describe())

	choose = [ close.loc[:, close.iloc[i] < 20 ] for i in range(0,close.shape[0]) ]
	#choose = [ close for i in range(0,close.shape[0]) ]
	#print([ c.iloc[0] for c in choose ])

	index_rate = getIndex(close)
	return_rate = getReturn(close, choose)

	rate = pd.concat([index_rate, return_rate], axis=1)
	rate.columns = [str(year)+'I',str(year)+'R']
	print(rate)
	return rate

def main():
	data = pd.concat([ getRate(year) for year in YEAR_COLUMN_MAP.keys() ], axis=1)
	data.plot()
	plt.savefig('/mnt/rate.svg')

if __name__ == "__main__":
    main()
