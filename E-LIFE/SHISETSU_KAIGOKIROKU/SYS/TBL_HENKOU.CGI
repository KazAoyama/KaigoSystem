#!/bin/bash
#
#
#
# Written by j.aoyagi(hands lab.inc)

exec 2> /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/SHISETSU_KAIGOKIROKU"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"


#}}}Functions#######################################

cat ${app_dir}/SYS/FILENAME |
yarr                        > ${tmp}-filename

for file in $(cat ${tmp}-filename);do
  mv ${app_dir}/TBL/${file} ${app_dir}/TBL/KAIGOJISSEKI/${file}
done

rm -f ${tmp}-*
exit 0

