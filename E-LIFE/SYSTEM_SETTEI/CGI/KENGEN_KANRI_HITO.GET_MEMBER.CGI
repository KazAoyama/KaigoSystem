#!/bin/bash
#
# KENGEN_KANRI.GET_SHISETSU.CGI :
#                     
#
# Usage : KENGEN_KANRI.GET_SHISETSU.CGI
#         POST メソッドで SHISETSU_CODE を渡す。
#
# Written by aoyagi  

exec 2> /home/hands/E-LIFE/SYSTEM_SETTEI/TRACE_LOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

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
app_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA/KENGEN_KANRI"
hometbl_dir="${home_dir}/E-LIFE/TBL"
apptbl_dir="${app_dir}/TBL"
kyoutsu_dir="${home_dir}/E-LIFE/KYOUTSU/HTML"

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

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
SHISETSU_CODE=$(nameread "SHISETSU_CODE" ${tmp}-name)
MEMBER_CODE=$(nameread "MEMBER_CODE" ${tmp}-name)
userid=$(nameread "userid" ${tmp}-name)
# 施設マスタの準備
self 1 2 /home/hands/E-LIFE/TBL/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER > $tmp-jigyousho_group_mst
self 1 2 /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_KIHON > $tmp-shisetsu_mst

cat $tmp-shisetsu_mst $tmp-jigyousho_group_mst > $tmp-disp_shisetsu_mst


cat /home/hands/E-LIFE//SYSTEM_SETTEI/POMPA/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN |
# 1:userid          2:SHISETSU_ID 3:KENGEN_GROUP 4:appID      5:MENU_NAME
# 6:DROPDOWN_STATUS 7:CGI_NAME    8:RINK_STATUS  9:CGI_STATUS 10:登録日時
LANG=C sort -u -k2,2n                                      |
self 1 2                                                   > ${tmp}-kengen
# 1:userid 2:SHISETSU_ID

if [ "$(cat ${tmp}-kengen | getfirst 1 1 | self 2)" = "0000" ];then
  echo "0000" "全施設"                                > $tmp-all_shisetsu
  awk '$1!="0000"{print $1,$2}' $tmp-disp_shisetsu_mst |
  cat -
# 1:SHISESTU_ID 2:施設名
else
  cat ${tmp}-kengen                                   |
  # 1:userid 2:SHISETSU_ID
  join1 key=2 $tmp-disp_shisetsu_mst                  |
# 1:userid 2:SHISETSU_ID 3:施設名
  awk '$2!=0{print $2,$3}'
fi                                                    > $tmp-shisetsu_master

if [ "$MODE" = "shisetsu" ]; then
  awk '$(NF-2)!=9{print $1,$2,$3}' ${hometbl_dir}/JYUUGYOUIN_MASTER/USER_KIHON   > $tmp-namae

  cat /home/hands/E-LIFE/TBL/JYUUGYOUIN_MASTER/USER_SHISETSU /home/hands/E-LIFE/TBL/JYUUGYOUIN_MASTER/EXTRA_USER_SHISETSU |
  awk '$9!=9'                                           |
  self 1 2                                              |
  awk '$2=="'${SHISETSU_CODE}'"{print $1}'              |
  LANG=C sort -u                                        |
  join1 key=1 $tmp-namae                                |
  LANG=C sort -k3,3                                     |
  delf 3                                                > $tmp-member_data
  

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
shisetsu_name=$(echo ${SHISETSU_CODE})


#######################################################################################
# namefileの再構成

cat <<- FIN > ${tmp}-name
shisetsu_name ${shisetsu_name}
member_name ${MEMBER_CODE}
FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/KENGEN_MASTER_HITO2.html |
  mojihame -l###SHISETSU_NAME### - $tmp-shisetsu_master  |
  mojihame -l###MEMBER_NAME###  - $tmp-member_data       |
  formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
