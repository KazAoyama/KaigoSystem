#!/bin/bash
#
# AJAX_NYUKYOSHA_KENSAKU.CGI:
#　カナ検索による対象者を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by K.Aoyama / 2014.01.07

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

#ゴミtmpの消去
rm -f $tmp-*

#=== 初期化 ===

# ディレクトリ設定(仮)

tbl_dir="${home_dir}/TBL/SHISETSU_MASTER"
kengen_dir="${home_dir}/TBL/KENGEN_KANRI"
html_dir="${home_dir}/KEIRI/HTML"

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name
#---

# カナの取得
KANA=$(nameread "KANA" $tmp-name)
userid=$(nameread "USERID" $tmp-name)
shisetsu=$(nameread "SHISETSU" $tmp-name)
tateya=$(nameread "TATEYA" $tmp-name)
floor=$(nameread "FLOOR" $tmp-name)


: > $tmp-shisetsu_riyousha
if [ -s $data_dir/UNEI/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS ] ; then
  cat $data_dir/UNEI/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS   |
  awk '$1=="'$shisetsu'"&&$2=="0'$tateya'"{print $3,$6}'     |
  if [ -z "$floor" -o "$floor" = "0" -o "$floor" = "_" ] ; then
     awk '{print $2}'
  else
     awk '$1=="'$floor'"{print $2}'
  fi |
  LANG=C sort -k1,1 > $tmp-shisetsu_riyousha
fi

cp $tmp-shisetsu_riyousha $work_dir/shisetsu_riyousha

[ -z "${KANA}" -o "${KANA}" = "_" ] && echo "@" "@" >  $tmp-taishousha_name_select_head

#cat ${home_dir}/TBL/RIYOUSHA/RIYOUSHA_MASTER |
cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER |
awk '$6!="9"'     |
awk '{print $1,$2,$3}' |
LANG=C sort -k1,1 |
join0 key=1 $tmp-shisetsu_riyousha |
# 1:利用者ID 2:利用者名

if [ "${KANA}" = "0" ] ; then
    awk '{print $1,$2}'    > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE0### active
###USERID### $userid
FIN

  elif [ "${KANA}" = "1" ] ; then
    awk '$3~/^ア/||$3~/^イ/||$3~/^ウ/||$3~/^エ/||$3~/^オ/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE1### active
FIN

  elif [ "${KANA}" = "2" ] ; then
    awk '$3~/^カ/||$3~/^キ/||$3~/^ク/||$3~/^ケ/||$3~/^コ/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE2### active
FIN

  elif [ "${KANA}" = "3" ] ; then
    awk '$3~/^サ/||$3~/^シ/||$3~/^ス/||$3~/^セ/||$3~/^ソ/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE3### active
FIN

  elif [ "${KANA}" = "4" ] ; then
    awk '$3~/^タ/||$3~/^チ/||$3~/^ツ/||$3~/^テ/||$3~/^ト/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE4### active
FIN

  elif [ "${KANA}" = "5" ] ; then
    awk '$3~/^ナ/||$3~/^ニ/||$3~/^ヌ/||$3~/^ネ/||$3~/^ノ/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE5### active
FIN

  elif [ "${KANA}" = "6" ] ; then
    awk '$3~/^ハ/||$3~/^ヒ/||$3~/^フ/||$3~/^ヘ/||$3~/^ホ/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE6### active
FIN

  elif [ "${KANA}" = "7" ] ; then
    awk '$3~/^マ/||$3~/^ミ/||$3~/^ム/||$3~/^メ/||$3~/^モ/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE7### active
FIN

  elif [ "${KANA}" = "8" ] ; then
    awk '$3~/^ヤ/||$3~/^ユ/||$3~/^ヨ/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE8### active
FIN

  elif [ "${KANA}" = "9" ] ; then
    awk '$3~/^ラ/||$3~/^リ/||$3~/^ル/||$3~/^レ/||$3~/^ロ/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE9### active
FIN

  elif [ "${KANA}" = "10" ] ; then
    awk '$3~/^ワ/||$3~/^ヲ/||$3~/^ン/{print $1,$2}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE10### active
FIN

  else
    awk '{print $1,$2}'    > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###ACTIVE0### active
FIN

  fi

cat $tmp-taishousha_name_select_head        |
# 1:番号 2:入居者ＩＤ 3:入居者名
rank                                        > $tmp-taishousha_select_value


# 施設名はログインユーザーの権限のある施設を取得
cat ${kengen_dir}/USER_KENGEN/${userid}.USER_KENGEN    |
# 1:userid 2:SHISETSU_ID 3:KENGEN_GROUP 4:appID 5:MENU_NAME 6:DROPDOWN_STATUS 7:CGI_NAME 8:RINK_STATUS 9:CGI_STATUS 10:登録日時
LANG=C sort -u -k2,2n                                      |
self 1 2                                                   > ${tmp}-kengen
# 1:userid 2:SHISETSU_ID
#if [ "$(cat ${tmp}-kengen | getfirst 1 1 | self 2)" = 0 ];then
#  awk '$1!=0' ${tbl_dir}/SHISETSU_KIHON       |
#  awk '{if($1=="'$shisetsu'"){print $1,$2,"selected"}else{print $1,$2,""}}'    > ${tmp}-shisetsu
# 1:SHISESTU_ID 2:施設名
#else
#  cat ${tmp}-kengen                        |
  # 1:userid 2:SHISETSU_ID
#  join1 key=2 ${tbl_dir}/SHISETSU_KIHON |
# 1:userid 2:SHISETSU_ID 3:施設名
#  awk '$2!=0{print $2,$3}'                 |
#  awk '{if(1=="'$shisetsu'"){print $1,$2,"selected"}else{print $1,$2,""}}'    > ${tmp}-shisetsu
#fi

self 1 2 ${home_dir}/TBL/SHISETSU_MASTER/SHISETSU_KIHON |
awk '$1=="'${shisetsu}'"' > $tmp-shisetsu_list

# フロアの取得
if [ -n "${floor}" -a "${floor}" != "_" ];then
  echo "0" "全て"                                              |
  cat - <(awk '$1=="'$shisetsu'"&&$2=="0'$tateya'"&&$4!="9"{print $3,$3}' ${tbl_dir}/SHISETSU_TATEYA_FLOOR)      |
# 1:FLOOR_CODE 2:FLOOR_NAME
  awk '{print $0,"'${floor}'"}'                                |
# 1:FLOOR_CODE 2:FLOOR_NAME 3:floor_name
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'   > ${tmp}-floor_name
else
  echo "0" "全て"                                              |
  cat - <(awk '$1=="'$shisetsu'"&&$2=="0'$tateya'"&&$4!="9"{print $3,$3}' ${tbl_dir}/SHISETSU_TATEYA_FLOOR)      |
  awk '{print $0,""}'                                      > ${tmp}-floor_name
fi

# 建屋名
cat ${tbl_dir}/TATEYA_NAME   |
LANG=C sort -k1,1            |
self 1 3                     > $tmp-tateya_name

cat ${tbl_dir}/SHISETSU_TATEYA_FLOOR   |
awk '$1=="'$shisetsu'"{print $2}'      |
LANG=C sort -k1,1 -u                   |
join1 key=1 $tmp-tateya_name |
awk '{print int($1),$2}'               > $tmp-tateya_mst 

#echo "1" "シニア" > $tmp-tateya_mst
#echo "2" "ケア" >> $tmp-tateya_mst

awk '{print $1,$2,"'$tateya'"}' $tmp-tateya_mst   |
awk '{if($1==$3){$3="selected"}else{$3=""};print $0}'    > $tmp-tateya_list

awk '$1=="'$tateya'"{print $2}' $tmp-tateya_mst > $tmp-disp_tateya

dispTateya=$(self 1 $tmp-disp_tateya)


###########################################################################
# calsedデータの整形
cat << FIN >> $tmp-calsed_data
###DISPTATEYA### $dispTateya
###EVENTTATEYA### $tateya
FIN

cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result


awk '/\<riyousha_kensaku_start\>/,/\<riyousha_kensaku_end\>/' ${html_dir}/POP_SENTAKU_NYUKYOSHA.html |
calsed -f $tmp-calsed_data_result -                     |
mojihame -l###TAISHOUSHA###  - $tmp-taishousha_select_value |
mojihame -l###SHISETSU_NAME### - $tmp-shisetsu_list |
mojihame -l###TATEYA_NAME### - $tmp-tateya_list |
mojihame -l###FLOOR_NAME### - $tmp-floor_name |
sed 's/###SPACE###/ /'     > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
