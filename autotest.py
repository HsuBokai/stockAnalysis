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

def readData(f, index_str, column_str_list):
	df = pd.read_csv(f)
	if f[:7] == 'monthly':
		df.columns = df.iloc[0]
	df['4number'] = pd.to_numeric(df[index_str], errors='coerce')
	df = df[df['4number'].notnull()]
	df['4number_str'] = df[index_str].astype(str)
	df = df.set_index('4number_str')
	df['value'] = np.nan
	for c in column_str_list:
		if c in df.columns:
			df.loc[df['value'].isnull(), 'value'] = df.loc[df['value'].isnull(), c]
	return pd.to_numeric(df['value'], errors='coerce')

def getData(folder, index_str, column_str_list):
	d = { f[-6:]:readData(f,index_str,column_str_list) for f in gb.glob(folder+'/*') }
	return pd.DataFrame(d).transpose().sort_index()

def cum2diff(df_cum):
	df = df_cum.rolling(4).apply(lambda x: max(x[3] - x[0], 0.01), raw=True)
	for date_str in df_cum.index:
		if date_str[-2:] in ['01','02','03']:
			df.loc[date_str] = df_cum.loc[date_str]
			df.loc[date_str, df.loc[date_str] < 0.01] = 0.01
	return df

def cum2last4season(df_cum):
	return cum2diff(df_cum).rolling(10).apply(lambda x: x[9]+x[6]+x[3]+x[0], raw=True)

def getMonth(m):
	if (m > 12):
		m-=12
	return '{:02d}'.format(m)

def getDate(year,m):
	if (m > 12):
		year+=1
		m-=12
	return '{:04d}{:02d}'.format(year,m)

def getClose(year,m):
	files = [ f for f in gb.glob('price/' + getDate(year,m) + '*') ]
	df = pd.read_csv(files[0])
	#cond1 = pd.to_numeric(df['收盤價'], errors='coerce') < 10
	#conds = [ df['證券代號'] == s for s in STOCKS.keys() ]
	#cond2 = ft.reduce(lambda c1, c2: c1 | c2, conds[1:], conds[0])
	#df = df[cond2]
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
	equality = pd.concat(equality_list,axis=1,sort=True).sum(axis=1)
	#print(equality)
	return equality / cost

def getFinance():
	finance = {}
	revenue = getData('monthly','公司代號',['當月營收'])
	finance['revenue'] = revenue.transpose() + 0.01
	finance['rev5mean'] = revenue.rolling(5).mean().transpose()
	#print(finance['revenue'])
	#print(finance['rev5mean'])
	eps_cum = getData('income','公司代號',['基本每股盈餘（元）'])
	finance['eps'] = cum2last4season(eps_cum).transpose()
	#print(finance['eps'].describe())
	#profit_cum = getData('income','公司代號',['本期淨利（淨損）'])
	#profit_cum = getData('income','公司代號',['本期稅後淨利（淨損）'])
	#rev_cum = getData('income','公司代號',['營業收入'])
	#finance['rev'] = cum2last4season(rev_cum).transpose()
	#print(finance['rev'].describe())
	finance['bps'] = getData('balance','公司代號',['每股參考淨值']).transpose()
	#print(finance['bps'].describe())
	finance['asset'] = getData('balance','公司代號',['資產總計','資產總額']).transpose()
	#print(finance['asset'].describe())
	finance['capital'] = getData('balance','公司代號',['權益總計','權益總額']).transpose()
	#print(finance['capital'].transpose()['2801'])
	finance['shares'] = getData('balance','公司代號',['股本']).transpose()
	#print(finance['shares'].describe())
	#print(finance)
	return finance

def getDecision(now, close, finance):
	#debug4number = '2330'
	#print(close.loc[now][debug4number])
	#print(finance['bps'][now].transpose()[debug4number])
	#print(finance['shares'][now].transpose()[debug4number])
	#print(finance['capital'][now].transpose()[debug4number])
	#print(finance['asset'][now].transpose()[debug4number])
	#print(finance['eps'][now].transpose()[debug4number])
	#print(finance['revenue'][now].transpose()[debug4number])
	#print(finance['rev5mean'][now].transpose()[debug4number])
	mining = pd.DataFrame({})
	mining['PB'] = close.transpose()[now] / finance['bps'][now]
	mining['PB_Rank'] = mining['PB'].rank(ascending=1)
	#print(mining['PB'])
	#print(mining['PB_Rank'])
	mining['PE'] = close.transpose()[now] / finance['eps'][now]
	mining['PE_Rank'] = mining['PE'].rank(ascending=1)
	#print(mining['PE'].describe())
	mining['ROE'] = finance['shares'][now] * finance['eps'][now] / finance['capital'][now]
	mining['ROE_Rank'] = mining['ROE'].rank(ascending=0)
	#print(mining['ROE'].describe())
	#print(mining['ROE_Rank'])
	mining['RA'] = finance['rev5mean'][now] / finance['asset'][now]
	mining['RA_Rank'] = mining['RA'].rank(ascending=0)
	#print(mining['RA'].describe())
	mining['SPR'] = finance['shares'][now] * close.transpose()[now] / finance['revenue'][now]
	mining['SPR_Rank'] = mining['SPR'].rank(ascending=1)
	#print(mining['SPR'].describe())
	############################## v2 ##############################
	mining['Rank'] = mining['PB_Rank'] + mining['PE_Rank'] + mining['ROE_Rank'] + mining['RA_Rank'] + mining['SPR_Rank']
	#print(mining.sort_values(by='Rank').head(100))
	return mining.sort_values(by='Rank').head(100).index
	############################## v1 ##############################
	cond1 = mining['ROE'] > 0.8
	cond2 = mining['PB'] < 0.8
	return mining[cond1 & cond2].index

def getRate(year, finance):
	close_dict = { getDate(year,m):getClose(year,m) for m in range(10,20) }
	close = pd.DataFrame(close_dict).transpose()
	#print(close)
	#print((close.iloc[-1,:] / close).mean(axis=1).describe())

	choose = [ getDecision(getDate(year,m), close, finance) for m in range(10,19) ]
	choose.append(choose[0])
	#choose = [ close.loc[:, close.iloc[i] < 20 ].columns for i in range(0,close.shape[0]) ]
	#choose = [ list(STOCKS.keys()) for i in range(0,close.shape[0]) ]
	#print(choose)

	index_rate = getIndex(close)
	return_rate = getReturn(close, choose)

	rate = pd.concat([index_rate, return_rate], axis=1, sort=True)
	rate.columns = [str(year)+'I',str(year)+'R']
	print(rate)
	return rate

def main():
	finance = getFinance()
	data = pd.concat([ getRate(year, finance) for year in YEAR_COLUMN_MAP.keys() ], axis=1, sort=True)
	#data.plot()
	#plt.savefig('/mnt/rate.svg')

if __name__ == "__main__":
    main()
