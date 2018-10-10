#!/bin/bash
#
# KAIGOJISSEKI_IKKATSU.CGI : 介護実績一括登録CGI
#
# Usage : KAIGOJISSEKI_IKKATSU.CGI namefile
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
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #登録する場合
  touroku )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.TOUROKU ${tmp}-param_name  > ${tmp}-data
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
      FILECHECK=$(cat $tmp-data | awk '$1=="error"')
      if [ "${FILECHECK}" -ne 0 ];then
        message=$(cat $tmp-data | awk '$1=="error"{print $2}')
      else
        message="登録しました"
      fi
    else
      message="エラーが発生しました"
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    ;;

  shusei_touroku )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.TOUROKU2 ${tmp}-param_name  > ${tmp}-data
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
      FILECHECK=$(cat $tmp-data | awk '$1=="error"')
      if [ "${FILECHECK}" -ne 0 ];then
        message=$(cat $tmp-data | awk '$1=="error"{print $2}')
      else
        message="登録しました"
      fi
    else
      message="エラーが発生しました"
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    ;;

  #複数人登録するのサブウインドウ表示
  ikkatsu )
   # ${cgi_dir}/KAIGOJISSEKI_IKKATSU.IKKATSU_SEARCH ${tmp}-param_name   > ${tmp}-ikkatsu_search
    ${cgi_dir}/KAIGOJISSEKI_IKKATSU.PRE_TOUROKU ${tmp}-param_name      > $tmp-search_id
    ${cgi_dir}/KAIGOJISSEKI_IKKATSU.IKKATSU_DISPLAY ${tmp}-param_name $tmp-search_id > ${tmp}-html
    ;;

  #複数人登録する場合
  ikkatsu_touroku )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.IKKATSU_TOUROKU ${tmp}-param_name  > ${tmp}-data
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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
       var ChildWindow = window.open("/E-LIFE/SHISETSU_KAIGOKIROKU/cgi-bin/KAIGOJISSEKI_IKKATSU.CGI","IKKATSU","width=300,height=600,resizable=yes,scrollbars=yes");
       ChildWindow.close();
     </script>
FIN
    ;;

  #複数人登録中止場合
  close )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       var ChildWindow = window.open("/E-LIFE/SHISETSU_KAIGOKIROKU/cgi-bin/KAIGOJISSEKI_IKKATSU.CGI","IKKATSU","width=300,height=600,resizable=yes,scrollbars=yes");
       ChildWindow.close();
     </script>
FIN
    ;;

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  # 修正する場合
  shusei )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH2 ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY2 ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  # 削除する場合
  delete )
    ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DELETE ${tmp}-param_name  > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;
  #その他の場合
  * )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOJISSEKI_IKKATSU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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

