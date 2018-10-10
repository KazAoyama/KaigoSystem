#!/bin/bash
#
# AJAX_CAREPLAN_DATE.CGI:
#　ケアプラン日付をを取得して返す。
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

#ゴミtmpの消去
rm -f $tmp-*

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
KAIGODO=$(nameread "KAIGODO" $tmp-name)

[ -z "${RISYOUSHAID}" -o "${RIYOUSHAID}" = "_" ] && echo "@" "@" >  $tmp-careplan_date_select_head

if [ ${KAIGODO} = "KAIGO" ] ; then
if [ -s ${apdata_dir}/CAREPLAN_KAIGO/${RIYOUSHAID}/CAREPLAN_DATE ] ; then
cat ${apdata_dir}/CAREPLAN_KAIGO/${RIYOUSHAID}/CAREPLAN_DATE |
awk '$(NF-2)!="9"'     |
awk '$1=="'${RIYOUSHAID}'"{print $2,$3}' |
LANG=C sort -k1r,1r >  $tmp-careplan_date_select_head
if [ "$(gyo $tmp-careplan_date_select_head)" = "0" ] ; then
  echo "@" "@" >  $tmp-careplan_date_select_head
fi
# 2:ケアプラン日付 3:ケアプラン日付（和暦）
else
echo "@" "@" >  $tmp-careplan_date_select_head
fi
else
if [ -s ${apdata_dir}/CAREPLAN_YOBO/${RIYOUSHAID}/CAREPLAN_DATE ] ; then
cat ${apdata_dir}/CAREPLAN_YOBO/${RIYOUSHAID}/CAREPLAN_DATE |
awk '$(NF-2)!="9"'     |
awk '$1=="'${RIYOUSHAID}'"{print $2,$3}' |
LANG=C sort -k1r,1r >  $tmp-careplan_date_select_head
if [ "$(gyo $tmp-careplan_date_select_head)" = "0" ] ; then
  echo "@" "@" >  $tmp-careplan_date_select_head
fi
# 2:ケアプラン日付 3:ケアプラン日付（和暦）
else
echo "@" "@" >  $tmp-careplan_date_select_head
fi
fi

awk '/\<careplansakuseibi_start\>/,/\<careplansakuseibi_end\>/' ${html_dir}/KYOTAKUSHIEN_CAREPLAN_MENU.html |
tee $tmp-ajax_test |
mojihame -l###CAREPLANSAKUSEIBI###  - $tmp-careplan_date_select_head      > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
