#!/bin/bash
#
# CARE_SHISETSU_CAREPLAN.GET_UNIT.CGI : FLOOR選択してUNITを返す
#                     
#
# Usage : CARE_SHISETSU_CAREPLAN.GET_UNIT.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by aoyagi  

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/CARE_KAIGOSAKUSEI/TRACE_LOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/CARE_KAIGOSAKUSEI/TRACE_LOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


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
app_dir="${home_dir}/E-LIFE/CARE_KAIGOSAKUSEI"
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
riyosha_name=$(nameread "riyosha_name" ${tmp}-name)

# SHISETSU_TATEYA_FLOOR_ROOMのマスタ準備
echo $shisetsu > $tmp-shisetsu
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM               |
# 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
join0 key=1 $tmp-shisetsu                                    |
#join0 key=2 <(echo "00")                                     |
awk '$9=="1"'                                                > $tmp-shisetsu_tateya_floor_id
# ユニットマスタの準備
cat ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME                     |
self 1 2                                                     > $tmp-unit_master

# 利用者マスタの準備
cat ${riyosha_dir}/RIYOUSHA_MASTER                           |
self 1 2                                                     > $tmp-riyosha_master

# SHISETSU_RIYOSHA_STATUSの準備
cat ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                  |
awk '$(NF-2)!="9"'                                           |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
join0 key=1 $tmp-shisetsu                                    |
#join0 key=2 <(echo "00")                                     |
awk '$8>="'${today}'"'                   > $tmp-riyosha_status

if [ "$MODE" = "floor" ]; then
  # floor一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       > ${tmp}-floor

  # unit一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  join0 key=3 <(echo "${floor}")                               |
  self 4                                                       |
  LANG=C sort -u -k1,1                                        |
  join1 key=1 $tmp-unit_master                                |
  LANG=C sort -k1,1n                                           > $tmp-unit

  # member
  unit=$(cat $tmp-shisetsu_tateya_floor_id                     |
         awk '$3=="'${floor}'"'                                |
         self 4 | head -n1)
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$3=="'${floor}'" && $4=="'${unit}'"{print $6}'          |
  LANG=C sort -k1,1                                           |
  join1 key=1 $tmp-riyosha_master                              |
  LANG=C sort -k1,1n                                           > $tmp-riyosha

elif [ "$MODE" = "unit" ];then
  # floor一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3 4                                                     |
  LANG=C sort -u -k1,2n                                        |
  awk '{print $0,"'${unit}'"}'                                 |
  awk '{if($2==$3){print $1,$1"F","selected"}else{print $1,$1"F",""}}'         > $tmp-floor

  # unit一覧
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  join0 key=3 <(echo "${floor}")                               |
  self 4                                                       |
  LANG=C sort -u -k1,1                                        |
  join1 key=1 $tmp-unit_master                                 |
  LANG=C sort -k1,1n                                        |
  awk '{print $0,"'${unit}'"}'                                 |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit


  # member
  cat $tmp-riyosha_status                                      |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$4=="'${unit}'"{print $6}'                              |
  LANG=C sort -k1,1                                           |
  join1 key=1 $tmp-riyosha_master                              |
  LANG=C sort -k1,1n                                           > $tmp-riyosha

else
  echo "${riyosha_name}" > $tmp-riyosha
fi

select_riyosha_id = $(self 1 $tmp-riyosha | head -1)

awk '$(NF-2)!="9"{print $2}' ${pompa_dir}/SHISETSU_CAREPLAN/${select_riyosha_id}/CARE_SHISETSU_CAREPLAN |
LANG=C sort -k1r,1r |
awk '{if($1=="'${Rireki}'"){print $1,$1,"selected"}else{print $1,$1,"　"};}' > $tmp-rireki


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


#######################################################################################
# namefileの再構成

cat <<- FIN > ${tmp}-name
floor ${floor}
FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/CARE_SHISETSU_CAREPLAN2.html |
  mojihame -l###FLOOR_NAME### - $tmp-floor        |
  mojihame -l###UNIT_NAME###  - $tmp-unit       |
  mojihame -l###RIYOSHA_NAME###  - $tmp-riyosha       |
  mojihame -l###RIREKI_SELECT###  - $tmp-rireki       |
  formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
