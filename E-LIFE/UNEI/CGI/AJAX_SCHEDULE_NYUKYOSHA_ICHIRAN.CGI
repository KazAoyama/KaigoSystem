#!/bin/bash
#
# AJAX_SCHEDULE_NYUKYOSHA_ICHIRAN.DISPLAY
# スケジュール一覧　表示用CGI
#
# Written by K.Aoyama :20131228

#--------------------------------------------------------------
# ログ
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).$HOSTNAME.$(date +%Y%m%d) ; set -xv
#--------------------------------------------------------------

#--------------------------------------------------------------
rm -f $tmp-*
#--------------------------------------------------------------

#--------------------------------------------------------------
function error_exit {
  rm -f $tmp-*
  exit 0
}
#--------------------------------------------------------------

#--------------------------------------------------------------

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name


# 必要な値の取得
eval $(name-source $tmp-name)
#--------------------------------------------------------------

# テスト

#--------------------------------------------------------------
# 入力データのチェック
# 施設
[ -z "${shisetsu}" -o "${shisetsu}" = "_" ] && error_exit "施設が不明です"

[ -z "${displayShisetsu}" -o "${displayShisetsu}" = "_" ] && displayShisetsu=$shisetsu

echo ${displayShisetsu} > $tmp-displayShisetsu

#--------------------------------------------------------------
# ヘッダー部分生成
#--------------------------------------------------------------
cat <<- FIN > $tmp-header
FIN

# ユーザマスタ
self 1 2 ${home_dir}/TBL/JYUUGYOUIN_MASTER/USER_MASTER  > $tmp-user_mst

# 入居者マスタ
self 1 2 ${apdata_dir}/RIYOUSHA/RIYOUSHA_MASTER > $tmp-riyousha_mst

###################################
# スケジュール種類
###################################
CGI_NAME="SCHEDULE_NYUKYOSHA"
schedule_code=$(awk '$(NF-2)!="9"&&$3=="'$CGI_NAME'"{print $1}' ${home_dir}/TBL/CONFIG/SCHEDULE_SHURUI | tail -1)


###################################
# スケジュールタイプマスタ
###################################
cat ${home_dir}/TBL/SCHEDULE_MASTER/SCEDULE_TYPE_MASTER |
# 非表示となっているスケジュールタイプも表示
awk '$4=="'$schedule_code'"&&$5=="'$shisetsu'"'       |
#awk '$(NF-2)!="9"&&$4=="'$schedule_code'"&&$5=="'$shisetsu'"'       |
# 1:集計グループID 2:集計グループ
#--------------------------------------------------------------
self 1 3  > ${tmp}-schedule_type_master


# 部屋スケジュール
cat ${apdata_dir}/SCHEDULE/SCHEDULE_RESERVATION |
awk '$(NF-2)!="9"&&$1=="'$displayShisetsu'"'       |
LANG=C sort -k1,2                           |
self 2 4                                    > $tmp-room_reservation

[ $(gyo $tmp-room_reservation) -eq 0 ] && echo "_" "_" > $tmp-room_reservation

# スケジュール後日付
cat ${apdata_dir}/SCHEDULE/SCHEDULE_ENDDATE |
awk '$(NF-2)!="9"&&$1=="'$displayShisetsu'"'       |
# スケジュールID 日付
self 2 5 |
LANG=C sort -k1,1 > $tmp-schedule_enddate

[ "$(gyo $tmp-schedule_enddate)" = "0" ] && echo "_" "_" > $tmp-schedule_enddate

#--------------------------------------------------------------
# スケジュールファイルの取得
cat ${apdata_dir}/SCHEDULE/SCHEDULE_SHOUSAI |
awk '$(NF-2)!="9"'                          |
LANG=C sort -k3,3                         |
join0 key=3 ${tmp}-schedule_type_master   |
delf NF-3/NF                              |
# 1:施設      2:スケジュールID 3:スケジュールタイプ 4:スケジュール名 5:開催日
# 6:開始時刻  7:終了時刻       8:予約状況           9:開催場所       10:費用
# 11:担当者1  12:担当者2       13:追記              14:建屋  15:終了日
#--------------------------------------------------------------
# 検索
# --------------------------
# 施設
# --------------------------
LANG=C sort -k1,1                    |
join0 key=1 $tmp-displayShisetsu     |
join2 +"_" key=1 $tmp-schedule_enddate |
awk '{if($2=="_"){$2=$6;print $0}}'   |
self 1 3/NF 2 |
tee $work_dir/kensakumae_schedule |
#
# 建屋
# --------------------------
if [ -z "${EventTateya}" -o "${EventTateya}" = "_" ] ; then
   cat -
else
   awk '$14=="'${EventTateya}'"'
fi  |
# --------------------------
# スケジュールタイプ
# --------------------------
if [ -z "${EventType}" -o "${EventType}" = "_" -o "${EventType}" = "0" ] ; then
   cat -
else
   awk '$3=="'${EventType}'"'
fi  |
# --------------------------
# スケジュール名
# --------------------------
if [ -z "${EventName}" -o "${EventName}" = "_" ] ; then
   cat -
else
   awk '$4~/'${EventName}'/'
fi  |
# --------------------------
# 開催開始日
# --------------------------
if [ -z "${EventStartDate}" -o "${EventStartDate}" = "_" ] ; then
   cat -
else
   awk '$NF>="'${EventStartDate}'"'
fi  |
# --------------------------
# 開催終了日
# --------------------------
if [ -z "${EventEndDate}" -o "${EventEndDate}" = "_" ] ; then
   cat -
else
   awk '$5<="'${EventEndDate}'"'
fi  |
delf NF |
LANG=C sort -k1,2                         > $tmp-all_event

cp $tmp-all_event $work_dir/all_event_nyukyosha

:> $tmp-schedule_list_sanka
if [ "$(gyo $tmp-all_event)" != "0" ] ; then
# 参加あり
cat $tmp-all_event                        |
join2 +_ key=1@2 - <(awk '$(NF-2)!="9"' ${apdata_dir}/SCHEDULE/SCHEDULE_SANKASHA | LANG=C sort -k1,2) |
delf NF-2/NF                              |
# 1:施設            2:スケジュールID 3:スケジュールタイプ 4:スケジュール名 5:開催日
# 6:開始時刻        7:終了時刻       8:予約状況           9:開催場所       10:費用
# 11:担当者1        12:担当者2       13:追記              14:建屋          15:利用者ID
# 16:利用者チェック 17:備考          18:費用
# --------------------------
# 参加者名
# --------------------------
if [ -z "${Riyoushaid}" -o "${Riyoushaid}" = "_" ] ; then
   cat -
else
   awk '$15=="'${Riyoushaid}'"'
fi  |
LANG=C sort -k15,15 |
join1 key=15 $tmp-riyousha_mst |
delf 15             |
# 1:施設ID   2:スケジュールID 3:スケジュール名 4:開催日       5:開始時刻
# 6:終了時刻 7:開催場所       8:担当者1        9:利用チェック 10.利用者名
self 1 2 4 5 6 7 9 11 16 15      |
# 担当者名を取得
LANG=C sort -k8,8       |
join2 +_ key=8 $tmp-user_mst  |
delf 8                  > $tmp-selected_event

cp $tmp-selected_event $work_dir/selected_event

cat $tmp-selected_event |
LANG=C sort -k1,2       |
join2 +_ key=1@2 - <(awk '$(NF-2)!="9"' ${apdata_dir}/SCHEDULE/SCHEDULE_GUEST | self 1 2 | LANG=C sort -k1,2) |
count 1 2               > $tmp-guest_count

cp $tmp-guest_count $work_dir/guest_count

cat $tmp-selected_event  |
LANG=C sort -k1,2        |
join2 +0 key=1@2 $tmp-guest_count  |
delf 1                   |
# 1:スケジュールID 2:参加人数 3:スケジュール名 4:開催日       5:開始時刻
# 6:終了時刻       7:開催場所 8:担当者         9:利用チェック 10:利用者名
self 1 3/8 2 10          |
LANG=C sort -k1,7        > $tmp-schedule_list_sanka
#LANG=C sort -k1,8       |
#count 1 8               |
# 利用チェックが入っていないのは
#awk '{if($8=="_"){$9="0"};print $0}'  |
#LANG=C sort -k1,7 -k9,9                     |
#getlast 1 7             |
#delf 8                  > $tmp-schedule_list_sanka
[ $(plus ${PIPESTATUS[@]}) -ne 0 ] && error_exit "スケジュール一覧取得エラー"
fi

cp $tmp-schedule_list_sanka $work_dir/schedule_list_sanka

:> $tmp-schedule_list_all_event
if [ "$(gyo $tmp-all_event)" != "0" ] ; then
# 全イベント
cat $tmp-all_event      |
awk '{print $0,"_","_","_","_"}'    |
LANG=C sort -k5,5 -k6,6 |
# 1:スケジュールID 2:スケジュール名 3:開催日 4:開始時刻 5:終了時刻
# 6:開催場所       7:担当者1 8:利用チェック
self 2 4 5 6 7 9 11 16       |
# 担当者名を取得
LANG=C sort -k7,7       |
join2 +_ key=7 $tmp-user_mst  |
delf 7                  |
# 1:スケジュールID 2:スケジュール名 3:開催日       4:開始時刻 5:終了時刻
# 6:開催場所       7:担当者        8:利用チェック
awk '{print $0}'  |
LANG=C sort -k1,7                     |
getlast 1 7             |
delf 8                  > $tmp-schedule_list_all_event
fi

cp $tmp-schedule_list_all_event $work_dir/schedule_list_all_event

:> $tmp-schedule_list
if [ "$(gyo $tmp-all_event)" != "0" ] ; then
# 参加利用者による制限
if [ -z "${Riyoushaid}" -o "${Riyoushaid}" = "_" ] ; then
  #join2 +"@" key=1@7 $tmp-schedule_list_sanka $tmp-schedule_list_all_event
  join1 key=1/7 $tmp-schedule_list_sanka $tmp-schedule_list_all_event
else
  join1 key=1/7 $tmp-schedule_list_sanka $tmp-schedule_list_all_event
fi |
LANG=C sort -k1,1       |
join2 +"@" key=1 $tmp-room_reservation |
self 1 3/NF 2           |
join2 +"_" key=1 $tmp-schedule_enddate |
tee $work_dir/schedule_enddatezumi |
awk '{if($2=="_"){$2=$4};print $0;}'   |
self 1 3/NF 2           |
LANG=C sort -k3r,3r -k4r,4r |
awk '{print $1,$2,$3,$4"～"$5,$6,$8,$7,$(NF-1),$9,$NF}' |
sed 's/ _ / @ /g'  > $tmp-schedule_list
fi

###########################################################################
# AJAX返信用HTMLフォーマット形成

awk '/\<schedulelist_start\>/,/\<schedulelist_end\>/' ${html_dir}/SCHEDULE_NYUKYOSHA_ICHIRAN2.html |
tee $work_dir/ajax_test |
#
mojihame -l###SCHEDULELIST###  - $tmp-schedule_list      > $tmp-html

#formhame -d"_"                - $tmp-name    > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN


## 終了
rm -f $tmp-*
exit 0
