#coding=utf-8

import pandas as pd
import glob as gb
import functools as ft
import numpy as np

def getDate(year,m):
	if (m > 12):
		year+=1
		m-=12
	return '{:04d}{:02d}'.format(year,m)

def getFormula(name, finance, time):
	if name == 'ROE':
		return finance['profit'][time]/finance['equ4avg'][time]
	if name == 'ROA':
		return finance['profit'][time]/finance['asset4avg'][time]
	if name == 'ROC':
		return finance['profit'][time]/finance['cap4avg'][time]
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
	for time in [getDate(year,m-3),getDate(year,m-4),getDate(year,m-5)]:
		base += getFormula(ref, finance, time)
	change = 0
	for time in [getDate(year,m-1),getDate(year,m-2),getDate(year,m-3)]:
		change += getFormula(ref, finance, time)
	return change / base

def getSigmoidPolation(df):
	df025 = df.quantile(0.25)
	df075 = df.quantile(0.75)
	dfZero = (df075 + df025) / 2
	dfOne = (df075 - df025) / 2
	x = (df - dfZero) / dfOne
	return 1 / ( 1 + 3 ** (-x) )

def getDecision(year, m, close, finance):
	now = getDate(year,m)
	prev = getDate(year,m-1)
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
	mining['PB'] = finance['bps'][halfYear] / close.transpose()[now]
	mining['PB_Rank'] = mining['PB'].rank(ascending=0)
	mining['PB_Percent'] = getSigmoidPolation(mining['PB'])
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
	mining['ROE_Percent'] = getSigmoidPolation(mining['ROE'])
	#print(mining['ROE'].describe())
	#print(mining['ROE_Rank'])
	mining['ROC'] = getFormula('ROC', finance, halfYear)
	mining['ROC_Rank'] = mining['ROC'].rank(ascending=0)
	mining['ROC_Percent'] = getSigmoidPolation(mining['ROC'])
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
	mining['SPR'] = finance['revenue'][prev] / (finance['shares'][halfYear] * close.transpose()[now])
	mining['SPR_Rank'] = mining['SPR'].rank(ascending=0)
	mining['SPR_Percent'] = getSigmoidPolation(mining['SPR'])
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
	#mining['cash'] = finance['cash'][halfYear]

	mining['shares-1'] = finance['shares'][lastYear]
	mining['debt-1'] = finance['debt'][lastYear]
	mining['assetFree-1'] = finance['assetFree'][lastYear]
	mining['ebit-1'] = finance['ebit'][lastYear]
	mining['asset4avg-1'] = finance['asset4avg'][lastYear]
	mining['profit-1'] = finance['profit'][lastYear]
	mining['rev-1'] = finance['rev'][lastYear]
	mining['debtFree-1'] = finance['debtFree'][lastYear]
	mining['debtNonFree-1'] = finance['debtNonFree'][lastYear]
	#mining['cash-1'] = finance['cash'][lastYear]

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
	mining['FreeRate_Percent'] = getSigmoidPolation(mining['FreeRate'])
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
	mining['EBIT_Rate_Percent'] = getSigmoidPolation(mining['EBIT_Rate'])
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
	mining['Total'] = mining['EBIT_Rate_Percent'] + mining['ROC_Percent'] + mining['PB_Percent'] + mining['ROE_Percent'] + mining['SPR_Percent'] + mining['FreeRate_Percent']
	mining['Total_Rank'] = mining['Total'].rank(ascending=0)
	#pd.set_option('display.max_columns', None)

	return mining.sort_values(by='Total_Rank')
