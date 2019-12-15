#!/bin/bash

bin_mysql="/usr/local/mariadb10/bin/mysql"
table_name="stock_investment"
data_file="/tmp/${table_name}.txt"
table_colume="(mDate DATE, mPrice FLOAT, mCost FLOAT, mDiff FLOAT, mPercent FLOAT)"
table_value="(mDate, mPrice, mCost, mDiff, mPercent)"

#$ docker run --rm -v  /volume1/homes/admin/stockAnalysis:/mnt -w /mnt --network eth0-macvlan stock:1 python calculate.py 20191213
#=====> output result file at ./stock_investment/20191213.txt
if [ ! -d ./${table_name} ]; then
	exit 0
fi
$bin_mysql -e "drop table my_db.${table_name}"
$bin_mysql -e "create table my_db.${table_name} ${table_colume}"
for filename in ./${table_name}/*.txt; do
	$bin_mysql -e "insert into my_db.${table_name} ${table_value} values `cat ${filename}`"
done
