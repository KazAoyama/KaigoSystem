#!/bin/bash
#
# KENGEN_KANRI.CGI : 権限管理テストCGI
#
# Usage : KENGEN_KANRI.CGI
#
# Written by aoyagi(handslab.Inc)

exec 2> /home/hands/E-LIFE/TEST/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/TEST"
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
    ${cgi_dir}/KENGEN_KANRI.DISPLAY ${tmp}-param_name > ${tmp}-html
    ;;

  #登録する場合
  touroku )
    ${cgi_dir}/KENGEN_KANRI.TOUROKU ${tmp}-param_name               > ${tmp}-touroku
    ${cgi_dir}/KENGEN_KANRI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KENGEN_KANRI.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
    ;;
  #検索する場合
  search )
    ${cgi_dir}/KENGEN_KANRI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KENGEN_KANRI.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
    ;;
  #メンバー追加する場合
  member_tsuika )
    ${cgi_dir}/KENGEN_KANRI.MEM_TSUIKA ${tmp}-param_name               > ${tmp}-new_member
    ${cgi_dir}/KENGEN_KANRI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KENGEN_KANRI.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
    ;;
  #メンバー削除する場合
  member_delete )
    ${cgi_dir}/KENGEN_KANRI.MEM_DELETE ${tmp}-param_name               > ${tmp}-del_member
    ${cgi_dir}/KENGEN_KANRI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KENGEN_KANRI.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
    ;;
  #権限丸ごと削除する場合
  all_delete )
    ${cgi_dir}/KENGEN_KANRI.ALL_DELETE ${tmp}-param_name               > ${tmp}-all_del
    ${cgi_dir}/KENGEN_KANRI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KENGEN_KANRI.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
    ;;
  #その他の場合
  * )
    ${cgi_dir}/KENGEN_KANRI.DISPLAY ${tmp}-param_name > ${tmp}-html
    ;;
esac

# HTMLファイルを表示する
echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
cat - ${tmp}-html

rm -f ${tmp}-*
exit 0

