#!/bin/bash
#
# KOJINJYOUHOU_SHOUSAI_ASSESSMENT.CGI : 個人情報詳細(契約)CGI
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
ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"
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
#    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.DISPLAY ${tmp}-param_name > $tmp-html
#  ;;
  # -------------------------

  #--------------------------
  #検索(初期表示で検索結果が出る)
  init)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.DISPLAY ${tmp}-param_name ${tmp}-check  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  search)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.SEARCH ${tmp}-param_name                > ${tmp}-search
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  #--------------------------
  #登録
  touroku)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.TOUROKU ${tmp}-param_name                 >${tmp}-touroku
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.SEARCH ${tmp}-param_name  ${tmp}-touroku  > ${tmp}-search
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search ${tmp}-touroku  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  #更新
  koushin)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.TOUROKU ${tmp}-param_name                 >${tmp}-touroku
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.SEARCH ${tmp}-param_name  ${tmp}-touroku  > ${tmp}-search
      ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search ${tmp}-touroku  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  #PDF出力
  pdf_print)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
     ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.SEARCH ${tmp}-param_name                  > ${tmp}-search
     ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT.PDF ${tmp}-param_name ${tmp}-check ${tmp}-search       > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
esac
#-------------------------------------------------------------

# 返す？
if [ "$(gyo ${tmp}-check)" -ne 0 ];then
  :
else
  message="権限がありません"
cat <<- FIN > $tmp-html2
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
fi

# HTMLファイルを表示する
if [ -e "$tmp-html" ];then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
else
  cat $tmp-html2
fi

# 終了
rm -f $tmp-*
exit 0
