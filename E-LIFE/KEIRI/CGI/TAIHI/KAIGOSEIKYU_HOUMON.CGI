#!/bin/bash
#
# KAIGOSEIKYU_HOUMON.CGI : 訪問介護介護請求CGI
#
# Usage : KAIGOSEIKYU_HOUMON.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)


# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/KEIRI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/KEIRI/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

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

work="/home/hands/E-LIFE/KEIRI/WORK"

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
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-search)" -ne 0 ];then
      :
    else
      message="対象データがありません"
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    fi
    ;;

  # FBする場合
  fb_sakusei )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.FB     ${tmp}-param_name               > ${tmp}-data
cp $tmp-data ${work}/jyu
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search $tmp-data > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-search)" -ne 0 ];then
      :
    else
      message="対象データがありません"
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
      :
    else
      message="エラーが発生しました"
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    fi
    if [ "$(cat ${tmp}-data | awk '$1=="error"' | gyo)" = 0 ];then
      :
    else
      MES="有効な口座が設定されていない利用者がいます"
      message="$(cat $tmp-data | awk '{print $2,$3}' | yarr | awk '{print "'${MES}'",$0}' | sed 's/ /\\n/g')"
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    fi
    ;;

  # 個人宛請求書印刷
  kojinseikyu )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_HOUMON_KOJIN.PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
  # 領収書印刷
  ryoshusho )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_HOUMON_RYOSHUSHO.PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
  # セット印刷
  set_print )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.SET_PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
  # 介護給付費集計一覧表
  kaigokyufu_ichiran )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_HOUMON_KAIGOKYUFU_ICHIRAN.PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
  # サービス請求額一覧表
  service_ichiran )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_HOUMON_SERVICE_ICHIRAN.PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
  # 介護給付費明細一覧表
  kaigokyufu_meisai )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_HOUMON_KAIGOKYUFU_MEISAI.PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
  # 日常生活費明細一覧表（日常生活費となっているが自費の明細のこと）
  jihi_meisai )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_HOUMON_JIHI_MEISAI.PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
  # 個人確定
  kojin_kakutei )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.KOJINKAKUTEI ${tmp}-param_name                              > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
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

  # 当月確定
  tougetsu_kakutei )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.TOUGETSUKAKUTEI ${tmp}-param_name                           > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
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

  # 確定解除
  kakutei_kaijo )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.KAIJO ${tmp}-param_name                           > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
      message="解除しました"
    else
      message="エラーが発生しました"
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    ;;

  # 請求対象からはずす
  jogai )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON.TAISHO_JOGAI ${tmp}-param_name                              > ${tmp}-jogai
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-jogai)" -ne 0 ];then
      message="更新しました"
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
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_HOUMON.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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

