#!/bin/bash
#
# TATEKAEKIN_KINSHUHYO.CGI : 立替金金種表登録用CGI
#
# Usage : TATEKAEKIN_KINSHUHYO.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)

exec 2> /home/hands/E-LIFE/TATEKAEKIN/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/TATEKAEKIN"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
ch_cgi_dir="${home_dir}/E-LIFE/TEST/CGI"


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
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.DISPLAY ${tmp}-param_name ${tmp}-search  > ${tmp}-html
    ;;

  #検索する場合
  search )
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
    ;;

  # 登録
  touroku )
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.TOUROKU ${tmp}-param_name                               > ${tmp}-data
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.DISPLAY ${tmp}-param_name $tmp-search                > ${tmp}-html
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
  #印刷する場合
  print )
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/TATEKAEKIN_KINSHUHYO.PRINT ${tmp}-param_name ${tmp}-search > ${tmp}-html
    ;;

esac



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
