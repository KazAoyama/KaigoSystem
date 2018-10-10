#!/bin/bash
#
# SHUKOU_TOUROKU.GET_RIYOSHA.CGI : SHISETSU,TATEYA,FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : SHUKOU_TOUROKU.GET_RIYOSHA.CGI
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
ShuseiId=$(nameread "ShuseiId" ${tmp}-name)
nengetsu=$(nameread "nengetsu" ${tmp}-name)
# 選択しているSHISETSU_CODE
userid=$(nameread "userid" ${tmp}-name)
shisetsu=$(nameread "shisetsu" ${tmp}-name)


# 利用者マスタの準備
awk '$(NF-2)!=9' ${riyosha_dir}/RIYOUSHA_MASTER               |
self 1 2 3                                                    > $tmp-riyosha_master
# 1:利用者ID 2:利用者名 3:利用者カナ

# SHISETSU_RIYOSHA_STATUSの準備
awk '$(NF-2)!=9' ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                  |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
awk '$1=="'${shisetsu}'"'                                    |
awk '$7<="'${today}'" && $8>="'${today}'"'                   > $tmp-riyosha_status

# Search
month=$(echo $nengetsu | awk '{print substr($1,1,4)substr($1,6,2)}')
awk '$(NF-2)!=9&&$1=="'${ShuseiId}'"' ${pompa_dir}/AZUKARIHIN/${shisetsu}/$month/AZUKARIHIN_MONTH > $tmp-monthly
awk '$(NF-2)!=9&&$1=="'${ShuseiId}'"' ${pompa_dir}/AZUKARIHIN/${shisetsu}/AZUKARIHIN_MI_SHORI |
cat $tmp-monthly - |
tail -n1 > $tmp-pompa
# 1:入退出管理id      2:外出日 3:フロア      4:居室      5:入居者id
# 6:外出区分番号      7:鍵     8:外出時間    9:戻り日    10:戻り時間
# 11:フロント担当者id 12:備考  13:有効フラグ 14:更新時間 15:userid

# 預り日
self 2 $tmp-pompa > $tmp-azukari_date

# フロア
floor=$(self 4 $tmp-pompa)
self 3 $tmp-riyosha_status |
LANG=C sort -u |
awk '{print $1,$1"F","'${floor}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-floor

# 居室
room=$(self 5 $tmp-pompa)
awk '$3=="'${floor}'"' $tmp-riyosha_status |
self 5 |
LANG=C sort -u |
awk '{print $1,$1,"'${room}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-room

# 入居者
riyosha_id=$(self 6 $tmp-pompa)
LANG=C sort -k3,3 $tmp-riyosha_master |
awk '{print $1,$2,"'${riyosha_id}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-riyosha_name

# 預り項目番号
self 7 $tmp-pompa > $tmp-azukari_number

# 預り項目
azukari_kubun=$(self 7 $tmp-pompa)
awk '$(NF-2)!=9' ${tbl_dir}/AZUKARIHIN/$shisetsu/AZUKARI_KUBUN |
awk '{print $1,$2,"'${azukari_kubun}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-azukari_kubun

# 数量
self 8 $tmp-pompa > $tmp-number

# 預り時間
self 3 $tmp-pompa > $tmp-azukari_time

# 戻り日
self 10 $tmp-pompa |
awk '{if($1=="_"){$1="@"};print}' > $tmp-return_day

# 戻り時間
self 11 $tmp-pompa |
awk '{if($1=="_"){$1="@"};print}' > $tmp-return_time

# 受付担当
uketsuke_staff=$(self 9 $tmp-pompa)
awk '$(NF-2)!=9' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_MASTER |
LANG=C sort -k3,3 |
awk '{print $1,$2,"'${uketsuke_staff}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-uketsukestaff
# お渡し担当
front_staff=$(self 12 $tmp-pompa)
awk '$(NF-2)!=9' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_MASTER |
LANG=C sort -k3,3 |
awk '{print $1,$2,"'${front_staff}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-frontstaff

# 備考
self 13 $tmp-pompa |
awk '{if($1=="_"){$1="@"};print}' > $tmp-biko

# ID
self 1 $tmp-pompa > $tmp-Shusei_id

# button
echo "@ none" > $tmp-button


#######################################################################################
  # HTMLを作成
  awk '/\<ajax_start_form\>/,/\<ajax_end_form\>/' ${html_dir}/AZUKARIHIN2.html |
  mojihame -l###INPUT_FLOOR_NAME### - $tmp-floor |
  mojihame -l###INPUT_ROOM_NAME### - $tmp-room |
  mojihame -l###INPUT_RIYOSHA_NAME### - $tmp-riyosha_name |
  mojihame -l###INPUT_AZUKARI_NUMBER### - $tmp-azukari_number |
  mojihame -l###INPUT_AZUKARI_KUBUN### - $tmp-azukari_kubun |
  mojihame -l###INPUT_NUMBER### - $tmp-number |
  mojihame -l###INPUT_AZUKARI_TIME### - $tmp-azukari_time |
  mojihame -l###INPUT_RETURN_DAY### - $tmp-return_day |
  mojihame -l###INPUT_RETURN_TIME### - $tmp-return_time |
  mojihame -l###INPUT_UKETSUKE### - $tmp-uketsukestaff |
  mojihame -l###INPUT_RESTAURANT### - $tmp-frontstaff |
  mojihame -l###INPUT_BIKO### - $tmp-biko |
  mojihame -l###SHUSEI_ID### - $tmp-Shusei_id |
  mojihame -l###INPUT_BUTTON### - $tmp-button |
  mojihame -l###input_azukari_date###  - $tmp-azukari_date    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
