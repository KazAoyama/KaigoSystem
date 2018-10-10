#!/bin/bash
#
# SERVICE_TOUROKU.GET_KINGAKU.CGI : サービス項目を選択してマスタの金額を返す
#                     
#
# Usage : SERVICE_TOUROKU.GET_KINGAKU.CGI
#         POST メソッドで SERVICE_CODE を渡す。
#
# Written by aoyagi  

exec 2> /home/hands/E-LIFE/KEIRI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

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
app_dir="${home_dir}/E-LIFE/KEIRI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA"
apptbl_dir="${app_dir}/TBL"
kyoutsu_dir="${home_dir}/E-LIFE/KYOUTSU/HTML"
master_tbl_dir="${home_dir}/E-LIFE/TBL/SEIKYU"

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
master=$(nameread "master" ${tmp}-name)
shisetsu=$(nameread "shisetsu" ${tmp}-name)
tateya=$(nameread "input_tateya" ${tmp}-name)

if [ "$MODE" = "master" ]; then
  # マスターを取得
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
  awk '{print $0,"'${master}'"}' |
  awk '{if($1==$4){print $1,$2,"selected",$3}else{print $1,$2,"_",$3}}' > ${tmp}-nyuryoku_master
  
  cat ${tmp}-nyuryoku_master |
  self 1 2 3                 > ${tmp}-nyuryoku_service_master
  nyuryoku_kingaku=$(cat ${tmp}-nyuryoku_master |
  awk '$3=="selected"'                                   |
  self 4)
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
master=$(echo ${master})

#######################################################################################
# namefileの再構成

cat <<- FIN > ${tmp}-name
master ${master}
FIN

cat <<- FIN | sed 's/ _$/ @/g' >> ${tmp}-calsed
###nyuryoku_kingaku### ${nyuryoku_kingaku}
FIN

  # HTMLを作成
  awk '/\<master_ajax_start\>/,/\<master_ajax_end\>/' ${html_dir}/SERVICE_TOUROKU2.html |
  mojihame -l###NYURYOKU_SERVICE_MASTER### - $tmp-nyuryoku_service_master        |
  calsed -f ${tmp}-calsed -                       |
  formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
