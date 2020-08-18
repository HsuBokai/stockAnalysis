#coding=utf-8

import sys
import pandas as pd
import requests
from io import StringIO
import time
import datetime as dt
import notice
import smtplib, ssl
from email.mime.text import MIMEText

from get_monthly_info import monthly_info
from get_finance import getFinance
from get_decision import getDecision

def my_send_email(content):
	port = 587  # For TLS
	smtp_server = notice.SERVER
	sender_email = notice.SENDER
	password = notice.PW
	receiver_email = notice.RECEIVER
	mail = MIMEText(content)
	mail['Subject'] = 'Volume Notice'
	context = ssl.create_default_context()
	try:
		with smtplib.SMTP(smtp_server, port) as server:
			server.ehlo()  # Can be omitted
			server.starttls(context=context)
			server.ehlo()  # Can be omitted
			server.login(sender_email, password)
			server.sendmail(sender_email, receiver_email, mail.as_string())
	except:
		print('Fail to send mail!')
		sys.exit(-2)
	print('mail sent!')

def main(argv):
	if 2 <= len(argv):
		date_str = argv[1]
	else:
		now=dt.datetime.now()
		date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
	year = int(date_str[0:4])
	month = int(date_str[4:6])
	try:
		today = pd.read_csv('./price_daily/'+ date_str).set_index('證券代號')
	except:
		my_send_email('Fail to crawl today price!')
		sys.exit(-1)
	today_name_index = today.set_index('證券名稱')
	today_name_index['volume'] = pd.to_numeric(today_name_index['成交股數'], errors='coerce')
	today_name_index['change'] = pd.to_numeric(today_name_index['漲跌價差'], errors='coerce')
	today_name_index['close'] = pd.to_numeric(today_name_index['收盤價'], errors='coerce')
	today_name_index['percent'] = today_name_index['change'] / today_name_index['close'] * 100
	results_dict = {}
	msg = ''
	for k,v in notice.NOTICE:
		volume = today_name_index.loc[k, 'volume']
		if volume > v*1000:
			rate = today_name_index.loc[k, 'percent'].round(3)
			sign = today_name_index.loc[k, '漲跌(+/-)']
			more = volume//1000 - v
			msg += '{} 成交張數超過 {} 多 {} 張, 漲跌幅 {}{} %\n'.format(k,v,more,sign,rate)
	msg += monthly_info()
	try:
		finance = getFinance()
		close_dict = {}
		close_dict[date_str[0:6]] = pd.to_numeric(today['收盤價'], errors='coerce')
		close = pd.DataFrame(close_dict).transpose()
		mining = getDecision(year, month, close, finance)
		mining['Name'] = today['證券名稱']
		stocks_sorted = mining.head(10)
		msg += str(mining['Total'].describe())
		msg += str(stocks_sorted[['Name','Price','Total']])
	except:
		pass
	if msg != '':
		print(msg)
		my_send_email(msg)

if __name__ == "__main__":
	main(sys.argv)
