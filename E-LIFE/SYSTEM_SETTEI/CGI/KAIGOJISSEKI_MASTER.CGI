#!/bin/bash
#
# KAIGOJISSEKI_MASTER.CGI : 介護実績マスター登録用CGI
#
# Usage : KAIGOJISSEKI_MASTER.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)

source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

#ゴミtmpの消去
rm -f $tmp-*

ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"


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
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                       > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MASTER.DISPLAY ${tmp}-param_name ${tmp}-check                > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  # 登録
  touroku )
    ${cgi_dir}/KAIGOJISSEKI_MASTER.TOUROKU ${tmp}-param_name                               > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                       > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MASTER.DISPLAY ${tmp}-param_name ${tmp}-check                > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
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

#  #検索する場合
#  search )
#    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
#    if [ $(gyo ${tmp}-check) -ne 0 ];then
#      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
#      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
#    else
#      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
#    fi
#    ;;
#
#  #Excel出力する場合
#  excel_out )
#    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
#    if [ $(gyo ${tmp}-check) -ne 0 ];then
#      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
#      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.EXCEL ${tmp}-param_name ${tmp}-search              > ${tmp}-download
#      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search ${tmp}-download > ${tmp}-html
#    else
#      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
#    fi
#    ;;

  #その他の場合
  * )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                      > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MASTER.SEARCH ${tmp}-param_name                             > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MASTER.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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

