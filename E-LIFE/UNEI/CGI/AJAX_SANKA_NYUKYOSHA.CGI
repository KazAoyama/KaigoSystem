#!/bin/bash
#
# AJAX_SANKA_NYUKYOSHA.CGI:
#　入居者を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by K.Aoyama / 2014.02.23

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


#=== 初期化 ===

# ディレクトリ設定(仮)

tbl_dir="${home_dir}/TBL/SHISETSU_MASTER"
kengen_dir="${home_dir}/TBL/KENGEN_KANRI"
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

# カナの取得
floor=$(nameread "FLOOR" $tmp-name)
EventTateya=$(nameread "TATEYA" $tmp-name)
userid=$(nameread "USERID" $tmp-name)
shisetsu=$(nameread "SHISETSU" $tmp-name)
ScheduleID=$(nameread "SCHEDULEID" $tmp-name)
Sort=$(nameread "SORT" $tmp-name)

today="$(date +%Y%m%d)"

##################################
# 入居者マスタ
##################################

cat ${data_dir}/UNEI/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |
awk '$(NF-2)!="9"&&$7<="'$today'"&&"'$today'"<=$8'  |
# 1:建屋 2:利用者ID
awk '$1=="'$shisetsu'"{print int($2),$3,$5,$6}'              |
awk '$1=="'$EventTateya'"{print $2,$3,$4}'                   |
if [ "$floor" = "0" ] ; then
  awk '{print $3,$2}'
else
  awk '$1=="'$floor'"{print $3,$2}'
fi |
LANG=C sort -k1,1 > $tmp-sanka_riyousha

cp $tmp-sanka_riyousha $work_dir/sanka_riyousha

#cat ${home_dir}/TBL/RIYOUSHA/RIYOUSHA_MASTER          |
cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER          |
awk '$5!="9"'             |
join1 key=1 $tmp-sanka_riyousha  |
self 1 3 2                 |
# 施設紐付け要
# 1:利用者ID 2:利用者名 3:部屋番号
awk '{print $1,$2,$3}'     > $tmp-riyousha_master

cp $tmp-riyousha_master $work_dir/riyousha_master

#--------------------------------------------------------------
# 利用者ファイルの取得
cat ${data_dir}/UNEI/SCHEDULE/SCHEDULE_SANKASHA  |
# 1:施設   2:スケジュールID 3:利用者ID 4:利用チェック 5:備考
# 6:費用 7:有効フラグ     8:処理時間 9:ユーザID
awk '$1=="'${shisetsu}'"&&$2=="'$ScheduleID'"'     |
delf 1 2 NF-2/NF                                   |
self 1 3 2 4                                       |
# 1:データ区分 2:利用者ID 3:備考 4:利用チェック 5:費用
awk '{print $0}'                               > $tmp-sankasha

# join2 落ち防止
[ "$(gyo $tmp-sankasha)" = "0" ] && echo "_" "_" "_" "_" > $tmp-sankasha

cp $tmp-sankasha $work_dir/sankasha

cat $tmp-riyousha_master |
join2 +@ key=1 $tmp-sankasha |
rank |
awk '{if($4=="1"){$4="checked"}else{$4="@"}print $0}' |
awk '{$1=$1-1;print $0}'     |
self 1 2 6 7 3 5 4 |
if [ "$Sort" = "2" ] ; then
   LANG=C sort -k7,7r -k4nr,4nr
else
   LANG=C sort -k7,7r -k4n,4n
fi |
sed 's/_/@/g'      > $tmp-sanka_riyousha_master

cp $tmp-sanka_riyousha_master $work_dir/sanka_riyousha_master

###########################################################################
# calsedデータの整形
cat <<FIN > $tmp-calsed_data
FIN

cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result


awk '/\<sanka_kensaku_start\>/,/\<sanka_kensaku_end\>/' ${html_dir}/SCHEDULE_SHOUSAI2.html |
calsed -f $tmp-calsed_data_result -                     |
mojihame -l###AJAXRIYOUSHA###  - $tmp-sanka_riyousha_master |
sed 's/###SPACE###/ /'     > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
