#!/bin/bash
#
# KEIYAKU_ICHIRAN.GET_RIYOSHA.CGI : SHISETSU,TATEYA,FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : KEIYAKU_ICHIRAN.GET_RIYOSHA.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by Y.kashiyama 2014/03/11

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/UNEI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#=== 初期化 ===
tmp=/var/tmp/${$}
today=$(date +%Y%m%d)

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/UNEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA"
apptbl_dir="${app_dir}/TBL"
kyoutsu_dir="${home_dir}/E-LIFE/KYOUTSU/HTML"
riyosha_dir="/DATA/E-LIFE/UNEI/RIYOUSHA"
keiyaku_dir="${home_dir}/E-LIFE/TBL/KEIYAKU_MASTER"
tbl_dir="${home_dir}/E-LIFE/TBL"

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name

# 選択しているSHISETSU_CODE
userid=$(nameread "userid" ${tmp}-name)
shisetsu=$(nameread "shisetsu" ${tmp}-name)
tokuhan=$(nameread "tokuhan" ${tmp}-name)

SHISETSUID="$(nameread "shisetsu" ${tmp}-name)"

if [ "${shisetsu}" != "0000" ] ; then
cat ${tbl_dir}/RIYOURYOU_MASTER/TOKUHAN_SHUBETSU                |
# 1:施設/事業所名 2:契約ID 3:有効フラグ

  # 施設番号が一致し、有効フラグが1:有効なもの
  awk '$1=="'${shisetsu}'"&&$(NF-2)!="9"&&$(NF-2)!="2"{print $2,$3}'  |
  LANG=C sort -u                                                      
else
  cat ${tbl_dir}/RIYOURYOU_MASTER/TOKUHAN_SHUBETSU              |
  awk '$(NF-2)!="9"&&$(NF-2)!="2"{print $2,$3}'                 |
  LANG=C sort -u
fi |
awk '{if($1=="'${tokuhan}'"){print $1,$2,"selected"}
      else{print $1,$2,"@"}}'                            |
awk 'BEGIN{print "@ 全て @"}{print $0}' > $tmp-tokuhan



#######################################################################################

#cp $tmp-* /home/hands/work/okuda

# HTMLを作成
awk '/\<tokuhan_td_start\>/,/\<tokuhan_td_end\>/' ${html_dir}/KEIYAKU_ICHIRAN2.html |
mojihame -lshisetsu_select - $tmp-shisetsu         |
mojihame -ltokuhan_select - $tmp-tokuhan  > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-exit 0
