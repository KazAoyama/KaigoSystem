#!/bin/bash
#
# KAIGOJISSEKI_IKKATSU.GET_RIYOSHA.CGI : FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : KAIGOJISSEKI_IKKATSU.GET_RIYOSHA.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by aoyagi  

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

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
app_dir="${home_dir}/E-LIFE/SHISETSU_KAIGOKIROKU"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA"
apptbl_dir="${app_dir}/TBL"
kyoutsu_dir="${home_dir}/E-LIFE/KYOUTSU/HTML"
riyosha_dir="/DATA/E-LIFE/UNEI/RIYOUSHA"
tbl_dir="${home_dir}/E-LIFE/TBL"
work="${app_dir}/WORK"


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
floor=$(nameread "floor" ${tmp}-name)
unit=$(nameread "unit" ${tmp}-name)
room=$(nameread "room" ${tmp}-name)
riyosha_name=$(nameread "riyosha_name" ${tmp}-name)

echo $shisetsu > $tmp-shisetsu
# ユニットマスタの準備
cat ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME                     |
self 1 2                                                     > $tmp-unit_master

# 利用者マスタの準備
awk '$(NF-2)!=9' ${riyosha_dir}/RIYOUSHA_MASTER                           |
self 1 2 3                                                    > $tmp-riyosha_master

# SHISETSU_RIYOSHA_STATUSの準備
awk '$(NF-2)!=9' ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                  |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
join0 key=1 $tmp-shisetsu                                    |
if [ $shisetsu = "0001" ];then
  join0 key=2 <(echo "02")
else
  join0 key=2 <(echo "00")
fi |
awk '$8>="'${today}'"'           |
self 1/6                                                     > $tmp-riyosha_status
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id

if [ "$MODE" = "floor" -o "$MODE" = "text_sakuseibi" ]; then
  # floor一覧
  self 3 $tmp-riyosha_status   |
  LANG=C sort -u -k1,1n        |
  awk '{print $1,$1"F","'${floor}'"}'       |
  awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > ${tmp}-floor

  # unit
  cat $tmp-riyosha_status                           |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  join0 key=3 <(echo "${floor}")                               |
  self 4                                                       |
  LANG=C sort -u -k1,1                                         |
  join1 key=1 $tmp-unit_master                                 > $tmp-unit

  # room
  echo "---" > $tmp-room_select
  cat $tmp-riyosha_status                            |
  join0 key=3 <(echo "${floor}")                               |
  self 5                                                       |
  cat $tmp-room_select - |
  awk '{print $1,$1}'                           > $tmp-room

  # member
  room="---"
  echo '_ 選択してください' > $tmp-riyosha_header
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"{print $6,$5,"'${room}'"}'              |
  # 1:利用者ID 2:居室 3:部屋name
  LANG=C sort -k1,1                                            |
  join1 key=1 $tmp-riyosha_master                              |
  # 1:利用者id 2:利用者名 3:かな 4:居室 5:室name
  LANG=C sort -k3,3 -u                                         |
  self 1 2 |
  cat $tmp-riyosha_header - > $tmp-riyosha


elif [ "$MODE" = "unit" ];then
  # floor一覧
  self 3 4 $tmp-riyosha_status                                 |
  LANG=C sort -u -k1,2n                                        |
  awk '{print $0,"'${floor}'"}'                                 |
  awk '{if($2==$3){print $1,$1"F","selected"}else{print $1,$1"F",""}}'         > $tmp-floor

  # unit
  cat $tmp-riyosha_status                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  join0 key=3 <(echo "${floor}")                               |
  self 4                                                       |
  LANG=C sort -u -k1,1                                        |
  join1 key=1 $tmp-unit_master                                 |
  awk '{print $0,"'${unit}'"}'                                 |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit
  
  cat $tmp-riyosha_status                            |
  awk '$4=="'${unit}'"{print $5}'                              |
  awk '{print $1,$1,"'${room}'"}'                           |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-room

  # member
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$4=="'${unit}'"{print $6}'                              |
  LANG=C sort -k1,1                                            |
  join1 key=1 $tmp-riyosha_master                              |
  LANG=C sort -k3,3 -u                                         > $tmp-riyosha

elif [ "${MODE}" = "room" ];then
  cat $tmp-riyosha_status                                      |
tee ${work}/status_statty |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  LANG=C sort -k5,5                                            |
  join0 key=5 <(echo "${room}")                                |
  self 3 4                                                     |
  LANG=C sort -u -k1,2                                         > $tmp-floor_unit
  UNIT=$(cat $tmp-floor_unit | self 2 | tail -n1)
  FLOOR=$(cat $tmp-floor_unit | self 1 | tail -n1)
  # floor
  self 3 $tmp-riyosha_status                                   |
  LANG=C sort -u                                               |
  awk '{print $0,"'${FLOOR}'"}'                                |
  awk '{if($1==$2){print $1,$1"F","selected"}else{print $1,$1"F",""}}' > $tmp-floor
  # unit
  cat $tmp-riyosha_status  |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  join0 key=3 <(echo "${FLOOR}")                               |
  self 4                                                       |
  LANG=C sort -u -k1,1                                         |
  join1 key=1 $tmp-unit_master                                 |
  awk '{print $0,"'${UNIT}'"}'                                 |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

  awk '$3=="'${FLOOR}'"{print $5}' $tmp-riyosha_status                   |
  awk '{print $1,$1,"'${room}'"}'                           |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-room
  
  # member
  awk '$3=="'${FLOOR}'"{print $0,"'${room}'"}' $tmp-riyosha_status  |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id 7:居室name
  LANG=C sort -k6,6                                            |
  join1 key=6 $tmp-riyosha_master                              |
  # 1:施設 2:建屋 3;フロア 4;ユニット 5:部屋番号 6:
  LANG=C sort -k8,8                                            |
  
  awk '{if($5==$9){print $6,$7,"selected"}else{print $6,$7,"@"}} ' > $tmp-riyosha


elif [ "$MODE" = "riyosha_name" ];then

  cat $tmp-riyosha_status                           |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  LANG=C sort -k6,6                                           |
  join0 key=6 <(echo "${riyosha_name}")                        |
  self 3 4                                                     |
  LANG=C sort -u -k1,2n                                        > $tmp-floor_unit
  UNIT=$(cat $tmp-floor_unit | self 2)
  FLOOR=$(cat $tmp-floor_unit | self 1)

  # unit
  cat $tmp-riyosha_status       |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  join0 key=3 <(echo "${FLOOR}")                               |
  self 4                                                       |
  LANG=C sort -u -k1,1                                        |
  join1 key=1 $tmp-unit_master                                 |
  awk '{print $0,"'${UNIT}'"}'                                 |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

  # floor
  self 3 $tmp-riyosha_status                                   |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $0,"'${FLOOR}'"}'                                |
  awk '{if($1==$2){print $1,$1"F","selected"}else{print $1,$1"F",""}}' > $tmp-floor
  
  # room
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '{print $0,"'${riyosha_name}'"}'                         |

  awk '{if($6==$7){print $5,$5,"selected"}else{print $5,$5,"@"}} ' |
  LANG=C sort -k1,2 -u                                         > $tmp-room

  # member
  awk '$3=="'${FLOOR}'"{print $6}' $tmp-riyosha_status         |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  LANG=C sort -k1,1                                            |
  join1 key=1 $tmp-riyosha_master                              |
  LANG=C sort -k3,3                                            |
  awk '{print $0,"'${riyosha_name}'"}'                         |
  awk '{if($1==$4){print $1,$2,"selected"}else{print $1,$2,""}} ' > $tmp-riyosha

else
  :
fi

#######################################################################################
# formhame前の実態参照変換
calsed "&" "&amp;" ${namefile}                      |
calsed "<" "&lt;"                                   |
calsed ">" "&gt;"                                   |
calsed "\"" "&quot;"                                |
# formhame前にキーワードが　"_"　のみの場合、消去
awk '{if($1~/SEARCH_WORD/){if($2~/^_$/){$2=""};}print}'  |
# formhame前にキーワードが検索ボックスの空白を "_"から" "に戻す
awk '{if($1~/SEARCH_WORD/){gsub(/_/," ",$2)};print}'     > $tmp-namefile

#######################################################################################

# formhameの準備
floor=$(echo ${floor})
unit=$(echo ${unit})


#######################################################################################
# namefileの再構成

#cat <<- FIN > ${tmp}-name
#floor ${floor}
#FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/KANGO_KAIGO_YOUYAKU2.html |
  mojihame -l###FLOOR_NAME### - $tmp-floor        |
  mojihame -l###UNIT_NAME###  - $tmp-unit       |
  mojihame -l###ROOM_NAME###  - $tmp-room       |
  mojihame -l###RIYOSHA_NAME###  - $tmp-riyosha > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
#rm -f $tmp-*
exit 0
