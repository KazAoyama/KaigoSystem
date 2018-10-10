#!/bin/bash
#
# CARE_KAIGOKEIKA.GET_RIYOSHA.CGI : FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : CARE_KAIGOKEIKA.GET_RIYOSHA.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by Aoyama

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/CARE_KAIGOSAKUSEI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/CARE_KAIGOSAKUSEI/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

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
app_dir="${home_dir}/E-LIFE/CARE_KAIGOSAKUSEI"
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


###########################################################
# フロア、ユニット、居室、対象者の選択AJAX処理部分を共通化
###########################################################
. ${home_dir}/E-LIFE/COMMON/COMMON_002.func

# 週間計画書取得
:> $tmp-kaigokeika_rireki
rank $tmp-riyosha |
LANG=C sort -k4,4r -k1,1 |
head -1 |
self 2 > $tmp-kaigokeika_taishousha

if [ $(gyo $tmp-kaigokeika_taishousha) -gt 0 ] ; then
   taishousha=$(cat $tmp-kaigokeika_taishousha)
   awk '$(NF-2)!="9"' ${pompa_dir}/SHISETSU_CAREPLAN/${taishousha}/CARE_KAIGOKEIKA   |
   self 2 2 |
   LANG=C sort -k1,1r -u |
   awk '{print $1,substr($1,1,4)"/"substr($1,5,2)"/"substr($1,7,2),""}' > $tmp-kaigokeika_rireki
fi

[ $(gyo $tmp-kaigokeika_rireki) -eq 0 ] && echo "_" "_" "" > $tmp-kaigokeika_rireki


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
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/CARE_KAIGOKEIKA2.html |
  mojihame -l###FLOOR_NAME### - $tmp-floor        |
  mojihame -l###UNIT_NAME###  - $tmp-unit       |
  mojihame -l###ROOM_NAME###  - $tmp-room       |
  mojihame -l###RIREKI_SELECT### - $tmp-kaigokeika_rireki |
  mojihame -l###RIYOSHA_NAME###  - $tmp-riyosha > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
