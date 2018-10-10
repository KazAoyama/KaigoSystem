#!/bin/bash
#
# RESTAURANT_CHUMON_KAKUTEI.CGI : レストラン注文確定CGI
#
# Usage : RESTAURANT_CHUMON_KAKUTEI.CGI
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
ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"


#------------------------------------------------------------
# 処理モードの決定
#20150819
#eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------

#クッキーから施設情報を取得
#c_shisetsu="$(nameread "c_shisetsu" ${tmp}-cookie)"


# TEST 20150921
c_shisetsu="0003"


#nameファイルに施設情報を追加
shisetsu="$c_shisetsu"
echo $shisetsu | awk '{print "shisetsu",$1}' >> $tmp-name


# 管理者モード（注文一覧経由の修正）でバーコードがセットされていない場合
# 処理を抜ける
if [ "$post_camera" = "mod"  -o  "$post_camera" = "del" ] ; then

  #モードの設定
  if [ "$post_camera" = "mod" ] ; then
    MODE="regist"

  elif [ "$post_camera" = "del" ] ; then
    MODE="delete"
  fi

  #ユーザ種別設定
  user_type="kanriuser"

  #バーコードが空の場合
  if [ "${barcode}" = ""  -o "${barcode}" = "_"  ] ; then

    message="コード情報がセットされていません。"
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
    #バーコード入っていなければそのままでる。
    exit 1

  else
  #バーコードセットされてる場合

    #ユーザ種別の判定
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

    else
      #入居者コードを変数と中間ファイルにセット
      nyukyosha_id=$(echo ${barcode}  | awk '{print substr($1,4)}')

      #カートファイルが存在している場合
      if [ -e ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type ] ; then

        #念のため10分以内にカートのレコードが操作されていることをチェック
        #※注文一覧から変更ボタン経由で更新したとき、万一古いカート（ごみ）が残っていたときにその
        #　内容を元に注文変更,注文消去:を実施されてしまうケースを回避するため。
        #　例：
        #　Bさんの注文を変更しようとしたが、誤って注文一覧画面ではAさんの注文の変更ボタンを押下し、QRはBさんのでスキャンしたとする
        #  。このときBさんのカートがサーバ上にないためエラーとなるが、Aさんのカートが残ってしまう。
        #  （QRアプリを経由した時点でBさんの入居者IDしか情報がないため、Aさんのカートをクリアすることができずごみとして残る。）
        #  その後、Aさんの注文を変更しようとしたところ、再び誤ってCさん(ここはBさんでもよい)の注文を画面で変更したうえでAさん
        #  のQRでスキャンすると前述のAさんの過去のごみカートをもとに注文変更してしまう。
        #　上記のように誤操作を繰り返した際（Aさんの形で処理されるパターン）に発生する事象でかなりのレアケースではあるが、
        #  回避策（確率をさらに下げる）として10分以内にカートが更新されていることをチェック。
        #  仮に10分以内この事象が発生した場合の影響範囲は「配膳未」の状態の注文情報。「配膳済」の注文情報の変更は
        #  注文確定処理(RESTAURANT_CHUMON_KAKUTEI.TOUROKU)でブロック(エラーにする)しているので食事実績作成済みの注文には影響ない。
        #  →注文変更の場合、レシートが出た時点、配膳時点、などで気づくことができる。
        #    注文消去の場合、結果的にQRの対象者の注文が消えるので目的通りとなる。
        #
        # カートに10分以内に更新されたレコードが存在することをチェック
        timesafe_chk=$( self NF-1 NF  ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type | awk ' $1$2>="'$(date +%Y%m%d%H%M%S  -d '10 minute ago')'"' | gyo )

        if [ $timesafe_chk -eq 0 ] ; then 

          #カートファイルが存在している場合、削除
          if [ -e ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type ] ; then
           rm -f ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type
          fi

          message="時間が経過しているため、再度操作をやり直してください。"
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
      #カートファイルが存在ししない場合

        message="ご入居者情報が一致しません。"
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
    fi

  fi

#  #入居者IDをセット
#  echo ${nyukyosha_id}  | awk '{print $1 }' > ${tmp}-user

  #nameファイルに入居者IDを追加
  echo ${nyukyosha_id}  | awk '{print "nyukyosha_id",$1}'  >> $tmp-name
  #nameファイルにユーザ種別を追加
  echo ${user_type}  | awk '{print "user_type",$1 }'       >> $tmp-name
  #nameファイルにユーザ種別を追加
  echo ${MODE}  | awk '{print "MODE",$1 }'                 >> $tmp-name


elif [ "$nyukyosha_id" = "" -o "$nyukyosha_id" = "_" ] ; then
#入居者IDが未セットの場合、

  message="ご入居者情報が指定されていません。"
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

#------------------------------------------------------------
#20150819
#upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
#cp -p $tmp-name $tmp-name_origin
#mv -f $tmp-name.new0 $tmp-name

#------------------------------------------------------------


#入居者IDをセット
#echo ${nyukyosha_id}  | awk '{print $1 }' > ${tmp}-user

##################################
# 入居者情報の取得
##################################
#cat ${data_dir}/UNEI/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |
#self 6 1 5 7 8 9                                          |
##1:入居者ID,2:施設ID,3:居室,4:入居日,5:退去日,6:削除フラグ
#LANG=C sort -k1,1                                         |
#対象ID絞込み
#join1 key=1 ${tmp}-user                                   |
#入居者レコード有効判定(削除フラグ、有効期間)
#awk '$(NF)!="9" && $4<="'$today'"&&"'$today'"<=$5' > $tmp-restaurant_chk_user

##cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER             |
#awk '$(NF-2)!="9"'                                        |
#対象ID絞込み ※利用者マスタは利用者IDでソート済みの前提
#join1 key=1 - $tmp-restaurant_chk_user                    |
#確認用ファイル
#tee $tmp-work-restaurant_chk_user         |
#マスタの氏名以外の情報は削除
#delf 3/7                                      > $tmp-restaurant_ok_user
#1:入居者ID,2:利用者(入居者)氏名,3:施設ID,4:居室,5:入居日,6:退去日,7:削除フラグ
#エラーチェック
#[ $(plus ${PIPESTATUS[@]}) -ne 0 ] && error_exit "入居者情報取得エラー"

#------------------------------------------------------------
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#------------------------------------------------------------
# 処理の分岐
case "${MODE}" in

  #登録する場合
  regist )

    #カートに有効なレコードがなければエラー
    meisai_cnt=$(cat  ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type | awk '$(NF-2)!=9' | gyo)
    if [ $meisai_cnt -eq 0 ] ; then

      message="注文メニューを選択してください。"

    #はめ込み文字データまとめファイル作成
#    echo "###MESSAGE###" $message     >  $tmp-calsed_result
#    echo "###USER_TYPE###" $user_type >> $tmp-calsed_result
#    #はめ込みまとめデータのはめ込み
#    calsed -f $tmp-calsed_result  ${html_dir}/RESTAURANT_MESSAGE.html > $tmp-html
#    echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
#    cat - ${tmp}-html
#    exit 1


      #確認画面に戻るため、ここではカート削除せず

      next_page="RESTAURANT_CHUMON_KAKUNIN.CGI"
      MODE="init"

      #カートが存在すれば、カートの無効レコードから処理日、処理対象食事時間帯を取得
      #注文アプリ経由の場合、target_day、target_shokuji_jikantaiがPOSTで飛んでくるが、一覧アプリの場合、QR認証を経由するため飛んでこないので
      #ここで取得する必要あり
      if [ -e ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type ] ; then
        #20150806add ※処理日、処理対象食事時間帯を取得
        target_day=$( cat ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type  | self 9 | getlast 1 1 )
        target_shokuji_jikantai=$( cat ${ap_dir}/SESSION/resutaurant-cart.$nyukyosha_id.$user_type  | self 10 | getlast 1 1 )
      fi


      #はめ込み文字データまとめファイル作成
      echo "###MESSAGE###" $message     >  $tmp-calsed_result
      echo "###USER_TYPE###" $user_type >> $tmp-calsed_result

      echo "###NEXT_PAGE###" $next_page >> $tmp-calsed_result
      echo "###MODE###" $MODE      >> $tmp-calsed_result
      echo "###NYUKYOSHA_ID###" $nyukyosha_id   >> $tmp-calsed_result

      #20150803 add
      echo "###TARGET_DAY###"     $target_day   >> $tmp-calsed_result
      echo "###TARGET_SHOKUJI_JIKANTAI###"     $target_shokuji_jikantai   >> $tmp-calsed_result

      #はめ込みまとめデータのはめ込み
      calsed -f $tmp-calsed_result  ${html_dir}/RESTAURANT_MESSAGE.html > $tmp-html
      echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
      cat  - ${tmp}-html
      exit 1

    fi

    if [ $ptest = "new" ] ; then
      ${cgi_dir}/RESTAURANT_CHUMON_KAKUTEI_TEST.TOUROKU ${tmp}-name > ${tmp}-touroku
    else
      ${cgi_dir}/RESTAURANT_CHUMON_KAKUTEI_TEST.TOUROKU_MOTO ${tmp}-name > ${tmp}-touroku
    fi 
        
    ${cgi_dir}/RESTAURANT_CHUMON_KAKUTEI.DISPLAY ${tmp}-name ${tmp}-touroku > ${tmp}-html
    
    ;;

  #削除する場合
  delete )
    ${cgi_dir}/RESTAURANT_CHUMON_KAKUTEI.TOUROKU ${tmp}-name > ${tmp}-touroku
    ${cgi_dir}/RESTAURANT_CHUMON_ICHIRAN.DISPLAY ${tmp}-name ${tmp}-touroku  > ${tmp}-html
    ;;

  * )
    ;;
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

