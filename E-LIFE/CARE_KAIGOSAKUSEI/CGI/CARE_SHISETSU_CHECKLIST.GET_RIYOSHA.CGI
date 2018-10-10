#!/bin/bash
#
# CARE_SHISETSU_CHECKLIST.GET_RIYOSHA.CGI : FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : CARE_SHISETSU_CHECKLIST.GET_RIYOSHA.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by R.suzuki

# 設定ファイル読込
source /home/hands/E-LIFE/CARE_KAIGOSAKUSEI/CGI/CARE_KAIGOSAKUSEI.INI
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/CARE_KAIGOSAKUSEI/CGI/CARE_SHISETSU_CHECKLIST.GET_RIYOSHA.func &> /dev/null

#--------------------ログ出力--------------------
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#=== 初期化 ===
tmp=/var/tmp/${$}
#today=$(date +%Y%m%d)

#ゴミtmpの消去
rm -f $tmp-*

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name

MODE=$(nameread "MODE" ${tmp}-name)


# aoyama部品に変更
setRiyoushaData $tmp-name $MODE "CARE_KAIGOSAKUSEI" "CARE_SHISETSU_CHECKLIST2.html" $tmp-html_wk
if [ $? != "0"  ] ;then
   error_exit
fi


: <<'#__COMENTOUT1'

 shisetsu=$(nameread "shisetsu" ${tmp}-name)
 floor=$(nameread "floor" ${tmp}-name)
 unit=$(nameread "unit" ${tmp}-name)
 room=$(nameread "room" ${tmp}-name)
 riyosha_name=$(nameread "riyosha_name" ${tmp}-name)



. ${home_dir}/COMMON/COMMON_002.func

# HTMLを作成
awk '/\<ajax_start\>/,/\<ajax_end\>/' ${html_dir}/CARE_SHISETSU_CHECKLIST2.html |
mojihame -l###FLOOR_NAME### - $tmp-floor        |
mojihame -l###UNIT_NAME###  - $tmp-unit       |
mojihame -l###ROOM_NAME###  - $tmp-room       |
mojihame -l###RIYOSHA_NAME###  - $tmp-riyosha > $tmp-html_wk
# aoyama部品に変更


#__COMENTOUT1


:> ${tmp}-checklist_rireki

mojihame -l###CHECKLIST_RIREKI###  $tmp-html_wk ${tmp}-checklist_rireki  > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
#rm -f $tmp-*
exit 0
