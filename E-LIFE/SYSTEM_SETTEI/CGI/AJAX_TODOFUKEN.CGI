#!/bin/bash
#
# AJAX_TODOFUKEN.CGI:
#　都道府県を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by K.Aoyama / 2013.12.29

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

#=== 初期化 ===
tmp=/var/tmp/${$}

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
THead=$(nameread "THead" $tmp-name)
HHead=$(nameread "HHead" $tmp-name)

cat << FIN > $tmp-calsed_data
FIN

# 都道府県名
  cat ${home_dir}/TBL/CONFIG/TODOUFUKEN_TABLE |
  LANG=C sort -k1,1 |
# 1:都道府県コード 2:都道府県名 3:カナ  
  if [ "${THead}" = "t0" ] ; then
    awk '{print $1,$2,"@"}'    > $tmp-todofuken_select_head

    # 頭文字ボタン(Check)をactiveに
cat << FIN >> $tmp-calsed_data
###TACTIVE0### active
FIN
  elif [ "${THead}" = "ta" ] ; then
    awk '$3~/^ア/||$3~/^イ/||$3~/^ウ/||$3~/^エ/||$3~/^オ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE1### active
FIN

  elif [ "${THead}" = "tk" ] ; then
    awk '$3~/^カ/||$3~/^キ/||$3~/^ク/||$3~/^ケ/||$3~/^コ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE2### active
FIN

  elif [ "${THead}" = "ts" ] ; then
    awk '$3~/^サ/||$3~/^シ/||$3~/^ス/||$3~/^セ/||$3~/^ソ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE3### active
FIN

  elif [ "${THead}" = "tt" ] ; then
    awk '$3~/^タ/||$3~/^チ/||$3~/^ツ/||$3~/^テ/||$3~/^ト/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE4### active
FIN

  elif [ "${THead}" = "tn" ] ; then
    awk '$3~/^ナ/||$3~/^ニ/||$3~/^ヌ/||$3~/^ネ/||$3~/^ノ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE5### active
FIN

  elif [ "${THead}" = "th" ] ; then
    awk '$3~/^ハ/||$3~/^ヒ/||$3~/^フ/||$3~/^ヘ/||$3~/^ホ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE6### active
FIN

  elif [ "${THead}" = "tm" ] ; then
    awk '$3~/^マ/||$3~/^ミ/||$3~/^ム/||$3~/^メ/||$3~/^モ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head


cat << FIN >> $tmp-calsed_data
###TACTIVE7### active
FIN

  elif [ "${THead}" = "ty" ] ; then
    awk '$3~/^ヤ/||$3~/^ユ/||$3~/^ヨ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE8### active
FIN

  elif [ "${THead}" = "tr" ] ; then
    awk '$3~/^ラ/||$3~/^リ/||$3~/^ル/||$3~/^レ/||$3~/^ロ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE9### active
FIN

  elif [ "${THead}" = "tw" ] ; then
    awk '$3~/^ワ/||$3~/^ヲ/||$3~/^ン/{print $1,$2,"@"}'   > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE10### active
FIN

  else
    echo "@ @ @"    > $tmp-todofuken_select_head

cat << FIN >> $tmp-calsed_data
###TACTIVE11### active
FIN

  fi  

SelectHead="$(cat $tmp-todofuken_select_head | head -1 |self 1)"

###########################################################################
# calsedデータの整形
cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result


awk '/\<todofuken_start\>/,/\<todofuken_end\>/' ${html_dir}/HOKENJA_MASTER2.html |
tee $work_dir/tmp-html |
 #
calsed -f $tmp-calsed_data_result -                     |
mojihame -ltodofuken_name_select  - $tmp-todofuken_select_head     >$tmp-html

cp $tmp-html $work_dir/html2

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
