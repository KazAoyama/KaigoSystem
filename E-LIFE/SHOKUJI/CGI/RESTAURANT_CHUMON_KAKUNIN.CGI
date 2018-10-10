#!/bin/bash
#
# RESTAURANT_CHUMON_KAKUNIN.CGI : レストラン注文確認CGI
#
# Usage : RESTAURANT_CHUMON_KAKUNIN.CGI
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
dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name

cookie-name                    |
LANG=C sort                    > ${tmp}-cookie
#------------------------------------------------------------

# ディレクトリ設定
#ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"


#------------------------------------------------------------
# 処理モードの決定
eval $(name-source $tmp-name)
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------

#クッキーから施設情報を取得
c_shisetsu="$(nameread "c_shisetsu" ${tmp}-cookie)"

#nameファイルに施設情報を追加
shisetsu="$c_shisetsu"
echo $shisetsu | awk '{print "shisetsu",$1}' >> $tmp-name



#------------------------------------------------------------
#20150819
#upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
#cp -p $tmp-name $tmp-name_origin
#mv -f $tmp-name.new0 $tmp-name

#------------------------------------------------------------

echo ${nyukyosha_id} | awk '{print $1}'  > ${tmp}-user

##################################
# 入居者情報の取得
##################################
#cat ${data_dir}/UNEI/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |
#self 6 1 5 7 8 9                                          |
##1:入居者ID,2:施設ID,3:居室,4:入居日,5:退去日,6:削除フラグ
#LANG=C sort -k1,1                                         |
##対象ID絞込み
#join1 key=1 ${tmp}-user                                   |
##入居者レコード有効判定(削除フラグ、有効期間)
#awk '$(NF)!="9" && $4<="'$target_day'"&&"'$target_day'"<=$5' > $tmp-restaurant_chk_user

#入居者レコード有効判定(削除フラグ、有効期間)
#awk '$6=="'${nyukyosha_id}'" && $7<="'$target_day'" && "'$target_day'"<=$8 && $(NF-2)!="9"' \
# 取得対象を対象施設内の入居者情報に限定（複数施設所属のケースを考慮） 20150907add　
awk '$1=="'$shisetsu'" && $6=="'${nyukyosha_id}'" && $7<="'$target_day'" && "'$target_day'"<=$8 && $(NF-2)!="9"' \
 ${data_dir}/UNEI/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS       |
self 6 1 5 7 8 9                                          |
#1:入居者ID,2:施設ID,3:居室,4:入居日,5:退去日,6:削除フラグ
#LANG=C sort -k1,1                                         > $tmp-restaurant_chk_user
#この段階ではまれに複数レコード（複数部屋契約）の可能性あり、入居日付でソート　20150907
LANG=C sort -k4,5                                         |
#入居者の最新入居情報のみ抽出　20150907
getlast 1 1         > $tmp-restaurant_chk_user



#cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER             |
awk '$(NF-2)!="9"' ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER  |
#対象ID絞込み ※利用者マスタは利用者IDでソート済みの前提
join1 key=1 - $tmp-restaurant_chk_user                        |
#マスタの氏名以外の情報は削除
delf 3/7                                      > $tmp-restaurant_ok_user
#1:入居者ID,2:利用者(入居者)氏名,3:施設ID,4:居室,5:入居日,6:退去日,7:削除フラグ

#エラーチェック
[ $(plus ${PIPESTATUS[@]}) -ne 0 ] && message="入居者情報取得エラー"


if [ ! -s $tmp-restaurant_ok_user ]; then
  message="ご利用権限がありません。"
  #処理をスキップするのでモードクリア
  MODE=""
fi


#------------------------------------------------------------
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#------------------------------------------------------------
# 処理の分岐
case "${MODE}" in
  #初期表示（注文確認画面or予約確認画面 注文カートが空でなければ予約確認画面）
  init )
    ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.DISPLAY ${tmp}-name  > ${tmp}-html
    ;;

#  #表示(必ず注文確認画面を表示)
#  display )
#    ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.DISPLAY ${tmp}-name  > ${tmp}-html
#    ;;

#  #登録する場合(数量指定画面の数量確定ボタン)
#  regist )
#    ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.TOUROKU ${tmp}-name   > ${tmp}-touroku
#
#    if [ $add_menu = "yes" ] ; then
#      #登録してさらにメニュー追加する場合
#      ${cgi_dir}/RESTAURANT_TOPMENU.DISPLAY ${tmp}-name  > ${tmp}-html
#    else
#      #メニュー追加せずに確認画面へ行く場合
#      ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.DISPLAY ${tmp}-name  > ${tmp}-html
#
#    fi
#    ;;

  #登録する場合(数量指定画面の数量確定ボタン)
  registall )
    ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.TOUROKU ${tmp}-name   > ${tmp}-touroku
    #メニュー追加せずに確認画面へ行く場合
    ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.DISPLAY ${tmp}-name   ${tmp}-touroku  > ${tmp}-html

    ;;

  #削除する場合
  delete )
     ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.TOUROKU ${tmp}-name   > ${tmp}-touroku
     ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.DISPLAY ${tmp}-name   > ${tmp}-html

    ;;

#  #修正する場合(数量指定画面の数量確定ボタン)
#  modify )
#    ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.TOUROKU ${tmp}-name  > ${tmp}-touroku
#    if [ $add_menu = "yes" ] ; then
#      #登録してさらにメニュー追加する場合
#      ${cgi_dir}/RESTAURANT_TOPMENU.DISPLAY ${tmp}-name  > ${tmp}-html
#    else
#      #メニュー追加せずに確認画面へ行く場合
#      ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.DISPLAY ${tmp}-name  > ${tmp}-html
#    fi
#    ;;

esac


#--------------------------------------------------------------

if [ "${message}" != "" ] ; then

  #カートファイルが存在している場合、削除
  if [ -e ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type ] ; then
    rm -f ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type
  fi

  #はめ込み文字データまとめファイル作成
  echo "###MESSAGE###" $message     >  $tmp-calsed_result
  echo "###USER_TYPE###" $user_type >> $tmp-calsed_result

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

