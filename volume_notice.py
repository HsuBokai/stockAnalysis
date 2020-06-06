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

def crawl_volume(date_str):
	print(date_str)
	r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date_str + '&type=ALL')
	ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '})
					for i in r.text.split('\n')
					if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	ret = ret.set_index('證券名稱')
	ret['成交股數'] = ret['成交股數'].str.replace(',','')
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

def crawl_monthly(year, month):
	date_str = '{:04d}{:02d}'.format(year, month)
	if year > 1990:
		year -= 1911
	url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'_0.html'
	if year <= 98:
		url = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'.html'
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	r = requests.get(url, headers=headers)
	r.encoding = 'big5'
	dfs = pd.read_html(StringIO(r.text), encoding='big-5')
	df = pd.concat([df for df in dfs if df.shape[1] <= 11 and df.shape[1] > 5])
	df.to_csv('/mnt/monthly/' + date_str)
	df = pd.read_csv('/mnt/monthly/' + date_str)
	df.columns = df.iloc[0]
	df = df.set_index('公司名稱')
	yoy = pd.to_numeric(df['去年同月增減(%)'], errors='coerce')
	mom = pd.to_numeric(df['上月比較增減(%)'], errors='coerce')
	mm = pd.concat([yoy, mom], axis=1)
	mm.columns = ['yoy','mom']
	time.sleep(10)
	return mm

def crawl_this_monthly():
	now = dt.datetime.now()
	if 1 == now.month:
		mm = crawl_monthly(now.year, 12)
	else:
		mm = crawl_monthly(now.year, now.month-1)
	key_list_new = [ x for x in notice.WATCHDOG if x in list(mm.index.values) ]
	new_data = mm.loc[key_list_new,:]
	return new_data

def monthly_info():
	this_file = '/mnt/monthly/this_monthly'
	old_data = pd.read_csv(this_file)
	key_list_old = old_data['公司名稱'].tolist()
	new_data = crawl_this_monthly()
	new_data.to_csv(this_file)
	key_list_new = list(new_data.index.values)
	key_list_addition = [ x for x in key_list_new if x not in key_list_old ]
	if 0 == len(key_list_addition):
		return ''
	else:
		return str(new_data.loc[key_list_addition,:])

def main(argv):
	if 2 <= len(argv):
		date_str = argv[1]
	else:
		now=dt.datetime.now()
		date_str = '{:04d}{:02d}{:02d}'.format(now.year,now.month,now.day)
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
	if msg != '':
		print(msg)
		my_send_email(msg)
	time.sleep(10)

if __name__ == "__main__":
	main(sys.argv)
