#!/bin/bash
#
# AJAX_RESTAURANT_CHUMON_ICHIRAN.CGI : レストラン注文一覧画面表示
#
# Usage : AJAX_RESTAURANT_CHUMON_ICHIRAN.CGI 
#
# Written by R.Ssuzuki Date:2015/06/03

# ログ
source /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

rm -f $tmp-*

# ディレクトリ設定
#test_tbl_dir="${home_dir}/TEST/TBL"
kengen_dir="${home_dir}/TBL/KENGEN_KANRI"

# 変数の定義
namedata=$1
#checkfile=$2
#result_data=$3
#koushin_data=$4

#20150803del
#search_day="$(date +%Y%m%d)"
#search_month="$(date +%Y%m)"
current_time="$(date +%H%M)"
cur_time="$(date +%Y%m%d%H%M%S)"

month=$(date +%Y%m)
today=$(date +%Y%m%d)
#施設　ひとまずセンター南で固定
#20150907 複数施設対応に伴い、クッキーからの取得(ここではＰＯＳＴから取得)に変更
#shisetsu="0003"

#1ページ最大行数
maxrows=100

#--------------------------------------------------------------

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name

#20150819del
##クッキーのデータ取得
#cookie-name                    |
#LANG=C sort                    > ${tmp}-cookie

# 必要な値の取得
eval $(name-source $tmp-name)
#20150819del
#eval $(name-source ${tmp}-cookie)


#期間指定検索モードの場合
if [ "$kikan_select_flg" = "1" ] ; then

  #20150817add
  #期間指定開始日の設定
  if [ "$kikan_day_from" != "" -a  "$kikan_day_from" != "_" ] ; then
    search_day_from=$(date -d $kikan_day_from +"%Y%m%d")
  else
    #期間指定終了日がセットされていたら、開始日が空でも31日前の日付をセットして検索可能にする。
    if [ "$kikan_day_to" != "" -a  "$kikan_day_to" != "_" ] ; then
      search_day_from="$(mdate $today/-30)"
    else
      search_day_from=""
    fi
  fi

  #期間指定終了日の設定
  if [ "$kikan_day_to" != "" -a  "$kikan_day_to" != "_" ] ; then
    search_day_to=$(date -d $kikan_day_to +"%Y%m%d") 
  else

    #期間指定開始日がセットされていたら、終了日が空でも今日の日付をセットして検索可能にする。
    if [ "$kikan_day_from" != "" -a  "$kikan_day_from" != "_" ] ; then
      search_day_to="$(date +%Y%m%d)"
    else
      search_day_to=""
    fi
  fi

  search_shokuji_jikantai_pattern=""

  #食事時間帯が検索条件で指定されている場合、正規表現パタン一致検索用変数へセット
  # 例：昼と夜が指定されてる場合、「23」のようにセット。
  [ "$kikan_chkstr_asa"  = "true" ] && search_shokuji_jikantai_pattern=$search_shokuji_jikantai_pattern"1"
  [ "$kikan_chkstr_hiru" = "true" ] && search_shokuji_jikantai_pattern=$search_shokuji_jikantai_pattern"2"
  [ "$kikan_chkstr_yoru" = "true" ] && search_shokuji_jikantai_pattern=$search_shokuji_jikantai_pattern"3"

  #今日分含め過去３１日分の日付を取得 。３１日以前の指定はjavascriptで抑止
  mdate -e $today/-30 |
  #縦に並び替え
  tarr |
  #注文情報（基本、メニューまとめ）の過去３１日分のファイルパス一覧を作成
  awk '$1>="'$search_day_from'" && $1<="'$search_day_to'" {print "'${pompa_dir}/${shisetsu}/'" substr($0,1,6) "/", "RESTAURANT_CHUMON_KIHON_" ,"RESTAURANT_CHUMON_MENU_MATOME_", $0}'  > $tmp-restaurant_chumon_past_list
  # 1:ディレクトリ 2:基本情報ファイル名の素 3:メニューまとめ情報ファイル名の素 4:日付

  #エラーチェック
  [ $(plus ${PIPESTATUS[@]}) -ne 0 ] && message="過去３１日分ファイルパス一覧作成エラー"

  ####################################################
  #過去３１日分の注文基本情報マージ版を作成
  ###################################################

  #ファイルパス一覧から過去３１日分の基本情報のパス一覧を作成
  awk '{print $1 $2 $4  }' $tmp-restaurant_chumon_past_list |
  #基本情報ファイルパスのリストから１行づつ日単位ファイルcatして１ファイルにマージ
  xargs cat  > $tmp-restaurant_chumon_kihon_past_merge  2>/dev/null
  # 1:施設ID 2:注文受付日 3:食事時間帯（朝昼夜）4:注文番号 5:入居者ID 6:入居者名 7:部屋番号  8:注文受付時刻 9:配膳済フラグ 10:削除フラグ 11:更新日時 12:ユーザID　

  #２個目のコマンド(xargs cat)はエラーになる場合がある(レストランが休みなどで基本情報ファイルがない場合)ので１コマンド目の結果だけチェック
  # ※レストランが休みの日があるかは定かでない
  [ ${PIPESTATUS[0]} -ne 0 ] && message="注文基本情報 期間指定分 マージ版作成エラー"


  ###################################################
  #過去３１日分の注文メニューまとめ情報マージ版を作成
  ###################################################

  #ファイルパス一覧から過去３１日分の注文メニューまとめ情報のパス一覧を作成
  awk '{print $1 $3 $4 }' $tmp-restaurant_chumon_past_list |
  #メニューまとめ情報ファイルパスのリストから１行づつ日単位ファイルcatして１ファイルにマージ
  xargs cat  > $tmp-restaurant_chumon_menu_matome_past_merge  2>/dev/null
  # 1:施設ID 2:注文受付日 3:食事時間帯（朝昼夜）4:注文番号 5:注文メニューまとめ

  #２個目(xargs cat)のコマンドはエラーになる場合がある(レストランが休みなどで注文メニューまとめ情報ファイルがない場合)ので１コマンド目の結果だけチェック
  # ※レストランが休みの日があるかは定かでない
  [ ${PIPESTATUS[0])} -ne 0 ] && message="注文メニューまとめ情報 期間指定分 マージ版作成エラー"

  #期間していされた日付分のファイルを処理対象とする
  DATA_KIHON=$(echo $tmp-restaurant_chumon_kihon_past_merge)
  DATA_MENU_MATOME=$(echo $tmp-restaurant_chumon_menu_matome_past_merge)

  #期間指定検索の場合、受付時刻欄に日付をセットする。
  hizukestr='substr($2,5,2)"/"substr($2,7,2)"<br>"'

  #取得する行番号をセット
  if [ "$select_page" = "" -o "$select_page" = "_" ] ; then
    #抽出開始行：１
    ROW_START=1
    #抽出終了行：抽出開始行　＋（ページ最大行数－１）
    ROW_END=$(lcalc -d $ROW_START'+'$maxrows'-1' )
  else
    #抽出開始行：（選択ページー１）×ページ最大行数　＋１１
    ROW_START=$(lcalc -d '('$select_page'-1)*'$maxrows'+1')
    #抽出終了行：抽出開始行　＋（ページ最大行数－１）
    ROW_END=$(lcalc -d $ROW_START'+'$maxrows'-1' )
  fi  

else
#期間指定でない場合

  search_day="$(date +%Y%m%d)"


  #食事時間帯（朝：昼：夕）の確認
  if [ $current_time -gt "1644" ] ; then
    # 1645以降以は夕食メニュー
    search_shokuji_jikantai_pattern="3"
  elif [ $current_time -gt "1044" ] ; then
    # 1045以降以は昼食メニュー
    search_shokuji_jikantai_pattern="2"
  elif [ $current_time -gt "0614" ] ; then
    # 0615以降以は朝食メニュー
    search_shokuji_jikantai_pattern="1"
  else
    # 0614以前は夕食メニューのまま
    search_shokuji_jikantai_pattern="3"
  fi


#デバッグ用
#search_day="20150803"
#search_shokuji_jikantai_pattern="3"

  #処理対象月の設定
  search_month="$(echo $search_day | cut -c-6 )"

  #ディレクトリ、ファイルなしエラーの回避 ※月初日などの発生ケースを想定
  mkdir -p ${pompa_dir}/${shisetsu}/${search_month}
  touch ${pompa_dir}/${shisetsu}/${search_month}/RESTAURANT_CHUMON_KIHON_${search_day}
  touch ${pompa_dir}/${shisetsu}/${search_month}/RESTAURANT_CHUMON_MENU_MATOME_${search_day}

  #当日分のファイルを処理対象とする
  DATA_KIHON=${pompa_dir}/${shisetsu}/${search_month}/RESTAURANT_CHUMON_KIHON_${search_day}
  DATA_MENU_MATOME=${pompa_dir}/${shisetsu}/${search_month}/RESTAURANT_CHUMON_MENU_MATOME_${search_day}

  #期間指定検索でない場合、受付時刻欄に日付をセットしない。
  hizukestr=''

fi

#--------------------------------------------------------

[ -z "${MODE}" ] && MODE="init"
#--------------------------------------------------------------

##################################
# 注文一覧の取得
##################################
#基本情報とメニューまとめ情報を結合

#注文基本情報ファイルが１行以上ある場合
if [ $(gyo $DATA_KIHON ) -gt 0  ] ; then

  cat $DATA_KIHON                       |
  # 1:施設ID 2:注文受付日 3:食事時間帯（朝昼夜）4:注文番号 5:入居者ID 6:入居者名 7:部屋番号 8:受付時刻 
  # 9:配膳済フラグ 10:削除フラグ 11:更新日時 12:ユーザID　

  #該当食事時間帯かつ有効レコードを抽出
  # モードが「検索」かつワード指定ありの場合
  if [ "${search_mode}" = "on" ] && [ "$search_word" != "" ] && [ "$search_word" != "_" ] ; then
    if [ "$search_type_str" = "order"  ] ; then
      #注文番号での検索(配膳ステータスに関係なく取得)
      awk '$3~/^['${search_shokuji_jikantai_pattern}']$/ && $4=="'$search_word'" && $10==1 {print $0,$2$8,"'$cur_time'"}'
    elif [ "$search_type_str" = "name"  ] ; then
      #入居者名前での検索(配膳ステータスに関係なく取得) ※部分一致検索
      awk '$3~/^['${search_shokuji_jikantai_pattern}']$/ && $6~/'$search_word'/ && $10==1 {print $0,$2$8,"'$cur_time'"}'
    elif [ "$search_type_str" = "room"  ] ; then
      #部屋番号での検索(配膳ステータスに関係なく取得)
      awk '$3~/^['${search_shokuji_jikantai_pattern}']$/ && $7=="'$search_word'" && $10==1 {print $0,$2$8,"'$cur_time'"}'
    else
      #デフォルトは注文番号で検索
      #注文番号での検索(配膳ステータスに関係なく取得)
      awk '$3~/^['${search_shokuji_jikantai_pattern}']$/ && $4=="'$search_word'" && $10==1 {print $0,$2$8,"'$cur_time'"}'
    fi

  # モードが「検索」かつ「配膳済み」指定の場合
  elif [ "${search_mode}" = "on" ] && [ "$search_type_str" = "haizenzumi" ] ; then
      #配膳ステータスが「配膳済み」のものだけ取得
      awk '$3~/^['${search_shokuji_jikantai_pattern}']$/ && $9==1 && $10==1 {print $0,$2$8,"'$cur_time'"}'

  # モードが「検索」かつ「配膳済み」以外を指定の場合
  elif [ "${search_mode}" = "on" ] && [ "$search_type_str" != "haizenzumi" ] ; then
      #配膳ステータス関係なく取得
      awk '$3~/^['${search_shokuji_jikantai_pattern}']$/  && $10==1 {print $0,$2$8,"'$cur_time'"}'

  else
    #該当施設の未配膳一覧を取得
    awk '$3~/^['${search_shokuji_jikantai_pattern}']$/ && $9==0 && $10==1  {print $0,$2$8,"'$cur_time'"}'
  fi|
  #注文まとめ情報とのジョイン
  join1 key=1/4  - $DATA_MENU_MATOME   |
  # 1:施設ID 2:注文受付日 3:食事時間帯（朝昼夜）4:注文番号 5:入居者ID 6:入居者名 7:部屋番号 8:受付時刻 9:配膳済フラグ
  #  10:削除フラグ 11:更新日時 12:ユーザID  13:注文受付日+受付時刻YYYYMMDDHHMMSS形式  14:現在時刻YYYYMMDDHHMMSS形式 15:注文メニューまとめ
  self 1/12 15 13 14 |
  # 1:施設ID 2:注文受付日 3:食事時間帯（朝昼夜）4:注文番号 5:入居者ID 6:入居者名 7:部屋番号 8:受付時刻 9:配膳済フラグ 
  # 10:削除フラグ 11:更新日時 12:ユーザID  13:注文メニューまとめ 14:注文受付日+受付時刻YYYYMMDDHHMMSS形式  15:現在時刻YYYYMMDDHHMMSS形式 
  #時刻の秒数変換
  calclock  14 15 |
  #14:注文時刻と15:現在時刻の比較（10分超過赤字アラートのため）
  lcalc '$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$17-$15' |
  # 1:施設ID 2:注文受付日 3:食事時間帯（朝昼夜）4:注文番号 5:入居者ID 6:入居者名 7:部屋番号 8:受付時刻 9:配膳済フラグ
  # 10:削除フラグ 11:更新日時 12:ユーザID  13:注文メニューまとめ 14:現在時刻 - 注文受付時刻
  # 表示用一覧作成
  #受付から600秒（10分）経過かつ未配膳の場合は赤字で表示

  #期間指定検索モードの場合、ページ送り表示
  if [ "$kikan_select_flg" = "1" ] ; then
    awk '{print '$hizukestr'substr($8,1,2)":"substr($8,3,2),$4,$6,$13,$7,$1,$2,$3,$5,$9==0?"未":"済",$8,$9==0?"display:;":"display:none;",$14>=600?$9==0?"color:#FF0000;":"color:;":"color:;",NR }END{print "rowcnt" ,NR}' |
    # 1:受付時刻  2:注文番号 3:入居者名 4:メニュー名 5:部屋番号 6:施設ID 7:注文受付日 8:食事時間帯（朝昼夜） 9:入居者ID
    #  10:配膳ステータス 11:注文時刻HHMMSS形式 12:button表示制御用 13:10分超過赤字アラート書式 14:レコード番号
    # ※最終行は、1:rowcnt 2:行数（条件に該当するレコード全行数。ページ分抽出前の段階のレコード数。）

    #抽出する行番号を指定、フッタレコード（条件該当レコード数情報）も残す
    awk '($14>='$ROW_START' && $14<='$ROW_END' )|| $1=="rowcnt"' >  $tmp-restaurant-chumon-ichiran_${shisetsu}

  else
  #期間指定検索モードでない場合、全件表示
    awk '{print '$hizukestr'substr($8,1,2)":"substr($8,3,2),$4,$6,$13,$7,$1,$2,$3,$5,$9==0?"未":"済",$8,$9==0?"display:;":"display:none;",$14>=600?$9==0?"color:#FF0000;":"color:;":"color:;",NR }END{print "rowcnt" ,NR}' >  $tmp-restaurant-chumon-ichiran_${shisetsu}
  fi
    # 1:受付時刻  2:注文番号 3:入居者名 4:メニュー名 5:部屋番号 6:施設ID 7:注文受付日 8:食事時間帯（朝昼夜） 9:入居者ID 
    #  10:配膳ステータス 11:注文時刻HHMMSS形式 12:button表示制御用 13:10分超過赤字アラート書式 14:レコード番号
    # ※最終行は、1:rowcnt 2:行数（条件に該当するレコード全行数。ページ分抽出前の段階のレコード数。）

   #エラーチェック
  [ $(plus ${PIPESTATUS[@]}) -ne 0 ] && message="注文一覧取得エラー"

  #条件該当レコード数の取得
  rowcnt=$(tail -n 1 $tmp-restaurant-chumon-ichiran_${shisetsu} | self 2 )


  #期間指定検索モードの場合、ページ情報を計算
  if [ "$kikan_select_flg" = "1" ] ; then

    current_page=$(echo $ROW_START $maxrows  |  lcalc '$1/$2'  | marume +age 1.0)
    max_page=$(echo $rowcnt $maxrows  |  lcalc '$1/$2'  | marume +age 1.0)

    #最終ページの場合、条件該当行数をもとに正確な最終レコード番号を算出
    #「全体行数をページ最大行数で割ったあまり」＋（（最終ページ　－　１ページ）×　ページ最大行数）
    if [ "$current_page" = "$max_page"  ] ; then
      DISP_ENDROW=$(echo $rowcnt $maxrows $max_page |  lcalc '$1%$2+(($3-1)*$2)')
    else
      #最終ページ以外の場合、ページ数とページ最大行数をもとに事前に算出した数字を採用
      DISP_ENDROW=$ROW_END
    fi

  #期間指定検索モードでない場合、ページ情報を計算しない
  else
     current_page=""
     max_page=""
     DISP_ENDROW=""
  fi

else
#注文基本情報がない場合
  :>  $tmp-restaurant-chumon-ichiran_${shisetsu}
fi


#検索結果HTML表示制御（検索時の条件指定内容保持のため）
#html_checked_order=""
#html_checked_name=""
#html_checked_room=""
# モードが検索の場合
#if [ "${search_mode}" = "on"  ] ; then
#
#  if [ "$search_type_str" = "order"  ] ; then
#    #注文番号での検索
#    html_checked_order='checked="checked"'
#  elif [ "$search_type_str" = "name"  ] ; then
#    #入居者名前での検索
#    html_checked_name='checked="checked"'
#  elif [ "$search_type_str" = "room"  ] ; then
#    #部屋番号での検索
#    html_checked_room='checked="checked"'
#  else
#    #デフォルト
#    #注文番号での検索
#    html_checked_order='checked="checked"'
#  fi
#else
#  #デフォルト
#  #注文番号での検索
#  html_checked_order='checked="checked"'
#fi

##検索ワードが空だとユニケージにより"_"に変換されるので空に戻す。
#if [ $search_word = "_" ] ; then
#  search_word=""
#fi

#はめ込み文字データまとめファイル作成
#echo "###SHISETSU_ID###"   ${shisetsu}             >  $tmp-calsed_result
#echo "###KENSAKU_WORD###"  ${search_word}          >> $tmp-calsed_result
#echo "###CHECKED_ORDER###" ${html_checked_order}   >> $tmp-calsed_result
#echo "###CHECKED_NAME###"  ${html_checked_name}    >> $tmp-calsed_result
#echo "###CHECKED_ROOM###"  ${html_checked_room}    >> $tmp-calsed_result
#echo "###KENSAKU_MODE###"   ${search_mode}          >> $tmp-calsed_result

#ユーザ種別（エンドユーザor管理ユーザ）:画面遷移を制御する
#TOPメニューまたは予約確認画面、から開始した場合はエンドユーザとする。
#注文一覧から開始した場合は管理ユーザとする。
#それ以外はPOSTされるuser_typeの内容で判定
#echo "###USER_TYPE###"   "kanriuser"    >> ${tmp}-calsed_result


#はめ込みまとめデータのはめ込み
#calsed -f $tmp-calsed_result ${html_dir}/RESTAURANT_CHUMON_ICHIRAN.html |

##リストデータはめ込み
#mojihame -l###CHUMON_ICHIRAN### -  $tmp-restaurant-chumon-ichiran_${shisetsu} > $tmp-html


###########################################################################
# AJAX返信用HTMLフォーマット形成

#リスト領域HTMLの切り出し
awk '/\<chumon_ichiran_start\>/,/\<chumon_ichiran_end\>/' ${html_dir}/RESTAURANT_CHUMON_ICHIRAN.html |
#ctailで最終行(レコード全行数の情報)を削ってから、リストデータはめ込み
mojihame -h###CHUMON_ICHIRAN###  - <(ctail -1 $tmp-restaurant-chumon-ichiran_${shisetsu})     |
calsed  "###ROWCNT###"  "$rowcnt"     |
calsed  "###ROWSTART###" "$ROW_START"  |
calsed  "###ROWEND###" "$DISP_ENDROW"  |
calsed  "###CURRENTPAGE###" "$current_page" |
calsed  "###MAXPAGE###" "$max_page"     |
#検索範囲チェック用（過去31日前か）
calsed  "###SEARCHDAY_FROM###" "$(mdate $today/-30)" > $tmp-html

#formhame -d"_"                - $tmp-name    > $tmp-html
if [ "$message" != ""  ] ; then
 echo $message  > $tmp-html
fi

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

rm -f ${tmp}-*
exit 0
