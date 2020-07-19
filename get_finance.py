#coding=utf-8

import pandas as pd
import glob as gb
import numpy as np

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
	file_list = [ f for f in sorted(gb.glob(folder+'/2*')) ]
	scope = 30
	d = { f[-6:]:readData(f,index_str,column_str_list) for f in file_list[0-scope:] }
	return pd.DataFrame(d).transpose().sort_index()

def cum2diff(df_cum):
	df = df_cum.rolling(4).apply(lambda x: x[3] - x[0], raw=True)
	for date_str in df_cum.index:
		if date_str[-2:] in ['01','02','03']:
			df.loc[date_str] = df_cum.loc[date_str]
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
	return pd.to_numeric(df.set_index('證券代號')['收盤價'], errors='coerce')

def getFinance():
	finance = {}
	revenue = getData('monthly','公司代號',['當月營收'])
	finance['revenue'] = revenue.transpose()
	rev5mean = revenue.rolling(5).mean()
	finance['rev5mean'] = rev5mean.transpose()
	finance['revgrowth'] = rev5mean.rolling(10).apply(lambda x: int(x[0]>x[5])+int(x[1]>x[6])+int(x[2]>x[7])+int(x[3]>x[8])+int(x[4]>x[9]), raw=True).transpose()

	eps_cum = getData('income','公司代號',['基本每股盈餘（元）'])
	finance['eps'] = cum2last4season(eps_cum).transpose()
	profit_cum = getData('income','公司代號',['本期稅後淨利（淨損）','本期淨利（淨損）'])
	finance['profit'] = cum2last4season(profit_cum).transpose()
	ebit_cum = getData('income','公司代號',['營業利益（損失）'])
	finance['ebit'] = cum2last4season(ebit_cum).transpose()
	rev_cum = getData('income','公司代號',['營業收入'])
	finance['rev'] = cum2last4season(rev_cum).transpose()

	finance['bps'] = getData('balance','公司代號',['每股參考淨值']).transpose()
	asset = getData('balance','公司代號',['資產總計','資產總額'])
	finance['asset'] = asset.transpose()
	finance['asset4avg'] = asset.rolling(10).apply(lambda x: (x[9]+x[6]+x[3]+x[0])/4, raw=True).transpose()
	finance['assetFree'] = getData('balance','公司代號',['流動資產']).transpose()
	finance['debt'] = getData('balance','公司代號',['負債總計','負債總額']).transpose()
	debtFree = getData('balance','公司代號',['流動負債'])
	finance['debtFree'] = debtFree.transpose()
	finance['debtNonFree'] = getData('balance','公司代號',['非流動負債']).transpose()
	equity = getData('balance','公司代號',['權益總計','權益總額'])
	finance['equity'] = equity.transpose()
	finance['equ4avg'] = equity.rolling(10).apply(lambda x: (x[9]+x[6]+x[3]+x[0])/4, raw=True).transpose()
	capital = asset - debtFree
	finance['capital'] = capital.transpose()
	finance['cap4avg'] = capital.rolling(10).apply(lambda x: (x[9]+x[6]+x[3]+x[0])/4, raw=True).transpose()
	shares = getData('balance','公司代號',['股本'])
	finance['shares'] = shares.transpose()
	finance['cash'] = getData('balance','公司代號',['現金及約當現金']).transpose()

	return finance
