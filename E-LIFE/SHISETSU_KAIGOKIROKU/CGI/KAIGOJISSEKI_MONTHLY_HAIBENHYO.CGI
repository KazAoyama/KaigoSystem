#!/bin/bash
#
# KAIGOJISSEKI_MONTHLY_HAIBENHYO.CGI : 月間排便表CGI
#
# Usage : KAIGOJISSEKI_MONTHLY_HAIBENHYO.CGI namefile
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
      ${cgi_dir}/KAIGOJISSEKI_MONTHLY_HAIBENHYO.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MONTHLY_HAIBENHYO.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MONTHLY_HAIBENHYO.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #印刷する場合
  print )
    rm ${download_dir}/*.KAIGOJISSEKI_MONTHLY_HAIBENHYO.pdf
    ${cgi_dir}/KAIGOJISSEKI_MONTHLY_HAIBENHYO.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOJISSEKI_MONTHLY_HAIBENHYO.PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
    ;;

  #その他の場合
  * )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MONTHLY_HAIBENHYO.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MONTHLY_HAIBENHYO.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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

