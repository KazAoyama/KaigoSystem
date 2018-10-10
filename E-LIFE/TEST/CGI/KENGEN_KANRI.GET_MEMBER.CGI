#!/bin/bash
#
# KENGEN_KANRI.GET_MEMBER.CGI : 施設選択して所属メンバーを返す
#                     
#
# Usage : KENGEN_KANRI.GET_MEMBER.CGI
#         POST メソッドで SHISETSU_CODE を渡す。
#
# Written by aoyagi  

exec 2> /home/hands/E-LIFE/TEST/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#=== 初期化 ===
tmp=/var/tmp/${$}

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/TEST"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA"
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

cp $tmp-name tmp-ajax_name
# MODE取得
MODE=$(nameread "MODE" ${tmp}-name)
# 選択しているSHISETSU_CODE
SHISETSU_CODE=$(nameread "SHISETSU_CODE" ${tmp}-name)

if [ "$MODE" = "shisetsu" ]; then
  # 施設一覧
  echo "999" "全施設"                                 |
  cat ${apptbl_dir}/SHISETSU_NAME -                   |
  awk '$1!="0"{print $0}'                             > $tmp-shisetsu_name

  # MEMBER一覧
  if [ "${SHISETSU_CODE}" = "999" ];then
    cat ${apptbl_dir}/SHOZOKU_SHISETSU_MEMBER  |
    awk '{print $2}'                           |
    LANG=C sort -k1,1n                         |
    join1 key=1 ${apptbl_dir}/STAFF_NAME       > ${tmp}-member_name
  else
    cat ${apptbl_dir}/SHOZOKU_SHISETSU_MEMBER  |
    awk '$1=="'${SHISETSU_CODE}'"{print $2}'   |
    join1 key=1 ${apptbl_dir}/STAFF_NAME       > ${tmp}-member_name
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
