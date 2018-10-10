#!/bin/bash
#
# AJAX_KOJINJYOUHOU_SHOUSAI_KOUZA_KINYUUKIKAN.CGI:
#　金融機関名・支店名のオプションタグ群を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by E.Okuda / 2013.11.27

#=== ログ ===
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
#=== 初期化 ===
tmp=/var/tmp/${$}
html_dir="${home_dir}/UNEI/HTML"

#ゴミtmpの消去
rm -f $tmp-*

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name
#---

# MODEの取得
MODE=$(nameread "MODE" $tmp-name)
KHead=$(nameread "KHead" $tmp-name)
KinyuuKikanVal=$(nameread "KinyuuKikanVal" $tmp-name)
SHead=$(nameread "SHead" $tmp-name)

### モードによる表示の分岐
case "${MODE}" in

  # 初期表示
  KinyuuKikan)

  #calsedデータの準備
cat << FIN > $tmp-calsed_data
###SCLASSACTIVE0### active
FIN

  # 金融機関名
  cat ${tbl_dir}/KINYUU_MASTER/KINYUUKIKAN_NAME |
  LANG=C sort -k1,1 |
  # 1:金融機関コード 2:金融機関名カナ 3:金融機関名  
  if [ "${KHead}" = "0" ] ; then
   awk '{print $1,$1,$3,"@"}'    > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "a" ] ; then
    awk '$2~/^ア/||$2~/^イ/||$2~/^ウ/||$2~/^エ/||$2~/^オ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "k" ] ; then
    awk '$2~/^カ/||$2~/^キ/||$2~/^ク/||$2~/^ケ/||$2~/^コ/||$2~/^ガ/||$2~/^ギ/||$2~/^グ/||$2~/^ゲ/||$2~/^ゴ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "s" ] ; then
    awk '$2~/^サ/||$2~/^シ/||$2~/^ス/||$2~/^セ/||$2~/^ソ/||$2~/^ザ/||$2~/^ジ/||$2~/^ズ/||$2~/^ゼ/||$2~/^ゾ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "t" ] ; then
    awk '$2~/^タ/||$2~/^チ/||$2~/^ツ/||$2~/^テ/||$2~/^ト/||$2~/^ダ/||$2~/^ヂ/||$2~/^ヅ/||$2~/^デ/||$2~/^ド/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "n" ] ; then
    awk '$2~/^ナ/||$2~/^ニ/||$2~/^ヌ/||$2~/^ネ/||$2~/^ノ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "h" ] ; then
    awk '$2~/^ハ/||$2~/^ヒ/||$2~/^フ/||$2~/^ヘ/||$2~/^ホ/||$2~/^バ/||$2~/^ビ/||$2~/^ブ/||$2~/^ベ/||$2~/^ボ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "m" ] ; then
    awk '$2~/^マ/||$2~/^ミ/||$2~/^ム/||$2~/^メ/||$2~/^モ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "y" ] ; then
    awk '$2~/^ヤ/||$2~/^ユ/||$2~/^ヨ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "r" ] ; then
    awk '$2~/^ラ/||$2~/^リ/||$2~/^ル/||$2~/^レ/||$2~/^ロ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  elif [ "${KHead}" = "w" ] ; then
    awk '$2~/^ワ/||$2~/^ヲ/||$2~/^ン/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head
  else
    echo "@ @ @ @"    > $tmp-kinyuukikan_select_head
  fi  

  SelectHead="$(cat $tmp-kinyuukikan_select_head | head -1 |self 1)"


  if [ ! -s $tmp-kinyuukikan_select_head ] ; then
    echo "@" "@" "↑金融機関を選択" "@"
  # $1が選択した金融機関のものにする
  else
  # 支店名
    cat ${tbl_dir}/KINYUU_MASTER/KINYUUKIKAN_SHITEN_NAME |
    LANG=C sort -k3,3 |
# 1:金融機関コード 2:支店コード  3:支店名カナ 4:支店名
    awk '$1=="'${SelectHead}'"{print $2,$2,$4,"@"}'
  fi              > $tmp-shiten_name_select_head

  ;;

  Shiten)

  [ -z "${KinyuuKikanVal}" -o "${KinyuuKikanVal}" = "_" ] && echo "@" "@" "@" "@" >  $tmp-shiten_name_select_head

cat ${tbl_dir}/KINYUU_MASTER/KINYUUKIKAN_SHITEN_NAME |
awk '$1=="'${KinyuuKikanVal}'"{print $2,$3,$4}' |
LANG=C sort -k1,1 |
# 1:支店コード 2:支店名カナ 3:支店名

    if [ "${SHead}" = "11" ] ; then
    echo "@ @ @ @"    > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE11### active
FIN

  elif [ "${SHead}" = "a" ] ; then
    awk '$2~/^ア/||$2~/^イ/||$2~/^ウ/||$2~/^エ/||$2~/^オ/||$2~/^ヴ/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE1### active
FIN

  elif [ "${SHead}" = "k" ] ; then
    awk '$2~/^カ/||$2~/^キ/||$2~/^ク/||$2~/^ケ/||$2~/^コ/||$2~/^ガ/||$2~/^ギ/||$2~/^グ/||$2~/^ゲ/||$2~/^ゴ/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE2### active
FIN

  elif [ "${SHead}" = "s" ] ; then
    awk '$2~/^サ/||$2~/^シ/||$2~/^ス/||$2~/^セ/||$2~/^ソ/||$2~/^ザ/||$2~/^ジ/||$2~/^ズ/||$2~/^ゼ/||$2~/^ゾ/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE3### active
FIN

  elif [ "${SHead}" = "t" ] ; then
    awk '$2~/^タ/||$2~/^チ/||$2~/^ツ/||$2~/^テ/||$2~/^ト/||$2~/^ダ/||$2~/^ヂ/||$2~/^ヅ/||$2~/^デ/||$2~/^ド/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE4### active
FIN

  elif [ "${SHead}" = "n" ] ; then
    awk '$2~/^ナ/||$2~/^ニ/||$2~/^ヌ/||$2~/^ネ/||$2~/^ノ/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE5### active
FIN

  elif [ "${SHead}" = "h" ] ; then
    awk '$2~/^ハ/||$2~/^ヒ/||$2~/^フ/||$2~/^ヘ/||$2~/^ホ/||$2~/^バ/||$2~/^ビ/||$2~/^ブ/||$2~/^ベ/||$2~/^ボ/||$2~/^パ/||$2~/^ピ/||$2~/^プ/||$2~/^ペ/||$2~/^ポ/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE6### active
FIN

  elif [ "${SHead}" = "m" ] ; then
    awk '$2~/^マ/||$2~/^ミ/||$2~/^ム/||$2~/^メ/||$2~/^モ/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE7### active
FIN

  elif [ "${SHead}" = "y" ] ; then
    awk '$2~/^ヤ/||$2~/^ユ/||$2~/^ヨ/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE8### active
FIN

  elif [ "${SHead}" = "r" ] ; then
    awk '$2~/^ラ/||$2~/^リ/||$2~/^ル/||$2~/^レ/||$2~/^ロ/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE9### active
FIN

  elif [ "${SHead}" = "w" ] ; then
    awk '$2~/^ワ/||$2~/^ヲ/||$2~/^ン/{print $1,$1,$3,"@"}'   > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE10### active
FIN

  else
    awk '{print $1,$1,$3,"@"}'    > $tmp-shiten_name_select_head

cat << FIN > $tmp-calsed_data
###SCLASSACTIVE0### active
FIN

  fi
   ;;
esac


###########################################################################
# calsedデータの整形
cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result


awk '/\<shiten_tr_start\>/,/\<shiten_tr_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KOUZA.html |
tee $tmp-ajax_test |
 #
  calsed -f $tmp-calsed_data_result -                     |
#  mojihame -lkouza_shurui_select - $tmp-kouza_shurui      |
#  mojihame -lkinyuukikan_name_select  - $tmp-kinyuukikan_select_head     >$tmp-html
  mojihame -lshiten_name_select  - $tmp-shiten_name_select_head      > $tmp-html

#formhame -d"_"                - $tmp-name    > $tmp-html

#cp  $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
