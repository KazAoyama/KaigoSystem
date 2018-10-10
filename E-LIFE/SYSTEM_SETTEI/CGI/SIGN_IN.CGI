#!/bin/bash
#
# SIGN_IN.CGI : ログイン画面CGI
#
# Usage : SIGN_IN.CGI
#
# Written by K.Aoyama(handslab.Inc)

exec 2> /home/hands/E-LIFE/SYSTEM_SETTEI/TRACE_LOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"


#}}}Functions#######################################

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-param_name)"
[ -n "${MODE}" ] || MODE="init"

#cp -p ${tmp}-param_name param_name_kengen_kanri_test

# 処理の分岐
case "${MODE}" in
  #初期表示
  init )
    ${cgi_dir}/SIGN_IN.DISPLAY ${tmp}-param_name > ${tmp}-html
    ;;
  #その他の場合
  * )
    ${cgi_dir}/SIGN_IN.DISPLAY ${tmp}-param_name > ${tmp}-html
    ;;
esac

# HTMLファイルを表示する
echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
cat - ${tmp}-html

rm -f ${tmp}-*
exit 0

