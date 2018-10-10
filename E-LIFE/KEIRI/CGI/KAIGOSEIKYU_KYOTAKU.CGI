#!/bin/bash
#
# KAIGOSEIKYU_KYOTAKU.CGI : 居宅支援介護請求CGI
#
# Usage : KAIGOSEIKYU_KYOTAKU.CGI namefile
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
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    ;;

  #検索する場合
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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

  # 予防の対象者検索する場合
  yobo_search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_YOBO.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-search)" -ne 0 ];then
      :
    else
      message="予防の対象データがありません"
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
    fi
    ;;

  # 個人確定
  kojin_kakutei )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.KOJINKAKUTEI ${tmp}-param_name                              > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
      if [ "$(cat $tmp-data | awk '{if($1=="error"){print $2}}' | gyo)" = 0 ];then
        message="登録しました"
      else
        message="$(cat $tmp-data | awk '{if($1=="error"){print $2}}')"
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

  # 予防の個人確定
  yobo_kojin_kakutei )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_YOBO.KOJINKAKUTEI ${tmp}-param_name                              > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_YOBO.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
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
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.TOUGETSUKAKUTEI ${tmp}-param_name                              > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
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
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.KAIJO ${tmp}-param_name                                    > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
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

  # 請求対象者からはずす
  jogai )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.TAISHO_JOGAI ${tmp}-param_name                              > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
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

  yobo_jogai )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.YOBO_TAISHO_JOGAI ${tmp}-param_name                              > ${tmp}-data
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_YOBO.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search      > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
    # message
    if [ "$(gyo ${tmp}-data)" -ne 0 ];then
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

  # データチェック
  download_kyufukanri )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name                                          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.SEARCH ${tmp}-param_name                                  > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.EXCEL ${tmp}-param_name                                  > ${tmp}-data
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search $tmp-data     > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;

  # 支援請求書・支援請求明細書照会する場合
  kaigokyufuhi_seikyusho )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_KAIGOKYUFUHI_SEIKYUSHO.PRINT ${tmp}-param_name               > ${tmp}-html
#    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
  ;;

  # 給付管理票照会する場合
  kyufukanrihyo )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_KYUFUKANRIHYO.PRINT ${tmp}-param_name $tmp-search        > ${tmp}-html
#    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
  ;;

  # 予防給付管理票照会する場合
  yobo_kyufukanri )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_YOBO.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_YOBO_KYUFUKANRIHYO.PRINT ${tmp}-param_name ${tmp}-search  > ${tmp}-html
#    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
  ;;

  # 介護給付費明細書照会する場合
  shisenmeisaisho )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_KAIGOKYUFUHI_MEISAISHO.PRINT ${tmp}-param_name               > ${tmp}-html
#    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
  ;;

  # 訪問介護介護給付費明細書照会する場合
  houmon_kaigo_meisaisho )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON_KAIGOKYUFUHI_MEISAISHO.PRINT ${tmp}-param_name               > ${tmp}-html
#    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
  ;;

  # 訪問介護予防給付費明細書照会する場合
  houmon_yobo_meisaisho )
    ${cgi_dir}/KAIGOSEIKYU_HOUMON_YOBO_KAIGOKYUFUHI_MEISAISHO.PRINT ${tmp}-param_name               > ${tmp}-html
#    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
  ;;

  # 介護給付費明細書照会する場合
  kaigodoshukei )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_KAIGODO_SHUKEI.PRINT ${tmp}-param_name               > ${tmp}-data
      : > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search $tmp-data  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;

  # 介護給付費明細書照会する場合
  kokuhoren )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_KOKUHOREN.PRINT ${tmp}-param_name               > ${tmp}-html
#    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
  ;;

  # 事業所別利用状況一覧のサブウインドウ表示
  jigyoshobetsu_ichiran )
    ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_JIGYOSHOBETSU_ICHIRAN.DISPLAY ${tmp}-param_name              > ${tmp}-html
  ;;

  # 事業所別利用状況一覧出力示
  jigyosho_ichiran_print )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU_JIGYOSHO_ICHIRAN.PRINT ${tmp}-param_name               > ${tmp}-data
      : > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search $tmp-data  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
cat <<- FIN > $tmp-html3
     <script type="text/javascript" language="javascript">
       var ChildWindow = window.open("/E-LIFE/KEIRI/cgi-bin/KAIGOSEIKYU_KYOTAKU.CGI","ICHIRAN","width=500,height=300,resizable=yes,scrollbars=yes");
       ChildWindow.close();
     </script>
FIN
  ;;
  #その他の場合
  * )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.SEARCH ${tmp}-param_name   > ${tmp}-search
      ${cgi_dir}/KAIGOSEIKYU_KYOTAKU.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
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

