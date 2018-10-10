#!/bin/bash
#
# CAREPLAN_IKKATSU_INSATSU.CGI : ケアプラン（介護）MENUCGI
#
# Usage : CAREPLAN_IKKATSU_INSATSU.CGI
#
# Written by K.AOYAMA(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/CAREPLAN/CGI/CAREPLAN.INI &> /dev/null
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
USERID="$(nameread "userid" ${tmp}-name)"
[ -n "${MODE}" ] || MODE="init"

# 処理の分岐
case "${MODE}" in
  #初期表示
  init )
    ${cgi_dir}/CAREPLAN_IKKATSU_INSATSU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;

  #印刷する場合
  allprint )
    mkdir -p ${home_dir}/CAREPLAN/DOWNLOAD/IKKATSU/$USER_ID
    rm -f ${home_dir}/CAREPLAN/DOWNLOAD/IKKATSU/$USER_ID/*
    # 複数の利用者リストの対応
    RiyoushaList="$(nameread "RiyoushaList" ${tmp}-name)"
    echo "${RiyoushaList}" |
    sed 's/,/ /g'          |
    tarr                   |
    LANG=C sort -k1,1      > $tmp-riyousha_list

    Careplan1="$(nameread "careplan1" ${tmp}-name)"
    Careplan2="$(nameread "careplan2" ${tmp}-name)"
    Careplan3="$(nameread "careplan3" ${tmp}-name)"
    Tantoushakaigi="$(nameread "tantoushakaigi" ${tmp}-name)"
    Tantoushairai="$(nameread "tantoushairai" ${tmp}-name)"
    KaigoShienKeika="$(nameread "kaigoshienkeika" ${tmp}-name)"
    Monitoring="$(nameread "monitoring" ${tmp}-name)"
    if [ ${Careplan1} = "1" ] ; then
        cat $tmp-riyousha_list |
        while read riyoushaid ;do
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name
          ${cgi_dir}/CAREPLAN_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
          ${cgi_dir}/CAREPLAN_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html            
        : ; done
    fi
    if [ ${Careplan2} = "1" ] ; then
        cat $tmp-riyousha_list |
        while read riyoushaid ;do
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name
          ${cgi_dir}/CAREPLAN2_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
          ${cgi_dir}/CAREPLAN2_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html            
        : ; done
    fi
    if [ ${Careplan3} = "1" ] ; then
        cat $tmp-riyousha_list |
        while read riyoushaid ;do
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name
          ${cgi_dir}/WEEKPLAN_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
          ${cgi_dir}/WEEKPLAN_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html            
        : ; done
    fi
    if [ ${Tantoushakaigi} = "1" ] ; then
        cat $tmp-riyousha_list |
        while read riyoushaid ;do
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name
          ${cgi_dir}/TANTOUSHAKAIGI_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
          ${cgi_dir}/TANTOUSHAKAIGI_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html            
        : ; done
    fi
    if [ ${KaigoShienKeika} = "1" ] ; then
        cat $tmp-riyousha_list |
        while read riyoushaid ;do
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name
          ${cgi_dir}/KAIGOSHIENKEIKA_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
          ${cgi_dir}/KAIGOSHIENKEIKA_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html            
        : ; done
    fi
    if [ ${Monitoring} = "1" ] ; then
        cat $tmp-riyousha_list |
        while read riyoushaid ;do
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name
          ${cgi_dir}/MONITORING_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
          ${cgi_dir}/MONITORING_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html            
        : ; done
    fi

    gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sPAPERSIZE=a4 -dNOPLATFONTS -sOutputFile=${home_dir}/CAREPLAN/DOWNLOAD/IKKATSU/$USER_ID/${USERID}_CAREPLAN_IKKATSU.PDF ${home_dir}/CAREPLAN/DOWNLOAD/IKKATSU/$USER_ID/*.pdf
# HTML の出力
cat << EOF > ${tmp}-html
<HTML>
  <HEAD>
    <SCRIPT type="text/javascript" language="Javascript">
      //<![CDATA[
      window.onload=init
      function init(){
           window.open("/E-LIFE/CAREPLAN/DOWNLOAD/IKKATSU/${USER_ID}/${USERID}_CAREPLAN_IKKATSU.PDF","pdfprint");
           window.self.close();
      }
      //]]>
    </SCRIPT>
  </HEAD>
</HTML>
EOF
    
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
    ${cgi_dir}/CAREPLAN_IKKATSU_INSATSU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;
esac


[ -s ${tmp}-html ] || {
cat << FIN > $tmp-html
    <script type="text/javascript" language="javascript">
      alert('対象のデータがありません');
    </script>
FIN
}

# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN


## 終了
rm -f ${tmp}-*
exit 0

