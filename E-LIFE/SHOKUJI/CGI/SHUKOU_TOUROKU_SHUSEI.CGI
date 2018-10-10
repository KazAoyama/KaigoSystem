#!/bin/bash
#
# SHUKOU_TOUOKU_SHUSEI.CGI : 嗜好登録修正CGI
#
# Usage : SHUKOU_TOUROKU_SHUSEI.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)


# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/SHOKUJI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/SHOKUJI/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/SHOKUJI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"

#}}}Functions#######################################

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-param_name)"
[ -n "${MODE}" ] || MODE="init"

# 処理の分岐
case "${MODE}" in
  #初期表示
  shusei )
    ${cgi_dir}/SHUKOU_TOUROKU_SHUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
    ${cgi_dir}/SHUKOU_TOUROKU_SHUSEI.DISPLAY ${tmp}-param_name ${tmp}-search  > ${tmp}-html
    ;;

  shinki )
    ${cgi_dir}/SHUKOU_TOUROKU_SHUSEI.DISPLAY ${tmp}-param_name > ${tmp}-html
    ;;

  #その他の場合
  * )
    ${cgi_dir}/SHUKOU_TOUROKU_SHUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
    ${cgi_dir}/SHUKOU_TOUROKU_SHUSEI.DISPLAY ${tmp}-param_name ${tmp}-search  > ${tmp}-html
    ;;
esac


# HTMLファイルを表示する
echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
cat - ${tmp}-html

rm -f ${tmp}-*
exit 0

