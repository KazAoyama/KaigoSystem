#!/bin/bash
#
# KENKOUSHINDANSHO_UPLOAD.CGI : 健康診断書アップロードCGI
#
# Usage : KENKOUSHINDANSHO_UPLOAD.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)


# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/UNEI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/UNEI/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/UNEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
ch_cgi_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI"
work="${app_dir}/WORK"


#}}}Functions#######################################

dd bs=${CONTENT_LENGTH} > ${tmp}-param

if [ -s ${tmp}-param ]; then
  # 入力データは MIME 形式か？
  if ismime ${tmp}-param; then
    # MIME 形式なので、そのまま。
    cat ${tmp}-param > ${tmp}-param_mime
    # NAME 形式のファイルも準備
tr -s " " <<- FIN > ${tmp}-param_name
MODE                   $(mime-read "MODE"               ${tmp}-param_mime)
riyosha_name           $(mime-read "riyosha_name"       ${tmp}-param_mime)
userid                 $(mime-read "userid"             ${tmp}-param_mime)
shisetsu               $(mime-read "shisetsu"           ${tmp}-param_mime)
biko                   $(mime-read "biko"               ${tmp}-param_mime)
FIN
 else
    # MIME 形式ではないので、name 形式に変換。
    cgi-name -d"_" -i"_" ${tmp}-param > ${tmp}-param_name
    : > ${tmp}-param_mime
  fi
else
  # ファイルがないか、空ファイルなので、空ファイル作成。
  : | tee ${tmp}-param_name ${tmp}-param_mime
fi
cp ${tmp}-param_mime ${work}/param_mime
#[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

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
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #UPLOADする場合
  upload )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.UPLOAD ${tmp}-param_name $tmp-param_mime             > ${tmp}-upload
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search $tmp-upload > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  # 削除する場合
  delete )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.DELETE ${tmp}-param_name $tmp-param_mime             > ${tmp}-delete
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search $tmp-delete > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;


  #その他の場合
  * )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KENKOUSHINDANSHO_UPLOAD.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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
