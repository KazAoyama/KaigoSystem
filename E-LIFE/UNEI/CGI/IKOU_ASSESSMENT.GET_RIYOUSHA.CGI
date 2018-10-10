#!/bin/bash
#
# SHISETSU_ASSESSMENT.GET_UNIT.CGI : FLOOR選択してUNITを返す
#                     
#
# Usage : SHISETSU_ASSESSMENT.GET_UNIT.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by aoyagi  

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/UNEI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/UNEI/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#=== 初期化 ===
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

today=$(date +%Y%m%d)
# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/UNEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA"
apptbl_dir="${app_dir}/TBL"
kyoutsu_dir="${home_dir}/E-LIFE/KYOUTSU/HTML"
riyosha_dir="/DATA/E-LIFE/UNEI/RIYOUSHA"
tbl_dir="${home_dir}/E-LIFE/TBL"


# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name

# MODE取得
MODE=$(nameread "MODE" ${tmp}-name)
# 選択しているSHISETSU_CODE
shisetsu=$(nameread "shisetsu" ${tmp}-name)
tateya=$(nameread "tateya" ${tmp}-name)
floor=$(nameread "floor" ${tmp}-name)
unit=$(nameread "unit" ${tmp}-name)
kyoshitsu=$(nameread "kyoshitsu" ${tmp}-name)
riyosha_name=$(nameread "riyosha_name" ${tmp}-name)
taikyo=$(nameread "taikyo" ${tmp}-name)

# 施設マスタ
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON                |
awk '$1=="'$shisetsu'"{print $2}'                            > $tmp-shisetsu_name
shisetsu_name=$(tail -1 $tmp-shisetsu_name | self 1)

# 建屋マスタ
cat ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME                   |
awk '$1=="01"'                                               |
awk '$(NF-2)!="9"{print $1,$3}'                              > $tmp-tateya_master

# SHISETSU_TATEYA_FLOOR_ROOMのマスタ準備
echo $shisetsu > $tmp-shisetsu
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM               |
# 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
join0 key=1 $tmp-shisetsu                                    |
awk '$(NF-2)!="9"'                                           > $tmp-shisetsu_tateya_floor_id
# ユニットマスタの準備
#cat ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME                     |
#self 1 2                                                     > $tmp-unit_master

# 利用者マスタの準備
cat ${riyosha_dir}/RIYOUSHA_MASTER                           |
self 1 2                                                     > $tmp-riyosha_master

# SHISETSU_RIYOSHA_STATUSの準備
cat ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                  |
awk '$(NF-2)!="9"'                                           |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
join0 key=1 $tmp-shisetsu                                    |
if [ "$taikyo" = "1" ] ; then
  cat -
else
  awk '$8>="'${today}'"'
fi |
cat - > $tmp-riyosha_status

if [ "$MODE" = "tateya" ]; then
  # 建屋一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{if($1=="'$tateya'"){print $1,$2,"selected"}else{print $1,$2,"@"};}'  > ${tmp}-tateya
  
  # フロア一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'$tateya'"'                                        |
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F","@"}'                                       > ${tmp}-floor

  # 居室一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'$tateya'"'                                        |
  self 5                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1,"@"}'                                          > ${tmp}-kyoshitsu

  # 利用者
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$2=="'${tateya}'"{print $6,$5}'          |
  LANG=C sort -k1,1                                           |
  join1 key=1 $tmp-riyosha_master                              |
  LANG=C sort -k3,3n                                           |
  delf 3 > $tmp-riyosha

elif [ "$MODE" = "floor" ]; then
  # 建屋一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{if($1=="'$tateya'"){print $1,$2,"selected"}else{print $1,$2,"@"};}'  > ${tmp}-tateya
  
  # フロア一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'$tateya'"'                        |
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{if($1=="'$floor'"){print $1,$1"F","selected"}else{print $1,$1"F","@"};}' > ${tmp}-floor

  # 居室一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  if [ "$floor" = "_" ] ; then
    # 全て
    awk '$2=="'$tateya'"'
  else
    awk '$2=="'$tateya'"&&$3=="'$floor'"'
  fi |
  self 5                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1,"@"}'                                          > ${tmp}-kyoshitsu

  # 利用者
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  if [ "$floor" = "_" ] ; then
    # 全て
    awk '$2=="'${tateya}'"{print $6,$5}'
  else
    awk '$2=="'${tateya}'"&&$3=="'$floor'"{print $6,$5}'
  fi |
  LANG=C sort -k1,1                                           |
  join1 key=1 $tmp-riyosha_master                              |
  LANG=C sort -k3,3n                                           |
  delf 3 > $tmp-riyosha

elif [ "$MODE" = "kyoshitsu" ]; then

  # 建屋一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{if($1=="'$tateya'"){print $1,$2,"selected"}else{print $1,$2,"@"};}'  > ${tmp}-tateya

  # フロア一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'$tateya'"'                        |
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{if($1=="'$floor'"){print $1,$1"F","selected"}else{print $1,$1"F","@"};}' > ${tmp}-floor

  # 居室一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  if [ "$floor" = "_" ] ; then
    # 全て
    awk '$2=="'$tateya'"'
  else
    awk '$2=="'$tateya'"&&$3=="'$floor'"'
  fi |
  self 5                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{if($1=="'$kyoshitsu'"){print $1,$1,"selected"}else{print $1,$1,"@"};}'   > ${tmp}-kyoshitsu

  # 利用者
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  if [ "$kyoshitsu" != "_" ] ; then
    awk '$2=="'${tateya}'"&&$5=="'$kyoshitsu'"{print $6,$5}'
  elif [ "$floor" != "_" ] ; then
    awk '$2=="'${tateya}'"&&$3=="'$floor'"{print $6,$5}'
  else
    awk '$2=="'${tateya}'"{print $6,$5}'
  fi |
  LANG=C sort -k1,1                                           |
  join1 key=1 $tmp-riyosha_master                              |
  LANG=C sort -k3,3n                                           |
  delf 3 > $tmp-riyosha

elif [ "$MODE" = "taikyo" ]; then

  # 建屋一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{if($1=="'$tateya'"){print $1,$2,"selected"}else{print $1,$2,"@"};}'  > ${tmp}-tateya

  # フロア一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'$tateya'"'                        |
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{if($1=="'$floor'"){print $1,$1"F","selected"}else{print $1,$1"F","@"};}' > ${tmp}-floor

  # 居室一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  if [ "$floor" = "_" ] ; then
    # 全て
    awk '$2=="'$tateya'"'
  else
    awk '$2=="'$tateya'"&&$3=="'$floor'"'
  fi |
  self 5                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{if($1=="'$kyoshitsu'"){print $1,$1,"selected"}else{print $1,$1,"@"};}'   > ${tmp}-kyoshitsu

  # 利用者
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  if [ "$kyoshitsu" != "_" ] ; then
    awk '$2=="'${tateya}'"&&$5=="'$kyoshitsu'"{print $6,$5}'
  elif [ "$floor" != "_" ] ; then
    awk '$2=="'${tateya}'"&&$3=="'$floor'"{print $6,$5}'
  else
    awk '$2=="'${tateya}'"{print $6,$5}'
  fi |
  LANG=C sort -k1,1                                           |
  join1 key=1 $tmp-riyosha_master                              |
  LANG=C sort -k3,3n                                           |
  delf 3 > $tmp-riyosha

else
  :
fi

taikyocheck=""
[ "${taikyo}" = "1" ] && taikyocheck="checked"


#######################################################################################
# namefileの再構成

cat <<- FIN > ${tmp}-calsed
###SHISETSUNAME### ${shisetsu_name}
###TAIKYOCHECK### ${taikyocheck}
FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/IKOU_ASSESSMENT2.html |
  calsed -f ${tmp}-calsed - |
  mojihame -l###TATEYA_NAME### - $tmp-tateya        |
  mojihame -l###FLOOR_NAME### - $tmp-floor        |
  mojihame -l###KYOSHITSU_NAME### - $tmp-kyoshitsu        |
  mojihame -l###RIYOSHA_NAME###  - $tmp-riyosha    > $tmp-html
##  formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
