#!/bin/bash
#
# SHISETSU_KAIGOKIROKU_ICHIRAN.GET_UNIT.CGI : FLOOR選択してUNITを返す
#                     
#
# Usage : SHISETSU_KAIGOKIROKU_ICHIRAN.GET_UNIT.CGI
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
floor=$(nameread "floor" ${tmp}-name)
shisetsu=$(nameread "shisetsu" ${tmp}-name)

# SHISETSU_TATEYA_FLOOR_ROOMのマスタ準備
echo $shisetsu > $tmp-shisetsu
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM               |
# 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
join0 key=1 $tmp-shisetsu                                    |
join0 key=2 <(echo "02")                                     |
awk '$9=="1"'                                                > $tmp-shisetsu_tateya_floor_id
# ユニットマスタの準備
cat ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME                     |
self 1 2                                                     > $tmp-unit_master

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
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-unit_master                                 > $tmp-unit
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


#######################################################################################
# namefileの再構成

cat <<- FIN > ${tmp}-name
floor ${floor}
FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/KAIGOJISSEKI_MONTHLY_HAIBENHYO2.html |
  mojihame -l###FLOOR_NAME### - $tmp-floor        |
  mojihame -l###UNIT_NAME###  - $tmp-unit       |
  formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
