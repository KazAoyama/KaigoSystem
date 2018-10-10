#!/bin/bash
#
# KEIYAKU_ICHIRAN.GET_RIYOSHA.CGI : SHISETSU,TATEYA,FLOORまたはUNITを選択してRIYOSHAを返す
#                     
#
# Usage : KEIYAKU_ICHIRAN.GET_RIYOSHA.CGI
#         POST メソッドで FLOOR_CODE を渡す。
#
# Written by Y.kashiyama 2014/03/11

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/UNEI/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#=== 初期化 ===
tmp=/var/tmp/${$}
today=$(date +%Y%m%d)

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/UNEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA"
apptbl_dir="${app_dir}/TBL"
kyoutsu_dir="${home_dir}/E-LIFE/KYOUTSU/HTML"
riyosha_dir="/DATA/E-LIFE/UNEI/RIYOUSHA"
keiyaku_dir="${home_dir}/E-LIFE/TBL/KEIYAKU_MASTER"
tbl_dir="${home_dir}/E-LIFE/TBL"

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name

# MODE取得
MODE=$(nameread "MODE" ${tmp}-name)
# 選択しているSHISETSU_CODE
userid=$(nameread "userid" ${tmp}-name)
shisetsu_select=$(nameread "shisetsu" ${tmp}-name)
tateya=$(nameread "tateya" ${tmp}-name)
floor=$(nameread "floor" ${tmp}-name)
unit=$(nameread "unit" ${tmp}-name)
kyoshitsu=$(nameread "kyoshitsu" ${tmp}-name)

SHISETSUID="$(nameread "shisetsu" ${tmp}-name)"

# SHISETSU_TATEYA_FLOOR_ROOMのマスタ準備
echo $shisetsu_select > $tmp-shisetsu
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM               |
# 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
join0 key=1 $tmp-shisetsu                                    |
awk '$9=="1"'                                                > $tmp-shisetsu_tateya_floor_id

# 建屋準備
cat ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME                   |
self 1 3                                                     > $tmp-tateya_master

# ユニットマスタの準備
cat ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME                     |
self 1 2                                                     > $tmp-unit_master

# 利用者マスタの準備
cat ${riyosha_dir}/RIYOUSHA_MASTER                           |
self 1 2                                                     > $tmp-riyosha_master

# SHISETSU_RIYOSHA_STATUSの準備
cat ${riyosha_dir}/SHISETSU_RIYOUSHA_STATUS                  |
# 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
if [ "$shisetsu_select" != "0000" ] ; then
  join0 key=1 $tmp-shisetsu                                    
else
  cat -
fi |
#awk '$7<="'${today}'" && $8>="'${today}'" && $(NF-2)!="9"'   |
awk '$8>="'${today}'" && $(NF-2)!="9"'                   |
LANG=C sort -u -k1,3n -k4,4n -k6,6n                          > $tmp-riyosha_status

# JIGYOUSHO_RIYOUSHA_STATUSの準備
cat ${riyosha_dir}/JIGYOUSHO_RIYOUSHA_STATUS                 |
# 1:事業所ID 2:入居者ID 3:契約開始日 4:契約終了日
LANG=C sort                                                  |
if [ "$shisetsu_select" != "0000" ] ; then
  join0 key=1 $tmp-shisetsu                                 
else
  cat -
fi |
awk '$4>"'${today}'" && $(NF-2)!="9" {print $1,$2}'          > $tmp-jigyousho_status

## 施設名はログインユーザーの権限のある施設を取得
#共通ヘッダー###########

awk '$(NF)!="9"{print $1,$2}' /home/hands/E-LIFE/TBL/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER > $tmp-jigyousho_group_mst
awk '$1!="1000"&&$(NF)!="9"{print $1,$2}' /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_KIHON > $tmp-shisetsu_mst

cat $tmp-shisetsu_mst $tmp-jigyousho_group_mst > $tmp-disp_shisetsu_mst


# 施設名はログインユーザーの権限のある施設を取得
cat /home/hands/E-LIFE/SYSTEM_SETTEI/POMPA/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN |
# 1:userid 2:SHISETSU_ID 3:KENGEN_GROUP 4:appID 5:MENU_NAME 6:DROPDOWN_STATUS 7:CGI_NAME 8:RINK_STATUS 9:CGI_STATUS 10:登録日時
awk '$7=="KEIYAKUJYOUHOU_ICHIRAN.CGI"'    |
LANG=C sort -u -k2,2n                     |
self 1 2                                  > ${tmp}-kengen
# 1:userid 2:SHISETSU_ID
if [ "$(cat ${tmp}-kengen | getfirst 1 1 | self 2)" = "0000" ];then
  awk '$1!="0000"{print $1,$2}' $tmp-disp_shisetsu_mst      |
  awk '{print $0,"'${SHISETSUID}'"}'              |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' 
# 1:SHISESTU_ID 2:施設名
else
  cat ${tmp}-kengen                        |
  # 1:userid 2:SHISETSU_ID
  join1 key=2 $tmp-disp_shisetsu_mst |
# 1:userid 2:SHISETSU_ID 3:施設名
  awk '$2!=0{print $2,$3}'                 |
  awk '{print $0,"'${SHISETSUID}'"}'              |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' 
fi |
  awk 'BEGIN{print "0000","全て"}{print $0}'  > ${tmp}-shisetsu

#cat /home/hands/E-LIFE//SYSTEM_SETTEI/POMPA/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN    |
## 1:userid 2:SHISETSU_ID 3:KENGEN_GROUP 4:appID 5:MENU_NAME 6:DROPDOWN_STATUS 7:CGI_NAME 8:RINK_STATUS 9:CGI_STATUS 10:登録日時
#LANG=C sort -u -k2,2n                                      |
#self 1 2                                                   > ${tmp}-kengen
## 1:userid 2:SHISETSU_ID
#if [ "$(cat ${tmp}-kengen | getfirst 1 1 | self 2)" = "0000" ];then
#  awk '$1!="0000"' ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON      |
#  self 1 2                                              |
#  awk '{print $0,"'${shisetsu_select}'"}'              |
#  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'  > ${tmp}-shisetsu
## 1:SHISESTU_ID 2:施設名
#else
#  cat ${tmp}-kengen                        |
#  # 1:userid 2:SHISETSU_ID
#  join1 key=2 ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
## 1:userid 2:SHISETSU_ID 3:施設名
#  awk '$2!=0{print $2,$3}'                 |
#  awk '{print $0,"'${shisetsu_select}'"}'              |
#  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'  > ${tmp}-shisetsu
#fi

# 実施者の取得
cat ${tbl_dir}/JYUUGYOUIN_MASTER/USER_MASTER                   |
self 1 2                                                       > $tmp-user_master
cat ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU                 |
# 1:userid 2:施設id  3:建屋 4:フロア 5:ユニットid
# 6:事業所詳細 7:役職（ケアマネかサ責） 8:介護支援専門員番号
LANG=C sort -k2,2n                                             |
join0 key=2 $tmp-shisetsu                                      |
awk '$3=="'${tateya}'" || $3=="_"'                             |
self 1                                                         |
LANG=C sort -k1,1n                                             |
join1 key=1 $tmp-user_master                                   |
awk '{print $1"+++"$2,$2}'                                     > $tmp-jisshisha_master
echo "_" "全て"                                                > $tmp-all_jisshisha
if [ -n "${JISSHISHA}" -a "${JISSHISHA}" != "_" ];then
  cat $tmp-all_jisshisha $tmp-jisshisha_master                 |
# 1:JISSISHA_CODE 2:JISSHISHA_NAME
  awk '{print $0,"'${JISSHISHA}'"}'                            |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}'   > ${tmp}-jisshisha
else
  cat $tmp-all_jisshisha $tmp-jisshisha_master                 |
  awk '{print $1,$2,""}'                                       > ${tmp}-jisshisha
fi

JIGYOUSHO_FLG=$(echo "${SHISETSUID}" | awk '{print substr($1,1,1)}')

if [ "$MODE" = "Shisetsu" ]; then
#  if [ ${JIGYOUSHO_FLG} = "1" -o ${SHISETSUID} = "0000" ]; then
  if [ ${JIGYOUSHO_FLG} = "1" ]; then
    # 建屋
    echo "@ @ @" > $tmp-tateya
    # フロア
    echo "@ @ @" > $tmp-floor
    # ユニット
    echo "@ @ @" > $tmp-unit
    # 居室
    echo "@ @ @" > $tmp-kyoshitsu
    # 入居者
    echo "_" "全て"                    > $tmp-all
    self 2 1 $tmp-jigyousho_status                             |
    # 1:施設id 2:利用者ID
    LANG=C sort                                                |
    join1 key=1 $tmp-riyosha_master                            |
    cat $tmp-all -                                             > $tmp-riyosha

  elif [ ${SHISETSUID} = "0000" ] ; then
    # 建屋
    echo "@ @ @" > $tmp-tateya
    # フロア
    echo "@ @ @" > $tmp-floor
    # ユニット
    echo "@ @ @" > $tmp-unit
    # 居室
    echo "@ @ @" > $tmp-kyoshitsu
    # 入居者
    echo "_" "全て"                    > $tmp-all

    # 全ての施設・事業所の権限があったら
    if [ "$(self 2 ${tmp}-kengen | head -1)" = "0000" ] ; then
      self 1 5 6 $tmp-riyosha_status       > $tmp-riyousha_1
      awk '{print $1,"_",$2}' $tmp-jigyousho_status     |
      cat $tmp-riyousha_1 -            |
#      LANG=C sort -u                   |
      LANG=C sort -k3,3                |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
      cjoin1 key=1 $tmp-riyosha_master  |
#      self 6 $tmp-riyosha_status       > $tmp-riyousha_1
#      self 2 $tmp-jigyousho_status     |
#      cat $tmp-riyousha_1 -            |
#      LANG=C sort -u                   |
#      join1 key=1 $tmp-riyosha_master  |
#      head -300                        |
      cat $tmp-all -                   > $tmp-riyosha
    # 一部の施設・事業所に権限があったら
    else
      self 2 $tmp-kengen               > $tmp-kengen_shisetsu
      join1 key=1 $tmp-kengen_shisetsu $tmp-riyosha_status   |
      self 6                           > $tmp-riyousha_1
      join1 key=1 $tmp-kengen_shisetsu $tmp-jigyousho_status |
      self 2                           |
      cat $tmp-riyousha_1 -            |
      LANG=C sort -u                   |
      join1 key=1 $tmp-riyosha_master  |
#      head -300                        |
      cat $tmp-all -                   > $tmp-riyosha
     fi

  else
    # tateya
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 2                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-tateya_master                               |
    awk '{print $0,"'${tateya}'"}'                               |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya
    # floor一覧
      #建屋が選択されずに自動的に何かを指している場合それをtateyaにする
      if [ "${tateya}" = "" -o "${tateya}" = "_" ] ;then
         if [ $(awk '$3=="selected"' $tmp-tateya | gyo ) = "1" ] ;then
            tateya=$(awk '$3=="selected"{print $1}' $tmp-tateya)
            # selectedがなかったら一番上の建屋
            [ -z "${tateya}" -o "${tateya}" = "_" ] && tateya=$(head -1 $tmp-tateya | self 1)
         else
         #何も選択していなくても表示されてるのは一番上
            tateya=$(head -1 $tmp-tateya | self 1)
         fi
      else
            tateya=$(awk '$3=="selected"{print $1}' $tmp-tateya)
            # selectedがなかったら一番上の建屋
            [ -z "${tateya}" -o "${tateya}" = "_" ] && tateya=$(head -1 $tmp-tateya | self 1)

      fi
    echo "_" "全て"                > $tmp-all_floor
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 3                                                       |
    LANG=C sort -u -k1,1n                                        |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-all_floor -                                         > ${tmp}-floor
    # keiyaku一覧
    echo "_" "全て"                                                > $tmp-all_keiyaku
    awk '$1=="'${shisetsu_select}'"&&$(NF-2)!="9"&&$(NF-2)!="2"' ${keiyaku_dir}/SHISETSU_KEIYAKU_MASTER |
    LANG=C sort                                                     |
    join1 key=1 ${tbl_dir}/KEIYAKU_MASTER/KEIYAKU_NAME -            |
    self 1 2                                                        |
#    self 1 3                                                       |
#    LANG=C sort -u                                                 |
    cat $tmp-all_keiyaku -                                         > ${tmp}-keiyaku
  
    if [ "${floor}" = "_" ];then
    # unit一覧
      echo "_" "全て"                  > $tmp-unit
    # member
      echo "_" "全て"                  > $tmp-all
      cat $tmp-riyosha_status          |
      awk '$2=="'${tateya}'"'          |
      # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
      self 1 5 6                       |
      LANG=C sort -k3,3                |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
#      self 6                                                     |
#      LANG=C sort -k1,1n                                         |
      cjoin1 key=1 $tmp-riyosha_master -                          |
      cat $tmp-all -                                             > $tmp-riyosha
  
    # kyoshitsu一覧
      echo "_" "全て"                       > $tmp-all_kyoshitsu
      cat $tmp-shisetsu_tateya_floor_id                          |
      # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
      awk '$2=="'${tateya}'"'                                      |
      self 5                                                     |
      LANG=C sort -u -k1,1n                                      |
      awk '{print $1,$1}'                                  |
      cat $tmp-all_kyoshitsu -                                        > $tmp-kyoshitsu
  
    else
      echo "_" "全て"                       > $tmp-unit
  
    # kyoshitsu一覧
      echo "_" "全て"                       > $tmp-all_kyoshitsu
      cat $tmp-shisetsu_tateya_floor_id                          |
      # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
      awk '$2=="'${tateya}'" || $3=="'${floor}'"'                |
      self 5                                                     |
      LANG=C sort -u -k1,1n                                      |
      awk '{print $1,$1}'                                  |
      cat $tmp-all_kyoshitsu -                                        > $tmp-kyoshitsu
  
      # member
      echo "_" "全て"                    > $tmp-all
      cat $tmp-riyosha_status                                    |
      # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
      awk '$3=="'${floor}'"{print $1,$5,$6}'                     |
      LANG=C sort -k3,3                |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
#      LANG=C sort -k1,1n                                         |
      join1 key=1 $tmp-riyosha_master                            |
      cat $tmp-all -                                             > $tmp-riyosha
    fi
  fi
elif [ "$MODE" = "Tateya" ]; then
  # tateya
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{print $0,"'${tateya}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya
  # floor一覧
  echo "_" "全て"                > $tmp-all_floor
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  awk '$2=="'${tateya}'"'                                      |
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         > ${tmp}-floor

  # unit一覧
  echo "_" "全て"                       > $tmp-unit

  # kyoshitsu一覧
  echo "_" "全て"                       > $tmp-all_kyoshitsu
  cat $tmp-shisetsu_tateya_floor_id                          |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  awk '$2=="'${tateya}'"'                                      |
  self 5                                                     |
  LANG=C sort -u -k1,1n                                      |
  awk '{print $1,$1}'                                  |
  cat $tmp-all_kyoshitsu -                                        > $tmp-kyoshitsu

  # member
  echo "_" "全て"                      > $tmp-all
  cat $tmp-riyosha_status                                    |
  # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
  awk '$2=="'${tateya}'"{print $1,$5,$6}'                    |
  LANG=C sort -k3,3                      |
  getfirst 3 3                     |
  LANG=C sort                      |
  self 3                           |
#  self 6                                                     |
#  LANG=C sort -k1,1n                                         |
  cjoin1 key=1 $tmp-riyosha_master -                          |
  cat $tmp-all -                                             > $tmp-riyosha
elif [ "$MODE" = "Floor" ]; then
  # tateya
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{print $0,"'${tateya}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya
  # floor一覧
  echo "_" "全て"                > $tmp-all_floor
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'${tateya}'"'                                      |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         |
  awk '{if($1=="'${floor}'"){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor

  if [ "${floor}" = "_" ];then
  # unit一覧
    echo "_" "全て"                       > $tmp-unit
  # kyoshitsu一覧
    echo "_" "全て"                       > $tmp-all_kyoshitsu
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 5                                                     |
    LANG=C sort -u -k1,1n                                      |
    awk '{print $1,$1}'                                  |
    cat $tmp-all_kyoshitsu -                                        > $tmp-kyoshitsu
  # member
    echo "_" "全て"                      > $tmp-all
    cat $tmp-riyosha_status                                    |
    awk '$2=="'${tateya}'"{print $1,$5,$6}'                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
      LANG=C sort -k3,3                |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
#    self 6                                                     |
#    LANG=C sort -k1,1n                                         |
    cjoin1 key=1 $tmp-riyosha_master -                         |
    cat $tmp-all -                                             > $tmp-riyosha
  else
    echo "_" "全て"                       > $tmp-all_unit
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
    cat $tmp-all_unit -                                        |
    awk '$1=="_" || $3=="'${floor}'"{print $1,$2}'             >  ${tmp}-unit
  # kyoshitsu一覧
    echo "_" "全て"                       > $tmp-all_kyoshitsu
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'" && $3=="'${floor}'"'                |
    self 5                                                     |
    LANG=C sort -u -k1,1n                                      |
    awk '{print $1,$1}'                                  |
    cat $tmp-all_kyoshitsu -                                        > $tmp-kyoshitsu
    # member
    echo "_" "全て"                    > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$3=="'${floor}'"{print $1,$5,$6}'                     |
      LANG=C sort -k3,3                |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
#    LANG=C sort -k1,1n                                         |
    cjoin1 key=1 $tmp-riyosha_master                            |
    cat $tmp-all -                                             > $tmp-riyosha
  fi

elif [ "$MODE" = "Unit" ];then
  # tateya
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{print $0,"'${tateya}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya
  # floor一覧
  if [ "${unit}" = "_" ];then
    echo "_" "全て"                > $tmp-all_floor
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 3                                                       |
    LANG=C sort -u -k1,1n                                        |
    awk '{print $1,$1"F"}'                                       |
    cat $tmp-all_floor -                                         |
    awk '{print $0,"'${floor}'"}'                                |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
    
    echo "_ 全て selected"            > $tmp-all_unit
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4 3                                                   |
    # 1:ユニットid 2:フロア
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
    if [ "${floor}" = "_" ];then
      cat $tmp-all_unit -
    else
      awk '$1=="_" || $3=="'${floor}'"' |
      cat $tmp-all_unit -
    fi                                    > ${tmp}-unit

  # kyoshitsu一覧
    echo "_" "全て"                       > $tmp-all_kyoshitsu
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$3=="'${floor}'"'                |
    self 5                                                     |
    LANG=C sort -u -k1,1n                                      |
    awk '{print $1,$1}'                                  |
    cat $tmp-all_kyoshitsu -                                        > $tmp-kyoshitsu

    # member
    echo "_" "全て"                    > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                     |
    awk '$3=="'${floor}'"{print $1,$5,$6}'                      |
      LANG=C sort -k3,3                |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
#    LANG=C sort -k1,1n                                         |
    cjoin1 key=1 $tmp-riyosha_master -                          |
    cat $tmp-all -                                             > $tmp-riyosha

  else
    # floor一覧
    echo "_" "全て"                > $tmp-all_floor
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 3 4                                                     |
    LANG=C sort -u -k1,2n                                        |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($2==$3){print $1,$1"F","selected"}else{print $1,$1"F",""}}' |
    cat $tmp-all_floor -                                         > $tmp-floor

    # unit一覧
    echo "_" "全て"                       > $tmp-all_unit
    cat $tmp-shisetsu_tateya_floor_id                            |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    join0 key=3 <(echo "${floor}")                               |
    self 4                                                       |
    LANG=C sort -u -k1,1n                                        |
    join1 key=1 $tmp-unit_master                                 |
    cat $tmp-all_unit -                                          |
    awk '{print $0,"'${unit}'"}'                                 |
    awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

  # kyoshitsu一覧
    echo "_" "全て"                       > $tmp-all_kyoshitsu
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$3=="'${floor}'"'                |
    self 5                                                     |
    LANG=C sort -u -k1,1n                                      |
    awk '{print $1,$1}'                                  |
    cat $tmp-all_kyoshitsu -                                        > $tmp-kyoshitsu

    # member
    echo "_" "全て"                    > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$2=="'${tateya}'"'                                    |
    awk '$4=="'${unit}'"{print $1,$5,$6}'                      |
#    LANG=C sort -k1,1n                                         |
      LANG=C sort -k3,3                     |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
    cjoin1 key=1 $tmp-riyosha_master                            |
    cat $tmp-all -                                             > $tmp-riyosha

  fi

elif [ "$MODE" = "Kyoshitsu" ]; then
  # tateya
  cat $tmp-shisetsu_tateya_floor_id                            |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 2                                                       |
  LANG=C sort -u -k1,1n                                        |
  join1 key=1 $tmp-tateya_master                               |
  awk '{print $0,"'${tateya}'"}'                               |
  awk '{if($1==$3){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-tateya
  # floor一覧
  echo "_" "全て"                > $tmp-all_floor
  cat $tmp-shisetsu_tateya_floor_id                            |
  awk '$2=="'${tateya}'"'                                      |
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  self 3                                                       |
  LANG=C sort -u -k1,1n                                        |
  awk '{print $1,$1"F"}'                                       |
  cat $tmp-all_floor -                                         |
  awk '{if($1=="'${floor}'"){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-floor
  # unit一覧
  echo "_" "全て"                       > $tmp-all_unit
  # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
  awk '$4=="'${unit}'"' $tmp-shisetsu_tateya_floor_id        |
  self 4                                                     |
  LANG=C sort -u -k1,1n                                      |
  join1 key=1 $tmp-unit_master                               |
  cat $tmp-all_unit -                                        |
  awk '{if($1=="'${unit}'"){print $1,$2,"selected"}else{print $1,$2,""}}' > $tmp-unit

  if [ "${kyoshitsu}" = "_" ];then
  # unit一覧
    echo "_" "全て"                       > $tmp-all_unit
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$2=="'${tateya}'"'                                      |
    self 4                                                     |
    LANG=C sort -u -k1,1n                                      |
    join1 key=1 $tmp-unit_master                               |
    cat $tmp-all_unit -                                        > $tmp-unit
  # kyoshitsu一覧
    echo "_" "全て"                       > $tmp-all_kyoshitsu
    cat $tmp-shisetsu_tateya_floor_id                          |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    awk '$3=="'${floor}'"'                |
    self 5                                                     |
    LANG=C sort -u -k1,1n                                      |
    awk '{print $1,$1}'                                  |
    cat $tmp-all_kyoshitsu -                                        > $tmp-kyoshitsu

  # member
    echo "_" "全て"                      > $tmp-all
    cat $tmp-riyosha_status                                    |
    awk '$3=="'${floor}'"'                                 |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    self 1 5 6                                                 |
#    LANG=C sort -k1,1n                                         |
      LANG=C sort -k3,3                      |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
    cjoin1 key=1 $tmp-riyosha_master                            |
    cat $tmp-all -                                             > $tmp-riyosha
  else
    # kyoshitsu一覧
    echo "_" "全て"                > $tmp-all
    awk '$5=="'${kyoshitsu}'"' $tmp-riyosha_status               |
    # 1:施設id 2:建屋id 3:フロア 4:ユニットid 5:居室 6・・・
    self 5                                                       |
    LANG=C sort -u -k1,1n                                        |
    awk '{print $1,$1}'                                  |
    cat $tmp-all -                                         |
    awk '{if($1=="'${kyoshitsu}'"){print $1,$2,"selected"}else{print $1,$2,""}}' > ${tmp}-kyoshitsu
    # member
    echo "_" "全て"                    > $tmp-all
    cat $tmp-riyosha_status                                    |
    # 1:施設id 2:建屋 3:フロア 4:ユニット 5:部屋番号 6:利用者id
    awk '$5=="'${kyoshitsu}'"{print $1,$5,$6}'                  |
      LANG=C sort -k3,3                |
      getfirst 3 3                     |
      LANG=C sort                      |
      self 3                           |
#    LANG=C sort -k1,1n                                         |
    cjoin1 key=1 $tmp-riyosha_master -                            |
    cat $tmp-all -                                             > $tmp-riyosha

  fi

else
  :
fi

cat $tmp-riyosha    |
uniq                |
head -500        > $tmp-riyousha_result

#i######################################################################################
# formhame前の実態参照変換
calsed "&" "&amp;" ${namefile}                      |
calsed "<" "&lt;"                                   |
calsed ">" "&gt;"                                   |
calsed "\"" "&quot;"                                |
# formhame前にキーワードが　"_"　のみの場合、消去
awk '{if($1~/SEARCH_WORD/){if($2~/^_$/){$2=""};}print}'  |
# formhame前にキーワードが検索ボックスの空白を "_"から" "に戻す
awk '{if($1~/SEARCH_WORD/){gsub(/_/," ",$2)};print}'     > $tmp-namefile

#######################################################################################

# formhameの準備
floor=$(echo ${floor})
unit=$(echo ${unit})


#######################################################################################
#cp $tmp-* /home/hands/work/okuda
# namefileの再構成

cat <<- FIN > ${tmp}-name
floor ${floor}
FIN

# HTMLを作成
awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/KEIYAKU_ICHIRAN2.html |
mojihame -lshisetsu_select - $tmp-shisetsu        |
mojihame -ltateya_select - $tmp-tateya        |
mojihame -lfloor_select - $tmp-floor        |
mojihame -lunit_select  - $tmp-unit       |
mojihame -lkyoshitsu_select - $tmp-kyoshitsu |
mojihame -lnyuukyosha_select  - $tmp-riyousha_result       |
mojihame -lkeiyaku_syurui_select - ${tmp}-keiyaku |
formhame -d"_"                - ${tmp}-name    > $tmp-html


# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-exit 0
