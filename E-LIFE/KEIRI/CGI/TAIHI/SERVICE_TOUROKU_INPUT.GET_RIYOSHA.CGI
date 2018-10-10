#!/bin/bash
#
# SERVICE_TOUROKU.GET_RIYOSHA.CGI : SHISETSU,TATEYA,FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : SERVICE_TOUROKU.GET_RIYOSHA.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by aoyagi  

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/KEIRI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/KEIRI/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


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
app_dir="${home_dir}/E-LIFE/KEIRI"
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
tateya=$(nameread "input_tateya" ${tmp}-name)
floor=$(nameread "nyuryoku_floor" ${tmp}-name)
unit=$(nameread "nyuryoku_unit" ${tmp}-name)
tatekae_day=$(nameread "tatekae_day" ${tmp}-name)
room=$(nameread "room" ${tmp}-name)

cat ${master_tbl_dir}/SERVICE_MASTER |
# 1:施設         2:建屋      3:サービスID 4:サービス区分(固定) 5:サービス名
# 6:集計グループ 7:単価      8:表示順     9:課税               10:有効フラグ
# 11:処理時間    12:ユーザID

LANG=C sort -k1,1 -k2,2            |
join0 key=1 <(echo ${shisetsu})      |
join0 key=2 <(echo ${tateya})        |
self 8 3 5 7                          |
# 1:表示順 2:サービスID 3:サービス名 4:単価
LANG=C sort -k1,1n                    |
self 2 3 4                            |
head -n 1                             > $tmp-init_service_master
nyuryoku_service_koumoku="$(cat $tmp-init_service_master | self 1)"


# SHISETSU_TATEYA_FLOOR_ROOMのマスタ準備
echo $shisetsu > $tmp-shisetsu
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM               |
# 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
join0 key=1 $tmp-shisetsu                                    |
awk '$9=="1"'                                                > $tmp-shisetsu_tateya_floor_id

# 建屋準備
cat ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME                   |
self 1 3                                                     > $tmp-tateya_master

# ユニットマスタの準備
cat ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME                     |
self 1 2                                                     > $tmp-unit_master

# 利用者マスタの準備
cat ${riyosha_dir}/RIYOUSHA_MASTER                           |
self 1 2 3                                                    > $tmp-riyosha_master

# SHISETSU_RIYOSHA_STATUSの準備
taikyogo=$(mdate ${tatekae_day}/-31)
awk '$(NF-2)!=9' ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                  |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
join0 key=1 $tmp-shisetsu                                    |
awk '$7<="'${tatekae_day}'" && $8>="'${taikyogo}'"'                   |
LANG=C sort -u -k1,3n -k4,4n -k6,6n                          > $tmp-riyosha_status

# 入力のサービスマスターの取得
cat ${master_tbl_dir}/SERVICE_MASTER |
# 1:施設         2:建屋      3:サービスID 4:サービス区分(固定) 5:サービス名
# 6:集計グループ 7:単価      8:表示順     9:課税               10:有効フラグ
# 11:処理時間    12:ユーザID

LANG=C sort -k1,1 -k2,2            |
join0 key=1 <(echo ${shisetsu})      |
join0 key=2 <(echo ${tateya})        |
awk '$(NF-2)!=9'                      |
self 8 3 5 7                          |
# 1:表示順 2:サービスID 3:サービス名 4:単価
LANG=C sort -k1,1n                    |
self 2 3 4                            |
awk '{print $0,"'${nyuryoku_service_koumoku}'"}' |
awk '{if($1==$4){print $1,$2,"selected",$3}else{print $1,$2,"_",$3}}' > ${tmp}-nyuryoku_master

cat ${tmp}-nyuryoku_master |
self 1 2 3                 > ${tmp}-nyuryoku_service_master
nyuryoku_kingaku=$(cat ${tmp}-nyuryoku_master |
awk '$3=="selected"'                                   |
self 4)

# 入力数量の取得
nyuryoku_suryo="1"
echo "###nyuryoku_suryo###" ${nyuryoku_suryo} >> ${tmp}-calsed1

# 入力の金額のチェック
if [ "${nyuryoku_kingaku}" = "_" ];then
  echo "###nyuryoku_kingaku###" "" >> ${tmp}-calsed1
else
  echo "###nyuryoku_kingaku###" "${nyuryoku_kingaku}" >> ${tmp}-calsed1
fi

# 入力の備考のチェック
if [ "${nyuryoku_biko}" = "_" ];then
  echo "###nyuryoku_biko###" "" >> ${tmp}-calsed1
else
  echo "###nyuryoku_biko###" "${nyuryoku_biko}" >> ${tmp}-calsed1
fi

echo "0 全て" > $tmp-all_floor

if [ "$MODE" = "tateya" ]; then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               > $tmp-tateya_name
  fi
  # floor一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'${tateya}'"'                                      |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         |
  awk '{print $0,"'${floor}'"}'                                |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  # unit一覧
  cat $tmp-shisetsu_tateya_floor_id                          |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  awk '$2=="'${tateya}'"'                                      |
  self 4                                                     |
  LANG=C sort -u -k1,1n                                      |
  join1 key=1 $tmp-unit_master                               > $tmp-unit

  # 居室
  echo "0 全て"                                              > $tmp-all_room
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$2=="'${tateya}'"'                                    |
  self 5 5                                                   |
  LANG=C sort -u                                             |
  cat $tmp-all_room -                                        > $tmp-room_name

  # member
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$2=="'${tateya}'"'                                      |
  if [ "${floor}" = 0 ];then
    cat -
  else
    awk '$3=="'${floor}'"'
  fi                                                         |
  self 6                                                     |
  LANG=C sort -k1,1n                                         |
  join1 key=1 $tmp-riyosha_master                            |
  LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha

elif [ "$MODE" = "floor" ]; then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               > $tmp-tateya_name
  fi
  # floor一覧
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
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4                                                     |
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               > $tmp-unit

    # 居室
    echo "0 全て"                                              > $tmp-all_room
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    self 5 5                                                   |
    LANG=C sort -u                                             |
    cat $tmp-all_room -                                        > $tmp-room_name

    # member
    cat $tmp-riyosha_status                                    |
    awk '$2=="'${tateya}'"'                                      |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha
  else
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
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
    cat $tmp-riyosha_status                                    |
    awk '$2=="'${tateya}'"'                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$3=="'${floor}'"{print $6}'                           |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha
  fi

elif [ "$MODE" = "unit" ];then
  # tateya
  if [ -n "${tateya}" -a "${tateya}" != "_" ];then
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               > $tmp-tateya_name
  fi
  # floor一覧
  if [ "${unit}" = "0" ];then
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 3                                                       |
    LANG=C sort -u -k1,1n                                        |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-all_floor -                                         |
    awk '{print $0,"'${floor}'"}'                                |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
    
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
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
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                      |
    if [ "${floor}" = 0 ];then
      self 6
    else
      awk '$3=="'${floor}'"{print $6}'
    fi                                                         |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha

  else
    # floor一覧
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 3 4                                                     |
    LANG=C sort -u -k1,2n                                        |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($2==$3){print $1,$1"F","selected"}else{print $1,$1"F",""}}' > $tmp-floor

    # unit一覧
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    join0 key=3 <(echo "${floor}")                               |
    self 4                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-unit_master                                 |
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
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"{print $6}'                          |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha

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
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya_name
  else
    cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               > $tmp-tateya_name
  fi
  # floor一覧
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
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4                                                     |
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               > $tmp-unit

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
    cat $tmp-riyosha_status                                    |
    awk '$2=="'${tateya}'"'                                      |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    if [ "${room}" -ne 0 ];then
      awk '$5=="'${room}'"'
    else
      cat -
    fi                                                         |
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha
  else
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
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
    cat $tmp-riyosha_status                                    |
    awk '$2=="'${tateya}'"'                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    if [ "${room}" -ne 0 ];then
      awk '$5=="'${room}'"'
    else
      cat -
    fi                                                         |
    self 6                                                     |
    LANG=C sort -k1,1n                                         |
    join1 key=1 $tmp-riyosha_master                            |
    LANG=C sort -k3,3 | delf 3                                 > $tmp-riyosha
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


#######################################################################################
  # HTMLを作成
  awk '/\<nyuryoku_ajax_start\>/,/\<nyuryoku_ajax_end\>/' ${html_dir}/SERVICE_TOUROKU2.html |
  mojihame -l###NYURYOKU_FLOOR_NAME### - $tmp-floor        |
  mojihame -l###NYURYOKU_TATEYA_NAME### - $tmp-tateya_name        |
  mojihame -l###NYURYOKU_UNIT_NAME###  - $tmp-unit       |
  mojihame -l###NYURYOKU_RIYOSHA_NAME###  - $tmp-riyosha       |
  mojihame -l###NYURYOKU_ROOM_NAME###  - $tmp-room_name       |
  mojihame -l###NYURYOKU_SERVICE_MASTER###  - $tmp-nyuryoku_service_master       |
  calsed -f ${tmp}-calsed1 -                          > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
#rm -f $tmp-*
exit 0
