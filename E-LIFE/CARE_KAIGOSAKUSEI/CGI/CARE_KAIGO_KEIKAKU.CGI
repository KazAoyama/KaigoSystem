#!/bin/bash
#
# CARE_KAIGO_KEIKAKU.CGI : 介護サービス計画書
#
# Usage : CARE_KAIGO_KEIKAKU.CGI
#
# Written by K.AOYAMA(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/CARE_KAIGOSAKUSEI/CGI/CARE_KAIGOSAKUSEI.INI &> /dev/null
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

# ディレクトリ設定
ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"

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

# 仮検証（テスト）用　後で処理を入れる必要あり
#echo "###LI_CCAREPLAN1### on" > ${tmp}-check
#echo "###LI_CCAREPLAN3### on" >> ${tmp}-check
#echo "###LI_CCAREPLAN4### on" >> ${tmp}-check
#echo "###LI_CCAREPLAN5### on" >> ${tmp}-check
#echo "###LI_CCAREPLAN6### on" >> ${tmp}-check
#echo "###LI_CCAREPLAN7### on" >> ${tmp}-check
#echo "###TOGGLE_SCHEDULE### dropdown" >> ${tmp}-check
#echo "###TOGGLE_KOJIN### dropdown" >> ${tmp}-check
#echo "###TOGGLE_RIYOU### dropdown" >> ${tmp}-check
#echo "###TOGGLE_CAREPLAN### dropdown" >> ${tmp}-check
#echo "###TOGGLE_KAIGO### dropdown" >> ${tmp}-check
#echo "###TOGGLE_SHOKUJI### dropdown" >> ${tmp}-check
#echo "###TOGGLE_SEIKYU### dropdown" >> ${tmp}-check


#MODEの確認
MODE="$(nameread "MODE" ${tmp}-name)"
[ -n "${MODE}" ] || MODE="init"

# 処理の分岐
case "${MODE}" in
  #初期表示
  init )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.SEARCH ${tmp}-name > $tmp-search
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.DISPLAY ${tmp}-name $tmp-check $tmp-search > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi
    ;;

  #登録する場合
  regist )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.TOUROKU ${tmp}-name > ${tmp}-data
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.DISPLAY ${tmp}-name $tmp-check ${tmp}-data > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi
    ;;
  #削除する場合
  delete )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.TOUROKU ${tmp}-name > ${tmp}-data
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.DISPLAY ${tmp}-name $tmp-check ${tmp}-data > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi
    ;;

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.DISPLAY $tmp-name $tmp-check ${tmp}-search > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi
    ;;

  #検索する場合
  print )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.PRINT $tmp-name ${tmp}-search > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi
    ;;

  #初期化する場合
  to_refresh )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
       ${cgi_dir}/CARE_KAIGO_KEIKAKU.DISPLAY $tmp-name $tmp-check > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi
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
    ${cgi_dir}/CARE_KAIGO_KEIKAKU.DISPLAY ${tmp}-name $tmp-check > ${tmp}-html
    ;;
esac

# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN


## 終了
rm -f ${tmp}-*
exit 0

