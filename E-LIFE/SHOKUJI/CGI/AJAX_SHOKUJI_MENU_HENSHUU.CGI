#!/bin/bash
#
# 食事メニュー変更
#            食事メニュー登録画面から呼び出しにて
#                                Ajax による使用を想定。
#
#
# Written by E.Okuda / 2014.01.08

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#=== ログ ===
exec 2> /home/hands/E-LIFE/SHOKUJI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null

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
SHOKUJIMENUID=$(nameread "SHOKUJIMENUID" $tmp-name)
Shisetsu=$(nameread "Shisetsu" $tmp-name)
Tateya=$(nameread "Tateya" $tmp-name)
today="$(date +%Y%m%d)"

awk '$1=="'${SHOKUJIMENUID}'"&&$(NF-2)!="9"&&$4=="'${Shisetsu}'"&&$5=="'${Tateya}'"{print $0}' ${pompa_dir}/${Shisetsu}/SHOKUJI_MENU  |
delf 4 5 > $tmp-data
# 1:メニューid  2:メニュー名      3:食事種類      4:入居者価格 5:ゲスト1価格
# 6:ゲスト2価格 7:スタッフ価格    8:朝食          9:昼食       10:夕食
# 11:おやつ     12:期間From(西暦) 13:期間To(和暦) 14:色        15:表示順
# 16:喫食対象   17:ＧＨ価格

  KikanFrom=$(awk '{print substr($12,1,4)"/"substr($12,5,2)"/"substr($12,7,2)}' $tmp-data)
  KikanTo=$(awk '{print $13!="99999999"?substr($13,1,4)"/"substr($13,5,2)"/"substr($13,7,2):"@"}' $tmp-data)
  ShokujiMenu=$(awk '{print $2}' $tmp-data)
  NyuukyoshaKakaku=$(awk '{print $4}' $tmp-data)
  Guest1Kakaku=$(awk '{print $5}' $tmp-data)
  Guest2Kakaku=$(awk '{print $6}' $tmp-data)
  StaffKakaku=$(awk '{print $7}' $tmp-data)
  GreenHouseKakaku=$(awk '{print $17}' $tmp-data)
  Choushoku=$(awk '{print $8}' $tmp-data)
  Chuushoku=$(awk '{print $9}' $tmp-data)
  Yuushoku=$(awk '{print $10}' $tmp-data)
  Oyatsu=$(awk '{print $11}' $tmp-data)
  Iro=$(awk '{print $14}' $tmp-data)
  Shokushu=$(awk '{print $3}' $tmp-data)
  Hyouji=$(awk '{print $15}' $tmp-data)
  KisshokuTaishou=$(awk '{print $16}' $tmp-data)

# 喫食対象=１だったらチェック
if [ "${KisshokuTaishou}" = "1" ] ; then
  KisshokuTaishouChecked="checked"
else
  KisshokuTaishouChecked="@"
fi

# 非表示食事
awk '$1=="'${SHOKUJIMENUID}'"&&$(NF-2)!="9"{print $0}' ${pompa_dir}/${Shisetsu}/SHOKUJI_RESTAURANT_MENU > $tmp-data_hihyouji_restaurant

  hideRestaurant=$(awk '{print $2}' $tmp-data_hihyouji_restaurant)

# レストラン非表示
if [ "${hideRestaurant}" = "1" ] ; then
  dispHideRestaurant="checked"
else
  dispHideRestaurant=""
fi

# ドリンクタイプ
awk '$1=="'${SHOKUJIMENUID}'"&&$(NF-2)!="9"{print $0}' ${pompa_dir}/${Shisetsu}/SHOKUJI_DRINKTYPE > $tmp-data_drink_type

  drinkType=$(awk '{print $2}' $tmp-data_drink_type)

# ドリンクの場合のタイプ
cat ${home_dir}/TBL/CONFIG/SHOKUJI_MENU_TYPE |
LANG=C sort -k4,4 |
awk '$1=="03"{if($2=="'${drinkType}'"){$4="checked"}else{$4="@"}print $2,$3,$4}' > $tmp-drink_type

# レストラン対象施設かどうか
cat ${home_dir}/TBL/CONFIG/RESTAURANT_SHISETSU_LIST |
while read res_shisetsuid ;do
    if [ "${res_shisetsuid}" = "${Shisetsu}" ] ; then
       echo "1" > $tmp-disp_restaurant
       break
    else
       echo "0" > $tmp-disp_restaurant
    fi
: ; done

checkRestaurant=$(cat $tmp-disp_restaurant)
# 現在はセンター南（0003）のみ -> 施設増える対応に変更
if [ "${checkRestaurant}" = "1" ] ; then
   restaurantSeigyo=""
else
   restaurantSeigyo="none"
fi

# 食種（ドリンク時はドリンクタイプ表示
if [ "${Shokushu}" = "03" ] ; then
   hideDrinkType=""
else
   hideDrinkType="none"
fi


# 消費税率を取得
cat ${tbl_dir}/ZEIRITSU_GENGOU_MASTER/ZEIRITSU  |
# 1:ID 2:税率 3:適用開始日 4:適用終了日 5:削除フラグ 6:更新日時 7:userid
awk '$3<="'${today}'"&&$4>="'${today}'"{print $0}'   |
self 2                                               > ${tmp}-zeiritsu
### 20140908変更
# zeiritsu=$(cat ${tmp}-zeiritsu | awk '{print $1}')
zeiritsu=$(cat ${tmp}-zeiritsu | awk '{print $1+"1"}')

NyuukyoshaZeikomi=$(echo "${NyuukyoshaKakaku}" | lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0 | awk '{print "税込"$1"円"}')
Guest1Zeikomi=$(echo "${Guest1Kakaku}" | lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0 | awk '{print "税込"$1"円"}')
Guest2Zeikomi=$(echo "${Guest2Kakaku}" | lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0 | awk '{print "税込"$1"円"}')
StaffZeikomi=$(echo "${StaffKakaku}" | lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0 | awk '{print "税込"$1"円"}')
GreenHouseZeikomi=$(echo "${GreenHouseKakaku}" | lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0 | awk '{print "税込"$1"円"}')
###########################################################

# 嵌め込みデータの作成
cat << FIN | sed 's/ _$/ @/g' > $tmp-calsed
###KIKANFROM### ${KikanFrom}
###KIKANTO### ${KikanTo}
###SHOKUJIMENU### ${ShokujiMenu}
###NYUUKYOSHAKAKAKU### ${NyuukyoshaKakaku}
###GUEST1KAKAKU### ${Guest1Kakaku}
###GUEST2KAKAKU### ${Guest2Kakaku}
###STAFFKAKAKU### ${StaffKakaku}
###GREENHOUSEKAKAKU### ${GreenHouseKakaku}
###SHOKUJIMENUID### ${SHOKUJIMENUID}
###Hyouji### ${Hyouji}
###NyuukyoshaZeikomi### ${NyuukyoshaZeikomi}
###Guest1Zeikomi### ${Guest1Zeikomi}
###Guest2Zeikomi### ${Guest2Zeikomi}
###StaffZeikomi### ${StaffZeikomi}
###GreenHouseZeikomi### ${GreenHouseZeikomi}
###KisshokuTaishouChecked### ${KisshokuTaishouChecked}
###HIDERESTAURANT### ${dispHideRestaurant}
###RESTAURANTSEIGYO### ${restaurantSeigyo}
###HIDEDRINKTYPE### ${hideDrinkType}
FIN

if [ ! -z ${Choushoku} -a ${Choushoku} = "1" ]; then
  echo "###ASACHECK###" "checked" >> ${tmp}-calsed
else
  echo "###ASACHECK###" "@"  >> ${tmp}-calsed
fi

if [ ! -z ${Chuushoku} -a ${Chuushoku} = "1" ]; then
  echo "###HIRUCHECK###" "checked" >> ${tmp}-calsed
else
  echo "###HIRUCHECK###" "@"  >> ${tmp}-calsed
fi

if [ ! -z ${Yuushoku} -a ${Yuushoku} = "1" ]; then
  echo "###YORUCHECK###" "checked" >> ${tmp}-calsed
else
  echo "###YORUCHECK###" "@"  >> ${tmp}-calsed
fi

if [ ! -z ${Oyatsu} -a ${Oyatsu} = "1" ]; then
  echo "###OYATSU###" "checked" >> ${tmp}-calsed
else
  echo "###OYATSU###" "@"  >> ${tmp}-calsed
fi

# 色
cat ${tbl_dir}/CONFIG/COLOR_TABLE |
awk '$1!="000"{print $0}'         |
awk '{if($1=="'${Iro}'"){print $1,$3,"selected"}
      else{print $1,$3,"@"}
      }'  > $tmp-color

# 食事種類
cat ${tbl_dir}/SHOKUJI/SHOKUJI_SHURUI |
awk '{if($1=="'${Shokushu}'"){print $0,"selected"}
      else{print $0,"@"}
      }'   > $tmp-shokuji_syurui
# 1:食事種類ID　2:食事種類


###########################################################################

awk '/\<shokuji_menu_tb_start\>/,/\<shokuji_menu_tb_end\>/' ${html_dir}/SHOKUJI_MENU_TOUROKU2.html |
tee $tmp-ajax_test |
 #
  mojihame -lcolor_select - $tmp-color                  |
  mojihame -lshokuji_shurui_select - $tmp-shokuji_syurui   |
  mojihame -l###DRINKTYPE### - $tmp-drink_type   |
  calsed -f $tmp-calsed -                               |
  sed 's/###SPACE###/ /g'                               |
  sed 's/\\n/\n/g'                                      |
  sed 's/###KAIGYO###/\n/g'                              > $tmp-html
#tee $tmp-formhame_mae |
#  formhame -d"_" - $tmp-name    > $tmp-html
#cp $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
