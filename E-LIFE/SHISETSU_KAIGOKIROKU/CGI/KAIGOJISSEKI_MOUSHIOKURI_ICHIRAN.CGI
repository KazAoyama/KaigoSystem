#!/bin/bash
#
# KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.CGI : 介護実績申し送り一覧CGI
#
# Usage : KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)

exec 2> /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d%H%M%S"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

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
      : > $tmp-search
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  # 修正
  touroku )
    ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.TOUROKU ${tmp}-param_name  > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(atama -1 ${tmp}-data | self 1)" != "error" ];then
      message="登録しました"
    else
      message="$(self 2 ${tmp}-data)"
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
       var ChildWindow = window.open("/E-LIFE/SHISETSU_KAIGOKIROKU/cgi-bin/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN_SHUSEI.CGI","shusei","width=1100,height=300,resizable=yes,scrollbars=yes");
       ChildWindow.close();
     </script>
FIN
    ;;

  # 新規登録
  new_touroku )
cat ${tmp}-param_name > /home/hands/work/kashiyama/param_name
    ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.TOUROKU ${tmp}-param_name  > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi

    # message
    if [ "$(atama -1 ${tmp}-data | self 1)" != "error" ];then
      message="登録しました"
    else
      message="$(self 2 ${tmp}-data)"
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
       var ChildWindow = window.open("/E-LIFE/SHISETSU_KAIGOKIROKU/cgi-bin/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN_SHUSEI.CGI","shusei","width=1100,height=300,resizable=yes,scrollbars=yes");
       ChildWindow.close();
     </script>
FIN
    ;;

  # 削除
  delete )
    ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DELETE ${tmp}-param_name  > ${tmp}-delete
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-delete)" -ne 0 ];then
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

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #Excel出力する場合
  excel_out )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.EXCEL ${tmp}-param_name ${tmp}-search              > ${tmp}-download
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search ${tmp}-download > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #その他の場合
  * )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_MOUSHIOKURI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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

