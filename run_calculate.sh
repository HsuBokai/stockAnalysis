#!/bin/bash
date_str=`date +'%Y%m%d'`; 

docker run --rm -v  /volume1/homes/admin/stockAnalysis:/mnt -w /mnt --network eth0-macvlan stock:1 python calculate.py ${date_str}

/usr/local/mariadb10/bin/mysql  -e "insert into my_db.stock_investment  (mDate, mPrice, mCost, mDiff, mPercent)  values `cat /volume1/homes/admin/stockAnalysis/stock_investment/${date_str}.txt`"
