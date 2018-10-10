#!/bin/bash
#
# SAMPLE_MAIN.CGI
# モードに応じて各CGIに処理を振り分ける
#
# Written by T.Osako (Tokyu-hands.co.jp) :20100615

# ログ
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
#------------------------------------------------------------

#------------------------------------------------------------
# 変数設定
tmp=/var/tmp/${$}

rm -f $tmp-*

#------------------------------------------------------------

#------------------------------------------------------------
# パラメーターの取得
dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)
#------------------------------------------------------------
#cp ${tmp}-param_name /home/hands/work/okuda
#------------------------------------------------------------
# 処理モードの決定
MODE="$(nameread "MODE" ${tmp}-param_name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#------------------------------------------------------------

#------------------------------------------------------------
#upl key=1 ${tmp}-cookie ${tmp}-param_name > ${tmp}-param_name.new0
#cp -p ${tmp}-param_name ${tmp}-param_name_origin
#mv -f ${tmp}-param_name.new0 ${tmp}-param_name
#
#echo "USER_ID kaizen" >> ${tmp}-param_name
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
#      cat ${tmp}-param_name   |
#      sed '/^MODE /d' |
#      cat $tmp-new_mode - > ${tmp}-param_name.new
#      mv -f ${tmp}-param_name.new ${tmp}-param_name
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
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KEIYAKU.DISPLAY ${tmp}-param_name /dev/null          > $tmp-html
  ;;
  #------------------------------------------------
  #------------------------------------------------
  # 登録ボタンをおしたとき
  search)
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KEIYAKU.SEARCH ${tmp}-param_name                    > $tmp-search
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KEIYAKU.DISPLAY ${tmp}-param_name $tmp-search       > $tmp-html
  ;;
  #------------------------------------------------
  #------------------------------------------------
  # 登録ボタンをおしたとき
  touroku)
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KEIYAKU.TOUROKU ${tmp}-param_name                    > $tmp-touroku
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KEIYAKU.SEARCH ${tmp}-param_name
    ${cgi_dir}/POP_KOJINJYOUHOU_SHOUSAI_KEIYAKU.DISPLAY ${tmp}-param_name ${tmp}-param_name $tmp-touroku       > $tmp-html
  ;;
  #------------------------------------------------

  #------------------------------------------------
  # セッションエラーまたはタイムアウト
# session_error | session_timeout)
#   onload="${MODE}();apl_close('1');"
#   msg="&nbsp;"
#   echo "###ONLOAD### $onload"                > $tmp-calsed
#   cat ${portal_html_dir}/SESSION_ERROR.html  |
#   calsed -f $tmp-calsed -                    > ${tmp}-html
# ;;
  #------------------------------------------------
esac


## HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html

FIN


## 終了
rm -f $tmp-*
exit 0
