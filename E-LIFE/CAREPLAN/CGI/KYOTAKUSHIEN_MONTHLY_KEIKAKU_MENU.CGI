#!/bin/bash
#
# KYOTAKUSHIEN_MONTHLY_KEIKAKU_MENU.CGI : 月間利用計画（介護）MENUCGI
#
# Usage : KYOTAKUSHIEN_MONTHLY_KEIKAKU_MENU.CGI
#
# Written by K.AOYAMA(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/CAREPLAN/CGI/CAREPLAN.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


rm -f $tmp-*


#------------------------------------------------------------
# パラメーターの取得
dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name
cookie-name                    |
LANG=C sort                    > ${tmp}-cookie
#------------------------------------------------------------


#------------------------------------------------------------
# 処理モードの決定
eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------

cp ${tmp}-name $work_dir/param_name

#------------------------------------------------------------
upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
cp -p $tmp-name $tmp-name_origin
mv -f $tmp-name.new0 $tmp-name

#echo "USER_ID kaizen" >> $tmp-name
#------------------------------------------------------------


##------------------------------------------------------------
## セッションチェック
#case "$MODE" in
#  *)
#    $function_dir/FUNCTION.SESSION_CHECK -chk $session_dir/$SESSION_ID > $tmp-session_result
#
#    # エラーの場合、MODEを変え、namedateも変換する
#    if [ "$(awk 'NR==1{print $1}' $tmp-session_result)" == "ng" ]; then
#      MODE="$(awk 'NR==1{print $2}' $tmp-session_result)"
#      echo "MODE $MODE" > $tmp-new_mode
#      cat $tmp-name   |
#      sed '/^MODE /d' |
#      cat $tmp-new_mode - > $tmp-name.new
#      mv -f $tmp-name.new $tmp-name
#    fi
#  ;;
#esac
##------------------------------------------------------------


#MODEの確認
MODE="$(nameread "MODE" ${tmp}-name)"
[ -n "${MODE}" ] || MODE="init"

# 処理の分岐
case "${MODE}" in
  #初期表示
  init )
    ${cgi_dir}/KYOTAKUSHIEN_MONTHLY_KEIKAKU_MENU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;

  #検索する場合
  search )
    ${cgi_dir}/KYOTAKUSHIEN_MONTHLY_KEIKAKU_MENU.SEARCH ${tmp}-name              > ${tmp}-search
    ${cgi_dir}/KYOTAKUSHIEN_MONTHLY_KEIKAKU_MENU.DISPLAY ${tmp}-name ${tmp}-search > ${tmp}-html
    ;;

  # セッションエラーまたはタイムアウト
#  session_error | session_timeout)
#    onload="${MODE}();apl_close('1');"
#    msg="&nbsp;"
#    echo "###ONLOAD### $onload"                > $tmp-calsed
#    cat ${portal_html_dir}/SESSION_ERROR.html  |
#    calsed -f $tmp-calsed -                    > ${tmp}-html
#  ;;

  #その他の場合
  * )
    ${cgi_dir}/KYOTAKUSHIEN_MONTHLY_KEIKAKU_MENU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;
esac

# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN


## 終了
rm -f ${tmp}-*
exit 0

