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
	d = { f[-6:]:readData(f,index_str,column_str_list) for f in gb.glob(folder+'/2*') }
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
	rev5mean = revenue.rolling(5).mean()
	finance['rev5mean'] = rev5mean.transpose() + 0.01
	#print(finance['revenue'])
	#print(finance['rev5mean'])
	finance['revgrowth'] = rev5mean.rolling(10).apply(lambda x: int(x[0]>x[5])+int(x[1]>x[6])+int(x[2]>x[7])+int(x[3]>x[8])+int(x[4]>x[9]), raw=True).transpose()
	#print(finance['revgrowth'])
	eps_cum = getData('income','公司代號',['基本每股盈餘（元）'])
	#print(eps_cum)
	finance['eps'] = cum2last4season(eps_cum).transpose()
	#print(finance['eps'].describe())
	profit_cum = getData('income','公司代號',['本期稅後淨利（淨損）','本期淨利（淨損）'])
	finance['profit'] = cum2last4season(profit_cum).transpose()
	#print(finance['profit'].describe())
	ebit_cum = getData('income','公司代號',['營業利益（損失）'])
	#print(ebit_cum)
	finance['ebit'] = cum2last4season(ebit_cum).transpose()
	#print(finance['ebit'].describe())
	#rev_cum = getData('income','公司代號',['營業收入'])
	#finance['rev'] = cum2last4season(rev_cum).transpose()
	#print(finance['rev'].describe())
	finance['bps'] = getData('balance','公司代號',['每股參考淨值']).transpose()
	#print(finance['bps'].describe())
	finance['asset'] = getData('balance','公司代號',['資產總計','資產總額']).transpose()
	#print(finance['asset'].describe())
	finance['assetFree'] = getData('balance','公司代號',['流動資產']).transpose()
	#finance['assetFree'] = getData('balance','公司代號',['現金及約當現金']).transpose()
	#print(finance['assetFree'].describe())
	finance['debt'] = getData('balance','公司代號',['負債總計','負債總額']).transpose()
	#print(finance['debt'].describe())
	capital = getData('balance','公司代號',['權益總計','權益總額'])
	finance['capital'] = capital.transpose()
	finance['cap4avg'] = capital.rolling(10).apply(lambda x: (x[9]+x[6]+x[3]+x[0])/4, raw=True).transpose()
	#print(finance['capital'])
	#print(finance['cap4avg'])
	shares = getData('balance','公司代號',['股本'])
	finance['shares'] = shares.transpose()
	#finance['sha4avg'] = shares.rolling(10).apply(lambda x: (x[9]+x[6]+x[3]+x[0])/4, raw=True).transpose()
	#print(finance['shares'].describe())
	#print(finance)
	return finance

def getFormula(name, finance, time):
	if name == 'ROE':
		return finance['profit'][time]/finance['cap4avg'][time]
	if name == 'RA':
		return finance['rev5mean'][time]/finance['asset'][time]

def getLongTermAvg(year, m, ref, finance):
	now = getDate(year,m)
	ret = getFormula(ref, finance, now)
	for time in [getDate(year,m-3),getDate(year,m-6),getDate(year,m-9)]:
		ret += getFormula(ref, finance, time)
	return ret

def getDecision(year, m, close, finance):
	now = getDate(year,m)
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
	mining['Price'] = close.transpose()[now]
	files = [ f for f in gb.glob('price/' + now + '*') ]
	mining['Name'] = pd.read_csv(files[0]).set_index('證券代號')['證券名稱']
	mining['PB'] = close.transpose()[now] / finance['bps'][now]
	mining['PB_Rank'] = mining['PB'].rank(ascending=1)
	#print(mining['PB'])
	#print(mining['PB_Rank'])
	mining['PE'] = close.transpose()[now] / finance['eps'][now]
	mining['PE_Rank'] = mining['PE'].rank(ascending=1)
	#print(mining['PE'].describe())
	mining['ROE'] = getLongTermAvg(year, m, 'ROE', finance)
	mining['ROE_Rank'] = mining['ROE'].rank(ascending=0)
	#print(mining['ROE'].describe())
	#print(mining['ROE_Rank'])
	mining['RA'] =  getLongTermAvg(year, m, 'RA', finance)
	mining['RA_Rank'] = mining['RA'].rank(ascending=0)
	#print(mining['RA'].describe())
	mining['SPR'] = finance['shares'][now] * close.transpose()[now] / finance['revenue'][now]
	mining['SPR_Rank'] = mining['SPR'].rank(ascending=1)
	#print(mining['SPR'].describe())
	mining['Rev_Growth'] = finance['revgrowth'][now]
	mining['Rev_Growth_Rank'] = mining['Rev_Growth'].rank(ascending=0)
	#mining['Bay'] = (close.transpose()[now] - finance['bps'][now])/finance['eps'][now]
	#mining['Bay_Rank'] = mining['Bay'].rank(ascending=1)

	mining['shares'] = finance['shares'][now]
	mining['debt'] = finance['debt'][now]
	mining['assetFree'] = finance['assetFree'][now]
	mining['ebit'] = finance['ebit'][now]

	mining['EBIT_BAY'] = ( finance['shares'][now] * close.transpose()[now] / 10 + finance['debt'][now] - finance['assetFree'][now] * 0.5 ) / finance['ebit'][now]
	mining['EBIT_BAY_Rank'] = mining['EBIT_BAY'].rank(ascending=1)
	#print(mining['EBIT_BAY'].describe())
	showTable = mining.sort_values(by='EBIT_BAY_Rank').head(10)
	#pd.set_option('display.max_columns', None)

	print(showTable)
	return showTable.index
	############################## v2 ##############################
	#mining['Rank'] = mining['PB_Rank'] + mining['PE_Rank'] + mining['ROE_Rank'] + mining['RA_Rank'] + mining['SPR_Rank']
	mining['Rank_Long'] = mining[['ROE_Rank','RA_Rank']].max(axis=1, skipna=False) + mining['Rev_Growth_Rank']
	mining['Rank_Short'] = mining[['PB_Rank','PE_Rank','SPR_Rank']].max(axis=1, skipna=False)
	#good = mining.sort_values(by='Rank').head(5)
	cond1 = mining['Price'] < 100
	print(mining[cond1].sort_values(by='Rank_Long').head(10).sort_values(by='Rank_Short').head(3))
	return mining[cond1].sort_values(by='Rank_Long').head(10).sort_values(by='Rank_Short').head(3).index
	############################## v1 ##############################
	cond1 = mining['ROE'] > 0.8
	cond2 = mining['PB'] < 0.8
	return mining[cond1 & cond2].index

def getRate(year, finance):
	close_dict = { getDate(year,m):getClose(year,m) for m in range(10,20) }
	close = pd.DataFrame(close_dict).transpose()
	#print(close)
	#print((close.iloc[-1,:] / close).mean(axis=1).describe())

	choose = [ getDecision(year,m, close, finance) for m in range(10,19) ]
	choose.append(choose[0])
	#choose = [ close.loc[:, close.iloc[i] < 20 ].columns for i in range(0,close.shape[0]) ]
	#choose = [ list(STOCKS.keys()) for i in range(0,close.shape[0]) ]
	print(choose)

	index_rate = getIndex(close)
	return_rate = getReturn(close, choose)

	rate = pd.concat([index_rate, return_rate], axis=1, sort=True)
	rate.columns = [str(year)+'I',str(year)+'R']
	print(rate)
	return rate

def getReturnLong(year, close, group):
	group_price = close[group]
	rate = group_price.iloc[9]/group_price.iloc[0]
	return rate.dropna(axis=0).mean(axis=0)

def getQuantile(year, finance):
	close_dict = { getDate(year,m):getClose(year,m) for m in range(10,20) }
	close = pd.DataFrame(close_dict).transpose()
	choose10 = getDecision(year, 10, close, finance)
	totalNum = len(choose10)
	groupNum = int(totalNum / 20)
	print(groupNum)
	rate = [ getReturnLong(year, close, choose10[ x*groupNum : (x+1)*groupNum ]) for x in range(0,20) ]
	quantile = pd.DataFrame(data=rate, index=range(0,20))
	quantile.columns = [str(year)]
	print(quantile)
	return quantile

def main():
	finance = getFinance()
	#data = pd.concat([ getRate(year, finance) for year in YEAR_COLUMN_MAP.keys() ], axis=1, sort=True)
	#data.plot()
	data = pd.concat([ getQuantile(year, finance) for year in YEAR_COLUMN_MAP.keys() ], axis=1, sort=True)
	data.plot.bar()
	plt.ylim([0.5,1.8])
	plt.grid(True)
	plt.savefig('/mnt/rate.svg')

if __name__ == "__main__":
    main()
