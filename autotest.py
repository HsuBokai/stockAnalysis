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
	#cond1 = pd.to_numeric(df['收盤價'], errors='coerce') < 10
	#conds = [ df['證券代號'] == s for s in STOCKS.keys() ]
	#cond2 = ft.reduce(lambda c1, c2: c1 | c2, conds[1:], conds[0])
	#df = df[cond2]
	return pd.to_numeric(df.set_index('證券代號')['收盤價'], errors='coerce')

def getIndex(close):
	equality = close.dropna(axis=1).mean(axis=1)
	#print(equality)
	return equality * range(1,equality.shape[0]+1) / equality.cumsum()

def getReturn1000(close, choose):
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

def getReturn(close, choose):
	returnRate = close.iloc[9] / close
	returnList = [ returnRate[c].iloc[idx].dropna().mean() for idx, c in enumerate(choose) ]
	returnAns = pd.DataFrame(data=returnList, index=close.index)
	return returnAns

def getReturnCumu(close, choose):
	returnRate = close.iloc[9] / close
	returnList = [ returnRate[c].iloc[idx].dropna().mean() for idx, c in enumerate(choose) ]
	returnListCumu = np.cumsum(returnList)
	returnListCumuMean = [ returnListCumu[idx] / (idx+1) for idx, c in enumerate(choose) ]
	return pd.DataFrame(data=returnListCumuMean, index=close.index)

def getFinance():
	finance = {}
	revenue = getData('monthly','公司代號',['當月營收'])
	finance['revenue'] = revenue.transpose()
	rev5mean = revenue.rolling(5).mean()
	finance['rev5mean'] = rev5mean.transpose()
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
	rev_cum = getData('income','公司代號',['營業收入'])
	finance['rev'] = cum2last4season(rev_cum).transpose()
	#print(finance['rev'].describe())
	finance['bps'] = getData('balance','公司代號',['每股參考淨值']).transpose()
	#print(finance['bps'].describe())
	asset = getData('balance','公司代號',['資產總計','資產總額'])
	finance['asset'] = asset.transpose()
	finance['asset4avg'] = asset.rolling(10).apply(lambda x: (x[9]+x[6]+x[3]+x[0])/4, raw=True).transpose()
	#print(finance['asset'].describe())
	#print(finance['asset4avg'].describe())
	finance['assetFree'] = getData('balance','公司代號',['流動資產']).transpose()
	#finance['assetFree'] = getData('balance','公司代號',['現金及約當現金']).transpose()
	#print(finance['assetFree'].describe())
	finance['debt'] = getData('balance','公司代號',['負債總計','負債總額']).transpose()
	#print(finance['debt'].describe())
	finance['debtFree'] = getData('balance','公司代號',['流動負債']).transpose()
	#print(finance['debtFree'].describe())
	finance['debtNonFree'] = getData('balance','公司代號',['非流動負債']).transpose()
	#print(finance['debtNonFree'].describe())
	capital = getData('balance','公司代號',['權益總計','權益總額'])
	finance['capital'] = capital.transpose()
	finance['cap4avg'] = capital.rolling(10).apply(lambda x: (x[9]+x[6]+x[3]+x[0])/4, raw=True).transpose()
	#print(finance['capital'])
	#print(finance['cap4avg'])
	shares = getData('balance','公司代號',['股本'])
	finance['shares'] = shares.transpose()
	#finance['sha4avg'] = shares.rolling(10).apply(lambda x: (x[9]+x[6]+x[3]+x[0])/4, raw=True).transpose()
	finance['cash'] = getData('balance','公司代號',['現金及約當現金']).transpose()
	#print(finance['cash'].describe())
	#print(finance)
	return finance

def getFormula(name, finance, time):
	if name == 'ROE':
		return finance['profit'][time]/finance['cap4avg'][time]
	if name == 'ROA':
		return finance['profit'][time]/finance['asset4avg'][time]
	if name == 'RA':
		return finance['rev5mean'][time]/finance['asset'][time]
	if name == 'OperationRate':
		return finance['ebit'][time] / finance['rev'][time]
	if name == 'Turnover':
		return finance['rev'][time] / finance['asset4avg'][time]
	if name == 'FreeRate':
		return finance['assetFree'][time] / finance['debtFree'][time]
	if name == 'Gearing':
		return finance['debtNonFree'][time] / finance['asset4avg'][time]
	return finance[name][time]

def getLongTermAvg(year, m, ref, finance):
	ret = 0
	#for time in [getDate(year,m),getDate(year,m-3),getDate(year,m-6),getDate(year,m-9)]:
	for time in [getDate(year,m-4),getDate(year,m-7),getDate(year-1,m+2),getDate(year-1,m-1)]:
		ret += getFormula(ref, finance, time)
	return ret

def getGrowth(year, m, ref, finance):
	halfYear = getDate(year,m-4)
	lastYear = getDate(year-1,m-4)
	compare = getFormula(ref, finance, halfYear) - getFormula(ref, finance, lastYear)
	compare.fillna(value=-1, inplace=True)
	return (compare > 0).astype(int) * 100000

def getPredict(year, m, ref, finance):
	base = 0
	for time in [getDate(year,m-2),getDate(year,m-3),getDate(year,m-4)]:
		base += getFormula(ref, finance, time)
	change = 0
	for time in [getDate(year,m),getDate(year,m-1),getDate(year,m-2)]:
		change += getFormula(ref, finance, time)
	return change / base

def getDecision(year, m, close, finance):
	now = getDate(year,m)
	#halfYear = getDate(year,m)
	halfYear = getDate(year,m-4)
	lastYear = getDate(year-1,m-4)
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
	mining['PB'] = close.transpose()[now] / finance['bps'][halfYear]
	mining['PB_Rank'] = mining['PB'].rank(ascending=1)
	#print(mining['PB'])
	#print(mining['PB_Rank'])
	mining['PE'] = close.transpose()[now] / finance['eps'][halfYear]
	mining['PE_Rank'] = mining['PE'].rank(ascending=1)
	#print(mining['PE'].describe())
	mining['PE_Predict'] = close.transpose()[now] / (finance['eps'][halfYear] * getPredict(year, m, 'revenue', finance))
	mining['PE_Predict_Rank'] = mining['PE_Predict'].rank(ascending=1)
	#print(mining['PE_Predict'])
	#print(mining['PE_Predict_Rank'].describe())
	mining['ROE'] = getFormula('ROE', finance, halfYear)
	mining['ROE_Rank'] = mining['ROE'].rank(ascending=0)
	#print(mining['ROE'].describe())
	#print(mining['ROE_Rank'])
	mining['ROA'] = getFormula('ROA', finance, halfYear)
	mining['ROA_Rank'] = mining['ROA'].rank(ascending=0)
	mining['ROA_Growth'] = getGrowth(year, m, 'ROA', finance)
	mining['ROA_OK'] = (mining['ROA'] > 0.0001).astype(int) * 100000
	#print(mining['ROA'])
	#print(mining['ROA_Rank'].describe())
	#print(mining['ROA_Growth'])
	#print(mining['ROA_OK'])
	mining['RA'] =  getFormula('RA', finance, halfYear)
	mining['RA_Rank'] = mining['RA'].rank(ascending=0)
	#print(mining['RA'].describe())
	mining['SPR'] = finance['shares'][halfYear] * close.transpose()[now] / finance['revenue'][halfYear]
	mining['SPR_Rank'] = mining['SPR'].rank(ascending=1)
	#print(mining['SPR'].describe())
	mining['Rev_Growth'] = getGrowth(year, m, 'rev5mean', finance)
	mining['Rev_Growth_Rank'] = mining['Rev_Growth'].rank(ascending=0)
	#mining['Bay'] = (close.transpose()[now] - finance['bps'][halfYear])/finance['eps'][halfYear]
	#mining['Bay_Rank'] = mining['Bay'].rank(ascending=1)

	mining['shares'] = finance['shares'][halfYear]
	mining['debt'] = finance['debt'][halfYear]
	mining['assetFree'] = finance['assetFree'][halfYear]
	mining['ebit'] = finance['ebit'][halfYear]
	mining['asset4avg'] = finance['asset4avg'][halfYear]
	mining['profit'] = finance['profit'][halfYear]
	mining['rev'] = finance['rev'][halfYear]
	mining['debtFree'] = finance['debtFree'][halfYear]
	mining['debtNonFree'] = finance['debtNonFree'][halfYear]
	mining['cash'] = finance['cash'][halfYear]

	mining['shares-1'] = finance['shares'][lastYear]
	mining['debt-1'] = finance['debt'][lastYear]
	mining['assetFree-1'] = finance['assetFree'][lastYear]
	mining['ebit-1'] = finance['ebit'][lastYear]
	mining['asset4avg-1'] = finance['asset4avg'][lastYear]
	mining['profit-1'] = finance['profit'][lastYear]
	mining['rev-1'] = finance['rev'][lastYear]
	mining['debtFree-1'] = finance['debtFree'][lastYear]
	mining['debtNonFree-1'] = finance['debtNonFree'][lastYear]
	mining['cash-1'] = finance['cash'][lastYear]

	mining['OperationRate'] = getFormula('OperationRate', finance, halfYear)
	mining['OperationRate_Rank'] = mining['OperationRate'].rank(ascending=0)
	mining['OperationRate_Growth'] = getGrowth(year, m, 'OperationRate', finance)
	#print(mining['OperationRate'])
	#print(mining['OperationRate_Rank'].describe())

	mining['Turnover'] = getFormula('Turnover', finance, halfYear)
	mining['Turnover_Rank'] = mining['Turnover'].rank(ascending=0)
	mining['Turnover_Growth'] = getGrowth(year, m, 'Turnover', finance)
	#print(mining['Turnover'])
	#print(mining['Turnover_Rank'].describe())

	mining['FreeRate'] = getFormula('FreeRate', finance, halfYear)
	mining['FreeRate_Rank'] = mining['FreeRate'].rank(ascending=0)
	mining['FreeRate_Growth'] = getGrowth(year, m, 'FreeRate', finance)
	#print(mining['FreeRate'])
	#print(mining['FreeRate_Rank'].describe())

	mining['Gearing_Growth'] = getGrowth(year, m, 'Gearing', finance)
	mining['Gearing_OK'] = (mining['Gearing_Growth'] * -1) + 100000
	#print(mining['Gearing_Growth'])
	#print(mining['Gearing_OK'].describe())

	mining['shares_Growth'] = getGrowth(year, m, 'shares', finance)
	mining['shares_OK'] = (mining['shares_Growth'] * -1) + 100000
	#print(mining['shares_Growth'])
	#print(mining['shares_OK'])
	mining['Market'] = finance['shares'][halfYear] * close.transpose()[now]
	mining['Market_Rank'] = mining['Market'].rank(ascending=0)
	mining['Market_OK'] = (mining['Market_Rank'] <= 500).astype(int) * 100000
	#print(mining['Market'].describe())
	mining['Cost'] = finance['shares'][halfYear] * close.transpose()[now] / 10 + finance['debt'][halfYear] - finance['assetFree'][halfYear] * 0.5
	mining['EBIT_Rate'] = finance['ebit'][halfYear] / mining['Cost']
	mining['EBIT_Rate_Rank'] = mining['EBIT_Rate'].rank(ascending=0)
	mining['EBIT_Rate_Predict'] = finance['ebit'][halfYear] * getPredict(year, m, 'revenue', finance) / mining['Cost']
	mining['EBIT_Rate_Predict_Rank'] = mining['EBIT_Rate_Predict'].rank(ascending=0)
	#print(mining['PE_Predict'])
	#print(mining['PE_Predict_Rank'].describe())
	#print(mining['EBIT_BAY'].describe())

	mining['F_Score'] = mining['ROA_OK'] + mining['ROA_Growth'] + mining['OperationRate_Growth'] + mining['Turnover_Growth'] + mining['FreeRate_Growth'] + mining['Rev_Growth']
	#for xx in list(range(0,7)):
	#	print(len((mining[mining['F_Score'] == xx*100000]).index))
	for ii in (mining[mining['F_Score'] == 6*100000]).index:
		mining.loc[ii,'F_Score'] = 5*100000
	mining['F_Score_Rank'] = mining['F_Score'].rank(ascending=0)
	#print(mining['F_Score'])
	#print(mining['F_Score_Rank'].describe())

	mining['Rank_Long'] = mining[['EBIT_Rate_Rank','PE_Rank']].max(axis=1, skipna=False)
	mining['UnderValue_Rank'] = mining[['EBIT_Rate_Rank','PE_Rank','SPR_Rank','PB_Rank']].max(axis=1, skipna=False)
	mining['Total'] = mining['EBIT_Rate_Predict'] + mining['F_Score']
	mining['Total_Rank'] = mining['Total'].rank(ascending=0)
	#pd.set_option('display.max_columns', None)

	print(mining.sort_values(by='Total_Rank').head(40))
	return mining.sort_values(by='Total_Rank').index
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

	index_cumu_rate = getIndex(close)
	return_rate = getReturn(close, choose)
	return_cumu_rate = getReturnCumu(close, choose)

	rate = pd.concat([index_cumu_rate, return_rate, return_cumu_rate], axis=1, sort=True)
	rate.columns = [str(year)+'I',str(year)+'r',str(year)+'R']
	print(rate)
	return rate

def getReturnLong(year, close, group):
	group_price = close[group]
	rate = group_price.iloc[7]/group_price.iloc[0]
	return rate.dropna(axis=0).mean(axis=0)

def getQuantile(year, finance):
	close_dict = { getDate(year,m):getClose(year,m) for m in range(11,19) }
	close = pd.DataFrame(close_dict).transpose()
	choose10 = getDecision(year, 11, close, finance)
	totalNum = len(choose10)
	groupNum = int(totalNum / 10)
	print(groupNum)
	for xx in list(range(0,20)):
		print(getReturnLong(year, close, choose10[xx:xx+1]))
	theTop = close[choose10[0:groupNum]]
	print((theTop.iloc[7]/theTop.iloc[0]).dropna(axis=0).describe())
	rate = [ getReturnLong(year, close, choose10[ x*groupNum : (x+1)*groupNum ]) for x in range(0,10) ]
	quantile = pd.DataFrame(data=rate, index=range(0,10))
	quantile.columns = [str(year)]
	print(quantile)
	return quantile

def main():
	finance = getFinance()
	#data = pd.concat([ getRate(year, finance) for year in YEAR_COLUMN_MAP.keys() ], axis=1, sort=True)
	#data.plot()
	data = pd.concat([ getQuantile(year, finance) for year in YEAR_COLUMN_MAP.keys() ], axis=1, sort=True)
	data['longterm'] = data.product(axis=1)
	print(data)
	data.plot()
	plt.ylim([0.5,1.8])
	plt.grid(True)
	plt.savefig('/mnt/rate.svg')

if __name__ == "__main__":
    main()
