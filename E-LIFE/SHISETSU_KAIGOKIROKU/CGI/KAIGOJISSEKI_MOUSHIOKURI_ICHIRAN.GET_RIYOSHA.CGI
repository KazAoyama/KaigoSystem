#!/bin/bash
#
# KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.GET_RIYOSHA.CGI : SHISETSU,TATEYA,FLOORまたはUNITを選択してRIYOSHAを返す
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
work=${app_dir}/WORK

#ゴミtmpの消去
rm -f $tmp-*

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
shisetsu_select=$(nameread "shisetsu_select" ${tmp}-name)
tateya=$(nameread "tateya" ${tmp}-name)
floor=$(nameread "floor" ${tmp}-name)
unit=$(nameread "unit" ${tmp}-name)
room=$(nameread "room" ${tmp}-name)
fromday=$(nameread "from" ${tmp}-name)
to_day=$(nameread "to" ${tmp}-name)




# SHISETSU_TATEYA_FLOOR_ROOMのマスタ準備
echo $shisetsu_select > $tmp-shisetsu
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM               |
# 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
join0 key=1 <(echo $shisetsu_select)                         |
awk '$9=="1"'                                                > $tmp-shisetsu_tateya_floor_id

# 建屋準備
cat ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME                   |
self 1 3                                                     > $tmp-tateya_mas
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR         |
join0 key=1 <(echo $shisetsu_select)                         |
awk '$4=="1"'                                                |
self 2                                                       |
LANG=C sort -u -k1,1                                         |
join1 key=1 $tmp-tateya_mas                                  > $tmp-tateya_master

# ユニットマスタの準備
cat ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME                     |
self 1 2                                                     > $tmp-unit_master

# 利用者マスタの準備
echo "99999999" "職員連絡"                                 > $tmp-riyosha_igai
cat ${riyosha_dir}/RIYOUSHA_MASTER                           |
self 1 2 3                                                     |
cat - $tmp-riyosha_igai                                      > $tmp-riyosha_master

# SHISETSU_RIYOSHA_STATUSの準備
cat ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                     |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
join0 key=1 <(echo $shisetsu_select)                            |
awk '$9==1'                                                     |
#awk '$7<="'${to_day}'" && $8>="'${fromday}'"'                   |
awk '$8>="'${fromday}'"'                   |
LANG=C sort -u -k1,3n -k4,4n -k6,6n                          > $tmp-riyosha_status

# 施設名はログインユーザーの権限のある施設を取得
cat /home/hands/E-LIFE//SYSTEM_SETTEI/POMPA/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN    |
# 1:userid 2:SHISETSU_ID 3:KENGEN_GROUP 4:appID 5:MENU_NAME 6:DROPDOWN_STATUS 7:CGI_NAME 8:RINK_STATUS 9:CGI_STATUS 10:登録日時
LANG=C sort -u -k2,2n                                      |
self 1 2                                                   > ${tmp}-kengen
# 1:userid 2:SHISETSU_ID
if [ "$(cat ${tmp}-kengen | getfirst 1 1 | self 2)" = "0000" ];then
  awk '$1!="0000"' ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON      |
  self 1 2                                              |
  awk '{print $0,"'${shisetsu_select}'"}'              |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'  > ${tmp}-shisetsu
# 1:SHISESTU_ID 2:施設名
else
  cat ${tmp}-kengen                        |
  # 1:userid 2:SHISETSU_ID
  join1 key=2 ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
# 1:userid 2:SHISETSU_ID 3:施設名
  awk '$2!=0{print $2,$3}'                 |
  awk '{print $0,"'${shisetsu_select}'"}'              |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'  > ${tmp}-shisetsu
fi

# 実施者の取得
cat ${tbl_dir}/JYUUGYOUIN_MASTER/USER_KIHON                    |
# 1:従業員ID 2:従業員名 3:従業員名カナ 4:勤務期間from 5:勤務時間to
# 6:ID 7:PASS 8:削除フラグ 9:更新日時 10:ユーザーID
awk '$4<="'${to_day}'" && $5>="'${fromday}'" && $9!="9"' |
self 1 2                                                       > $tmp-user_master
cat ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU ${tbl_dir}/JYUUGYOUIN_MASTER/EXTRA_USER_SHISETSU   |
# 1:userid 2:施設id  3:建屋 4:フロア 5:ユニットid
# 6:事業所詳細 7:役職（ケアマネかサ責） 8:介護支援専門員番号
LANG=C sort -k2,2n                                             |
join0 key=2 <(echo $shisetsu_select)                           |
awk '$3=="'${tateya}'" || $3=="_"'                             |
if [ "${floor}" = 0 ];then
  cat -
else
  awk '$4=="'${floor}'" || $4=="_"'
fi                                                             |
self 1                                                         |
LANG=C sort -k1,1n                                             |
join1 key=1 $tmp-user_master                                   |
awk '{print $1"+++"$2,$2}'                                     |
LANG=C sort -u                                                 > $tmp-jisshisha_master
echo "0" "全て"                                                > $tmp-all_jisshisha
if [ -n "${JISSHISHA}" -a "${JISSHISHA}" != "_" ];then
  cat $tmp-all_jisshisha $tmp-jisshisha_master                 |
# 1:JISSISHA_CODE 2:JISSHISHA_NAME
  awk '{print $0,"'${JISSHISHA}'"}'                            |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'   > ${tmp}-jisshisha
else
  cat $tmp-all_jisshisha $tmp-jisshisha_master                 |
  awk '{print $1,$2,""}'                                       > ${tmp}-jisshisha
fi

if [ "$MODE" = "shisetsu" -o "${MODE}" = "date" ]; then
  # tateya
  cat $tmp-tateya_master                                       |
  awk '{print $0,"'${tateya}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya

  # floor一覧
  echo "0" "全て"                > $tmp-all_floor
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  awk '$2=="'${tateya}'"'                                      |
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         > ${tmp}-floor

  if [ "${floor}" = 0 ];then
  # unit一覧
     echo "0" "全て"                                            > $tmp-unit
#    echo "0" "全て"                       > $tmp-all_unit
#    cat $tmp-shisetsu_tateya_floor_id                          |
#    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
#    awk '$2=="'${tateya}'"'                                      |
#    self 4                                                     |
#    LANG=C sort -u -k1,1n                                      |
#    join1 key=1 $tmp-unit_master                               |
#    cat $tmp-all_unit -                                        > $tmp-unit
  # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        > $tmp-room_name
  # member
    echo "00" "全て"                                           > $tmp-all
    echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                      |
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3                                          |
    delf 3                                                     |
    cat $tmp-all $tmp-sonota_riyosha -                         > $tmp-riyosha
  else
    echo "0" "全て"                                            > $tmp-unit

  # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        > $tmp-room_name
#    # member
    echo "00" "全て"                    > $tmp-all
    echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                      |
    if [ "${floor}" = 0 ];then
      cat
    else
      awk '$3=="'${floor}'"{print $6}'                           
    fi                                                         |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3                                          |
    delf 3                                                     |
    cat $tmp-all $tmp-sonota_riyosha -                         > $tmp-riyosha
  fi
elif [ "$MODE" = "tateya" ]; then
  # tateya
  cat $tmp-tateya_master                                       |
  awk '{print $0,"'${tateya}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya

  # floor一覧
  echo "0" "全て"                > $tmp-all_floor
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  awk '$2=="'${tateya}'"'                                      |
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         > ${tmp}-floor

#  # unit一覧
   echo "0" "全て"                                             > ${tmp}-unit
#  echo "0" "全て"                       > $tmp-all_unit
#  cat $tmp-shisetsu_tateya_floor_id                          |
#  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
#  awk '$2=="'${tateya}'"'                                      |
#  self 4                                                     |
#  LANG=C sort -u -k1,1n                                      |
#  join1 key=1 $tmp-unit_master                               |
#  cat $tmp-all_unit -                                        > $tmp-unit
  # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        > $tmp-room_name

#  # member
  echo "00" "全て"                      > $tmp-all
  echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$2=="'${tateya}'"'                                      |
  self 6                                                     |
  LANG=C sort -k1,1n                                         |
  join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3                                          |
    delf 3                                                     |
  cat $tmp-all $tmp-sonota_riyosha -                           > $tmp-riyosha
elif [ "$MODE" = "floor" ]; then
  # tateya
  cat $tmp-tateya_master                                       |
  awk '{print $0,"'${tateya}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya

  # floor一覧
  echo "0" "全て"                > $tmp-all_floor
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'${tateya}'"'                                      |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  if [ "${floor}" = 0 ];then
  # unit一覧
     echo "0" "全て"                                          > ${tmp}-unit
#    echo "0" "全て"                       > $tmp-all_unit
#    cat $tmp-shisetsu_tateya_floor_id                          |
#    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
#    awk '$2=="'${tateya}'"'                                      |
#    self 4                                                     |
#    LANG=C sort -u -k1,1n                                      |
#    join1 key=1 $tmp-unit_master                               |
#    cat $tmp-all_unit -                                        > $tmp-unit
    # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        > $tmp-room_name

  # member
    echo "00" "全て"                      > $tmp-all
    echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
    cat $tmp-riyosha_status                                    |
    awk '$2=="'${tateya}'"'                                      |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3                                          |
    delf 3                                                     |
    cat $tmp-all $tmp-sonota_riyosha -                         > $tmp-riyosha
  else
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
    cat $tmp-all_unit -                                        |
    awk '$1=="0" || $3=="'${floor}'"{print $1,$2}'             >  ${tmp}-unit

    # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'" && $3=="'${floor}'"'                |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        > $tmp-room_name

    # member
    echo "00" "全て"                    > $tmp-all
    echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                      |
    awk '$3=="'${floor}'"{print $6}'                           |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3                                          |
    delf 3                                                     |
    cat $tmp-all $tmp-sonota_riyosha -                         > $tmp-riyosha
  fi

elif [ "$MODE" = "unit" ];then
  # tateya
  cat $tmp-tateya_master                                       |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{print $0,"'${tateya}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya

  # floor一覧
  if [ "${unit}" = "0" ];then
    echo "0" "全て"                > $tmp-all_floor
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 3                                                       |
    LANG=C sort -u -k1,1n                                        |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-all_floor -                                         |
    awk '{print $0,"'${floor}'"}'                                |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
    
    echo "0" "全て" "selected"            > $tmp-unit_all
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
    cat $tmp-all_unit -                                        |
    if [ "${floor}" = "0" ];then
      cat -
    else
      awk '$1=="0" || $3=="'${floor}'"'
    fi                                    > ${tmp}-unit

    # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        > $tmp-room_name


    # member
    echo "00" "全て"                    > $tmp-all
    echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                      |
    awk '$3=="'${floor}'"{print $6}'                           |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3                                          |
    delf 3                                                     |
    cat $tmp-all $tmp-sonota_riyosha -                            > $tmp-riyosha

  else
    # floor一覧
    echo "0" "全て"                > $tmp-all_floor
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 3 4                                                     |
    LANG=C sort -u -k1,2n                                        |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($2==$3){print $1,$1"F","selected"}else{print $1,$1"F",""}}' |
    cat $tmp-all_floor -                                         > $tmp-floor

    # unit一覧
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    join0 key=3 <(echo "${floor}")                               |
    self 4                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-unit_master                                 |
    cat $tmp-all_unit -                                          |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

    # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        > $tmp-room_name

    # member
    echo "00" "全て"                    > $tmp-all
    echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                      |
    awk '$4=="'${unit}'"{print $6}'                            |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3                                          |
    delf 3                                                     |
    cat $tmp-all $tmp-sonota_riyosha -                          > $tmp-riyosha
  fi
elif [ "$MODE" = "room" ]; then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'
  else
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master
  fi                                                             > $tmp-tateya

  # floor一覧
  echo "0" "全て"                > $tmp-all_floor
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'${tateya}'"'                                      |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  if [ "${floor}" = 0 ];then
    # unit一覧
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-all_unit                                         > $tmp-unit

    # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        |
    awk '{print $0,"'${room}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-room_name

    # member
    echo "00" "全て"                      > $tmp-all
    echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
    cat $tmp-riyosha_status                                    |
    awk '$2=="'${tateya}'"'                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    if [ "${room}" -ne 0 ];then
      awk '$5=="'${room}'"'                                    |
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 |
    cat - $tmp-all $tmp-sonota_riyosha
    else
      cat -                                                    |
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 |
    cat $tmp-all $tmp-sonota_riyosha -
    fi                                                         > $tmp-riyosha
  else
    echo "0" "全て"                       > $tmp-all_unit
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
    cat $tmp-all_unit -                                        |
    awk '$1=="0" || $3=="'${floor}'"{print $1,$2}'             >  ${tmp}-unit

    # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'" && $3=="'${floor}'"'                |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        |
    awk '{print $0,"'${room}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-room_name

    # member
    echo "00" "全て"                    > $tmp-all
    echo "99999999" "職員連絡"                               > $tmp-sonota_riyosha
    cat $tmp-riyosha_status                                    |
    awk '$2=="'${tateya}'"'                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$3=="'${floor}'"'                                     |
    if [ "${room}" -ne 0 ];then
      awk '$5=="'${room}'"'                                    |
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 |
    cat - $tmp-all $tmp-sonota_riyosha
    else
      cat -                                                    |
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 |
    cat $tmp-all $tmp-sonota_riyosha -
    fi                                                         > $tmp-riyosha
  fi
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

cat <<- FIN > ${tmp}-name
floor ${floor}
FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN2.html |
  mojihame -l###SHISETSU_NAME### - $tmp-shisetsu        |
  mojihame -l###TATEYA_NAME### - $tmp-tateya        |
  mojihame -l###FLOOR_NAME### - $tmp-floor        |
  mojihame -l###UNIT_NAME###  - $tmp-unit       |
  mojihame -l###ROOM_NAME###  - $tmp-room_name       |
  mojihame -l###RIYOSHA_NAME###  - $tmp-riyosha       |
  mojihame -l###JISSHISHA_NAME### - ${tmp}-jisshisha |
  formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
