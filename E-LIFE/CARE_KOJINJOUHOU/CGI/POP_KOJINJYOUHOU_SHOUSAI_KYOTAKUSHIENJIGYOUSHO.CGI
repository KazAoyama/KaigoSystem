#!/bin/bash
#
# POP_KOJINJYOUHOU_SHOUSAI_KYOTAKUSHIENJIGYOUSHO.CGI : 個人情報詳細(契約)CGI
# 
# 
#
# Written by E.Okuda :2013/12/9

exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null

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
  init)
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KYOTAKUSHIENJIGYOUSHO.DISPLAY ${tmp}-param_name > $tmp-html
  ;;
  # -------------------------
  #--------------------------
  # 検索
  search)
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KYOTAKUSHIENJIGYOUSHO.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KYOTAKUSHIENJIGYOUSHO.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  # 登録
  touroku | sakujyo)
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KYOTAKUSHIENJIGYOUSHO.TOUROKU ${tmp}-param_name               > ${tmp}-touroku
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KYOTAKUSHIENJIGYOUSHO.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
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

