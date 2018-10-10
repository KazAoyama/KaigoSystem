#!/bin/bash
#
# TATEKAEKIN.GET_RIYOSHA.CGI : SHISETSU,TATEYA,FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : TATEKAEKIN.GET_RIYOSHA.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by aoyagi  

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/TATEKAEKIN/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/TATEKAEKIN/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


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
app_dir="${home_dir}/E-LIFE/TATEKAEKIN"
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
userid=$(nameread "userid" ${tmp}-name)
shisetsu=$(nameread "shisetsu" ${tmp}-name)
tateya=$(nameread "input_tateya" ${tmp}-name)
floor=$(nameread "nyuryoku_floor" ${tmp}-name)
unit=$(nameread "nyuryoku_unit" ${tmp}-name)
tatekaebi=$(nameread "tatekaebi" ${tmp}-name)
room=$(nameread "room" ${tmp}-name)
riyosha=$(nameread "riyosha" $tmp-name)

# SHISETSU_TATEYA_FLOOR_ROOMのマスタ準備
echo $shisetsu > $tmp-shisetsu

# SHISETSU_RIYOSHA_STATUSの準備
taikyogo=$(mdate ${tatekaebi}/-31)
awk '$(NF-2)!=9' ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS     |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
join0 key=1 $tmp-shisetsu                                    |
#awk '$2=="'${tateya}'"' |
awk '$7<="'${tatekaebi}'" && $8>="'${taikyogo}'"'    > $tmp-riyosha_status
# 建屋準備
cat ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME                   |
self 1 3                                                     > $tmp-tateya_master

# ユニットマスタの準備
cat ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME                     |
self 1 2                                                     > $tmp-unit_master

# 利用者マスタの準備
awk '$(NF-2)!=9' ${riyosha_dir}/RIYOUSHA_MASTER              |
self 1 2 3                                                   > $tmp-riyosha_master


# 施設名はログインユーザーの権限のある施設を取得
cat /home/hands/E-LIFE//SYSTEM_SETTEI/POMPA/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN    |
# 1:userid 2:SHISETSU_ID 3:KENGEN_GROUP 4:appID 5:MENU_NAME 6:DROPDOWN_STATUS 7:CGI_NAME 8:RINK_STATUS 9:CGI_STATUS 10:登録日時
LANG=C sort -u -k2,2n                                      |
self 1 2                                                   > ${tmp}-kengen
# 1:userid 2:SHISETSU_ID
if [ "$(cat ${tmp}-kengen | getfirst 1 1 | self 2)" = "0000" ];then
  awk '$1!="0000"' ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON      |
  self 1 2                                              |
  awk '{print $0,"'${shisetsu}'"}'              |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'  > ${tmp}-shisetsu
# 1:SHISESTU_ID 2:施設名
else
  cat ${tmp}-kengen                        |
  # 1:userid 2:SHISETSU_ID
  join1 key=2 ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
# 1:userid 2:SHISETSU_ID 3:施設名
  awk '$2!=0{print $2,$3}'                 |
  awk '{print $0,"'${shisetsu}'"}'              |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'  > ${tmp}-shisetsu
fi


if [ "$MODE" = "tateya" ]; then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    self 2 $tmp-riyosha_status                                   |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    self 2 $tmp-riyosha_status                                   |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                               > $tmp-tateya_name
  fi
  # floor一覧
  awk '$2=="'${tateya}'"' $tmp-riyosha_status |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       > $tmp-floor

  # unit一覧
  awk '$2=="'${tateya}'"' $tmp-riyosha_status |
  self 4                                                     |
  LANG=C sort -u -k1,1                                      |
  join1 key=1 $tmp-unit_master                               > $tmp-unit

  awk '$2=="'${tateya}'"' $tmp-riyosha_status |
  self 5 5 |
# 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  LANG=C sort -u                                               > $tmp-room_name

  # member
  room=$(head -n1 $tmp-room_name | self 1)
  awk '$2=="'${tateya}'"' $tmp-riyosha_status                |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  self 6 5 7                                                |
  LANG=C sort -k1,1 -k3,3 |
  getlast 1 1 |
  delf 3 |
  # 1:利用者ID 2:居室
  LANG=C sort -k1,1                                         |
  join1 key=1 $tmp-riyosha_master                            |
  # 1:利用者ID 2:利用者名 3:かな 4:居室
  LANG=C sort -k3,3                                          |
  awk '{print $1,$2,$4,"'${room}'"}' |
  awk '{if($3==$4){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-riyosha
elif [ "$MODE" = "floor" ]; then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    self 2 $tmp-riyosha_status                                  |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    self 2 $tmp-riyosha_status                                |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                          > $tmp-tateya_name
  fi
  # floor一覧
  awk '$2=="'${tateya}'"' $tmp-riyosha_status |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-floor_all -                                         |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  awk '$2=="'${tateya}'"' $tmp-riyosha_status |
  self 4 3                                                   |
  # 1:ユニットid 2:フロア
  LANG=C sort -u -k1,1                                      |
  join1 key=1 $tmp-unit_master                               |
  awk '$1=="0" || $3=="'${floor}'"{print $1,$2}'             >  ${tmp}-unit

  awk '$2=="'${tateya}'"&&$3=="'${floor}'"' $tmp-riyosha_status |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 5 5                                                     |
  LANG=C sort -u                                             > $tmp-room_name

  # member
  room=$(head -n1 $tmp-room_name | self 1)
  awk '$2=='${tateya}'' $tmp-riyosha_status                |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"{print $6,$5,$7}'                    |
  LANG=C sort -k1,1 -k3,3 |
  getlast 1 1 |
  delf 3 |
  # 1:利用者id 2:居室
  LANG=C sort -k1,1                                         |
  join1 key=1 $tmp-riyosha_master                            |
  # 1:利用者id 2:利用者名 3:かな 4:居室
  LANG=C sort -k3,3 | 
  awk '{print $1,$2,$4,"'${room}'"}' |
  awk '{if($3==$4){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-riyosha

elif [ "$MODE" = "unit" ];then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    self 2 $tmp-riyosha_status                                  |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    self 2 $tmp-riyosha_status                           |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                         > $tmp-tateya_name
  fi
  # floor一覧
  if [ "${unit}" = "0" ];then
    awk '$2=="'${tateya}'"' $tmp-riyosha_status |
    self 3                                                       |
    LANG=C sort -u -k1,1n                                        |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-floor_all -                                         |
    awk '{print $0,"'${floor}'"}'                                |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
    
    awk '$2=="'${tateya}'"' $tmp-riyosha_status |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1                                      |
    join1 key=1 $tmp-unit_master                               |
      awk '$1=="0" || $3=="'${floor}'"'    > ${tmp}-unit

    awk '$3=="'${floor}'"' $tmp-riyosha_status |
    self 5 5                                                     |
    LANG=C sort -u                                            > $tmp-room_name

  # member
  room=$(head -n1 $tmp-room_name | self 1)
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'"{print $6,$5,$7}'                    |
  LANG=C sort -k1,1 -k3,3 |
  getlast 1 1 |
  delf 3 |
  # 1:利用者id 2:居室
  LANG=C sort -k1,1                                         |
  join1 key=1 $tmp-riyosha_master                            |
  # 1:利用者id 2:利用者名 3:かな 4:居室
  LANG=C sort -k3,3 | 
  awk '{print $1,$2,$4,"'${room}'"}' |
  awk '{if($3==$4){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-riyosha

  else
    # floor一覧
    awk '$2=="'${tateya}'"' $tmp-riyosha_status |
    self 3                                                       |
    LANG=C sort -u -k1,1n                                        |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-floor_all -                                         > $tmp-floor

    # unit一覧
    awk '$2=="'${tateya}'"' $tmp-riyosha_status |
    join0 key=3 <(echo "${floor}")                               |
    self 4                                                       |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-unit_master                                 |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

    awk '$3=="'${floor}'"' $tmp-riyosha_status |
    self 5 5                                                     |
    LANG=C sort -u                                        > $tmp-room_name

  # member
  room=$(head -n1 $tmp-room_name | self 1)
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$4=="'${unit}'"{print $6,$5,$7}'                    |
  LANG=C sort -k1,1 -k3,3 |
  getlast 1 1 |
  delf 3 |
  # 1:利用者id 2:居室
  LANG=C sort -k1,1                                         |
  join1 key=1 $tmp-riyosha_master                            |
  # 1:利用者id 2:利用者名 3:かな 4:居室
  LANG=C sort -k3,3 | 
  awk '{print $1,$2,$4,"'${room}'"}' |
  awk '{if($3==$4){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-riyosha
  fi
elif [ "$MODE" = "room" ]; then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    self 2 $tmp-riyosha_status                |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    self 2 $tmp-riyosha_status                                  |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                        > $tmp-tateya_name
  fi
  # floor一覧
  awk '$2=="'${tateya}'"' $tmp-riyosha_status                  |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  awk '$2=="'${tateya}'"' $tmp-riyosha_status |
  self 4 3                                                   |
  # 1:ユニットid 2:フロア
  LANG=C sort -u -k1,1                                      |
  join1 key=1 $tmp-unit_master                               |
  awk '$1=="0" || $3=="'${floor}'"{print $1,$2}'             >  ${tmp}-unit

  awk '$2=="'${tateya}'"&&$3=="'${floor}'"' $tmp-riyosha_status |
  self 5 5                                                     |
  LANG=C sort -u                                               |
  awk '{print $0,"'${room}'"}'                                 |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-room_name

  # member
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'" && $5=="'${room}'"{print $6}' |
  LANG=C sort -k1,1                                         |
  join1 key=1 $tmp-riyosha_master                            |
  LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha
elif [ "$MODE" = "riyosha" ]; then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    self 2 $tmp-riyosha_status                |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    self 2 $tmp-riyosha_status                                  |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                        > $tmp-tateya_name
  fi
  # floor一覧
  awk '$2=="'${tateya}'"' $tmp-riyosha_status                  |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  awk '$2=="'${tateya}'"' $tmp-riyosha_status |
  self 4 3                                                   |
  # 1:ユニットid 2:フロア
  LANG=C sort -u -k1,1                                      |
  join1 key=1 $tmp-unit_master                               |
  awk '$1=="0" || $3=="'${floor}'"{print $1,$2}'             >  ${tmp}-unit

  room=$(awk '$6=="'${riyosha}'"{print $5}' $tmp-riyosha_status| head -n1)
  awk '$2=="'${tateya}'"&&$3=="'${floor}'"' $tmp-riyosha_status |
  self 5 5                                                     |
  LANG=C sort -u                                               |
  awk '{print $0,"'${room}'"}'                                 |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-room_name

  # member
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'" && $5=="'${room}'"{print $6}' |
  LANG=C sort -k1,1                                         |
  join1 key=1 $tmp-riyosha_master                            |
  LANG=C sort -k3,3 | delf 3                                 |
  awk '{print $1,$2,"'${riyosha}'"}' |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-riyosha
else
  room=$MODE
  # tateya
  tateya=$(awk '$5=="'${room}'"{print $2}' $tmp-riyosha_status|head -n1)
  floor=$(awk '$5=="'${room}'"{print $3}' $tmp-riyosha_status|head -n1)
  unit=$(awk '$5=="'${room}'"{print $4}' $tmp-riyosha_status|head -n1)
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    self 2 $tmp-riyosha_status                |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    self 2 $tmp-riyosha_status                                  |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-tateya_master                        > $tmp-tateya_name
  fi
  # floor一覧
  awk '$2=="'${tateya}'"' $tmp-riyosha_status                  |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  awk '$2=="'${tateya}'"' $tmp-riyosha_status |
  self 4 3                                                   |
  # 1:ユニットid 2:フロア
  LANG=C sort -u -k1,1                                      |
  join1 key=1 $tmp-unit_master                               |
  awk '$1=="0" || $3=="'${floor}'"{print $1,$2}'             >  ${tmp}-unit

  awk '$2=="'${tateya}'"&&$3=="'${floor}'"' $tmp-riyosha_status |
  self 5 5                                                     |
  LANG=C sort -u                                               |
  awk '{print $0,"'${room}'"}'                                 |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-room_name

  # member
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'" && $5=="'${room}'"{print $6}' |
  LANG=C sort -k1,1                                         |
  join1 key=1 $tmp-riyosha_master                            |
  LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha
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


#######################################################################################
  # HTMLを作成
awk '/\<nyuryoku_ajax_start\>/,/\<nyuryoku_ajax_end\>/' ${html_dir}/TATEKAEKIN2.html |
mojihame -l###NYURYOKU_FLOOR_NAME### - $tmp-floor        |
mojihame -l###NYURYOKU_UNIT_NAME###  - $tmp-unit       |
mojihame -l###NYURYOKU_RIYOSHA_NAME###  - $tmp-riyosha       |
mojihame -l###NYURYOKU_ROOM_NAME###  - $tmp-room_name       |
mojihame -l###NYURYOKU_TATEYA_NAME###  - $tmp-tateya_name       > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
