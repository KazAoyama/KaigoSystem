#!/bin/bash
#
# AZUKARIKIN.GET_INPUT_RIYOSHA.CGI :
#                     
#
# Usage : AZUKARIKIN.GET_INPUT_RIYOSHA.CGI
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
master_tbl_dir="${home_dir}/E-LIFE/TBL/SEIKYU"
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
userid=$(nameread "userid" ${tmp}-name)
shisetsu=$(nameread "shisetsu" ${tmp}-name)
floor=$(nameread "floor" ${tmp}-name)
room=$(nameread "room" ${tmp}-name)
riyosha=$(nameread "riyosha" ${tmp}-name)


# 利用者マスタの準備
awk '$(NF-2)!=9' ${riyosha_dir}/RIYOUSHA_MASTER               |
self 1 2 3                                                    > $tmp-riyosha_master
# 1:利用者ID 2:利用者名 3:利用者カナ

# SHISETSU_RIYOSHA_STATUSの準備
awk '$(NF-2)!=9' ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                  |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
awk '$1=="'${shisetsu}'"'                                    |
awk '$7<="'${today}'" && $8>="'${today}'"'                   > $tmp-riyosha_status

if [ "$MODE" = "floor" ]; then
  # floor一覧
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  # 居室
  awk '$3=="'${floor}'"' $tmp-riyosha_status                 |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  self 5 5                                                   |
  LANG=C sort -u                                             > $tmp-room_name
  
  # member
  ROOOM=$(self 1 $tmp-room_name | head -n1)
  awk '$3=="'${floor}'"' $tmp-riyosha_status                |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  self 6 5                                                    |
  LANG=C sort -k1,1                                          |
  join1 key=1 $tmp-riyosha_master                            |
  LANG=C sort -k3,3 | delf 3                                 |
  awk '{print $1,$2,$3,"'${ROOOM}'"}' |
  awk '{if($3==$4){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-riyosha

elif [ "$MODE" = "room" ]; then
  # floor一覧
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  # 居室
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"'                                     |
  self 5 5                                                   |
  LANG=C sort -u                                             |
  awk '{print $0,"'${room}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-room_name

  # member
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"'                                     |
  awk '$5=="'${room}'"' |
  self 6                                                     |
  LANG=C sort -k1,1                                          |
  join1 key=1 $tmp-riyosha_master                            |
  LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha
elif [ "$MODE" = "riyosha" ]; then
  # floor一覧
  floor=$(awk '$6=="'${riyosha}'"{print $3}' $tmp-riyosha_status | head -n1)
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  # 居室
  room=$(awk '$6=="'${riyosha}'"{print $5}' $tmp-riyosha_status | head -n1)
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"'                                     |
  self 5 5                                                   |
  LANG=C sort -u                                             |
  awk '{print $0,"'${room}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-room_name

  # member
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"'                                     |
  awk '$5=="'${room}'"' |
  self 6                                                     |
  LANG=C sort -k1,1                                          |
  join1 key=1 $tmp-riyosha_master                            |
  LANG=C sort -k3,3 | delf 3                                 |
  awk '{print $1,$2,"'${riyosha}'"}' |
  awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-riyosha


else
  # floor一覧
  floor=$(awk '$5=="'${MODE}'"{print $3}' $tmp-riyosha_status | head -n1)
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  # 居室
  room=$MODE
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"'                                     |
  self 5 5                                                   |
  LANG=C sort -u                                             |
  awk '{print $0,"'${room}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-room_name

  # member
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"'                                     |
  awk '$5=="'${room}'"' |
  self 6                                                     |
  LANG=C sort -k1,1                                          |
  join1 key=1 $tmp-riyosha_master                            |
  LANG=C sort -k3,3 | delf 3                                 |
  awk '{print $1,$2,"'${riyosha}'"}' |
  awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-riyosha
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


#######################################################################################
  # HTMLを作成
  awk '/\<ajax_start_input\>/,/\<ajax_end_input\>/' ${html_dir}/AZUKARIKIN2.html |
  mojihame -l###INPUT_FLOOR_NAME### - $tmp-floor        |
  mojihame -l###INPUT_RIYOSHA_NAME###  - $tmp-riyosha   |
  mojihame -l###INPUT_ROOM_NAME###  - $tmp-room_name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
