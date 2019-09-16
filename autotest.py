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
	#'5820' : '日盛金', \
	#'5876' : '上海商銀', \
	'5880' : '合庫金', \
	}

YEAR_COLUMN_MAP = { \
	2018: 0, \
	#2017: 12, \
	#2016: 24, \
	#2015: 36, \
	}

def readData(f, index_str, column_str):
	df = pd.read_csv(f)
	if f[:7] == 'monthly':
		df.columns = df.iloc[0]
	df['4number'] = pd.to_numeric(df[index_str], errors='coerce')
	df = df[df['4number'].notnull()]
	return pd.to_numeric(df.set_index(index_str)[column_str], errors='coerce')

def getData(folder, index_str, column_str):
	d = { f[-6:]:readData(f,index_str,column_str) for f in gb.glob(folder+'/*') }
	return pd.DataFrame(d).transpose().sort_index()

def getMonth(m):
	if (m > 12):
		m-=12
	return '{:02d}'.format(m)

def getClose(year,m):
	if (m > 12):
		year+=1
		m-=12
	date_str = '{:04d}{:02d}'.format(year,m)
	files = [ f for f in gb.glob('price/' + date_str + '*') ]
	df = pd.read_csv(files[0])
	#cond1 = pd.to_numeric(df['收盤價'], errors='coerce') < 10
	conds = [ df['證券代號'] == s for s in STOCKS.keys() ]
	cond2 = ft.reduce(lambda c1, c2: c1 | c2, conds[1:], conds[0])
	df = df[cond2]
	return pd.to_numeric(df.set_index('證券代號')['收盤價'], errors='coerce')

def getIndex(close):
	equality = close.dropna(axis=1).mean(axis=1)
	#print(equality)
	return equality * range(1,equality.shape[0]+1) / equality.cumsum()

def getReturn(close, choose):
	cost_list = np.cumsum([ close[c].iloc[idx].sum()  for idx, c in enumerate(choose) ])
	#print(cost_list)
	cost = pd.DataFrame(data=cost_list, index=close.index).sum(axis=1)
	#print(cost)
	equality_list = [ close[c].sum(axis=1) for idx, c in enumerate(choose) ]
	for idx in range(0,close.shape[0]):
		equality_list[idx].iloc[:idx] = 0
	#print(equality_list[0])
	equality = pd.concat(equality_list,axis=1).sum(axis=1)
	#print(equality)
	return equality / cost

def getRate(year):
	close_dict = { getMonth(m):getClose(year,m) for m in range(10,20) }
	close = pd.DataFrame(close_dict).transpose()
	#print(close)
	#print((close.iloc[-1,:] / close).mean(axis=1).describe())

	revenue = getData('monthly','公司代號','當月營收')
	#print(revenue)
	revenue4 = revenue.rolling(4).mean()
	#print(revenue4)
	#print(revenue4.shift(-1) - revenue4)
	#print(revenue)
	eps = getData('income','公司代號','基本每股盈餘（元）')
	#print(eps)
	rev_cum = getData('income','公司代號','營業收入')
	print(rev_cum[2330])
	bps = getData('balance','公司代號','每股參考淨值')
	#print(bps)
	asset = getData('balance','公司代號','資產總計')
	#print(asset)
	capital = getData('balance','公司代號','權益總計')
	#print(capital)

	choose = [ close.loc[:, close.iloc[i] < 20 ].columns for i in range(0,close.shape[0]) ]
	#choose = [ list(STOCKS.keys()) for i in range(0,close.shape[0]) ]
	#print(choose)

	index_rate = getIndex(close)
	return_rate = getReturn(close, choose)

	rate = pd.concat([index_rate, return_rate], axis=1)
	rate.columns = [str(year)+'I',str(year)+'R']
	print(rate)
	return rate

def main():
	data = pd.concat([ getRate(year) for year in YEAR_COLUMN_MAP.keys() ], axis=1)
	#data.plot()
	#plt.savefig('/mnt/rate.svg')

if __name__ == "__main__":
    main()
