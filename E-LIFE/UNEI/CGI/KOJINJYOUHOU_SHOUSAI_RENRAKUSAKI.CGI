#!/bin/bash
#
# KOJINJYOUHOU_SHOUSAI_RENRAKUSAKI.CGI : 個人情報詳細(契約)CGI
# 
# 
#
# Written by E.Okuda :2013/12/9

exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
app_dir="${home_dir}/UNEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"

#-------------------------------------------------------------

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)

#-------------------------------------------------------------
# 処理モードの決定
MODE="$(nameread "MODE" ${tmp}-param_name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#-------------------------------------------------------------

#--i-----------------------------------------------------------
# 処理の分岐
case "$MODE" in

  # -------------------------
  # 初期表示
#  init)
#    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_RENRAKUSAKI.DISPLAY ${tmp}-param_name > $tmp-html
#  ;;
  # -------------------------

  #--------------------------
  #検索(初期表示で検索結果が出る)
  init)
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_RENRAKUSAKI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_RENRAKUSAKI.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #連絡先情報Excel出力
  KazokuPrint)
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_RENRAKUSAKI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KAZOKU.EXCEL ${tmp}-param_name ${tmp}-search > ${tmp}-html
  ;;

esac
#-------------------------------------------------------------


# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
