#!/bin/bash
#
# AJAX_ASSESSMENT_KENSAKU.CGI:
#　アセスメント日付を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by K.Aoyama / 2014.01.04

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/CAREPLAN/CGI/CAREPLAN.INI &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


#=== 初期化 ===
tmp=/var/tmp/${$}

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name
#---

# 利用者の取得
RIYOUSHAID=$(nameread "RIYOUSHAID" $tmp-name)
KEIKAKUSAKUSEIDATE=$(nameread "KEIKAKUSAKUSEIDATE" $tmp-name)

:> $tmp-assesment_date
if [ -s ${pompa_dir}/CAREPLAN_KAIGO/${RIYOUSHAID}/CAREPLAN_ASSESSMENT ] ; then
cat ${pompa_dir}/CAREPLAN_KAIGO/${RIYOUSHAID}/CAREPLAN_ASSESSMENT |
awk '$4!="9"'     |
awk '$1=="'${RIYOUSHAID}'"&&$2=="'${KEIKAKUSAKUSEIDATE}'"{print $3}' |
LANG=C sort -k1,1 >  $tmp-assesment_date
# 2:担当者会議日付 3:担当者会議日付（和暦）
fi

:> $tmp-assessment_date
if [ $(gyo $tmp-assesment_date) = "1" ] ; then
# 和暦変換（変更日）
   assessment_date=$(self 1 $tmp-assesment_date)
   awk '$5!="9"' ${home_dir}/TBL/ZEIRITSU_GENGOU_MASTER/GENGOU |
   self 1/4 |
   awk '$3<="'$assessment_date'"&&"'$assessment_date'"<=$4' |
   awk '{print $2,"'$assessment_date'",substr($3,1,4)-1}'    |
   awk '{print $1,substr($2,1,4)-$3,int(substr($2,5,2)),int(substr($2,7,2))}'  |
   awk '{print $1$2"年"$3"月"$4"日"}'                          > $tmp-assessment_date
fi

AssessmentDate=$(self 1 $tmp-assessment_date)  

cat <<FIN > $tmp-calsed
###ASSESSMENTBI### $AssessmentDate
FIN

awk '/\<assessment_ajax_start\>/,/\<assessment_ajax_end\>/' ${html_dir}/KYOTAKUSHIEN_CAREPLAN_MENU.html |
tee $tmp-ajax_test |
calsed -f $tmp-calsed - > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
