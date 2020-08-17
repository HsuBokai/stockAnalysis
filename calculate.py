#coding=utf-8

import sys
import pandas as pd
import requests
from io import StringIO
import time
import datetime as dt
import buy

from get_close import crawlPrice

def main(argv):
	if 2 <= len(argv):
		date_str = argv[1]
		now=dt.datetime(int(date_str[0:4]),int(date_str[4:6]),int(date_str[6:8]))
	else:
		now=dt.datetime.now()
		date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
	try:
		today = crawlPrice(date_str)
	except:
		sys.exit(-1)
	today.to_csv('./price_daily/'+ date_str)
	today_name_index = today.set_index('證券名稱')
	close = pd.to_numeric(today_name_index['收盤價'], errors='coerce')
	results_dict = {}
	buy_list = buy.BUY + buy.BUY_MOTHER + buy.BUY_MOTHER_2
	for year,month,date,stock,cost,shares in buy_list:
		if now < dt.datetime(year,month,date):
			continue
		price = close[stock]*shares
		diff = price - cost
		if stock not in results_dict:
			results_dict[stock] = [price , cost, diff]
		else:
			results_dict[stock][0] += price
			results_dict[stock][1] += cost
			results_dict[stock][2] += diff
	results = pd.DataFrame(data=results_dict.values(), index=results_dict.keys(), columns = ['price','cost','diff'])
	results_sum = results.sum()
	db_date = '{:04d}-{:02d}-{:02d}'.format(now.year, now.month, now.day)
	db_price = results_sum['price']
	db_cost = results_sum['cost']
	db_diff = results_sum['diff']
	db_percent = db_diff / db_cost * 100
	db = '(\'{}\', {:9.2f}, {:9.2f}, {:9.2f}, {:9.2f})'.format(db_date, db_price, db_cost, db_diff, db_percent)
	results['price_percent'] = results['price'] / db_price * 100
	print(results)
	print('===== ToTal Sum =====')
	print('(date, price, cost, diff, percent)')
	print(db)
	db_file = '/mnt/stock_investment/{}.txt'.format(date_str)
	with open(db_file, 'w') as myfile:
		myfile.write(db)
	time.sleep(10)

if __name__ == "__main__":
    main(sys.argv)
