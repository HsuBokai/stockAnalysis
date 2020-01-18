#!/bin/bash
date_str=`date +'%Y%m%d'`;

docker run --rm -v  /volume1/homes/admin/stockAnalysis:/mnt -w /mnt --network eth0-macvlan stock:1 python calculate.py ${date_str}
result_file="/volume1/homes/admin/stockAnalysis/stock_investment/${date_str}.txt"
if [ ! -f ${result_file} ]; then
	echo "${result_file} not found!"
	exit 0
fi
value=`cat ${result_file}`
echo "y4b062jo4gj4" | /usr/local/mariadb10/bin/mysql  -u admin -h localhost -p  -e "insert into my_db.stock_investment  (mDate, mPrice, mCost, mDiff, mPercent)  values ${value}"
echo "${date_str} success!"
exit 0
