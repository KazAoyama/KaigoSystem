#!/bin/bash
#
# RESTAURANT_TOPMENU.CGI : レストラントップメニューCGI
#
# Usage : RESTAURANT_TOPMENU.CGI
#
# Written by R.Suzuki Date:2015/05/13 

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


rm -f $tmp-*

#--------------------------------------------------------------
#--------------------------------------------------------------



#------------------------------------------------------------
# パラメーターの取得
# パラメーターの取得
#アイコン起動時はPOSTデータがないため上記でエラーになるのを回避。
if [ "${CONTENT_LENGTH}" != "" ] ; then
dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name
else
:> $tmp-name
fi

#20150907復活
#20150819
cookie-name                    |
LANG=C sort                    > ${tmp}-cookie





#------------------------------------------------------------

# ディレクトリ設定
#ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"


#------------------------------------------------------------
# 処理モードの決定
#20150819
#eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
#[ -z "${MODE}" ] && MODE="init"
[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#------------------------------------------------------------

#クッキーから施設情報を取得 20150907
c_shisetsu="$(nameread "c_shisetsu" ${tmp}-cookie)"


#------------------------------------------------------------
#20150819
#upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
#cp -p $tmp-name $tmp-name_origin
#mv -f $tmp-name.new0 $tmp-name

#------------------------------------------------------------

current_time="$(date +%H%M)"


if [ "${MODE}" = "init"  ] ; then

#★デバッグ用 実際のバーコー ((barcod))はPOSTで受け取る。
#testid="00000151"
#testid="00000546"
#testid="00000491"
#testid="00000GGG"

#　?久子
#testid="00000562"
#testid="00001258"
#barcode=$(echo "NYK$testid")

  ##20150907 add ↓
  user_type="enduser"
  #nameファイルにユーザタイプを追加
  echo $user_type | awk '{print "user_type",$1}' >> $tmp-name

  #入居者コードを変数と中間ファイルにセット
  nyukyosha_id=$(echo ${barcode}  | awk '{print substr($1,4)}')


  #nameファイルに入居者IDを追加
  echo ${barcode}  | awk '{print "nyukyosha_id",substr($1,4)}' >> $tmp-name

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



  #20150803add↓
  #処理対象日付の設定
  target_day="$(date +%Y%m%d)"

#デバッグ用
#target_day="20150811"

  #処理対象月の設定
  target_month="$(echo $target_day | cut -c-6 )"

  #nameファイルに処理対象日付を追加
  echo $target_day | awk '{print "target_day",$1}' >> $tmp-name

  #食事時間帯（朝：昼：夕）の確認
  if [ $current_time -gt "1644" ] ; then
    # 1645以降以は夕食メニュー
    target_shokuji_jikantai=3
  elif [ $current_time -gt "1044" ] ; then
    # 1045以降以は昼食メニュー
    target_shokuji_jikantai=2
  elif [ $current_time -gt "0614" ] ; then
    # 0615以降以は朝食メニュー
    target_shokuji_jikantai=1
  else
    # 0614以前は夕食メニューのまま
    target_shokuji_jikantai=3
  fi

#デバッグ用
#target_shokuji_jikantai="1"

  #nameファイルに処理対象食事時間帯を追加
  echo $target_shokuji_jikantai | awk '{print "target_shokuji_jikantai",$1}' >> $tmp-name

#  user_type="enduser"
#  #nameファイルにユーザタイプを追加
#  echo $user_type | awk '{print "user_type",$1}' >> $tmp-name

  #20150803add↑


  if [ "$barcode" = "" ] ; then
    message="ご利用権限がありません。"
    #はめ込み文字データまとめファイル作成
    echo "###MESSAGE###" $message     >  $tmp-calsed_result

    #20150803 add
    echo "###TARGET_DAY###"     $target_day   >> $tmp-calsed_result
    echo "###TARGET_SHOKUJI_JIKANTAI###"     $target_shokuji_jikantai   >> $tmp-calsed_result

    #はめ込みまとめデータのはめ込み
    calsed -f $tmp-calsed_result  ${html_dir}/RESTAURANT_MESSAGE.html > $tmp-html
    echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
    cat - ${tmp}-html
    exit 1
  fi



  user_shubetu=$(echo ${barcode}  | awk '{print substr($1,1,3)}')

  if [ "$user_shubetu" != "NYK" ] ; then
    message="ご入居者以外はご利用できません。"
    #はめ込み文字データまとめファイル作成
    echo "###MESSAGE###" $message     >  $tmp-calsed_result
    echo "###USER_TYPE###" $user_type >> $tmp-calsed_result

    #20150803 add
    echo "###TARGET_DAY###"     $target_day   >> $tmp-calsed_result
    echo "###TARGET_SHOKUJI_JIKANTAI###"     $target_shokuji_jikantai   >> $tmp-calsed_result

    #はめ込みまとめデータのはめ込み
    calsed -f $tmp-calsed_result  ${html_dir}/RESTAURANT_MESSAGE.html > $tmp-html
    echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
    cat - ${tmp}-html
    exit 1
  fi

else

  #nameファイルに施設情報を追加 20150907add
  shisetsu="$c_shisetsu"
  echo $shisetsu | awk '{print "shisetsu",$1}' >> $tmp-name

fi

# 入居者情報の取得
##################################
#入居者レコード有効判定(削除フラグ、有効期間)
#awk '$6=="'${nyukyosha_id}'" && $7<="'$target_day'" && "'$target_day'"<=$8 && $(NF-2)!="9"' \
# 取得対象を対象施設内の入居者情報に限定（複数施設所属のケースを考慮） 20150907add　
awk '$1=="'$shisetsu'" && $6=="'${nyukyosha_id}'" && $7<="'$target_day'" && "'$target_day'"<=$8 && $(NF-2)!="9"' \
 ${data_dir}/UNEI/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS        |
self 6 1 5 7 8 9                                          |
#1:入居者ID,2:施設ID,3:居室,4:入居日,5:退去日,6:削除フラグ
#LANG=C sort -k1,1                                         > $tmp-restaurant_chk_user
#この段階ではまれに複数レコード（複数部屋契約）の可能性あり、入居日付でソート　20150907
LANG=C sort -k4,5                                         |
#入居者の最新入居情報のみ抽出　20150907
getlast 1 1         > $tmp-restaurant_chk_user


awk '$(NF-2)!="9"'  ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER  |
#対象ID絞込み ※利用者マスタは利用者IDでソート済みの前提
join1 key=1 - $tmp-restaurant_chk_user                    |
#確認用ファイル
tee $tmp-work-restaurant_chk_user         |
#マスタの氏名以外の情報は削除
delf 3/7                                      > $tmp-restaurant_ok_user
#1:入居者ID,2:利用者(入居者)氏名,3:施設ID,4:居室,5:入居日,6:退去日,7:削除フラグ


#エラーチェック
[ $(plus ${PIPESTATUS[@]}) -ne 0 ] && message="入居者情報取得エラー"

#入居者名前
nyukyosha_name=$(cat $tmp-restaurant_ok_user | awk '{print $2}')
#部屋番号
room_no=$(cat $tmp-restaurant_ok_user | awk '{print $4}')

#20150907 複数施設対応に伴い、クッキーからの取得に変更
#施設IDセット
#shisetsu=$(cat $tmp-restaurant_ok_user | awk '{print $3}')

if [ $(gyo ${tmp}-restaurant_ok_user) -lt 1 ]; then
  message="ご利用権限がありません。"
  #処理をスキップするのでモードクリア
  MODE=""
fi




#------------------------------------------------------------
# 処理の分岐
case "${MODE}" in
  #初期表示
  init )


    #ディレクトリ作成（ない場合）
    mkdir -p ${ap_dir}/SESSION/

    #注文カートファイル削除
    rm ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type

    ##################################
    # 食事予約を取得し注文カートにセット
    ##################################

#20150803del
#    #食事時間帯（朝：昼：夕）の確認
#    if [ $current_time -gt "1644" ] ; then
#      # 1645以降以は夕食メニュー
#      target_shokuji_jikantai=3
#    elif [ $current_time -gt "1044" ] ; then
#      # 1045以降以は昼食メニュー
#      target_shokuji_jikantai=2
#    elif [ $current_time -gt "0614" ] ; then
#      # 0615以降以は朝食メニュー
#      target_shokuji_jikantai=1
#    else
#      # 0614以前は夕食メニューのまま
#      target_shokuji_jikantai=3
#    fi


    #食事予約ファイルが存在する場合
    if [ -s /DATA/E-LIFE/SHOKUJI/RESTAURANT/${shisetsu}/${target_month}/SCHEDULE_RESTAURANT_ORDER ] ; then


        #メニュー表示制御マスタが存在しない場合への対処（ジョインエラー回避）
        :> $tmp-restaurant_menu
        if [ -s ${home_dir}/SHOKUJI/POMPA/${shisetsu}/SHOKUJI_RESTAURANT_MENU ] ; then
          self 1 2 ${home_dir}/SHOKUJI/POMPA/${shisetsu}/SHOKUJI_RESTAURANT_MENU |
          LANG=C sort -k1,1 > $tmp-restaurant_menu
        fi
        [ $(gyo $tmp-restaurant_menu) -eq 0 ] && echo "_" "_" > $tmp-restaurant_menu

        ###########################################################################
        #予約メニューをスケジュール（運営-スケジュールＭＥＮＵ-ご入居者予定）から取得する

#        cat /DATA/E-LIFE/SHOKUJI/RESTAURANT/${shisetsu}/${target_month}/SCHEDULE_RESTAURANT_ORDER |
        #1:施設ID 2:スケジュールID 3:予約日 4:食事メニューID 5:入居者数量 6:ゲスト数量 7:キャンセル日 8:食事実績ID1 9:食事実績ID2 10:入居者ID 11:食事時間帯区分 12:削除フラグ 13:日付時刻 14:ユーザID
        awk '$1=="'${shisetsu}'" && $3=="'${target_day}'" && $10=="'${nyukyosha_id}'" && $7=="_" && $8=="_" && $9=="_" && $11=="'$target_shokuji_jikantai'" && $(NF-2)!="9" { print "'${nyukyosha_id}'",$4,$5,$6,$2}' \
        /DATA/E-LIFE/SHOKUJI/RESTAURANT/${shisetsu}/${target_month}/SCHEDULE_RESTAURANT_ORDER |
        LANG=C sort -k2,2  | 
        #予約日が今日で未キャンセル、食事実績なしの予約を抽出
        #1:入居者ID 2:メニューID 3:入居者数量 4:ゲスト数量
        #食事メニューとつき合わせ
        join1 key=2 ${home_dir}/SHOKUJI/POMPA/${shisetsu}/SHOKUJI_MENU  - |
        #1:入居者ID 2:メニューID 3:メニュー名 4:食事種類 5:施設ID 6:建屋ID 7:入居者価格 8:ゲスト１価格
        #9:ゲスト２価格 10:スタッフ価格 11:朝食 12:昼食 13:夕食 14:おやつ 15:期間From(西暦) 16:期間To(西暦)
        #17:表示色 18:表示順 19:喫食率計算対象 20:予備項目3 21:予備項目4 22:予備項目5 23:削除フラグ 24:日時 
        #25:ユーザー 26:入居者数量 27:ゲスト数量 28:スケジュールID
        awk '$(NF-2)!="9" && $15<="'$target_day'" && "'$target_day'"<=$16 {print $1,$2,$11,$12,$13,$26=="_"?0:$26,$27=="_"?0:$27,$28,"_","_","'$target_day'","'$target_shokuji_jikantai'","_","_","1","'$(date +%Y%m%d)'","'$(date +%H%M%S)'" }'    |
        # 1:入居者ID 2:メニューID 3:朝食フラグ 4:昼食フラグ 5:夕食フラグ 6:入居者数量 7:ゲスト数量
        #  8:予約フラグ(スケジュールID) 9:注文番号 10:注文受付時刻 11:注文受付日付 12:食事時間帯  13:予備１、14:予備２ 15:削除フラグ 16:更新日付 17:更新時刻
 
        # レストラン非表示の処理
        #    join2 +"_" key=2 <(self 1 2 ${home_dir}/SHOKUJI/POMPA/${shisetsu}/SHOKUJI_RESTAURANT_MENU) |
        join2 +"_" key=2 $tmp-restaurant_menu - |
        awk '$3!="1"' |
        # 食事時間帯による表示メニュー判定
        if [ $target_shokuji_jikantai -eq 1 ] ; then
         awk '$4=="1"'
        elif [ $target_shokuji_jikantai -eq 2 ] ; then
         awk '$5=="1"'
        else
         awk '$6=="1"'
        fi |
        #表示フラグ、朝食フラグ 昼食フラグ 夕食フラグを削除
        delf 3/6        |
        #連番を付与
        juni            |
        # 1:連番 2:入居者ID 3:メニューID 4:入居者数量 5:ゲスト数量 6:予約フラグ(スケジュールID) 7:注文番号
        #  8:注文受付時刻 9:注文受付日付 10:食事時間帯 11:予備１ 12:予備２ 13:削除フラグ 14:更新日付 15:更新時刻
        maezero 1.4 > ${tmp}-resutaurant_cart.$nyukyosha_id


        #エラーチェック
        [ $(plus ${PIPESTATUS[@]}) -ne 0 ] && message="予約メニュー取得エラー"


        ###########################################################################
        #予約メニューがすでに注文されてるか注文明細をチェックし、
        #注文されてる場合は該当する予約メニューをカートから除外する。

        #ディレクトリなかったら作成
        if [ ! -e ${pompa_dir}/${shisetsu}/${target_month} ] ; then
          mkdir -p ${pompa_dir}/${shisetsu}/${target_month}
        fi

        
        #ファイルが存在しないとき（初回実行時）のための予防措置
        touch ${pompa_dir}/${shisetsu}/${target_month}/RESTAURANT_CHUMON_MEISAI_${target_day}
        

#        cat ${pompa_dir}/${shisetsu}/${target_month}/RESTAURANT_CHUMON_MEISAI_${target_day}                 |
        # 1:施設ID 2:注文受付日 3:食事時間帯（朝昼夜）4:注文番号 5:注文明細ペア番号 6:入居者ID 7:入居者ゲストフラグ
        # 8:食事種類 9:メニューID 10:メニュー名 11:表示順(>スペースは999999に変換済み) 12:数量  13:食事実績
        # 14:予約フラグ(スケジュールID)　15:予備１ 16:予備２ 17:予備３ 18:予備４
        # 19:削除フラグ 20:更新日時 21:ユーザID　

        # 該当する食事時間帯に入居者が注文した予約メニュー(予約フラグ(スケジュールID))を絞り込む
        # ※マスタがゼロ件だと結合エラーになるためダミーレコード追加
        awk '$3=="'$target_shokuji_jikantai'" && $6=="'$nyukyosha_id'" &&  $14!="_"  && $(NF-2)!="9"  { print $14,"orderd"}END{print "dummy","dummy"}' \
        ${pompa_dir}/${shisetsu}/${target_month}/RESTAURANT_CHUMON_MEISAI_${target_day} |
        #予約フラグ(スケジュールID)でソートしてカート内の予約メニューとジョイン
        LANG=C sort -k1,1                                                                      |
        join2 key=6 - <(LANG=C sort -k6,6 ${tmp}-resutaurant_cart.$nyukyosha_id )              |
        # 1:連番 2:入居者ID 3:メニューID 4:入居者数量 5:ゲスト数量 6:予約フラグ(スケジュールID) 
        # 7:注文済み判定用のフィールド 8:注文番号 9:注文受付時刻
        #  10:注文受付日付 11:食事時間帯 12:予備１ 13:予備２ 14:削除フラグ 15:更新日付 16:更新時刻
        #まだ注文されていない予約メニューだけ残す
        awk '$7!="orderd"'    |
        #注文済み判定用のフィールドを削ってカートを作成
        delf 7               > ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type
        # 1:連番 2:入居者ID 3:メニューID 4:入居者数量 5:ゲスト数量 6:予約フラグ(スケジュールID) 7:注文番号 8:注文受付時刻 
        # 9:注文受付日付 10:食事時間帯 11:予備１ 12:予備２ 13:削除フラグ 14:更新日付 15:更新時刻

        #エラーチェック
        [ $(plus ${PIPESTATUS[@]}) -ne 0 ] && message="カート内注文済み予約メニュー除外エラー"

    else
        #予約ファイルがない場合は空のカートを作成
        touch ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type
    fi

    #予約有無の判定
    if [ $(gyo ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type) -gt 0 ] ; then

      #予約ありの場合、予約確認画面を表示
      ${cgi_dir}/RESTAURANT_CHUMON_KAKUNIN.DISPLAY ${tmp}-name > ${tmp}-html

    else
      #予約なしの場合、メニュー画面表示
      ${cgi_dir}/RESTAURANT_TOPMENU.DISPLAY ${tmp}-name  > ${tmp}-html
    fi

    ;;

  #表示
  display )
      #メニュー画面表示
      ${cgi_dir}/RESTAURANT_TOPMENU.DISPLAY ${tmp}-name  > ${tmp}-html
    ;;

  #ドリンクメニュー表示
  drink )
      #メニュー画面表示
      ${cgi_dir}/RESTAURANT_TOPMENU.DISPLAY ${tmp}-name  > ${tmp}-html
    ;;

  #登録する場合
  regist )
    ${cgi_dir}/RESTAURANT_TOPMENU.DISPLAY ${tmp}-name  > ${tmp}-html

    ;;

esac

if [ "${message}" != "" ];then

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




## 終了
rm -f ${tmp}-*
exit 0

