#!/bin/bash
#
# FIRMBANKING.CGI : ファームバンキング用CGI
#
# Usage : FIRMBANKING.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)

exec 2> /home/hands/E-LIFE/KEIRI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/KEIRI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
ch_cgi_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI"


#}}}Functions#######################################

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-param_name)"
[ -n "${MODE}" ] || MODE="init"


# 処理の分岐
case "${MODE}" in
  #初期表示
  init )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      : > ${tmp}-search
      ${cgi_dir}/FIRMBANKING.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/TEST_SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/FIRMBANKING.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/FIRMBANKING.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/TEST_SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  # 登録
  touroku )
    ${cgi_dir}/SERVICE_TOUROKU.TOUROKU ${tmp}-param_name                                   > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                       > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/SERVICE_TOUROKU.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/SERVICE_TOUROKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
    else
      ${ch_cgi_dir}/TEST_SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
      message="登録しました"
    else
      message="エラーが発生しました"
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    ;;

  # 上書登録
  uwagaki )
    ${cgi_dir}/SERVICE_TOUROKU.TOUROKU ${tmp}-param_name                               > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                       > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/SERVICE_TOUROKU.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/SERVICE_TOUROKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
    else
      ${ch_cgi_dir}/TEST_SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
      message="上書登録しました"
    else
      message="エラーが発生しました"
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    ;;

  # 修正
  shusei )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                       > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/SERVICE_TOUROKU.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/SERVICE_TOUROKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search           > ${tmp}-html
    else
      ${ch_cgi_dir}/TEST_SIGN_IN.CGI ${tmp}-param_name
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       \$('#nyuryoku_open').show("blind","","slow");
     </script>
FIN
    ;;

  # 削除
  delete )
    ${cgi_dir}/SERVICE_TOUROKU.DELETE ${tmp}-param_name                               > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                       > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/SERVICE_TOUROKU.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/SERVICE_TOUROKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
    else
      ${ch_cgi_dir}/TEST_SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
      message="削除しました"
    else
      message="エラーが発生しました"
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    ;;

  #その他の場合
  * )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/FIRMBANKING.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/TEST_SIGN_IN.CGI ${tmp}-param_name
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
  if [ -e "${tmp}-html3" ];then
    echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
    cat - ${tmp}-html ${tmp}-html3
  else
    echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
    cat - ${tmp}-html
  fi
else
  cat $tmp-html2
fi

rm -f ${tmp}-*
exit 0

