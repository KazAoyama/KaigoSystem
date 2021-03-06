#!/bin/bash
#
# AJAX_SCHEDULE_ROOM.CGI
# スケジュール一覧　表示用CGI
#
# Written by aoyagi

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

# 期間の"-"トル
KIKAN_FROM=$(echo ${EventStartDate} | sed 's/-/\//g')
KIKAN_TO=$(echo ${EventEndDate} | sed 's/-/\//g')

#--------------------------------------------------------------
# スケジュールファイルの取得
awk '$4=="05" && $5=="'${shisetsu}'" && $6!=9' ${home_dir}/TBL/SCHEDULE_MASTER/SCEDULE_TYPE_MASTER |
self 1 | LANG=C sort                        > $tmp-schedule_type_master


cat ${apdata_dir}/SCHEDULE/SCHEDULE_RESERVATION |
awk '$1=="'${shisetsu}'" && $(NF-2)!="9"'       |
LANG=C sort -k3,3                           |
tee ${work_dir}/buta |
delf NF-3/NF                                |
# 1:施設      2:スケジュールID 3:スケジュールタイプ 4:スケジュール名 5:開催日
# 6:開始時刻  7:終了時刻       8:予約状況           9:開催場所       10:費用
# 11:担当者1  12:担当者2       13:追記              14:建屋
#--------------------------------------------------------------
# 検索
# --------------------------
# 施設
# --------------------------
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
if [ -z "${EventType}" -o "${EventType}" = "_" -o "${EventType}" = "00000" ] ; then
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
if [ -z "${KIKAN_FROM}" -o "${KIKAN_FROM}" = "_" ] ; then
   cat -
else
   awk '$5>="'${KIKAN_FROM}'"'
fi  |
# --------------------------
# 開催終了日
# --------------------------
if [ -z "${KIKAN_TO}" -o "${KIKAN_TO}" = "_" ] ; then
   cat -
else
   awk '$5<="'${KIKAN_TO}'"'
fi  |
tee ${work_dir}/debu |
LANG=C sort -k1,2                         > $tmp-all_event

:> $tmp-schedule_list_sanka
if [ "$(gyo $tmp-all_event)" != "0" ] ; then
# 参加あり
cat $tmp-all_event                        |
join2 +_ key=1@2 - <(cat ${apdata_dir}/SCHEDULE/SCHEDULE_SANKASHA) |
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
LANG=C sort -k5,5 -k6,6 |
# 1:スケジュールID 2:スケジュール名 3:開催日 4:開始時刻 5:終了時刻
# 6:開催場所       7:担当者1 8:利用チェック
self 2 4 5 6 7 9 11 16       |
# 担当者名を取得
LANG=C sort -k7,7       |
join2 +_ key=7 $tmp-user_mst  |
delf 7                  |
# 1:スケジュールID 2:スケジュール名 3:開催日       4:開始時刻 5:終了時刻
# 6:開催場所       7:担当者        8:利用チェック 9:参加人数
LANG=C sort -k1,8       |
count 1 8               |
# 利用チェックが入っていないのは
awk '{if($8=="_"){$9="0"};print $0}'  |
LANG=C sort -k1,7 -k9,9                     |
getlast 1 7             |
delf 8                  > $tmp-schedule_list_sanka
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
  join2 +0 key=1@7 $tmp-schedule_list_sanka $tmp-schedule_list_all_event
else
  join1 key=1/7 $tmp-schedule_list_sanka $tmp-schedule_list_all_event
fi |
LANG=C sort -k3,3 -k4,4 |
awk '{print $1,$2,$3,$4"～"$5,$6,$8,$7}'  > $tmp-schedule_list
fi

###########################################################################
# AJAX返信用HTMLフォーマット形成

awk '/\<schedulelist_start\>/,/\<schedulelist_end\>/' ${html_dir}/SCHEDULE_ROOM_ICHIRAN2.html |
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
