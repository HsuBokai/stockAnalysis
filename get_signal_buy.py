#coding=utf-8

import sys
import pandas as pd

def get_ma(date_index, file_list):
	today_ma = pd.read_csv(file_list[date_index]).set_index('4number_str')
	return today_ma

def signal_buy(date_index, file_list, key_list):
	today_ma = get_ma(date_index, file_list)
	yesterday_ma = get_ma(date_index-1, file_list)
	mining = pd.DataFrame({})
	mining['below_high240'] = yesterday_ma['ma1'] < yesterday_ma['h240']
	mining['near_high240'] = yesterday_ma['ma1'] > (yesterday_ma['h240']*0.6)
	mining['volume_dec'] = yesterday_ma['vS20'] < 0
	mining['volume_low'] = (yesterday_ma['v5'] < yesterday_ma['v10'])
	mining['volume_ma_max'] = yesterday_ma[['v240','v120','v60','v40','v20','v10']].max(axis=1, skipna=True)
	mining['volume_pulse'] = today_ma['v1'] > mining.loc[today_ma['v1'].index, 'volume_ma_max']
	mining['volume_inc'] = today_ma['maS2'] > 0
	mining['width_dec'] = (yesterday_ma['wS20'] < 0) & (yesterday_ma['w5'] < yesterday_ma['w10'])
	mining['width_ma_max'] = yesterday_ma[['w240','w120','w60','w40','w20','w10']].max(axis=1, skipna=True)
	mining['width_low'] = ((yesterday_ma['h5'] - yesterday_ma['l5']) / yesterday_ma['ma1']) < (mining['width_ma_max'] * 1.5)
	mining['price_up'] = yesterday_ma['maS60'] > 0
	mining['price_inc'] = today_ma['maS2'] > 0
	mining['price_pulse'] = today_ma['ma1'] > (today_ma['vma20']/today_ma['v20'])
	mining['yesterday'] = yesterday_ma['ma1'] < (yesterday_ma['vma20']/yesterday_ma['v20'])
	mining['rsv_high'] = yesterday_ma['rsv10'] > 0.4
	mining['rsv_inc'] = today_ma['rsvS2'] > 0
	mining['rsv_pulse'] = today_ma['rsv1'] > 0.5
	mining['rsv10_0'] = (today_ma['ma2'] - today_ma['l10'])/(today_ma['h10'] - today_ma['l10'])
	r = mining.loc[key_list, :]
	#r = mining
	result = r[r['volume_dec'] & r['volume_low'] & r['volume_pulse'] & r['width_dec'] & r['width_low'] & r['price_up'] & r['price_inc'] & r['price_pulse'] & r['rsv_high'] & r['rsv_inc']]
	return result.index
