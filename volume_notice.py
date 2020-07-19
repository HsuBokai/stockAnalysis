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
from get_close import getClose
from get_decision import getDecision

def crawl_volume(date_str):
	print(date_str)
	r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_str + '&type=ALL')
	ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '})
					for i in r.text.split('\n')
					if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	ret = ret.set_index('證券名稱')
	ret['成交股數'] = ret['成交股數'].str.replace(',','')
	time.sleep(10)
	return pd.to_numeric(ret['成交股數'], errors='coerce')

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
		volume = crawl_volume(date_str)
	except:
		print('Fail to get data!')
		sys.exit(-1)
	results_dict = {}
	msg = ''
	for k,v in notice.NOTICE:
		if volume[k] > v*1000:
			msg += '{} 成交張數超過 {} 多 {} 張\n'.format(k,v,(volume[k]//1000-v))
	msg += monthly_info()
	finance = getFinance()
	close = getClose(date_str)
	stocks_sorted = getDecision(year, month, close, finance).head(10)
	msg += str(stocks_sorted[['Name','Price']])
	if msg != '':
		print(msg)
		my_send_email(msg)

if __name__ == "__main__":
	main(sys.argv)
