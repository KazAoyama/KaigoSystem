#!/bin/bash
#
# KAIGOJISSEKI_DATA_KENSAKU.GET_RIYOSHA.CGI : FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : KAIGOJISSEKI_DATA_KENSAKU_GET_RIYOSHA.CGI
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
room=$(nameread "room" $tmp-name)
riyosha_name=$(nameread "riyosha_name" $tmp-name)
nengetsumonth=$(nameread "nengetsumonth" ${tmp}-name)
nengetsu=$(echo ${nengetsumonth} | sed 's/-//g')

# SHISETSU_TATEYA_FLOOR_ROOMのマスタ準備
echo $shisetsu > $tmp-shisetsu

# ユニットマスタの準備
awk '$(NF-2)!=9' ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME        |
self 1 2                                                     > $tmp-unit_master

# 利用者マスタの準備
awk '$(NF-2)!=9' ${riyosha_dir}/RIYOUSHA_MASTER              |
self 1 2                                                     > $tmp-riyosha_master

awk '$(NF-2)!=9' ${riyosha_dir}/RIYOUSHA_MASTER              |
self 1 2 3                                                   > $tmp-riyosha_master_kana
# SHISETSU_RIYOSHA_STATUSの準備
awk '$(NF-2)!=9' ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS     |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
join0 key=1 $tmp-shisetsu                                    |
if [ $shisetsu = "0001" ];then
  join0 key=2 <(echo "02")
else
  join0 key=2 <(echo "00")
fi |
awk '$7<="'${nengetsu}'31" && $8>="'${nengetsu}'01"'  > $tmp-riyosha_status


if [ "$MODE" = "floor" -o $MODE = "text_sakuseibi" ]; then
  # floor一覧
  echo "0" "全て"                > $tmp-all_floor
  self 3 $tmp-riyosha_status   |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  LANG=C sort -u               |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         > ${tmp}-floor

  if [ "${floor}" = 0 ];then
  # unit一覧
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-riyosha_status                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 4                                                     |
    LANG=C sort -u                                       |
    join1 key=1 $tmp-unit_master                               |
    cat $tmp-all_unit -                                        > $tmp-unit

    # room
    echo "000" "全て"                      > $tmp-room_all
    cat $tmp-riyosha_status                            |
    self 5 5                                           |
    cat $tmp-room_all - |
    LANG=C sort -u > $tmp-room

  # member
    echo "00" "全て"                      > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    self 6                                                     |
    LANG=C sort -u -k1,1                                       |
    join1 key=1 $tmp-riyosha_master_kana                       |
    LANG=C sort -k3,3 |
    delf 3 > $tmp-riyosha
  else
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-riyosha_status                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1                                      |
    join1 key=1 $tmp-unit_master                               |
    cat $tmp-all_unit -                                        |
    awk '$1=="0" || $3=="'${floor}'"{print $1,$2}'             >  ${tmp}-unit

    # room
    echo "000" "全て"                      > $tmp-room_all
    awk '$3=="'${floor}'"' $tmp-riyosha_status         |
    self 5 5                                           |
    cat $tmp-room_all - |
    LANG=C sort -u |
    awk '{print $0,"'${room}'"}'                           |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-room

    # member
    echo "00" "全て"                    > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$3=="'${floor}'"{print $6}'                           |
    LANG=C sort -k1,1                                         |
    join2 key=1 $tmp-riyosha_master_kana                      |
    LANG=C sort -k3,3 |
    delf 3  > $tmp-riyosha
  fi

elif [ "$MODE" = "unit" ];then
  if [ "${unit}" = "0" ];then
    echo "0" "全て"                > $tmp-all_floor
    self 3 $tmp-riyosha_status                      |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    LANG=C sort -u                                         |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-all_floor -                                         |
    awk '{print $0,"'${floor}'"}'                                |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
    
    echo "0" "全て" "selected"            > $tmp-unit_all
    cat $tmp-riyosha_status               |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1                                      |
    join1 key=1 $tmp-unit_master                               |
    cat $tmp-all_unit -                                        |
    if [ "${floor}" = "0" ];then
      cat -
    else
      awk '$1=="0" || $3=="'${floor}'"'
    fi                                    > ${tmp}-unit

    # room
    echo "000" "全て"                      > $tmp-room_all
    awk '$3=="'${floor}'"' $tmp-riyosha_status         |
    self 5 5                                           |
    cat $tmp-room_all - |
    LANG=C sort -u |
    awk '{print $0,"'${room}'"}'                           |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-room

    # member
    echo "00" "全て"                    > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$3=="'${floor}'"{print $6}'                           |
    LANG=C sort -k1,1                                         |
    join1 key=1 $tmp-riyosha_master_kana                      |
    LANG=C sort -k3,3 |
    delf 3   > $tmp-riyosha

  else
    # floor一覧
    echo "0" "全て"                > $tmp-all_floor
    cat $tmp-riyosha_status                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 3 4                                                     |
    LANG=C sort -u -k1,2n                                        |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($2==$3){print $1,$1"F","selected"}else{print $1,$1"F",""}}' |
    cat $tmp-all_floor -                                         > $tmp-floor

    # unit一覧
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-riyosha_status                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    join0 key=3 <(echo "${floor}")                               |
    self 4                                                       |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-unit_master                                 |
    cat $tmp-all_unit -                                          |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

    # room
    echo "000" "全て"                      > $tmp-room_all
    awk '$3=="'${floor}'"' $tmp-riyosha_status         |
    self 5 5                                           |
    cat $tmp-room_all - |
    LANG=C sort -u |
    awk '{print $0,"'${room}'"}'                           |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-room

    # member
    echo "00" "全て"                    > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$4=="'${unit}'"{print $6}'                            |
    LANG=C sort -k1,1                                         |
    join1 key=1 $tmp-riyosha_master_kana                      |
    LANG=C sort -k3,3 |
    delf 3                        > $tmp-riyosha

  fi
elif [ "$MODE" = "room" ];then
  if [ "${room}" = "000" ];then
    echo "0" "全て"                > $tmp-all_floor
    self 3 $tmp-riyosha_status                      |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    LANG=C sort -u                                         |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-all_floor -                                         |
    awk '{print $0,"'${floor}'"}'                                |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
    
    # unit一覧
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-riyosha_status                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    join0 key=3 <(echo "${floor}")                               |
    self 4                                                       |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-unit_master                                 |
    cat $tmp-all_unit -                                          |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

    # room
    echo "000" "全て"                      > $tmp-room_all
    if [ $floor = "0" ];then
      cat $tmp-riyosha_status
    else
      awk '$3=="'${floor}'"' $tmp-riyosha_status
    fi |
    self 5 5                                           |
    cat $tmp-room_all - |
    LANG=C sort -u |
    awk '{print $0,"'${room}'"}'                           |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-room

    # member
    echo "00" "全て"                    > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    if [ $floor = "0" ];then
      self 6
    else
      awk '$3=="'${floor}'"{print $6}'
    fi |
    LANG=C sort -k1,1 -u                                       |
    join1 key=1 $tmp-riyosha_master_kana |
    LANG=C sort -k3,3 |
    delf 3                        > $tmp-riyosha
  else
    echo "0" "全て"                > $tmp-all_floor
    self 3 $tmp-riyosha_status                      |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    LANG=C sort -u                                         |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-all_floor -                                         |
    awk '{print $0,"'${floor}'"}'                                |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
    
    # unit一覧
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-riyosha_status                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    join0 key=3 <(echo "${floor}")                               |
    self 4                                                       |
    LANG=C sort -u -k1,1                                        |
    join1 key=1 $tmp-unit_master                                 |
    cat $tmp-all_unit -                                          |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

    # room
    echo "000" "全て"                      > $tmp-room_all
    if [ $floor = "0" ];then
      cat $tmp-riyosha_status
    else
      awk '$3=="'${floor}'"' $tmp-riyosha_status
    fi |
    self 5 5                                           |
    cat $tmp-room_all - |
    LANG=C sort -u |
    awk '{print $0,"'${room}'"}'                           |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-room

    # member
    echo "00" "全て"                    > $tmp-all
    if [ $floor = "0" ];then
      cat $tmp-riyosha_status
    else
      awk '$3=="'${floor}'"' $tmp-riyosha_status
    fi |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    self 6 5 |
    # 1:利用者id 2:居室
    LANG=C sort -k1,1 -u                                       |
    join1 key=1 $tmp-riyosha_master_kana |
    # 1:利用者id 2:利用者名 3:かな 4:居室
    LANG=C sort -k3,3 |
    awk '{print $1,$2,$4,"'${room}'"}' |
    # 1:利用者id 2:利用者名 3:居室 4:name
    awk '{if($3==$4){print $1,$2,"selected"}else{print $1,$2,"@"}}'  > $tmp-riyosha
  fi
else
  echo "0" "全て"                > $tmp-all_floor
  self 3 $tmp-riyosha_status                      |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  LANG=C sort -u                                         |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
  
  # unit一覧
  echo "0" "全て"                       > $tmp-all_unit
  cat $tmp-riyosha_status                          |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  if [ $floor = "0" ];then
    cat -
  else
    join0 key=3 <(echo "${floor}") 
  fi |
  self 4                                                       |
  LANG=C sort -u -k1,1                                        |
  join1 key=1 $tmp-unit_master                                 |
  cat $tmp-all_unit -                                          |
  awk '{print $0,"'${unit}'"}'                                 |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

  # room
  echo "000" "全て" "00000000"                     > $tmp-room_all
  if [ $floor = "0" ];then
    cat $tmp-riyosha_status
  else
    awk '$3=="'${floor}'"' $tmp-riyosha_status
  fi |
  self 5 5 6                                         |
  # 1:居室 2:居室 3:利用者ID
  cat $tmp-room_all - |
  LANG=C sort -u |
  awk '{print $0,"'${riyosha_name}'"}'                           |
  awk '{if($3==$4){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-room

  # member
  echo "00" "全て"                    > $tmp-all
  if [ $floor = "0" ];then
    cat $tmp-riyosha_status
  else
    awk '$3=="'${floor}'"' $tmp-riyosha_status
  fi |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  self 6 |
  LANG=C sort -k1,1 -u                                       |
  join1 key=1 $tmp-riyosha_master_kana |
  LANG=C sort -k3,3 |
  awk '{print $1,$2,"'${riyosha_name}'"}'                    |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > $tmp-riyosha
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

cat <<- FIN > ${tmp}-name
floor ${floor}
FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/CARECALL_RIREKI2.html |
  mojihame -l###FLOOR_NAME### - $tmp-floor        |
  mojihame -l###UNIT_NAME###  - $tmp-unit       |
  mojihame -l###ROOM_NAME###  - $tmp-room       |
  mojihame -l###RIYOSHA_NAME###  - $tmp-riyosha       |
  formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
