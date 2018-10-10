#!/bin/bash
#
# KAIGOJISSEKI_ICHIRAN_HYOJI.CGI : 介護実績一覧表示CGI
#
# Usage : KAIGOJISSEKI_ICHIRAN_HYOJI.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/SHISETSU_KAIGOKIROKU"
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
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #修正画面を表示する場合
  shusei )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.SEARCH2 ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.DISPLAY2 ${tmp}-param_name ${tmp}-check ${tmp}-search    > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #修正する場合
  touroku )
    ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.TOUROKU ${tmp}-param_name  > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #削除する場合
  delete )
    ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.DELETE ${tmp}-param_name  > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #その他の場合
  * )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_ICHIRAN_HYOJI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
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

rm -f ${tmp}-*
exit 0

