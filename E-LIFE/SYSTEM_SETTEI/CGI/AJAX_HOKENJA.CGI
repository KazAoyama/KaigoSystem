#!/bin/bash
#
# AJAX_HOKENJA.CGI:
#　保険者を取得して返す。
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
TodofukenVal=$(nameread "TodofukenVal" $tmp-name)
HHead=$(nameread "HHead" $tmp-name)

### モードによる表示の分岐
case "${MODE}" in

  # 初期表示
  Todofuken)

  #calsedデータの準備
cat << FIN > $tmp-calsed_data
###HACTIVE0### active
FIN

  # 都道府県
  cat ${home_dir}/TBL/CONFIG/TODOUFUKEN_TABLE |
  LANG=C sort -k1,1 |
  # 1:都道府県コードコード 2:都道府県 3:頭文字 
  if [ "${THead}" = "t0" ] ; then
   awk '{print $1,$2,"@"}'    > $tmp-todofuken_select_head
  elif [ "${THead}" = "ta" ] ; then
    awk '$3~/^ア/||$3~/^イ/||$3~/^ウ/||$3~/^エ/||$3~/^オ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "tk" ] ; then
    awk '$3~/^カ/||$3~/^キ/||$3~/^ク/||$3~/^ケ/||$3~/^コ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "ts" ] ; then
    awk '$3~/^サ/||$3~/^シ/||$3~/^ス/||$3~/^セ/||$3~/^ソ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "tt" ] ; then
    awk '$3~/^タ/||$3~/^チ/||$3~/^ツ/||$3~/^テ/||$3~/^ト/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "tn" ] ; then
    awk '$3~/^ナ/||$3~/^ニ/||$3~/^ヌ/||$3~/^ネ/||$3~/^ノ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "th" ] ; then
    awk '$3~/^ハ/||$3~/^ヒ/||$3~/^フ/||$3~/^ヘ/||$3~/^ホ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "tm" ] ; then
    awk '$3~/^マ/||$3~/^ミ/||$3~/^ム/||$3~/^メ/||$3~/^モ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "ty" ] ; then
    awk '$3~/^ヤ/||$3~/^ユ/||$3~/^ヨ/{print $1,$1,$3,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "tr" ] ; then
    awk '$3~/^ラ/||$3~/^リ/||$3~/^ル/||$3~/^レ/||$3~/^ロ/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  elif [ "${THead}" = "tw" ] ; then
    awk '$3~/^ワ/||$3~/^ヲ/||$3~/^ン/{print $1,$2,"@"}'   > $tmp-todofuken_select_head
  else
    echo "@ @ @"    > $tmp-todofuken_select_head
  fi  

  SelectHead="$(cat $tmp-todofuken_select_head | head -1 |self 1)"


  if [ ! -s $tmp-todofuken_select_head ] ; then
    echo "@" "@" "←都道府県を選択" "@"
  # $1が選択した都道府県のものにする
  else
  # 保険者名
    cat ${home_dir}/TBL/HOKENJA/HOKENJA_TABLE |
    awk '$6!="9"'     |
    LANG=C sort -k3,3 |
# 1:保険者コード 2:保険者番号 3:都道府県コード 4:保険者名 5:保険者カナ
    awk '$3=="'${SelectHead}'"{print $1,$2,$4,"@"}'
  fi              > $tmp-hokenja_name_select_head

  ;;

  Hokenja)

  [ -z "${TodofukenVal}" -o "${TodofukenVal}" = "_" ] && echo "@" "@" "@" "@" >  $tmp-hokenja_name_select_head

cat ${home_dir}/TBL/HOKENJA/HOKENJA_TABLE |
awk '$6!="9"'     |
awk '$3=="'${TodofukenVal}'"{print $1,$2,$5,$4}' |
LANG=C sort -k1,1 |
# 1:保険者コード 2:保険者番号 3:保険者名カナ 4:保険者名

    if [ "${HHead}" = "11" ] ; then
    echo "@ @ @ @"    > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE11### active
FIN

  elif [ "${HHead}" = "ha" ] ; then
    awk '$3~/^ア/||$3~/^イ/||$3~/^ウ/||$3~/^エ/||$3~/^オ/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE1### active
FIN

  elif [ "${HHead}" = "hk" ] ; then
    awk '$3~/^カ/||$3~/^キ/||$3~/^ク/||$3~/^ケ/||$3~/^コ/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE2### active
FIN

  elif [ "${HHead}" = "hs" ] ; then
    awk '$3~/^サ/||$3~/^シ/||$3~/^ス/||$3~/^セ/||$3~/^ソ/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE3### active
FIN

  elif [ "${HHead}" = "ht" ] ; then
    awk '$3~/^タ/||$3~/^チ/||$3~/^ツ/||$3~/^テ/||$3~/^ト/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE4### active
FIN

  elif [ "${HHead}" = "hn" ] ; then
    awk '$3~/^ナ/||$3~/^ニ/||$3~/^ヌ/||$3~/^ネ/||$3~/^ノ/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE5### active
FIN

  elif [ "${HHead}" = "hh" ] ; then
    awk '$3~/^ハ/||$3~/^ヒ/||$3~/^フ/||$3~/^ヘ/||$3~/^ホ/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE6### active
FIN

  elif [ "${HHead}" = "hm" ] ; then
    awk '$3~/^マ/||$3~/^ミ/||$3~/^ム/||$3~/^メ/||$3~/^モ/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE7### active
FIN

  elif [ "${HHead}" = "hy" ] ; then
    awk '$3~/^ヤ/||$3~/^ユ/||$3~/^ヨ/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE8### active
FIN

  elif [ "${HHead}" = "hr" ] ; then
    awk '$3~/^ラ/||$3~/^リ/||$3~/^ル/||$3~/^レ/||$3~/^ロ/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE9### active
FIN

  elif [ "${HHead}" = "hw" ] ; then
    awk '$3~/^ワ/||$3~/^ヲ/||$3~/^ン/{print $1,$2,$4,"@"}'   > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE10### active
FIN

  else
    awk '{print $1,$2,$4,"@"}'    > $tmp-hokenja_name_select_head

cat << FIN > $tmp-calsed_data
###HACTIVE0### active
FIN

  fi
   ;;
esac


###########################################################################
# calsedデータの整形
cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result


awk '/\<hokenja_start\>/,/\<hokenja_end\>/' ${html_dir}/HOKENJA_MASTER2.html |
tee $tmp-ajax_test |
 #
  calsed -f $tmp-calsed_data_result -                     |
  mojihame -lhokenja_name_select  - $tmp-hokenja_name_select_head      > $tmp-html

#formhame -d"_"                - $tmp-name    > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
