#coding=utf-8

import sys
import pandas as pd
import glob as gb
import numpy as np
import matplotlib.pyplot as plt

import notice

from get_signal_buy import signal_buy
from get_signal_buy import get_ma

def main(argv):
	folder = 'price_ma/'
	key_list = [ x[0] for x in notice.WATCHDOG if x[2] == 'O' ]
	file_list = [ f for f in sorted(gb.glob(folder + '2*')) ]
	rate = []
	for idx,f in enumerate(file_list[:-40-1]):
		if idx < 5:
			continue
		select = signal_buy(idx, file_list, key_list)
		if len(select) > 0:
			today_ma = get_ma(idx, file_list)
			future_ma = get_ma(idx+40, file_list)
			select_rate = [future_ma.at[s,'ma5'] / today_ma.at[s,'ma1'] for s in select]
			rate += select_rate
			print(file_list[idx])
			print(list(select))
			print(list(select_rate))
	print(pd.DataFrame(rate, columns=['rate']).describe())
	plt.hist(rate , np.arange(0.5,2,0.01))
	plt.title("histogram")
	plt.savefig('/mnt/rate_hist.svg')

if __name__ == "__main__":
    main(sys.argv)
