#!/bin/bash
#
# CARE_SHISETSU_CHECKLIST.CGI : ケア施設チェックリストCGI
#
# Usage : CARE_SHISETSU_CHECKLIST.CGI
#
# Written by R.suzuki(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/CARE_KAIGOSAKUSEI/CGI/CARE_KAIGOSAKUSEI.INI &> /dev/null
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



#入居者IDをクッキーの値で更新（後続処理のuplで上書きされる前提）
#if [ "$ck_riyoshaid" != "" -a "$ck_riyoshaid" != "_" ] ; then
#
#  echo "Riyoushaid $ck_riyoshaid" >> $tmp-name
#  echo "riyosha_name $ck_riyoshaid" >> $tmp-name

##入居者IDをクッキーの値で更新（後続処理のuplで上書きされる前提）
#elif [ "$ck_room" != "" -a "$ck_room" != "---" -a "$ck_room" != "_" ] ; then
#
#  echo "room_select $ck_room" >> $tmp-name
#
  # 部屋番号をもとに利用者IDを取得する
  # SHISETSU_RIYOUSHA_STATUS
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id 7:契約開始
  # TODO:同一部屋番号複数入居者のケースの優先順はAJAX部品に合わせる

#  Riyoushaid=$(awk '$(NF-2)!=9 && $5=="'${ck_room}'"{print $6,$7} ' ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS  |  LANG=C sort -k2,2 | self 1  |  head -n1 )
#  echo "Riyoushaid  $Riyoushaid" >> $tmp-name
#  echo "riyosha_name   $Riyoushaid" >> $tmp-name
#
#fi

#    #入居者IDをクッキーの値で更新（後続処理のuplで上書きされる前提）
#    if [ "$ck_riyoshaid" != "" -a "$ck_riyoshaid" != "_" ] ; then
#     echo "Riyoushaid $ck_riyoshaid" >> $tmp-name
#     echo "riyosha_name $ck_riyoshaid" >> $tmp-name
#    fi

if [ "${MODE}" = "init" ] ; then
    #リクエストに入居者IDがセットされておらず、クッキーに入居者IDがセットされて
    #いる場合、クッキーの値でリクエストを更新（後続処理のuplで上書きされる前提）
    if [ "$riyosha_name" == "" -o "$riyosha_name" == "_" ] && [ "$ck_riyoshaid" != "" -a "$ck_riyoshaid" != "_" ] ; then
      echo "Riyoushaid $ck_riyoshaid" >> $tmp-name
      echo "riyosha_name $ck_riyoshaid" >> $tmp-name
    fi
fi


#S_CHK=$(date +%Y%m%d%H%M%S.%N)

#------------------------------------------------------------
#upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
LANG=C sort -k1,1  $tmp-name |
upl key=1 ${tmp}-cookie - > $tmp-name.new0
cp -p $tmp-name $tmp-name_origin
mv -f $tmp-name.new0 $tmp-name

#echo "USER_ID kaizen" >> $tmp-name
#------------------------------------------------------------

#E_CHK=$(date +%Y%m%d%H%M%S.%N)

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

    #入居者IDをクッキーの値で更新（後続処理のuplで上書きされる前提）
#    if [ "$ck_riyoshaid" != "" -a "$ck_riyoshaid" != "_" ] ; then
#     echo "Riyoushaid $ck_riyoshaid" >> $tmp-name
#     echo "riyosha_name $ck_riyoshaid" >> $tmp-name
#    fi

    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.SEARCH ${tmp}-name > $tmp-init
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.DISPLAY ${tmp}-name ${tmp}-check ${tmp}-init > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi
    ;;

  #登録する場合
  regist )

    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.TOUROKU ${tmp}-name > ${tmp}-data
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.SEARCH ${tmp}-name > $tmp-search
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.DISPLAY ${tmp}-name ${tmp}-check ${tmp}-data $tmp-search> ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi

    ;;

  #検索する場合
  search | search_room)

    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.SEARCH ${tmp}-name              > ${tmp}-search
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.DISPLAY ${tmp}-name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi

    ;;

  #印刷する場合
  print )

    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.SEARCH ${tmp}-name              > ${tmp}-search
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.PRINT ${tmp}-name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
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
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/CARE_SHISETSU_CHECKLIST.DISPLAY ${tmp}-name ${tmp}-check > ${tmp}-html
    else
       ${ch_cgi_dir}/SIGN_IN.CGI
    fi

    ;;
esac





# HTMLの出力（ヘッダでクッキーに情報セットしている。）
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN


## 終了
rm -f ${tmp}-*
exit 0

