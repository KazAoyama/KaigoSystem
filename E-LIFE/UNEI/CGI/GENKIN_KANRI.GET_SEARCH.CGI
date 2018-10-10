#!/bin/bash
#
# GENKIN_KANRI.GET_SEARCH.CGI : 
#                     
#
# Usage : GENKIN_KANRI.GET_SEARCH.CGI
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
nengappi=$(nameread "nengappi" ${tmp}-name)
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
month=$(echo $nengappi | awk '{print substr($1,1,4)substr($1,6,2)}')
awk '$(NF-2)!=9&&$1=="'${ShuseiId}'"' ${pompa_dir}/GENKIN_KANRI/${shisetsu}/$month/GENKIN_KANRI_$month |
tail -n1 > $tmp-pompa
# 1:現金管理id          2:フロア            3:居室          4:入居者id    5:立替項目id
# 6:立替項目id          7:日付              8:収入数        9:収入金      10:支出数
# 11:支出金額           12:対応者id         13:印刷対象区分 14:印刷済区分 15:申込書番号
# 16:立替金移行対象区分 17:立替金移行済区分 18:請求対象区分 19:備考       20:有効フラグ
# 21:更新時間           22:userid

# 立替
self 16 $tmp-pompa |
awk '{if($1==1){print "checked"}else{print "@"}}' > $tmp-tatekae

# フロア
floor=$(self 2 $tmp-pompa)
self 3 $tmp-riyosha_status |
LANG=C sort -u |
awk '{print $1,$1"F","'${floor}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-floor

# 居室
room=$(self 3 $tmp-pompa)
awk '$3=="'${floor}'"' $tmp-riyosha_status |
self 5 |
LANG=C sort -u |
awk '{print $1,$1,"'${room}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-room

# 入居者
riyosha_id=$(self 4 $tmp-pompa)
LANG=C sort -k3,3 $tmp-riyosha_master |
awk '{print $1,$2,"'${riyosha_id}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-riyosha_name

# 収入数
self 8 $tmp-pompa > $tmp-shunyu_su

# 収入金額
self 9 $tmp-pompa > $tmp-shunyu_kingaku

# 科目
kamoku=$(self 5 $tmp-pompa)
awk '$(NF-2)!=9' ${tbl_dir}/TATEKAEKIN_KOMOKU/$shisetsu/TATEKAEKIN_KOMOKU |
awk '{print $1,$2,"'${kamoku}'"}' |
awk '{if($1==$3){$3="selected"}else{$3="@"};print}' > $tmp-kamoku

# 請求
self 18 $tmp-pompa |
awk '{if($1==1){print "checked"}else{print "@"}}' > $tmp-seikyu

# 支出数
self 10 $tmp-pompa > $tmp-shishutsu_su

# 支出金額
self 11 $tmp-pompa > $tmp-shishutsu_kingaku

# 備考
self 19 $tmp-pompa |
awk '{if($1=="_"){$1="@"};print}' > $tmp-biko

# ID
self 1 $tmp-pompa > $tmp-Shusei_id

# button
echo "@ none" > $tmp-button


#######################################################################################
  # HTMLを作成
  awk '/\<ajax_start_form\>/,/\<ajax_end_form\>/' ${html_dir}/GENKIN_KANRI2.html |
  mojihame -l###INPUT_FLOOR_NAME### - $tmp-floor |
  mojihame -l###INPUT_ROOM_NAME### - $tmp-room |
  mojihame -l###INPUT_RIYOSHA_NAME### - $tmp-riyosha_name |
  mojihame -l###input_tatekae_check### - $tmp-tatekae |
  mojihame -l###INPUT_SHUNYU_SU### - $tmp-shunyu_su |
  mojihame -l###INPUT_SHUNYU_KINGAKU### - $tmp-shunyu_kingaku |
  mojihame -l###INPUT_KAMOKU### - $tmp-kamoku |
  mojihame -l###INPUT_SEIKYU_CHECK### - $tmp-seikyu |
  mojihame -l###INPUT_SHISHUTSU_SU### - $tmp-shishutsu_su |
  mojihame -l###INPUT_SHISHUTSU_KINGAKU### - $tmp-shishutsu_kingaku |
  mojihame -l###INPUT_BIKO### - $tmp-biko |
  mojihame -l###SHUSEI_ID### - $tmp-Shusei_id |
  mojihame -l###INPUT_BUTTON### - $tmp-button > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
