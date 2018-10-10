#!/bin/bash
#
# NYUUINGAIHAKU_SHOUSAI.CGI : 個人情報詳細(基本)CGI
# 
# 
#
# Written by E.Okuda :2013/12/3

exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source  /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
# 変数設定
tmp=/var/tmp/${$}

# ディレクトリ設定
app_dir="${home_dir}/UNEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
shokuji_cgi_dir="${home_dir}/SHOKUJI/CGI"

#ゴミtmpの消去
rm -f $tmp-*

#-------------------------------------------------------------

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)

#-------------------------------------------------------------

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
#    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.DISPLAY ${tmp}-param_name > $tmp-html
#  ;;
  # -------------------------

  #--------------------------
  #初期表示
  init)
#    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #検索
  search)
    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
  ;;
  #--------------------------


  #--------------------------
  #登録(更新登録)
  touroku)
    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.TOUROKU ${tmp}-param_name                       > ${tmp}-touroku
#    if [ "$(awk '$1=="result"{print $2}' ${tmp}-touroku)" = "ok" -a ${KesshyokuTouroku} == "1" ]; then
    if [ "$(awk '$1=="result"{print $2}' ${tmp}-touroku)" = "ok" ]; then
      ${shokuji_cgi_dir}/KESSHOKU_JISSEKI_HANEI.CGI ${tmp}-param_name ${tmp}-touroku > $tmp-kesshoku
    else
      :
    fi
    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-touroku        > ${tmp}-html
  ;;

  #--------------------------
  #削除
  sakujyo)
    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.SAKUJYO ${tmp}-param_name                       > ${tmp}-touroku
#    if [ "$(awk '$1=="result"{print $2}' ${tmp}-touroku)" = "ok" -a ${KesshyokuTouroku} == "1" ]; then
    if [ "$(awk '$1=="result"{print $2}' ${tmp}-touroku)" = "ok" ]; then
      ${shokuji_cgi_dir}/KESSHOKU_JISSEKI_HANEI.CGI ${tmp}-param_name ${tmp}-touroku > $tmp-kesshoku
    else
      :
    fi
    ${cgi_dir}/NYUUINGAIHAKU_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-touroku        > ${tmp}-html
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

