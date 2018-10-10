#!/bin/bash
#
# AJAX_TANTOUSHAKAIGI_YOBO_KENSAKU.CGI:
#　担当者会議開催日付を取得して返す。
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

if [ -s ${pompa_dir}/CAREPLAN_YOBO/${RIYOUSHAID}/TANTOUSHAKAIGI_YOBO ] ; then
cat ${pompa_dir}/CAREPLAN_YOBO/${RIYOUSHAID}/TANTOUSHAKAIGI_YOBO |
awk '$16!="9"'     |
awk '$1=="'${RIYOUSHAID}'"&&$2=="'${KEIKAKUSAKUSEIDATE}'"{print $4,$5}' |
LANG=C sort -k1,1 >  $tmp-tantoushakaigi_date_select_head
# 2:担当者会議日付 3:担当者会議日付（和暦）
else
echo "@" "@" >  $tmp-tantoushakaigi_date_select_head
fi


awk '/\<tantoushakaigikaisaidate_start\>/,/\<tantoushakaigikaisaidate_end\>/' ${html_dir}/KYOTAKUSHIEN_CAREPLAN_YOBO_MENU.html |
tee $tmp-ajax_test |
mojihame -l###KAIGIKAISAIBI###  - $tmp-tantoushakaigi_date_select_head      > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
