#!/bin/bash
#
# パスワード変更画面CGI
#
# Written by Tomoaki Imai

source /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f ${tmp}-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
cgi_nisshi_dir="${home_dir}/E-LIFE/UNEI/CGI"
cgi_careplan_dir="${home_dir}/E-LIFE/CAREPLAN/CGI"
cgi_houmonkaigo_dir="${home_dir}/E-LIFE/HOUMONKAIGO/CGI"
tbl_dir="${home_dir}/E-LIFE/TBL"
ch_cgi_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI"

#}}}Functions#######################################

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)

[ -n "${MODE}" ] || MODE="init"
# 処理の分岐
case "${MODE}" in
  # 変更
  change_password)
    ${cgi_dir}/CHANGE_PASSWORD.CHECK ${tmp}-param_name > ${tmp}-check
    if [ ${?} -eq 0 ]; then
      ${cgi_dir}/CHANGE_PASSWORD.TOUROKU ${tmp}-param_name ${tmp}-message > ${tmp}-result
      if [ ${?} -eq 0 ]; then
        redirect_url="/E-LIFE/SYSTEM_SETTEI/cgi-bin/SIGN_IN.CGI"
      else
        message=$(awk '$1=="MESSAGE"{print $2}' ${tmp}-message)
        ${cgi_dir}/CHANGE_PASSWORD.DISPLAY ${tmp}-param_name ${tmp}-check > ${tmp}-html
      fi
    else
      message=$(awk '$1=="MESSAGE"{print $2}' ${tmp}-check)
      echo "alert(\"${message}\");" > ${tmp}-message
      ${cgi_dir}/CHANGE_PASSWORD.DISPLAY ${tmp}-param_name ${tmp}-check |
      filehame -l###MESSAGE### - ${tmp}-message                         > ${tmp}-html
    fi
    ;;
  #その他の場合
  *)
    ;;
esac

# HTMLファイルを表示する
if [ -z "${redirect_url}" ]; then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
else
  echo "Status: 301"
  echo "Location: ${redirect_url}"
  echo
fi

# rm -f ${tmp}-*
exit 0
