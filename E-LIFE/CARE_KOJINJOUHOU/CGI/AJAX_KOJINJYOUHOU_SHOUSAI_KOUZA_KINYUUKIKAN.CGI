#!/bin/bash
#
# AJAX_KOJINJYOUHOU_SHOUSAI_KOUZA_KINYUUKIKAN.CGI:
#　金融機関名・支店名のオプションタグ群を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by E.Okuda / 2013.11.27

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

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
SHead=$(nameread "SHead" $tmp-name)

cat << FIN > $tmp-calsed_data
###KouzaBikou### ${KouzaBikou}
FIN

# 金融機関名
  cat ${tbl_dir}/KINYUU_MASTER/KINYUUKIKAN_NAME |
  LANG=C sort -k1,1 |
# 1:金融機関コード 2:金融機関名カナ 3:金融機関名  
  if [ "${KHead}" = "0" ] ; then
    awk '{print $1,$1,$3,"@"}'    > $tmp-kinyuukikan_select_head

    # 頭文字ボタン(Check)をactiveに
cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE0### active
FIN
  elif [ "${KHead}" = "a" ] ; then
    awk '$2~/^ア/||$2~/^イ/||$2~/^ウ/||$2~/^エ/||$2~/^オ/||$2~/^ヴ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE1### active
FIN

  elif [ "${KHead}" = "k" ] ; then
    awk '$2~/^カ/||$2~/^キ/||$2~/^ク/||$2~/^ケ/||$2~/^コ/||$2~/^ガ/||$2~/^ギ/||$2~/^グ/||$2~/^ゲ/||$2~/^ゴ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE2### active
FIN

  elif [ "${KHead}" = "s" ] ; then
    awk '$2~/^サ/||$2~/^シ/||$2~/^ス/||$2~/^セ/||$2~/^ソ/||$2~/^ザ/||$2~/^ジ/||$2~/^ズ/||$2~/^ゼ/||$2~/^ゾ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE3### active
FIN

  elif [ "${KHead}" = "t" ] ; then
    awk '$2~/^タ/||$2~/^チ/||$2~/^ツ/||$2~/^テ/||$2~/^ト/||$2~/^ダ/||$2~/^ヂ/||$2~/^ヅ/||$2~/^デ/||$2~/^ド/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE4### active
FIN

  elif [ "${KHead}" = "n" ] ; then
    awk '$2~/^ナ/||$2~/^ニ/||$2~/^ヌ/||$2~/^ネ/||$2~/^ノ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE5### active
FIN

  elif [ "${KHead}" = "h" ] ; then
    awk '$2~/^ハ/||$2~/^ヒ/||$2~/^フ/||$2~/^ヘ/||$2~/^ホ/||$2~/^バ/||$2~/^ビ/||$2~/^ブ/||$2~/^ベ/||$2~/^ボ/||$2~/^パ/||$2~/^ピ/||$2~/^プ/||$2~/^ペ/||$2~/^ポ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE6### active
FIN

  elif [ "${KHead}" = "m" ] ; then
    awk '$2~/^マ/||$2~/^ミ/||$2~/^ム/||$2~/^メ/||$2~/^モ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head


cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE7### active
FIN

  elif [ "${KHead}" = "y" ] ; then
    awk '$2~/^ヤ/||$2~/^ユ/||$2~/^ヨ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE8### active
FIN

  elif [ "${KHead}" = "r" ] ; then
    awk '$2~/^ラ/||$2~/^リ/||$2~/^ル/||$2~/^レ/||$2~/^ロ/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE9### active
FIN

  elif [ "${KHead}" = "w" ] ; then
    awk '$2~/^ワ/||$2~/^ヲ/||$2~/^ン/{print $1,$1,$3,"@"}'   > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE10### active
FIN

  else
    echo "@ @ @ @"    > $tmp-kinyuukikan_select_head

cat << FIN >> $tmp-calsed_data
###KCLASSACTIVE11### active
FIN

  fi  

SelectHead="$(cat $tmp-kinyuukikan_select_head | head -1 |self 1)"
#[ -z "${SHead}" -o "${SHead}" = "_" ] && SHead="$(head -1 $tmp-kinyuukikan_select_head |self 1)"

# 支店名
#  cat ${tbl_dir}/KINYUU_MASTER/KINYUUKIKAN_SHITEN_NAME |
#  LANG=C sort -k2,2 |
# 1:金融機関コード 2:支店コード  3:支店名カナ 4:支店名

#if [ -z "${KHead}" -o "${KHead}" = "_" -o "${KHead}" = "0" ] ; then
#  echo "@" "@" "↑金融機関を選択" "@"
# $1が選択した金融機関のものにする
#else
#  awk '$1=="'${SelectHead}'"{print $2,$2,$4,"@"}'
#fi              > $tmp-shiten_name_select_head

###################
# 口座種類
###################

#echo "1 2" |
#tarr         |
#awk '{if($1=="1"){print $0,"普通"}
#      else if($1=="2"){print $0,"当座"}
#     }'      |
## 口座種類が選択されていたらselected
#awk '{if($1=="'${KouzaShurui}'"){print $0,"selected"}
#      else{print $0,"@"}
#     }'     > $tmp-kouza_shurui
# 1:口座種類コード 2:口座種類名

###########################################################################
# calsedデータの整形
cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result


awk '/\<kinyuukikan_tr_start\>/,/\<kinyuukikan_tr_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KOUZA.html |
tee $tmp-ajax_test |
 #
  calsed -f $tmp-calsed_data_result -                     |
#  mojihame -lkouza_shurui_select - $tmp-kouza_shurui      |
  mojihame -lkinyuukikan_name_select  - $tmp-kinyuukikan_select_head     >$tmp-html
#  mojihame -lshiten_name_select  - $tmp-shiten_name_select_head      > $tmp-html

#formhame -d"_"                - $tmp-name    > $tmp-html

#cp  $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
