#!/bin/bash
#
# DENKI_SUIDOU_TORIKOMI.CGI : 電気・水道取込
#
# Written by J.Mikami

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/KEIRI/CGI/DENWAKAKIN_RIYOU_JYOUHOU.INI &> /dev/null
mkdir -p /home/hands/E-LIFE/KEIRI/TRACE_LOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/KEIRI/TRACE_LOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


rm -f $tmp-*


#------------------------------------------------------------
# パラメーターの取得

dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name
cookie-name                    |
LANG=C sort                    > ${tmp}-cookie
#------------------------------------------------------------

# ディレクトリ設定
ch_cgi_dir="${home_dir}/TEST/CGI"


#------------------------------------------------------------
# 処理モードの決定
eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------

#------------------------------------------------------------
upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
#cp -p $tmp-name $tmp-name_origin
mv -f $tmp-name.new0 $tmp-name


#------------------------------------------------------------

#MODEの確認
MODE="$(nameread "MODE" ${tmp}-name)"
[ -n "${MODE}" ] || MODE="init"

# 処理の分岐
case "${MODE}" in
  # 初期表示
  init )
    ${home_dir}/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
       ${cgi_dir}/DENKI_SUIDOU_TORIKOMI.DISPLAY ${tmp}-name ${tmp}-check /dev/null > ${tmp}-html
    else
      ${home_dir}/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-name
    fi
    ;;

   # エクセル出力電気
   excel_denki )
     ${home_dir}/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-name > ${tmp}-check
     if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/DENKI_SUIDOU_TORIKOMI.SEARCH ${tmp}-name               > ${tmp}-search
        ${cgi_dir}/DENKI_SUIDOU_TORIKOMI.EXCEL ${tmp}-name                > ${tmp}-html 
     else
       ${home_dir}/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-name > ${tmp}-html
     fi
   ;;

   # エクセル出力水道
   excel_suidou )
     ${home_dir}/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-name > ${tmp}-check
     if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/DENKI_SUIDOU_TORIKOMI.SEARCH ${tmp}-name               > ${tmp}-search
        ${cgi_dir}/DENKI_SUIDOU_TORIKOMI.EXCEL ${tmp}-name                > ${tmp}-html
     else
       ${home_dir}/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-name > ${tmp}-html
     fi
   ;; 
 
   # セッションエラーまたはタイムアウト
   session_error | session_timeout)
     onload="${MODE}();apl_close('1');"
     msg="&nbsp;"
     echo "###ONLOAD### $onload"                > $tmp-calsed
     cat ${portal_html_dir}/SESSION_ERROR.html  |
     calsed -f $tmp-calsed -                    > ${tmp}-html
   ;;

  # その他の場合
  * )
    ${home_dir}/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/DENKI_SUIDOU_TORIKOMI.DISPLAY ${tmp}-name ${tmp}-check /dev/null > ${tmp}-html
    else
      ${home_dir}/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-name
    fi
    ;;
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


## 終了
rm -f ${tmp}-*
exit 0

