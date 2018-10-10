#!/bin/bash
#
# HELPER_KATSUDOU_INSATSU.CGI : 訪問介護ヘルパー活動実績照会CGI
#
# Usage : HELPER_KATSUDOU_INSATSU.CGI
#
# Written by K.AOYAMA(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/HOUMONKAIGO/CGI/HOUMONKAIGO.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

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

#cp ${tmp}-name $work_dir/param_name

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
    ${cgi_dir}/HELPER_KATSUDOU_INSATSU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;

  print )
    case "$ChouhyouSentaku" in
       # ホームヘルパー活動記録
       0 )
       mkdir -p ${home_dir}/HOUMONKAIGO/DOWNLOAD/$USER_ID
       rm -f ${home_dir}/HOUMONKAIGO/DOWNLOAD/$USER_ID/*
 
       ${cgi_dir}/HELPER_KATSUDOU_KIROKU.SEARCH ${tmp}-name > ${tmp}-search
        
       cat ${tmp}-search |
       awk '$1=="l"{print}' |
       self 2            |
       # 1:担当ヘルパーID
       LANG=C sort -u    |
       while read helper_id ;do
         awk '$1!="Helperid"' ${tmp}-name |
         cat - <(echo "Helperid" $helper_id) > ${tmp}-name_0
         mv ${tmp}-name_0 ${tmp}-name

         ${cgi_dir}/HELPER_KATSUDOU_KIROKU.PRINT ${tmp}-name ${tmp}-search 
       done
       gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sPAPERSIZE=a4 -dNOPLATFONTS -sOutputFile=${home_dir}/HOUMONKAIGO/DOWNLOAD/$USER_ID/HELPER_KATSUDOU_KIROKU.PDF ${home_dir}/HOUMONKAIGO/DOWNLOAD/$USER_ID/*.PDF
       # HTML の出力
cat << EOF > ${tmp}-html
<HTML>
  <HEAD>
    <SCRIPT type="text/javascript" language="Javascript">
      //<![CDATA[
      window.onload=init
      function init(){
           window.open("/E-LIFE/HOUMONKAIGO/DOWNLOAD/$USER_ID/HELPER_KATSUDOU_KIROKU.PDF","pdfprint");
           window.self.close();
      }
      //]]>
    </SCRIPT>
  </HEAD>
</HTML>
EOF
       #${cgi_dir}/HELPER_KATSUDOU_KIROKU.SEARCH ${tmp}-name > ${tmp}-search
       #${cgi_dir}/HELPER_KATSUDOU_KIROKU.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       # ${cgi_dir}/HELPER_KATSUDOU_INSATSU.SEARCH ${tmp}-name > ${tmp}-search
       # ${cgi_dir}/HELPER_KATSUDOU_INSATSU.EXCEL ${tmp}-name $tmp-search > ${tmp}-html
       ;;
       1 )
       mkdir -p ${home_dir}/HOUMONKAIGO/DOWNLOAD/IKKATSU/$USER_ID
       rm -f ${home_dir}/HOUMONKAIGO/DOWNLOAD/IKKATSU/$USER_ID/*
       ${cgi_dir}/GEKKAN_KATSUDOU_JISSEKI_ICHIRAN.SEARCH ${tmp}-name > ${tmp}-search
       awk '$1=="help"{print $2}'  ${tmp}-search |
       while read helper ;do
         echo "Helperid" $helper |
         cat ${tmp}-name -         > ${tmp}-name_new
         ${cgi_dir}/GEKKAN_KATSUDOU_JISSEKI_ICHIRAN.PRINT ${tmp}-name_new ${tmp}-search 
       done
       gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sPAPERSIZE=a4 -dNOPLATFONTS -sOutputFile=${home_dir}/HOUMONKAIGO/DOWNLOAD/IKKATSU/$USER_ID/GEKKAN_KATSUDOU_JISSEKI_ICHIRAN_HELPER.pdf ${home_dir}/HOUMONKAIGO/DOWNLOAD/IKKATSU/$USER_ID/*_GKJIH.PDF
       # HTML の出力
cat << EOF > ${tmp}-html
<HTML>
  <HEAD>
    <SCRIPT type="text/javascript" language="Javascript">
      //<![CDATA[
      window.onload=init
      function init(){
           window.open("/E-LIFE/HOUMONKAIGO/DOWNLOAD/IKKATSU/$USER_ID/GEKKAN_KATSUDOU_JISSEKI_ICHIRAN_HELPER.pdf","pdfprint");
           window.self.close();
      }
      //]]>
    </SCRIPT>
  </HEAD>
</HTML>
EOF





       ;;
       2 )
       ${cgi_dir}/GEKKAN_KATSUDOU_JISSEKI_ICHIRAN_SHUKEI.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/GEKKAN_KATSUDOU_JISSEKI_ICHIRAN_SHUKEI.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       ;;
       3 )
       ${cgi_dir}/HELPER_HOUMON_NINZU.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/HELPER_HOUMON_NINZU.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       ;;

       6)
       ${cgi_dir}/GEKKAN_JISSEKI_ICHIRAN_HELPER.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/GEKKAN_JISSEKI_ICHIRAN_HELPER.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html 
       ;;

       7 )
       ${cgi_dir}/HELPER_NENKAN_KATSUDOU_ICHIRAN.SEARCH ${tmp}-name > ${tmp}-search
       ${cgi_dir}/HELPER_NENKAN_KATSUDOU_ICHIRAN.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       ;;

       8 )
       ${cgi_dir}/HELPER_KATSUDOU_SERVICE_JIKAN.SEARCH ${tmp}-name >  ${tmp}-search
       ${cgi_dir}/HELPER_KATSUDOU_SERVICE_JIKAN.PRINT ${tmp}-name ${tmp}-search > ${tmp}-html
       ;;
       

       
    esac

    ;;

  #検索する場合
#  search )
#    ${cgi_dir}/HELPER_KATSUDOU_INSATSU.SEARCH ${tmp}-name              > ${tmp}-search
#    ${cgi_dir}/HELPER_KATSUDOU_INSATSU.DISPLAY ${tmp}-name ${tmp}-search > ${tmp}-html
#    ;;


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
    ${cgi_dir}/HELPER_KATSUDOU_INSATSU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;
esac

# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN


## 終了
rm -f ${tmp}-*
exit 0

