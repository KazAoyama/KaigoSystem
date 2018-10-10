#!/bin/bash
#
# KIZUKI_TOUROKU.CGI : 個人情報詳細(基本)CGI
# 
# 
#
# Written by E.Okuda :2013/12/3

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
cgi_dir="${home_dir}/UNEI/CGI"
ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"
#-------------------------------------------------------------

# パラメーターの取得
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
#    ${cgi_dir}/KIZUKI_TOUROKU.DISPLAY ${tmp}-param_name > $tmp-html
#  ;;
  # -------------------------

  #--------------------------
  #init(初期表示)
  init)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
    ${cgi_dir}/KIZUKI_TOUROKU.DISPLAY ${tmp}-param_name ${tmp}-check > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  #検索
  search)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
    ${cgi_dir}/KIZUKI_TOUROKU.SEARCH ${tmp}-param_name        > $tmp-search
    ${cgi_dir}/KIZUKI_TOUROKU.DISPLAY ${tmp}-param_name ${tmp}-check $tmp-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  #登録(更新登録)
  touroku)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
    ${cgi_dir}/KIZUKI_TOUROKU.TOUROKU ${tmp}-param_name ${tmp}-param   > ${tmp}-touroku
    ${cgi_dir}/KIZUKI_TOUROKU.SEARCH ${tmp}-param_name ${tmp}-touroku  > $tmp-search
    ${cgi_dir}/KIZUKI_TOUROKU.DISPLAY ${tmp}-param_name ${tmp}-check $tmp-search ${tmp}-touroku > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  #登録(更新登録)
  delete)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
    ${cgi_dir}/KIZUKI_TOUROKU.TOUROKU ${tmp}-param_name ${tmp}-param   > ${tmp}-touroku
    ${cgi_dir}/KIZUKI_TOUROKU.SEARCH ${tmp}-param_name ${tmp}-touroku  > $tmp-search
    ${cgi_dir}/KIZUKI_TOUROKU.DISPLAY ${tmp}-param_name ${tmp}-check $tmp-search ${tmp}-touroku > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;

  #--------------------------
  #--------------------------
  #PDF出力
  print)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
    ${cgi_dir}/KIZUKI_TOUROKU.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KIZUKI_TOUROKU.PRINT ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;


esac
#-------------------------------------------------------------


# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f ${tmp}-*
exit 0
