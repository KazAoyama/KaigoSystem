#!/bin/bash
#
# AJAX_CAREPLAN_RENRAKU_SHISETSU.CGI : 入居者を選択して施設を返す
#                     
#
# Usage : AJAX_CAREPLAN_RENRAKU_SHISETSU.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by aoyama

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/CAREPLAN/CGI/CAREPLAN.INI &> /dev/null
#--------------------ログ出力--------------------
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv



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

# ディレクトリ設定
home_dir="/home/hands/E-LIFE"
riyosha_dir="/DATA/E-LIFE/UNEI/RIYOUSHA"
tbl_dir="${home_dir}/TBL"


# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name

# 選択しているSHISETSU_CODE
relstaff=$(nameread "relStaff" ${tmp}-name)
relshisetsu=$(nameread "relShisetsu" ${tmp}-name)
reldate=$(nameread "relDate" ${tmp}-name | awk '{print substr($1,1,4)substr($1,6,2)substr($1,9,2)}')
shisetsu=$(nameread "shisetsu" ${tmp}-name)

: > $tmp-all-shisetsu
if [ "${relstaff}" = "99999999" ] ; then
      cat ${riyosha_dir}/JIGYOUSHO_RIYOUSHA_STATUS |
      awk '$(NF-2)!="9"&&$1=="'${shisetsu}'"&&$3<="'${reldate}'"&&"'${reldate}'"<=$4{print $2}' |
      LANG=C sort -k1,1 |
      getlast 1 1 > $tmp-riyousha_id
      cat ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS |
      awk '$(NF-2)!="9"&&$7<="'${reldate}'"&&"'${reldate}'"<=$8'              |
      LANG=C sort -k6,6               |
      join1 key=6 $tmp-riyousha_id |
      awk '{print $1,$2}' |
      LANG=C sort -k1,2 -u > $tmp-all-shisetsu
fi

# SHISETSU_RIYOSHA_STATUSの準備
echo "aaaa" "事業所内" "aa"                                > $tmp-jigyousho_nai
cat ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                     |
awk '$(NF-2)!="9"&&$7<="'${reldate}'"&&"'${reldate}'"<=$8'      |
awk '$6=="'$relstaff'"' |
self 1 2                |
cat - $tmp-all-shisetsu |
LANG=C sort -k1,1       |
join1 key=1 <(self 1 2 ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON) |
# 1:施設ID 2:施設名 3:建屋
LANG=C sort -k1,1        |
cat $tmp-jigyousho_nai - |
awk '{if($3=="01"){print $1$3,$2"(シニア)",$3}else if($3=="02"){print $1$3,$2"(ケア)",$3}else{print $1$3,$2,$3}}' |
awk '{if($1=="'${relshisetsu}'"){print $1,$2,"selected"}else{print $1,$2,"@"}}'> $tmp-sel_shisetsu

# HTMLを作成
awk '/\<ajax-rel-staff-start\>/,/\<ajax-rel-staff-end\>/' ${home_dir}/CAREPLAN/HTML/CAREPLAN_RENRAKU_TSUIKA.html |
mojihame -l###RELSHISETSU### - ${tmp}-sel_shisetsu |
formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
