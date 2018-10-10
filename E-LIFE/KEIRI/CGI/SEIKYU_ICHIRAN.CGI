#!/bin/bash
#
# SEIKYU_ICHIRAN.CGI : 請求一覧CGI
#
# Usage : SEIKYU_ICHIRAN.CGI namefile
#
# Written by S.Otsubo

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/KEIRI/CGI/SEIKYU_ICHIRAN.INI &> /dev/null

# ログ
[ ! -e /home/hands/E-LIFE/KEIRI/TRACE_LOG/${today} ] && mkdir /home/hands/E-LIFE/KEIRI/TRACE_LOG/${today}
exec 2> /home/hands/E-LIFE/KEIRI/TRACE_LOG/${today}/LOG.$(basename ${0}).${HOSTNAME}.${current_time}; set -xv

#ゴミtmpの消去
rm -f $tmp-*

#}}}Functions#######################################

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-param_name)"
[ -n "${MODE}" ] || MODE="init"


# 処理の分岐
case "${MODE}" in
  # --------------
  # 初期表示
  init )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        : > ${tmp}-search
        ${cgi_dir}/SEIKYU_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 検索
  kensaku )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/SEIKYU_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
        ${cgi_dir}/SEIKYU_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 出力
  excel_out )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/SEIKYU_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
        ${cgi_dir}/SEIKYU_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
esac

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

#rm -f ${tmp}-*
exit 0

