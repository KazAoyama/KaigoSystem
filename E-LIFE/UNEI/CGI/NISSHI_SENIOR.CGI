#!/bin/bash
#
# NISSHI_SENIOR.CGI 日誌（シニア）CGI
#
# Usage : NISSHI_SENIOR.CGI
#
# Written by K.AOYAMA(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
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

# ディレクトリ設定
ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"

#------------------------------------------------------------
# 処理モードの決定
eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------

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

self 1 3 $home_dir/TBL/JYUUGYOUIN_MASTER/USER_SHISETSU |
awk '$1=="'$userid'"' > $tmp-user_tateya

user_tateya=$(self 2 $tmp-user_tateya)

[ "$user_tateya" = "_" ] && user_tateya="01"

cat /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR |
awk '$1=="'$shisetsu'"&&$(NF-2)!="9"' |
tee $tmp-select_shisetsu_tateya      |
awk '$2=="'$user_tateya'"{print $2}' |
getlast 1 1      > $tmp-shisetsu_tateya

if [ "$(gyo $tmp-shisetsu_tateya)" = "0" ] ; then
    Tateya=$(self 2 $tmp-select_shisetsu_tateya | LANG=C sort -k1,1 | tail -1)
    user_tateya=$(self 2 $tmp-select_shisetsu_tateya | LANG=C sort -k1,1 | tail -1)
fi

# 処理の分岐
case "${MODE}" in
  #初期表示
  init )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      if [ -z "$Tateya" -o "$Tateya" = "_" ] ; then
         if [ "$user_tateya" = "02" ] ; then
            ${cgi_dir}/NISSHI_CARE.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
         else
            ${cgi_dir}/NISSHI_SENIOR.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
         fi
      elif [ "$Tateya" = "02" -o "$Tateya" = "2" ] ; then
         ${cgi_dir}/NISSHI_CARE.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
      else
         ${cgi_dir}/NISSHI_SENIOR.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
      fi
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-name
    fi
    ;;

  print )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/NISSHI_SENIOR.PRINT ${tmp}-name ${tmp}-check > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-name
    fi
    ;;
  #検索する場合
#  search )
#    ${cgi_dir}/NISSHI_SENIOR.SEARCH ${tmp}-name              > ${tmp}-search
#    ${cgi_dir}/NISSHI_SENIOR.DISPLAY ${tmp}-name ${tmp}-search > ${tmp}-html
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
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      if [ -z "$Tateya" -o "$Tateya" = "_" ] ; then
         if [ "$user_tateya" = "02" ] ; then
            ${cgi_dir}/NISSHI_CARE.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
         else
            ${cgi_dir}/NISSHI_SENIOR.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
         fi
      else
         ${cgi_dir}/NISSHI_SENIOR.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
      fi
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-name
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
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
else
  cat $tmp-html2
fi


## 終了
rm -f ${tmp}-*
exit 0

