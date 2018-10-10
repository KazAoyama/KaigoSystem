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
source /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/CGI/SHISETSU_KAIGOKIROKU.INI &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


#=== 初期化 ===
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定(仮)
homed_dir="/home/hands"
app_dir="${homed_dir}/E-LIFE/SHISETSU_KAIGOKIROKU"
apptbl_dir="${app_dir}/TBL"
test_tbl_dir="${homed_dir}/TEST/TBL"
test_pompa_dir="${homed_dir}/E-LIFE/TEST/POMPA"


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
shisetsu=$(nameread "SHISETSU" $tmp-name)

[ -z "${KANA}" -o "${KANA}" = "_" ] && echo "@" "@" >  $tmp-taishousha_name_select_head

cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER |
awk '$6!="9"'     |
awk '{print $1,$2,$3}' |
LANG=C sort -k1,1 |
# 1:利用者ID 2:利用者名

if [ "${KANA}" = "0" ] ; then
    echo "@ @ @"    > $tmp-taishousha_name_select_head

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


###########################################################################
# calsedデータの整形
cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result


awk '/\<riyousha_kensaku_start\>/,/\<riyousha_kensaku_end\>/' ${html_dir}/POP_SELECT_NYUKYOSHA.html |
calsed -f $tmp-calsed_data_result -                     |
mojihame -l###TAISHOUSHA###  - $tmp-taishousha_select_value |
sed 's/###SPACE###/ /'     > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
