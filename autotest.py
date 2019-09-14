#coding=utf-8

import pandas as pd
import glob as gb
import functools as ft

STOCKS = { \
	'2801' : '彰銀', \
	'2809' : '京城銀', \
	'2812' : '台中銀', \
	'2834' : '台企銀', \
	'2836' : '高雄銀', \
	'2845' : '遠東銀', \
	'2849' : '安泰銀', \
	'2880' : '華南金', \
	#'2883' : '開發金', \
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

def autotest(y):
	close_dict = {}
	for m in range(10,13):
		date_str = '{:04d}{:02d}'.format(y,m)
		close_dict[date_str] = getClose(date_str)
	y+=1
	for m in range(1,8):
		date_str = '{:04d}{:02d}'.format(y,m)
		close_dict[date_str] = getClose(date_str)
	close = pd.DataFrame(close_dict).transpose()
	#print(close)
	#print(close.iloc[-1,:] / close)
	print((close.iloc[-1,:] / close).mean(axis=1).describe())

def main():
	for year in YEAR_COLUMN_MAP.keys():
		autotest(year)

if __name__ == "__main__":
    main()
