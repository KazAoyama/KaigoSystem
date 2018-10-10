#!/bin/bash
#
# AJAX_SHISETSU_INFO_SELECT.CGI : 施設、建屋、FLOORまたはUNITを選択して居室を返す
#                     
#
# Usage : AJAX_SHISETSU_INFO_SELECT.CGI
#         POST メソッドで 建屋、フロア、ユニット、居室 を渡す。
#
# Written by aoyagi  

source /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).$HOSTNAME.$(date +%Y%m%d) ; set -xv

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#ゴミtmpの消去
rm -f $tmp-*


# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name

cp $tmp-name tmp-ajax_name
# MODE取得
MODE=$(nameread "MODE" ${tmp}-name)
# 選択しているSHISETSU_CODE
shisetsu=$(nameread "shisetsu" ${tmp}-name)
tateya=$(nameread "tateya" ${tmp}-name)
floor=$(nameread "floor" ${tmp}-name)
unit=$(nameread "unit" ${tmp}-name)

if [ "$MODE" = "unit" ]; then
  # 施設
  awk '$1=="'$shisetsu'"{print $1,$2,"@"}' ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_KIHON   > $tmp-shisetsu
  # 建屋一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR    |
  awk '$1=="'$shisetsu'"{print $2}'                     |
  getlast 1 1                                           |
  join1 key=1 <(self 1 3 ${home_dir}/TBL/SHISETSU_MASTER/TATEYA_NAME)  |
  awk '{print $0,"'$tateya'"}'                          |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > ${tmp}-tateya
  # フロア一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR             |
  awk '$1=="'$shisetsu'"&&$2=="'${tateya}'"{print $3,$3"F","'$floor'"}'        |
  getlast 1 3                                 |
  awk 'BEGIN{print "@","全て","@"};{print $0}'  | 
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}'      > ${tmp}-floor
  # ユニット一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT        |
  awk '$1=="'$shisetsu'"&&$2=="'$tateya'"&&$3=="'${floor}'"{print $4}'                  |
  join1 key=1 ${home_dir}/TBL/SHISETSU_MASTER/UNIT_NAME                 |
  awk '{print $1,$2,"'$unit'"}'                      |
  awk 'BEGIN{print "@","全て","@"};{print $0}'  |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}'       >  ${tmp}-unit
  # 居室一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM   |
  awk '$1=="'$shisetsu'"&&$2=="'${tateya}'"&&$3=="'$floor'"&&$4=="'$unit'"{print $5,$5,"@"}'          |
  awk 'BEGIN{print "@","全て","@"};{print $0}'                         > $tmp-kyoshitsu
elif [ "$MODE" = "floor" ];then
  # 施設
  awk '$1=="'$shisetsu'"{print $1,$2,"@"}' ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_KIHON   > $tmp-shisetsu
  # 建屋一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR    |
  awk '$1=="'$shisetsu'"{print $2}'                     |
  getlast 1 1                                           |
  join1 key=1 <(self 1 3 ${home_dir}/TBL/SHISETSU_MASTER/TATEYA_NAME)  |
  awk '{print $0,"'$tateya'"}'                          |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > ${tmp}-tateya
  # フロア一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR             |
  awk '$1=="'$shisetsu'"&&$2=="'${tateya}'"{print $3,$3"F","'$floor'"}'        |
  getlast 1 3                                 |
  awk 'BEGIN{print "@","全て","@"};{print $0}'  | 
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}'      > ${tmp}-floor
  # ユニット一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT             |
#  if [ -z "$floor" -o "$floor" = "_" ] ; then
#     awk '$1=="'$shisetsu'"&&$2=="'$tateya'"'
#  else
#     awk '$1=="'$shisetsu'"&&$2=="'$tateya'"&&$3=="'$floor'"'
#  fi |
  awk '$1=="'$shisetsu'"&&$2=="'$tateya'"&&$3=="'$floor'"'    |
  self 4                                      |
  LANG=C sort -k1,1                           |
  join1 key=1 <(self 1 2 ${home_dir}/TBL/SHISETSU_MASTER/UNIT_NAME)         |
  awk '{print $0,"@"}'                                                  |
  awk 'BEGIN{print "@","全て","@"};{print $0}'                         >  ${tmp}-unit
  # 居室一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM   |
  if [ -z "$floor" -o "$floor" = "_" ] ; then
    awk '$1=="'$shisetsu'"&&$2=="'${tateya}'"{print $5,$5,"@"}'
  else
    awk '$1=="'$shisetsu'"&&$2=="'${tateya}'"&&$3=="'$floor'"{print $5,$5,"@"}'
  fi |
  awk 'BEGIN{print "@","全て","@"};{print $0}'                         > $tmp-kyoshitsu

elif [ "$MODE" = "tateya" ];then
  # 施設
  awk '$1=="'$shisetsu'"{print $1,$2,"@"}' ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_KIHON   > $tmp-shisetsu
  # 建屋一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR    |
  awk '$1=="'$shisetsu'"{print $2}'                     |
  getlast 1 1                                           |
  join1 key=1 <(self 1 3 ${home_dir}/TBL/SHISETSU_MASTER/TATEYA_NAME)  |
  awk '{print $0,"'$tateya'"}'                          |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,"@"}}' > ${tmp}-tateya
  # フロア一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR             |
  awk '$1=="'$shisetsu'"&&$2=="'${tateya}'"{print $3,$3"F","@"}'        |
  awk 'BEGIN{print "@","全て","@"};{print $0}'   > ${tmp}-floor     
  # unit一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT        |
  awk '$1=="'$shisetsu'"&&$2=="'${tateya}'"&&$3=="'$floor'"{print $4}'                  |
  join1 key=1 <(self 1 2 ${home_dir}/TBL/SHISETSU_MASTER/UNIT_NAME)     |
  awk '{print $0,"@"}'                                                  |
  awk 'BEGIN{print "@","全て","@"};{print $0}'                         >  ${tmp}-unit
  # 居室一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM   |
  awk '$1=="'$shisetsu'"&&$2=="'${tateya}'"{print $5,$5,"@"}'          |
  awk 'BEGIN{print "@","全て","@"};{print $0}'                         > $tmp-kyoshitsu
elif [ "$MODE" = "shisetsu" ];then
  # 施設
  awk '$1=="'$shisetsu'"{print $1,$2,"@"}' ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_KIHON   > $tmp-shisetsu
  # 建屋
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR    |
  awk '$1=="'$shisetsu'"{print $2}'                     |
  getlast 1 1                                           |
  join1 key=1 <(self 1 3 ${home_dir}/TBL/SHISETSU_MASTER/TATEYA_NAME)  |
  awk '{print $0,"@"}'                                   > ${tmp}-tateya
  # フロア一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR             |
  awk '$1=="'$shisetsu'"{print $3,$3"F","@"}'            |
  awk 'BEGIN{print "@","全て","@"};{print $0}'         > ${tmp}-floor     
  # unit一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT        |
  awk '$1=="'$shisetsu'"{print $4}'                  |
  join1 key=1 <(self 1 2 ${home_dir}/TBL/SHISETSU_MASTER/UNIT_NAME)     |
  awk '{print $0,"@"}'                                                  |
  awk 'BEGIN{print "@","全て","@"};{print $0}'                         >  ${tmp}-unit
  # 居室一覧
  cat ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM   |
  awk '$1=="'$shisetsu'"{print $5,$5,"@"}'                             |
  awk 'BEGIN{print "@","全て","@"};{print $0}'                         > $tmp-kyoshitsu
else
  :
fi

#######################################################################################

# formhameの準備
shisetsu=$(echo ${shisetsu})
tateya=$(echo ${tateya})
floor=$(echo ${floor})
unit=$(echo ${unit})


#######################################################################################
# namefileの再構成

cat <<- FIN > ${tmp}-name
floor ${floor}
FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/RIYOURYOU_MASTER_RIYOURYOU_CHINRYOU.html |
  mojihame -l###SHISETSU_NAME### - $tmp-shisetsu      |
  mojihame -l###TATEYA_NAME### - $tmp-tateya      |
  mojihame -l###FLOOR_NAME### - $tmp-floor        |
  mojihame -l###UNIT_NAME###  - $tmp-unit         |
  mojihame -l###KYOSHITSU_NAME###  - $tmp-kyoshitsu   > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
