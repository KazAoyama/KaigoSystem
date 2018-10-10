#!/bin/bash
#
# SCHEDULE_EVENT_TOUROKU.CGI : スケジュール詳細CGI
#
# Usage : SCHEDULE_CARE_TOUROKU.CGI
#
# Written by aoyagi

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

cp $tmp-name $work_dir/param_name

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
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/SCHEDULE_SHISETSU_TOUROKU.DISPLAY ${tmp}-name ${tmp}-check  > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-name
    fi
    ;;

  #検索
  search )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    cp $tmp-check $work_dir/check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
       ${cgi_dir}/SCHEDULE_SHISETSU_TOUROKU.SEARCH ${tmp}-name > $tmp-search
       ${cgi_dir}/SCHEDULE_SHISETSU_TOUROKU.DISPLAY ${tmp}-name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-name
    fi
    ;;

  #登録する場合
  regist )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/SCHEDULE_SHISETSU_TOUROKU.TOUROKU ${tmp}-name > ${tmp}-data
#       ${cgi_dir}/SCHEDULE_CARE_TOUROKU.SEARCH ${tmp}-name > $tmp-search
#      ${cgi_dir}/SCHEDULE_CARE_TOUROKU.DISPLAY ${tmp}-name ${tmp}-check $tmp-search ${tmp}-data > ${tmp}-html
      ${cgi_dir}/SCHEDULE_SHISETSU_TOUROKU.DISPLAY ${tmp}-name ${tmp}-check ${tmp}-data > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-name
    fi
    ;;

  #更新する場合
  update )
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/SCHEDULE_SHISETSU_TOUROKU.TOUROKU ${tmp}-name > ${tmp}-data
#       ${cgi_dir}/SCHEDULE_CARE_TOUROKU.SEARCH ${tmp}-name > $tmp-search
#      ${cgi_dir}/SCHEDULE_CARE_TOUROKU.DISPLAY ${tmp}-name ${tmp}-check $tmp-search ${tmp}-data > ${tmp}-html
      ${cgi_dir}/SCHEDULE_SHISETSU_TOUROKU.DISPLAY ${tmp}-name ${tmp}-check ${tmp}-data > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-name
    fi
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
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    cp $tmp-check $work_dir/check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/SCHEDULE_CARE_TOUROKU.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
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

