#!/bin/bash
#
# KENGEN_CHECK.CGI : 権限確認用共通CGI
#
# Usage : KENGEN_CHECK.CGI ${namefile}
#
# Written by j.aoyagi(hands lab.inc)

#--------------------設定ファイル読込--------------------
source /home/hands/.bashrc &> /dev/null
#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/SYSTEM_SETTEI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/SYSTEM_SETTEI/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv
#--------------------変数設定--------------------
tmp=/var/tmp/$$
namefile=${1}
current_time="$(date "+%Y%m%d%H%M%S")"
today="$(date +%Y%m%d)"
this_month="$(date +%Y%m)"
# ディレクトリの設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
tbl_dir="${home_dir}/E-LIFE/TBL/KENGEN_KANRI"
apptbl_dir="${app_dir}/TBL"
pompa_dir="${app_dir}/POMPA/KENGEN_KANRI"
input_dir="${app_dir}/INPUT"
download_dir="${app_dir}/DOWNLOAD"
temp_dir="${app_dir}/TEMPLATE"
work="${app_dir}/WORK"

#ゴミtmpの消去
rm -f $tmp-*

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
echo ${shisetsu} > ${tmp}-shisetsu

cat ${pompa_dir}/USER_KENGEN/${userid}.USER_KENGEN          > ${tmp}-user_kengen
# 1:USER_ID    2:施設コード 3:権限グループコード 4:順番           5:MENU名
# 6:MENUフラグ 7:CGI_NAME   8:CGIフラグ          9:権限ステータス 10:登録日時間

# 全施設見れる人かチェック
ALL_SHISETSU_OK=$(self 2 ${tmp}-user_kengen            |
LANG=C sort -u | head -n1)

if [ "${ALL_SHISETSU_OK}" = "0000" ];then
  cat ${tmp}-user_kengen                            |
  # 1:USER_ID    2:施設コード 3:権限グループコード 4:順番           5:MENU名
  # 6:MENUフラグ 7:CGI_NAME   8:CGIフラグ          9:権限ステータス 10:登録日時間
  LANG=C sort -k7,7 -k8,8 -k9,9n                     |
  # 1:順番   2:CGIフラグ  3:USER_ID  4:施設コード     5:権限グループコード
  # 6:MENU名 7:MENUフラグ 8:CGI_NAME 9:権限ステータス 10:登録日時間
  getlast 7 7
  # 1:USER_ID    2:施設コード 3:権限グループコード 4:順番           5:MENU名
  # 6:MENUフラグ 7:CGI_NAME   8:CGIフラグ          9:権限ステータス 10:登録日時間
else
  cat ${tmp}-user_kengen                            |
  # 1:USER_ID    2:施設コード 3:権限グループコード 4:順番           5:MENU名
  # 6:MENUフラグ 7:CGI_NAME   8:CGIフラグ          9:権限ステータス 10:登録日時間
  cjoin0 key=2 ${tmp}-shisetsu                       |
  # 1:USER_ID    2:施設コード 3:権限グループコード 4:順番           5:MENU名
  # 6:MENUフラグ 7:CGI_NAME   8:CGIフラグ          9:権限ステータス 10:登録日時間
  LANG=C sort -k7,7 -k8,8 -k9,9n                         |
  getlast 7 7
fi                                                   |
awk '$7!="KAIGOJISSEKI_ALERT_MASTER.CGI"&&$7!="MOUSHIOKURI_MASTER.CGI"' > ${tmp}-user_kengen_get
cp ${tmp}-user_kengen_get ${work}/kengen_get

# ログインする施設に権限がなければここでおわり
if [ "$(gyo $tmp-user_kengen_get)" = 0 ];then
  exit 1
else
  :
fi

cat  ${tmp}-user_kengen_get                        |
# 1:USER_ID    2:施設コード 3:権限グループコード 4:順番           5:MENU名
# 6:MENUフラグ 7:CGI_NAME   8:CGIフラグ          9:権限ステータス 10:登録日時間
self 5 6 7 8                                       > ${tmp}-user_kengen_tbl
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ


cat <<- FIN | sed 's/ _$/ @/g' > ${tmp}-calsed_menu_name
UNEI_MENU ###DROPDOWN_ACTIVE1###
SHOKUJI_JOHO_MENU ###DROPDOWN_ACTIVE2###
TATEKAEKIN_MENU ###DROPDOWN_ACTIVE3###
NYUKYOSHA_SEIKYU_MENU ###DROPDOWN_ACTIVE4###
KAIGOHOKEN_SEIKYU_MENU ###DROPDOWN_ACTIVE5###
KANGOKAIGO_KIROKU_MENU ###DROPDOWN_ACTIVE6###
CAREPLAN_MENU ###DROPDOWN_ACTIVE7###
HOUMONKAIGO_MENU ###DROPDOWN_ACTIVE8### 
SYSTEM_MENU ###DROPDOWN_ACTIVE9###
FIN

cat ${tmp}-user_kengen_tbl                        |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
calsed -f ${tmp}-calsed_menu_name                 |
LANG=C sort -u                                    |
self 1 2                                          > ${tmp}-calsed_moto
# 1:置換文字 2:on

cat <<- FIN | sed 's/ _$/ @/g' > ${tmp}-calse_you
GONYUKYOSHA_SCHEDULE.CGI ###LI_UNEI3###
SCHEDULE_KANRI ###LI_UNEI2###
SCHEDULE_ICHIRAN.CGI ###LI_UNEI4###
KIHONJYOUHOU_ICHIRAN.CGI ###LI_UNEI5###
NISSHI.CGI ###LI_UNEI1###
NYUUINGAIHAKU_ICHIRAN.CGI ###LI_UNEI6###
MOUSHIOKURI_ICHIRAN.CGI ###LI_UNEI7###
KEIYAKUJYOUHOU_ICHIRAN.CGI ###LI_UNEI8###
SHOKUJI_JISSEKI_GEKKAN.CGI ###LI_SHOKUJI2###
SHOKUJI_JISSEKI_ICHIRAN.CGI ###LI_SHOKUJI3###
SHOKUJI_MEISAI_IKKATSU_SHUTSURYOKU.CGI ###LI_SHOKUJI4###
SHOKUJI_YOYAKU.CGI ###LI_SHOKUJI1###
SHOKUJI_MENU_TOUROKU.CGI ###LI_SHOKUJI6###
SHOKUJI_SHUUKEI.CGI ###LI_SHOKUJI7###
KESSHOKUHYOU.CGI ###LI_SHOKUJI8###
KISSHOKURITSU_ICHIRAN.CGI ###LI_SHOKUJI9###
SHOKUJI_SHOUSAI_TOUROKU.CGI ###LI_SHOKUJI5###
RIYOUSHABETSU_SERVICERYOKIN_TOUROKU.CGI ###LI_NYUUKYOSHASEIKYU1###
KOJINATE_SEIKYU.CGI ###LI_NYUUKYOSHASEIKYU3###
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
SCHEDULE_MASTER.CGI ###LI_SYSTEMSETTEI1###
SCHEDULE_TYPE_MASTER.CGI ###LI_SYSTEMSETTEI2###
SHISETSUJOHO_MASTER.CGI ###LI_SYSTEMSETTEI3###
JYUGYOIN_MASTER.CGI ###LI_SYSTEMSETTEI4###
KENGEN_MASTER.CGI ###LI_SYSTEMSETTEI5###
KEIYAKU_MASTER.CGI ###LI_SYSTEMSETTEI6###
RIYORYO_MASTER.CGI ###LI_SYSTEMSETTEI7###
SERVICE_MASTER.CGI ###LI_SYSTEMSETTEI8###
SHUKEIGROUP_MASTER.CGI ###LI_SYSTEMSETTEI9###
TATEKAEKIN_MASTER.CGI ###LI_SYSTEMSETTEI10###
KAIGOJISSEKI_MASTER.CGI ###LI_SYSTEMSETTEI11###
MOUSHIOKURI_MASTER.CGI ###LI_SYSTEMSETTEI13###
ZEIRITSU_MASTER.CGI ###LI_SYSTEMSETTEI14###
KINYU_MASTER.CGI ###LI_SYSTEMSETTEI15###
HOKENSHA_MASTER.CGI ###LI_SYSTEMSETTEI16###
JIGYOSHA_MASTER.CGI ###LI_SYSTEMSETTEI17###
SERVICE_JIGYOSHO_MASTER.CGI ###LI_SYSTEMSETTEI18###
SEIKYUSAKI_MASTER.CGI ###LI_SYSTEMSETTEI19###
MASTER_SEIKYU_SHOMEI.CGI ###LI_SYSTEMSETTEI20###
CARECALL_RIREKI.CGI ###LI_KANGOKAIGOKIROKU14###
SENIOR_ASSENMENT.CGI ###LI_UNEI9###
JIKOHOU_TOUROKU.CGI ###LI_UNEI10###
JIKOHOU_ETSURAN.CGI ###LI_UNEI11###
IKOU_ASSENMENT.CGI ###LI_UNEI12###
KENKOUSHINDANSHO_UPLOAD.CGI ###LI_UNEI13###
BUTYO_SHIRYO.CGI ###LI_UNEI14###
KISSHOKURITSU.CGI ###LI_SHOKUJI9###
DENKI_SUIDO.CGI ###LI_NYUUKYOSHASEIKYU7###
TAIKYO_SEISAN.CGI ###LI_NYUUKYOSHASEIKYU9###
KONDATE_TOUROKU.CGI ###LI_SHOKUJI10###
SHUKOU_TOUROKU.CGI ###LI_SHOKUJI11###
FIN
if [ "${shisetsu}" -gt 1000 ];then
  echo "###DROPDOWN_ACTIVE2###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE3###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE4###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE6###" "off" >> ${tmp}-calsed_moto
  echo "###TOGGLE_UNEI###" "dropdown" >> ${tmp}-calsed_moto
  echo "###TOGGLE_SHOKUJI###" "" >> ${tmp}-calsed_moto
  echo "###TOGGLE_NYUKYOSHASEIKYU###" "" >> ${tmp}-calsed_moto
  echo "###TOGGLE_KAIGOHOKENSEIKYU###" "dropdown" >> ${tmp}-calsed_moto
  echo "###TOGGLE_KANGOKAIGO###" "" >> ${tmp}-calsed_moto
  echo "GONYUKYOSHA_SCHEDULE.CGI off" >> $tmp-jigyosho_you
  echo "SCHEDULE_KANRI off" >> $tmp-jigyosho_you
  echo "SCHEDULE_ICHIRAN.CGI off" >> $tmp-jigyosho_you
  echo "NISSHI.CGI off" >> $tmp-jigyosho_you
  echo "NYUUINGAIHAKU_ICHIRAN.CGI off" >> $tmp-jigyosho_you
elif [ "${shisetsu}" = "1000" -o $shisetsu = "0008" -o $shisetsu = "0009" -o $shisetsu = "0010" -o $shisetsu = "0007" -o $shisetsu = "0011"  ];then
  echo "###DROPDOWN_ACTIVE2###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE3###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE4###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE6###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE5###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE7###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE8###" "off" >> ${tmp}-calsed_moto
  echo "###TOGGLE_UNEI###" "dropdown" >> ${tmp}-calsed_moto
  echo "###TOGGLE_SHOKUJI###" "" >> ${tmp}-calsed_moto
  echo "###TOGGLE_NYUKYOSHASEIKYU###" "" >> ${tmp}-calsed_moto
  echo "###TOGGLE_KAIGOHOKENSEIKYU###" "dropdown" >> ${tmp}-calsed_moto
  echo "###TOGGLE_KANGOKAIGO###" "" >> ${tmp}-calsed_moto
  echo "GONYUKYOSHA_SCHEDULE.CGI off" >> $tmp-jigyosho_you
  echo "SCHEDULE_KANRI off" >> $tmp-jigyosho_you
  echo "SCHEDULE_ICHIRAN.CGI off" >> $tmp-jigyosho_you
  echo "NISSHI.CGI off" >> $tmp-jigyosho_you
  echo "NYUUINGAIHAKU_ICHIRAN.CGI off" >> $tmp-jigyosho_you
  echo "SENIOR_ASSENMENT.CGI off" >> $tmp-jigyosho_you
  echo "IKOU_ASSENMENT.CGI off" >> $tmp-jigyosho_you
  echo "BUTYO_SHIRYO.CGI off" >> $tmp-jigyosho_you
  echo "KIHONJYOUHOU_ICHIRAN.CGI off" >> $tmp-jigyosho_you
  echo "MOUSHIOKURI_ICHIRAN.CGI off" >> $tmp-jigyosho_you
  echo "KEIYAKUJYOUHOU_ICHIRAN.CGI off" >> $tmp-jigyosho_you
  echo "KENKOUSHINDANSHO_UPLOAD.CGI off" >> $tmp-jigyosho_you
else
  echo "###DROPDOWN_ACTIVE5###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE7###" "off" >> ${tmp}-calsed_moto
  echo "###DROPDOWN_ACTIVE8###" "off" >> ${tmp}-calsed_moto
  echo "###TOGGLE_UNEI###" "dropdown" >> ${tmp}-calsed_moto
  echo "###TOGGLE_SHOKUJI###" "dropdown" >> ${tmp}-calsed_moto
  echo "###TOGGLE_NYUKYOSHASEIKYU###" "dropdown" >> ${tmp}-calsed_moto
  echo "###TOGGLE_KAIGOHOKENSEIKYU###" "" >> ${tmp}-calsed_moto
  echo "###TOGGLE_KANGOKAIGO###" "dropdown" >> ${tmp}-calsed_moto
fi
cat ${tmp}-user_kengen_tbl                       |
# 1:MENU名 2:MENUフラグ 3:CGI_NAME 4:CGIフラグ
self 3 4                                         |
# 1:CGI_NAME 2:CGIフラグ
if [ -e $tmp-jigyosho_you ];then
  cat - $tmp-jigyosho_you                        |
  LANG=C sort -k1,1 -k2,2r                       |
  getlast 1 1                                    
else
  cat -
fi                                               |
calsed -f ${tmp}-calse_you -                     > ${tmp}-calsed_moto2

# 合体
cat ${tmp}-calsed_moto ${tmp}-calsed_moto2       |
# 1:置換文字 2:on
awk '{gsub(/off/,"disabled",$2);print}'          |
LANG=C sort -k1,1 -k2,2r | getlast 1 1           > ${tmp}-goto_calsed

ROOM_MASTER=$(awk '$1=="###LI_SYSTEMSETTEI2###"{print $2}' ${tmp}-goto_calsed)
TENENT=$(awk '$1=="###LI_NYUUKYOSHASEIKYU7###"{print $2}' $tmp-goto_calsed)
echo "###LI_NYUUKYOSHASEIKYU10### ${TENENT}"     > $tmp-tenant
echo "###LI_SYSTEMSETTEI12### ${ROOM_MASTER}"     > $tmp-room_master
cat ${tmp}-goto_calsed  $tmp-tenant $tmp-room_master |
awk '{if($1=="###LI_SYSTEMSETTEI12###"){$2="'${ROOM_MASTER}'"};print}' |
tee ${work}/yamazaki |
awk '$1!="TATEKAEKIN.CGI" && $1!="KAIGOSEIKYU_SHISETSU.CGI" && $1!="CAREPLAN_MENU.CGI" && $1!="HOUMONKAIGO_MENU.CGI" && $1!="KENKOUSHINDANSHO_UPLOAD.CGI"'


# 終了
rm -f $tmp-*

exit 0
