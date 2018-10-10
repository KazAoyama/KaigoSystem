#!/bin/bash
#
# KENGEN_KANRI.GET_MEMBER.CGI : 施設選択して所属メンバーを返す
#                     
#
# Usage : KENGEN_KANRI.GET_MEMBER.CGI
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
pompa_dir="${app_dir}/POMPA"
hometbl_dir="${home_dir}/E-LIFE/TBL"
apptbl_dir="${app_dir}/TBL"
kyoutsu_dir="${home_dir}/E-LIFE/KYOUTSU/HTML"
work="${app_dir}/WORK"
today=$(date +%Y%m%d)

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
userid=$(nameread "userid" ${tmp}-name)
# 施設マスタの準備
awk '$(NF-2)!=9' ${hometbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
self 1 2                                          > $tmp-shisetsu_kihon
awk '$(NF-2)!=9' ${hometbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
self 1 2                                          > $tmp-jigyousho_kihon
cat $tmp-shisetsu_kihon $tmp-jigyousho_kihon      |
LANG=C sort -k1,1                                 > $tmp-shisetsu_master
cp $tmp-shisetsu_master ${work}/shisetsuuu

cat /home/hands/E-LIFE//SYSTEM_SETTEI/POMPA/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN |
# 1:userid          2:SHISETSU_ID 3:KENGEN_GROUP 4:appID      5:MENU_NAME
# 6:DROPDOWN_STATUS 7:CGI_NAME    8:RINK_STATUS  9:CGI_STATUS 10:登録日時
LANG=C sort -u -k2,2                                       |
self 2                                                     > ${tmp}-kengen
# 1:userid 2:SHISETSU_ID
cp ${tmp}-kengen ${work}/kengengen


if [ "$MODE" = "shisetsu" ]; then
  # 施設一覧
  if [ "$(awk '$1=="0000"' $tmp-kengen | gyo)" -ne 0 ];then
    cat $tmp-shisetsu_master        > ${tmp}-shisetsu_name
  else
   awk '$1!="0000"' $tmp-kengen    > $tmp-master
   cat $tmp-shisetsu_master          |
   join0 key=1 $tmp-master         > $tmp-shisetsu_name
  fi

  # MEMBER一覧
  if [ "${SHISETSU_CODE}" = "999" ];then
    cat ${hometbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU ${hometbl_dir}/JYUUGYOUIN_MASTER/EXTRA_USER_SHISETSU |
    awk '$(NF-2)!=9'                                    |
    LANG=C sort -k2,2                                   |
    join0 key=2 $tmp-kengen                             |
    LANG=C sort -u -k1,1                                |
    self 1                                     |
    join1 key=1 <(awk '$(NF-2)!=9' ${hometbl_dir}/JYUUGYOUIN_MASTER/USER_KIHON) |
    self 1 2 3                                  |
    LANG=C sort -k3,3                           > ${tmp}-member_name
  else
    cat ${hometbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU ${hometbl_dir}/JYUUGYOUIN_MASTER/EXTRA_USER_SHISETSU |
tee ${work}/user_totyu |
    awk '$2=="'${SHISETSU_CODE}'"&&$(NF-2)!=9{print $1}'            |
    LANG=C sort -u -k1,1                                |
#    join1 key=1 <(awk '$(NF-2)!=9&&$4<="'${today}'"&&$5>="'${today}'"' ${hometbl_dir}/JYUUGYOUIN_MASTER/USER_KIHON)  |
    join1 key=1 <(awk '$(NF-2)!=9&&$5>="'${today}'"' ${hometbl_dir}/JYUUGYOUIN_MASTER/USER_KIHON)  |
    self 1 2 3                                          |
    LANG=C sort -k3,3                                   > ${tmp}-member_name
  fi
else
  :
fi
cp ${tmp}-member_name ${work}/member_name
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
input_shisetsu_select=$(echo ${SHISETSU_CODE})


#######################################################################################
# namefileの再構成

cat <<- FIN > ${tmp}-name
SHISETSU_CODE ${SHISETSU_CODE}
input_shisetsu_select ${input_shisetsu_select}
FIN

  # HTMLを作成
  awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/KENGEN_MASTER2.html |
  mojihame -l###INPUT_SHISETSU_NAME### - $tmp-shisetsu_name        |
  mojihame -l###INPUT_NAME###  - $tmp-member_name       |
  formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
