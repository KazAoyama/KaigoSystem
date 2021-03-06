#!/bin/bash
#
# GEKKAN_RIYOU_KEIKAKU_INSATSU.CGI : ケアプラン（介護）MENUCGI
#
# Usage : GEKKAN_RIYOU_KEIKAKU_INSATSU.CGI
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
    ${cgi_dir}/GEKKAN_RIYOU_KEIKAKU_IKKATSU_INSATSU.DISPLAY ${tmp}-name > ${tmp}-html
    ;;

  #印刷する場合
  allprint )
    mkdir -p ${home_dir}/CAREPLAN/DOWNLOAD/IKKATSU_GEKKAN/$USER_ID
    rm -f ${home_dir}/CAREPLAN/DOWNLOAD/IKKATSU_GEKKAN/$USER_ID/*
    # 複数の利用者リストの対応
    RiyoushaList="$(nameread "RiyoushaList" ${tmp}-name)"
    echo "${RiyoushaList}" |
    sed 's/,/ /g'          |
    tarr                   |
    LANG=C sort -k1,1      > $tmp-riyousha_list

    cp $tmp-riyousha_list $work_dir/riyousha_list

    Riyouhyou="$(nameread "Riyouhyou" ${tmp}-name)"
    RiyouhyouBeppyou="$(nameread "RiyouhyouBeppyou" ${tmp}-name)"
    Teikyouhyou="$(nameread "Teikyouhyou" ${tmp}-name)"
    TeikyouhyouBeppyou="$(nameread "TeikyouhyouBeppyou" ${tmp}-name)"
#    RiyoushaFutan="$(nameread "RiyoushaFutan" ${tmp}-name)"
    if [ ${Riyouhyou} = "1" ] ; then
        cat $tmp-riyousha_list |
        while read riyoushaid ;do
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name
          ${cgi_dir}/RIYOUHYOU_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
          ${cgi_dir}/RIYOUHYOU_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html
        : ; done
    fi
    if [ ${RiyouhyouBeppyou} = "1" ] ; then
        cat $tmp-riyousha_list |
        while read riyoushaid ;do
           echo "Riyoushaid" $riyoushaid >> ${tmp}-name
           ${cgi_dir}/RIYOUHYOU_BEPPYOU_KAIGO_PRINT.SEARCH ${tmp}-name > ${tmp}-search
           ${cgi_dir}/RIYOUHYOU_BEPPYOU_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html
        : ; done
    fi

# 提供票、提供票別表は関係ある事業者ごとに出力する。
    if [ ${Teikyouhyou} = "1" ] ; then
      : > $tmp-taishou_jigyousho

       cat $tmp-riyousha_list |
       while read riyoushaid ;do
          riyouhyou_timestamp=0
          if [ -s ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOU_RECORD_KAIGO ] ; then
             riyouhyou_timestamp=$(ls --full-time ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOU_RECORD_KAIGO | awk '{gsub(/-/,"",$6);gsub(/:/,"",$7);print $6substr($7,1,6)}')
          fi
          # 利用票別表ファイルの取得
          if [ -s ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO ] ; then
          # 利用票が更新が最近の場合そちらを優先させるため、タイムスタンプを取得
             beppyou_timestamp=$(ls --full-time ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO | awk '{gsub(/-/,"",$6);gsub(/:/,"",$7);print $6substr($7,1,6)}')

             if [ $beppyou_timestamp -gt $riyouhyou_timestamp ] ; then
               cat ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO   |
               awk '$(NF-2)!="9"'            |
#--------------------------------------------------------------
# 利用者ID
               awk '$2=="'${riyoushaid}'"'   |
#--------------------------------------------------------------
# 日付
# --------------------------
#
               awk '$3=="'${hdTaishouYear}'"&&$4=="'$hdTaishouMonth'"'  |
               self 6 |
               uniq   > $tmp-taishou_jigyousho
             fi
          fi
          if [ $(gyo $tmp-taishou_jigyousho) -eq 0 ] ; then

       # 利用票別表ファイルが既に存在する場合はそちらを優先して取得
       # 利用票ファイルの取得
            cat ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOU_RECORD_KAIGO   |
            awk '$(NF-2)!="9"'            |
         #--------------------------------------------------------------
         # 利用者ID
            awk '$2=="'${riyoushaid}'"'   |
         #--------------------------------------------------------------
         # 日付
         # --------------------------
         #
            awk '$3=="'${hdTaishouYear}'"&&$4=="'$hdTaishouMonth'"'  |
         # --------------------------
            self 14 |
            uniq > $tmp-taishou_jigyousho
          fi
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name       
          self 1 $tmp-taishou_jigyousho |
          while read taishoujigyousho ; do
            echo "Jigyoushaid" $taishoujigyousho >> ${tmp}-name
            ${cgi_dir}/TEIKYOUHYOU_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
            ${cgi_dir}/TEIKYOUHYOU_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html
          : ; done
       : ;done
    fi
    if [ ${TeikyouhyouBeppyou} = "1" ] ; then
      : > $tmp-taishou_jigyousho
      cat $tmp-riyousha_list |
      while read riyoushaid ;do
         riyouhyou_timestamp=0
         if [ -s ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOU_RECORD_KAIGO ] ; then
            riyouhyou_timestamp=$(ls --full-time ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOU_RECORD_KAIGO | awk '{gsub(/-/,"",$6);gsub(/:/,"",$7);print $6substr($7,1,6)}')
         fi
      # 利用票別表ファイルの取得
         if [ -s ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO ] ; then
      # 利用票が更新が最近の場合そちらを優先させるため、タイムスタンプを取得
            beppyou_timestamp=$(ls --full-time ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO | awk '{gsub(/-/,"",$6);gsub(/:/,"",$7);print $6substr($7,1,6)}')

            if [ $beppyou_timestamp -gt $riyouhyou_timestamp ] ; then
                cat ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO   |
#--------------------------------------------------------------
# 利用者ID
                awk '$2=="'${riyoushaid}'"'   |
#--------------------------------------------------------------
# 日付
# --------------------------
#
                awk '$3=="'${hdTaishouYear}'"&&$4=="'$hdTaishouMonth'"'  |
                self 6 |
                uniq   > $tmp-taishou_jigyousho
            fi
          fi
          if [ $(gyo $tmp-taishou_jigyousho) -eq 0 ] ; then

       # 利用票別表ファイルが既に存在する場合はそちらを優先して取得
       # 利用票ファイルの取得
            cat ${pompa_dir}/GETSUGAKU_RIYOU_KAIGO/${riyoushaid}/RIYOUHYOU_RECORD_KAIGO   |
            awk '$(NF-2)!="9"'            |
         #--------------------------------------------------------------
         # 利用者ID
            awk '$2=="'${riyoushaid}'"'   |
         #--------------------------------------------------------------
         # 日付
         # --------------------------
         #
            awk '$3=="'${hdTaishouYear}'"&&$4=="'$hdTaishouMonth'"'  |
         # --------------------------
            self 14 |
            uniq > $tmp-taishou_jigyousho
          fi
          echo "Riyoushaid" $riyoushaid >> ${tmp}-name       
          self 1 $tmp-taishou_jigyousho |
          while read taishoujigyousho ; do
            echo "Jigyoushaid" $taishoujigyousho >> ${tmp}-name
            ${cgi_dir}/TEIKYOUHYOU_BEPPYOU_KAIGO_PRINT.SEARCH ${tmp}-name > ${tmp}-search
            ${cgi_dir}/TEIKYOUHYOU_BEPPYOU_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html            
          : ; done
       : ;done
    fi
#    if [ ${RiyoushaFutan} = "1" ] ; then
#        ${cgi_dir}/RIYOUSHA_FUTAN_KAIGO.SEARCH ${tmp}-name > ${tmp}-search
#        ${cgi_dir}/RIYOUSHA_FUTAN_KAIGO.PRINT $tmp-name ${tmp}-search >> ${tmp}-html            
#    fi


    gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sPAPERSIZE=a4 -dNOPLATFONTS -sOutputFile=${home_dir}/CAREPLAN/DOWNLOAD/IKKATSU_GEKKAN/$USER_ID/${USERID}_GEKKAN_RIYOU_KEIKAKU.PDF ${home_dir}/CAREPLAN/DOWNLOAD/IKKATSU_GEKKAN/$USER_ID/*.pdf
# HTML の出力
cat << EOF > ${tmp}-html
<HTML>
  <HEAD>
    <SCRIPT type="text/javascript" language="Javascript">
      //<![CDATA[
      window.onload=init
      function init(){
           window.open("/E-LIFE/CAREPLAN/DOWNLOAD/IKKATSU_GEKKAN/${USER_ID}/${USERID}_GEKKAN_RIYOU_KEIKAKU.PDF","pdfprint");
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
    ${cgi_dir}/GEKKAN_RIYOU_KEIKAKU_IKKATSU_INSATSU.DISPLAY ${tmp}-name > ${tmp}-html
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

