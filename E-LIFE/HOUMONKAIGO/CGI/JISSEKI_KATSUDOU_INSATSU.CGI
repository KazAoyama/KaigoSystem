#!/bin/bash
#
# JISSEKI_KATSUDOU_INSATSU.CGI : 訪問介護活動実績照会CGI
#
# Usage : JISSEKI_KATSUDOU_INSATSU.CGI
#
# Written by K.AOYAMA(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/HOUMONKAIGO/CGI/HOUMONKAIGO.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


rm -f $tmp-*


#------------------------------------------------------------
# パラメーターの取得
dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name
cookie-name                    |
LANG=C sort                    > ${tmp}-cookie
#------------------------------------------------------------


#------------------------------------------------------------
# 処理モードの決定
eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------

cp ${tmp}-name $work_dir/param_name

#------------------------------------------------------------
upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
cp -p $tmp-name $tmp-name_origin
mv -f $tmp-name.new0 $tmp-name

#echo "USER_ID kaizen" >> $tmp-name
#------------------------------------------------------------


##------------------------------------------------------------
## セッションチェック
#case "$MODE" in
#  *)
#    $function_dir/FUNCTION.SESSION_CHECK -chk $session_dir/$SESSION_ID > $tmp-session_result
#
#    # エラーの場合、MODEを変え、namedateも変換する
#    if [ "$(awk 'NR==1{print $1}' $tmp-session_result)" == "ng" ]; then
#      MODE="$(awk 'NR==1{print $2}' $tmp-session_result)"
#      echo "MODE $MODE" > $tmp-new_mode
#      cat $tmp-name   |
#      sed '/^MODE /d' |
#      cat $tmp-new_mode - > $tmp-name.new
#      mv -f $tmp-name.new $tmp-name
#    fi
#  ;;
#esac
##------------------------------------------------------------


#MODEの確認
MODE="$(nameread "MODE" ${tmp}-name)"
[ -n "${MODE}" ] || MODE="init"

# 処理の分岐
case "${MODE}" in
  #初期表示
  init )
    ${cgi_dir}/JISSEKI_KATSUDOU_INSATSU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;

  print )
    case "$ChouhyouSentaku" in
       # ホームヘルプサービス援助記録（巡回型）
       0 )
       ;;
       # ホームヘルプサービス援助記録（滞在型）
       1 )
       ;;
       # ホームヘルプサービス援助記録（乗降介助）
       2 )
       ;;
       # 月間利用実績一覧表（サービス別）
       4 )
       ${cgi_dir}/GEKKAN_RIYOU_JISSEKI_ICHIRAN_SERVICE.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/GEKKAN_RIYOU_JISSEKI_ICHIRAN_SERVICE.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       ;;
########################################################################################################


       # 月間利用実績明細一覧表
       5 )
       ${cgi_dir}/GEKKAN_RIYOU_JISSEKI_MEISAI_ICHIRAN.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/GEKKAN_RIYOU_JISSEKI_MEISAI_ICHIRAN.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       ;;
       # 月間サービス提供回数集計表（介護度別）
       6 )
       ${cgi_dir}/GEKKAN_SERVICE_TEIKYOU_SHUKEI_KAIGODO.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/GEKKAN_SERVICE_TEIKYOU_SHUKEI_KAIGODO.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       ;;
#       # 月間実績一覧表（ヘルパー別）
#       7 )
#       ${cgi_dir}/GEKKAN_JISSEKI_ICHIRAN_HELPER.SEARCH ${tmp}-name > ${tmp}-search
#       ${cgi_dir}/GEKKAN_JISSEKI_ICHIRAN_HELPER.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html ;;
       # 予定実績対比表
       8 )
       mkdir -p ${home_dir}/HOUMONKAIGO/DOWNLOAD/$USER_ID
       rm -f ${home_dir}/HOUMONKAIGO/DOWNLOAD/$USER_ID/*


       ${cgi_dir}/YOTEI_JISSEKI_TAIHIHYOU.SEARCH ${tmp}-name > ${tmp}-search
         self 1 ${tmp}-search |
         LANG=C sort -u       |
       while read riyoushaid ;do 
         awk '$1!="Riyoushaid"' ${tmp}-name |
         tee /var/tmp/idnashi_name |
         cat - <(echo "Riyoushaid" $riyoushaid) > ${tmp}-name_0
         mv ${tmp}-name_0 ${tmp}-name

         ${cgi_dir}/YOTEI_JISSEKI_TAIHIHYOU.PRINT ${tmp}-name ${tmp}-search 
       done
       gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sPAPERSIZE=a4 -dNOPLATFONTS -sOutputFile=${home_dir}/HOUMONKAIGO/DOWNLOAD/$USER_ID/YOTEI_JISSEKI_TAIHIHYOU.PDF ${home_dir}/HOUMONKAIGO/DOWNLOAD/$USER_ID/*.PDF
       # HTML の出力
cat << EOF > ${tmp}-html
<HTML>
  <HEAD>
    <SCRIPT type="text/javascript" language="Javascript">
      //<![CDATA[
      window.onload=init
      function init(){
           window.open("/E-LIFE/HOUMONKAIGO/DOWNLOAD/$USER_ID/YOTEI_JISSEKI_TAIHIHYOU.PDF","pdfprint");
           window.self.close();
      }
      //]]>
    </SCRIPT>
  </HEAD>
</HTML>
EOF



       ;;
       # 月間サービス合計表（介護度別）
       9 )
       ${cgi_dir}/GEKKAN_SERVICE_GOUKEI_KAIGODO.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/GEKKAN_SERVICE_GOUKEI_KAIGODO.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       ;;
    esac
    ;;

  # セッションエラーまたはタイムアウト
#  session_error | session_timeout)
#    onload="${MODE}();apl_close('1');"
#    msg="&nbsp;"
#    echo "###ONLOAD### $onload"                > $tmp-calsed
#    cat ${portal_html_dir}/SESSION_ERROR.html  |
#    calsed -f $tmp-calsed -                    > ${tmp}-html
#  ;;

  #その他の場合
  * )
    ${cgi_dir}/JISSEKI_KATSUDOU_INSATSU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;
esac

# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN


## 終了
rm -f ${tmp}-*
exit 0

