#!/bin/bash
#
# KENGEN_CHECK.CGI : 権限チェック用テストCGII
#
# Usage : KENGEN_CHECK.CGI ${namefile}
#
# Written by j.aoyagi(hands lab.inc)

#--------------------ログ出力--------------------

exec 2> /home/hands/E-LIFE/TEST/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

#--------------------設定ファイル読込--------------------
source /home/hands/.bashrc &> /dev/null


#--------------------変数設定--------------------
tmp=/var/tmp/$$
namefile=${1}
current_time="$(date "+%Y%m%d%H%M%S")"
today="$(date +%Y%m%d)"
this_month="$(date +%Y%m)"

# ディレクトリの設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/TEST"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
tbl_dir="${home_dir}/E-LIFE/TBL"
apptbl_dir="${app_dir}/TBL"
pompa_dir="${app_dir}/POMPA"
input_dir="${app_dir}/INPUT"
aplog_dir="${app_dir}/AP_LOG"
download_dir="${app_dir}/DOWNLOAD"
temp_dir="${app_dir}/TEMPLATE"



# 必要な値の取得
cat ${namefile} > ${tmp}-name

#--------------------エラー時の対応--------------------
function error_exit(){
  message=$1
  echo ${message}

  rm -f $tmp-*
  exit 1
}

eval $(name-source ${namefile})

################# まずはユーザー情報を取得 ###################################
echo ${userid} > ${tmp}-user
echo ${shisetsu} > ${tmp}-shisetsu

cat ${pompa_dir}/USER_KENGEN/${userid}.USER_KENGEN          > ${tmp}-user_kengen
# 1:USER_ID 2:施設コード 3:権限グループコード 4:順番 5:MENU名 6:MENUフラグ 7:CGI_NAME 8:CGIフラグ 9:権限ステータス 10:登録日時間



# 全施設見れる人かチェック
ALL_SHISETSU_OK=$(cat ${tmp}-user_kengen            |
self 2                                              |
uniq | awk 'NR==1')

if [ "${ALL_SHISETSU_OK}" = "0" ];then
  cat ${tmp}-user_kengen                            |
  # 1:USER_ID 2:施設コード 3:権限グループコード 4:順番 5:MENU名 6:MENUフラグ 7:CGI_NAME 8:CGIフラグ 9:権限ステータス 10:登録日時間
  LANG=C sort -k4,4n -k8,8n                         |
  self 4 8 1/3 5/7 9 10                             |
  # 1:順番 2:CGIフラグ 3:USER_ID 4:施設コード 5:権限グループコード 6:MENU名 7:MENUフラグ 8:CGI_NAME 9:権限ステータス 10:登録日時間
  getlast 1 1                                       |
  self 3 4 5 1 6 7 8 2 9 10                           > ${tmp}-user_kengen_get
  # 1:USER_ID 2:施設コード 3:権限グループコード 4:順番 5:MENU名 6:MENUフラグ 7:CGI_NAME 8:CGIフラグ 9:権限ステータス 10:登録日時間
else
  cat ${tmp}-user_kengen                            |
  # 1:USER_ID 2:施設コード 3:権限グループコード 4:順番 5:MENU名 6:MENUフラグ 7:CGI_NAME 8:CGIフラグ 9:権限ステータス 10:登録日時間
  join0 key=2 ${tmp}-shisetsu                       |
  # 1:USER_ID 2:施設コード 3:権限グループコード 4:順番 5:MENU名 6:MENUフラグ 7:CGI_NAME 8:CGIフラグ 9:権限ステータス 10:登録日時間
  LANG=C sort -k4,4n -k8,8n                         |
  self 4 8 1/3 5/7 9 10                             |
  # 1:順番 2:CGIフラグ 3:USER_ID 4:施設コード 5:権限グループコード 6:MENU名 7:MENUフラグ 8:CGI_NAME 9:権限ステータス 10:登録日時間
  getlast 1 1                                       |
  self 3 4 5 1 6 7 8 2 9 10                           > ${tmp}-user_kengen_get
  # 1:USER_ID 2:施設コード 3:権限グループコード 4:順番 5:MENU名 6:MENUフラグ 7:CGI_NAME 8:CGIフラグ 9:権限ステータス 10:登録日時間
fi

cat  ${tmp}-user_kengen_get                        |
# 1:USER_ID 2:施設コード 3:権限グループコード 4:順番 5:MENU名 6:MENUフラグ 7:CGI_NAME 8:CGIフラグ 9:権限ステータス 10:登録日時間
self 5 6 7 8                                       > ${tmp}-user_kengen_tbl
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="UNEI_MENU"'                             |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE1###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="SHOKUJI_JOHO_MENU"'                     |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE2###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="TATEKAEKIN_MENU"'                     |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE3###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="NYUKYOSHA_SEIKYU_MENU"'                     |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE4###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="KAIGOHOKEN_SEIKYU_MENU"'                     |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE5###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="KANGOKAIGO_KIROKU_MENU"'                     |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE6###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="CAREPLAN_MENU"'                     |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE7###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="HOUMONKAIGO_MENU"'                     |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE8###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
awk '$1=="SYSTEM_MENU"'                     |
uniq                                              |
awk '{print "###DROPDOWN_ACTIVE9###",$2}'   >> ${tmp}-calsed_moto
# 1:置換文字 2:on

cat <<- FIN | sed 's/ _$/ @/g' > ${tmp}-calse_you
GONYUKYOSHA_SCHEDULE.CGI ###LI_UNEI3###
SCHEDULE_KANRI ###LI_UNEI2###
SCHEDULE_ICHIRAN.CGI ###LI_UNEI4###
KIHONJYOUHOU_ICHIRAN.CGI ###LI_UNEI5###
NISSHI.CGI ###LI_UNEI1###
NYUUIN_GAIHAKU_JOHO.CGI ###LI_UNEI6###
MOUSHIOKURI_ICHIRAN.CGI ###LI_UNEI7###
KEIYAKUJOHO_ICHIRAN.CGI ###LI_UNEI8###
SHOKUJI_JISSEKI_NYUKYOSHA_GEKKAN.CGI ###LI_SHOKUJI2###
SHOKUJI_JISSEKI_NYUKYOSHA_ICHIRAN.CGI ###LI_SHOKUJI3###
SHOKUJI_MEISAI_IKKATSU_SHUTSURYOKU.CGI ###LI_SHOKUJI4###
SHOKUJI_YOYAKU.CGI ###LI_SHOKUJI1###
SHOKUJI_SHURUI_TOUROKU.CGI ###LI_SHOKUJI6###
SHOKUJI_SHUKEI_HYOJI.CGI ###LI_SHOKUJI7###
KESSHOKUHYO.CGI ###LI_SHOKUJI8###
SHOKUJI_MEISAI_SHOSAI.CGI ###LI_SHOKUJI5###
RIYOUSHABETSU_SERVICERYOKIN_TOUROKU.CGI ###LI_NYUUKYOSHASEIKYU1###
KOJINATE_SEIKYU.CGI ###LI_NYUUKYOSHASEIKYU3###
iKKATSU_SERVICERYOKIN_TOUROKU.CGI ###LI_NYUUKYOSHASEIKYU2###
SEIKYU_ICHIRAN.CGI ###LI_NYUUKYOSHASEIKYU4###
SHOKYAKU_KANRI.CGI ###LI_NYUUKYOSHASEIKYU5###
DENWA_KAKIN.CGI ###LI_NYUUKYOSHASEIKYU6###
FIRMBANKING.CGI ###LI_NYUUKYOSHASEIKYU8###
KAIGOSEIKYU_HOUMONKAIGO.CGI ###LI_KAIGOHOKENSEIKYU2###
KOKUHODATA_SAKUSEI.CGI ###LI_KAIGOHOKENSEIKYU4###
KAIGOSEIKYU_KYOTAKU.CGI ###LI_KAIGOHOKENSEIKYU1###
KAIGOJISSEKI_ICHIRAN_TOUROKU.CGI ###LI_KANGOKAIGOKIROKU4###
KAIGOJISSEKI_ICHIRAN.CGI ###LI_KANGOKAIGOKIROKU5###
KAIGOJISSEKI_KENSAKU.CGI ###LI_KANGOKAIGOKIROKU6###
KAIGOJISSEKI_SUIIHYO.CGI ###LI_KANGOKAIGOKIROKU7###
MONTHLY_VITAL_GRAPH.CGI ###LI_KANGOKAIGOKIROKU8###
SHISETSU_ASSESSMENT.CGI ###LI_KANGOKAIGOKIROKU2###
WEEKLY_VITAL_GRAPH.CGI ###LI_KANGOKAIGOKIROKU9###
KAIGOJISSEKI_IKKATSU.CGI ###LI_KANGOKAIGOKIROKU3###
MONTHLY_HAIBEN_GRAPH.CGI ###LI_KANGOKAIGOKIROKU10###
WEEKLY_HAIBEN_GRAPH.CGI ###LI_KANGOKAIGOKIROKU11###
KAIGO_KANGO_YOUYAKU.CGI ###LI_KANGOKAIGOKIROKU1###
WEEKLY_HAIBENHYO.CGI ###LI_KANGOKAIGOKIROKU13###
MONTHLY_HAIBENHYO.CGI ###LI_KANGOKAIGOKIROKU12###
FIN

cp ${tmp}-user_kengen_tbl ${app_dir}/user_kengen_tbl

cat ${tmp}-user_kengen_tbl                       |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
self 3 4                                         |
# 1:CGI_NAME 2:CGIフラグ
calsed -f ${tmp}-calse_you -                     > ${tmp}-calsed_moto2

cp ${tmp}-calsed_moto2 ${app_dir}/calsed_moto2

# 合体
cat ${tmp}-calsed_moto ${tmp}-calsed_moto2       |
# 1:置換文字 2:on
awk '{gsub(/off/,"disabled",$2);print}'            > ${tmp}-goto_calsed

cp ${tmp}-goto_calsed ${app_dir}/goto_calsed
cat ${tmp}-goto_calsed  |
awk '$1!="TATEKAEKIN.CGI" && $1!="KAIGOSEIKYU_SHISETSU.CGI" && $1!="CAREPLAN_MENU.CGI" && $1!="HOUMONKAIGO_MENU.CGI"'


# 終了
rm -f $tmp-*

exit 0
