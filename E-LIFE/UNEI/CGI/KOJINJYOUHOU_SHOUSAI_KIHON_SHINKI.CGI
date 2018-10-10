#!/bin/bash
#
# KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.CGI : 個人情報詳細(基本)CGI
# 
# 
#
# Written by E.Okuda :2013/12/3

exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
cgi_dir="${home_dir}/UNEI/CGI"

#-------------------------------------------------------------

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)


#-------------------------------------------------------------
# 処理モードの決定
MODE="$(nameread "MODE" ${tmp}-param_name)"

#[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#-------------------------------------------------------------

#--i-----------------------------------------------------------
# 処理の分岐
case "$MODE" in

  # -------------------------
  # 初期表示
#  init)
#    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.DISPLAY ${tmp}-param_name > $tmp-html
#  ;;
  # -------------------------

  #--------------------------
  #検索(初期表示で検索結果が出る)
  init)
#    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.DISPLAY ${tmp}-param_name  > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #CHECK(初期表示で検索結果が出る)
  check)
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.CHECK ${tmp}-param_name               > ${tmp}-check
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.DISPLAY ${tmp}-param_name ${tmp}-check  > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #登録(更新登録)
  touroku)
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.CHECK ${tmp}-param_name                  > ${tmp}-check
   if [ "$(awk '$1=="result"{print $2}' ${tmp}-check)" != "check_ng" ] ; then
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.TOUROKU ${tmp}-param_name ${tmp}-check   > ${tmp}-touroku
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
   else
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KIHON_SHINKI.DISPLAY ${tmp}-param_name ${tmp}-check  > ${tmp}-html
   fi
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

