#!/bin/bash
#
# AJAX_HOKENJA_DETAIL.CGI:
#　事業所を取得。
# Ajax による使用を想定。
#
#
# Written by K.Aoyama / 2013.12.27

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null

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

# POSTパラメータの取得
HokenjaID=$(nameread "slHokenja" $tmp-name)

: > tmp-jigyousho_master_html
# 保険者マスター
cat ${home_dir}/TBL/HOKENJA/HOKENJA_TABLE |
LANG=C sort -k1,1 |
# 1:保険者ID 2:保険者番号 3:都道府県コード 4:名前 5:カナ
awk '$1=="'${HokenjaID}'"{print $1,$2,$3,$4,$5}'    > $tmp-hokenja_detail

hokenjaid=$(awk '{print $1}' $tmp-hokenja_detail)
bangou=$(awk '{print $2}' $tmp-hokenja_detail)
todoufuken=$(awk '{print $3}' $tmp-hokenja_detail)
namae=$(awk '{print $4}' $tmp-hokenja_detail)
kana=$(awk '{print $5}' $tmp-hokenja_detail)

cat << FIN > $tmp-calsed_data
###HOKENJA### $hokenjaid
###BANGOU### $bangou
###NAMAE### $namae
###KANA### $kana
FIN

cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result

awk '/\<hokenja_detail_select_start\>/,/\<hokenja_detail_select_end\>/' ${html_dir}/HOKENJA_MASTER2.html |
calsed -f $tmp-calsed_data_result - > $tmp-html

cp $tmp-html $work_dir/html_hokenja

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
