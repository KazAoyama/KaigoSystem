#!/bin/bash
#
# RESTAURANT_CHUMON_ICHIRAN.CGI : レストラン実績更新CGI
#
# Usage : RESTAURANT_CHUMON_ICHIRAN.CGI
#
# Written by R.Suzuki Date:2015/05/15 

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


rm -f $tmp-*


#------------------------------------------------------------
# パラメーターの取得
#アイコン起動時はPOSTデータがないため上記でエラーになるのを回避。
if [ "${CONTENT_LENGTH}" != "" ] ; then
dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name
else
: > $tmp-name
fi

cookie-name                    |
LANG=C sort                    > ${tmp}-cookie
#------------------------------------------------------------



#------------------------------------------------------------
# 処理モードの決定
#20150819:
#eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------


#------------------------------------------------------------
#20150819
#upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
#cp -p $tmp-name $tmp-name_origin
#mv -f $tmp-name.new0 $tmp-name

#------------------------------------------------------------

current_time="$(date +%H%M)"

#------------------------------------------------------------
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#------------------------------------------------------------

#クッキーから施設情報を取得
c_shisetsu="$(nameread "c_shisetsu" ${tmp}-cookie)"


#このタイミングでカートファイルが存在している場合、カート削除　20150805
#注文確定や注文消去の際に対象者以外のQRコードをかざした際、カートが残っ
#ているとその人の注文情報を変更・消去してしまうため。
#（実際の運用では基本的に発生しないと思われるケース）
if [ -e ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type ] ; then
  rm -f ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type
fi

##20150907 add ↓

user_type="kanriuser"
#nameファイルにユーザタイプを追加
echo $user_type | awk '{print "user_type",$1}' >> $tmp-name

########################################################
#クッキーの施設情報が未設定の場合は施設選択画面を表示
########################################################
if [ "$c_shisetsu" = "" ] ; then

  ${cgi_dir}/RESTAURANT_SETTEI.DISPLAY ${tmp}-name  > ${tmp}-html

  # HTMLファイルを表示する
  if [ -e "$tmp-html" ];then
    echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
    cat - ${tmp}-html
    exit 0
  fi
fi

#nameファイルに施設情報を追加
shisetsu="$c_shisetsu"
echo $shisetsu | awk '{print "shisetsu",$1}' >> $tmp-name
##20150907 add ↑

# 処理の分岐
case "${MODE}" in
  #初期表示
  init )

    ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.DISPLAY ${tmp}-name > ${tmp}-html
    ;;

  #登録する場合(配膳済みにする)
  regist )
     ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.TOUROKU ${tmp}-name  > ${tmp}-touroku
     ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.DISPLAY ${tmp}-name  ${tmp}-touroku  > ${tmp}-html

    ;;

  #更新する場合
  henkou )
    ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.TOUROKU ${tmp}-name > ${tmp}-touroku
    ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.DISPLAY ${tmp}-touroku  > ${tmp}-html
    ;;

  #未配膳にする場合
  mihaizen )
    ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.TOUROKU ${tmp}-name > ${tmp}-touroku
    ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.DISPLAY ${tmp}-name  ${tmp}-touroku > ${tmp}-html
    ;;

  #レシート再印刷の場合
  print )
    ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.TOUROKU ${tmp}-name > ${tmp}-touroku
    ${cgi_dir}/RESTAURANT_CHUMON_KAKUTEI.DISPLAY ${tmp}-name ${tmp}-touroku > ${tmp}-html
    ;;

  #表示
  display )
    ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.DISPLAY ${tmp}-name > ${tmp}-html
    ;;


  #その他の場合
  * )
    ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.DISPLAY ${tmp}-name > ${tmp}-html
    ;;
esac

#--------------------------------------------------------------

if [ "${message}" != "" ] ; then
  #はめ込み文字データまとめファイル作成
  echo "###MESSAGE###" $message     >  $tmp-calsed_result
  echo "###USER_TYPE###" "kanriuser" >> $tmp-calsed_result

  #20150803 add
  echo "###TARGET_DAY###"     $target_day   >> $tmp-calsed_result
  echo "###TARGET_SHOKUJI_JIKANTAI###"     $target_shokuji_jikantai   >> $tmp-calsed_result

  #はめ込みまとめデータのはめ込み
  calsed -f $tmp-calsed_result  ${html_dir}/RESTAURANT_MESSAGE.html > $tmp-html

fi
# HTMLファイルを表示する
if [ -e "$tmp-html" ];then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
fi

#--------------------------------------------------------------

## 終了
rm -f ${tmp}-*
exit 0

