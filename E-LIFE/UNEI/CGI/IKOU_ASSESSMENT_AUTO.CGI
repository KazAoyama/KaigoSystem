#!/bin/bash
#
# IKOU_ASSESSMENT.CGI : アセスメント自動応答CGI
#
# Usage : IKOU_ASSESSMENT_AUTO.CGI
#
# Written by K.AOYAMA(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

Riyoushaid=$1
USERID=$2

echo ${USERID} |
join1 key=1 <(self 1 2 ${home_dir}/TBL/JYUUGYOUIN_MASTER/USER_MASTER) |
delf 1 > $tmp-jyugyoin_name

USERNAME=$(self 1 $tmp-jyugyoin_name)

eventtype="ping"

cat << FIN > $tmp-stream
event:ping
data:{"Riyoushaid":"${Riyoushaid}","USERID":"${USERID}","USERNAME":"$USERNAME"}
FIN

cp $tmp-stream $work_dir/stream_assessment

# HTMLファイルを表示する
echo -e 'Content-Type: text/event-stream; Cache-Control: no-cache; \n\n' |
cat - $tmp-stream


## 終了
rm -f ${tmp}-*

exit 0
