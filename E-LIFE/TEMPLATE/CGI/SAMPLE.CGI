#!/bin/bash
#
# SAMPLE_MAIN.CGI
# モードに応じて各CGIに処理を振り分ける
#
# Written by T.Osako (Tokyu-hands.co.jp) :20100615

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/BUSINESS_AIRPORT/SAMPLE/CGI/SAMPLE.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).$HOSTNAME.$(date +%Y%m%d%H%M%S).$$ ; set -xv
#------------------------------------------------------------

#------------------------------------------------------------
rm -f $tmp-*
#------------------------------------------------------------

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

#------------------------------------------------------------
upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
cp -p $tmp-name $tmp-name_origin
mv -f $tmp-name.new0 $tmp-name

echo "USER_ID kaizen" >> $tmp-name
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

#------------------------------------------------------------
## 処理の分岐
case "${MODE}" in
  #------------------------------------------------
  # 初期表示
  init )
    ${cgi_dir}/SAMPLE.DISPLAY $tmp-name /dev/null          > $tmp-html
  ;;
  #------------------------------------------------


  #------------------------------------------------
  # 検索ボタンを押したとき
  to_search)
    ${cgi_dir}/SAMPLE.SEARCH $tmp-name                     > $tmp-listdata
    ${cgi_dir}/SAMPLE.DISPLAY $tmp-name $tmp-listdata      > $tmp-html
  ;;
  #------------------------------------------------


  #------------------------------------------------
  # 更新したとき
  to_koshin)
    ${cgi_dir}/SAMPLE.TOUROKU $tmp-name                    > $tmp-touroku
    ${cgi_dir}/SAMPLE.DISPLAY $tmp-name $tmp-touroku       > $tmp-html
  ;;
  #------------------------------------------------


  #------------------------------------------------
  # セッションエラーまたはタイムアウト
  session_error | session_timeout)
    onload="${MODE}();apl_close('1');"
    msg="&nbsp;"
    echo "###ONLOAD### $onload"                > $tmp-calsed
    cat ${portal_html_dir}/SESSION_ERROR.html  |
    calsed -f $tmp-calsed -                    > ${tmp}-html
  ;;
  #------------------------------------------------
esac


## HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html

FIN


## 終了
rm -f $tmp-*
exit 0
