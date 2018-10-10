#!/bin/bash
#
# AJAX_SHOKUJI_MENU_CHANGE.CGI 食事～メニュ～価格を取得するCGI
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
home_dir="/home/hands/E-LIFE"
app_dir="${home_dir}/SHOKUJI"
pompa_dir="${app_dir}/POMPA"
# MODEの取得
MODE=$(nameread "MODE" $tmp-name)

 Shisetsu=$(nameread   "Shisetsu"   $tmp-name)
 Tateya=$(nameread     "Tateya"     $tmp-name)
 Shokuji=$(nameread    "Shokuji"   $tmp-name)
 Taishoubi=$(nameread "Taishoubi" $tmp-name | sed 's/\///g')
 Shokushu=$(nameread   "Shokushu"   $tmp-name)
 Menu=$(nameread       "Menu"       $tmp-name)
 Suuryou=$(nameread    "Suuryou"     $tmp-name)

 if [ -z "${Taishoubi}" ] ; then

  TaishouYear=$(nameread   "TaishouYear"   $tmp-name)
  TaishouMonth=$(nameread   "TaishouMonth"   $tmp-name | maezero 1.2)
  [ ! -z "${TaishouYear}" ] && Taishoubi_from=$(echo "${TaishouYear}${TaishouMonth}""31")  # 最大年月日
  [ ! -z "${TaishouYear}" ] && Taishoubi_to=$(echo "${TaishouYear}${TaishouMonth}""01")    # 最小年月日

  [ -z "${Taishoubi_from}" ] && Taishoubi_from=$(date +%Y%m%d)
  [ -z "${Taishoubi_to}" ] && Taishoubi_to=$(date +%Y%m%d)
 else

  Taishoubi_from="$(echo "${Taishoubi}")"
  Taishoubi_to="$(echo "${Taishoubi}")"

 fi

# 削除だった場合
if [ "${Shokuji}" = "9" ] ; then
  
  SAKUJYO="disabled"
#  : > $tmp-shokuji     
#  : > $tmp-taishou          
#  : > $tmp-shokuji_shurui    
#  : > $tmp-shokuji_menu

else
  SAKUJYO="@"
fi

# 食事
echo "9 削除" |
cat ${tbl_dir}/CONFIG/SHOKUJI_MASTER -  |
awk '{if($1=="'${Shokuji}'"){print $0,"selected"}
      else{print $0,"@"}
     }'   > $tmp-shokuji

cat ${pompa_dir}/${Shisetsu}/SHOKUJI_MENU |
# 1:メニューid 2:メニュー名  3:食事種類    4:施設ID          5:建屋ID
# 6:入居者価格 7:ゲスト1価格 8:ゲスト2価格 9:スタッフ価格    10:朝食
# 11:昼食      12:夕食       13:おやつ     14:期間From(西暦) 15:期間To(和暦)
# 16:色

if [ ! -z "${Shisetsu}" -a ! -z "${Tateya}" -a "${MODE}" != "StaffNyuuryoku" ] ; then
  awk '$4=="'${Shisetsu}'"&&$5=="'${Tateya}'"&&$(NF-2)!="9"{print $0}' 
else
  awk '$4=="'${Shisetsu}'"&&$(NF-2)!="9"{print $0}'
fi |
# 朝食
if [ "${Shokuji}" = "1" ] ; then
  awk '$10=="1"&&$14<="'${Taishoubi_from}'"&&$15>="'${Taishoubi_to}'"&&$(NF-2)!="9"{print $0}'  > $tmp-data

# 昼食
elif [ "${Shokuji}" = "2" ] ; then
  awk '$11=="1"&&$14<="'${Taishoubi_from}'"&&$15>="'${Taishoubi_to}'"&&$(NF-2)!="9"{print $0}'  > $tmp-data

# 夕食
elif [ "${Shokuji}" = "3" ] ; then
  awk '$12=="1"&&$14<="'${Taishoubi_from}'"&&$15>="'${Taishoubi_to}'"&&$(NF-2)!="9"{print $0}'  > $tmp-data

# おやつ
elif [ "${Shokuji}" = "4" ] ; then
  awk '$13=="1"&&$14<="'${Taishoubi_from}'"&&$15>="'${Taishoubi_to}'"&&$(NF-2)!="9"{print $0}'  > $tmp-data
else

  awk '$14<="'${Taishoubi_from}'"&&$15>="'${Taishoubi_to}'"&&$(NF-2)!="9"{print $0}'  > $tmp-data
fi
# 1:メニューid 2:メニュー名 3:食事種類        4:施設ID        5:建屋ID
# 6:入居者価格 7:ゲスト価格 8:スタッフ価格    9:朝食          10:昼食
# 11:夕食      12:おやつ    13:期間From(西暦) 14:期間To(和暦) 15:色

# 対象者
#echo "1 2 3 4" |
#tarr  |
#awk '{if($1=="1"){print $0,"基本"}
#      else if($1=="2"){print $0,"入居者"}
#      else if($1=="3"){print $0,"ゲスト"}
#      else if($1=="4"){print $0,"スタッフ"}
#     }'    |
#awk '{if($1=="'${Taishousha}'"){print $0,"selected"}
#      else{print $0,"@"}
#     }'  > $tmp-taishou

# 食事種類
cat ${tbl_dir}/CONFIG/SHOKUJI_SHURUI |
awk '{if($1=="'${Shokushu}'"){print $0,"selected"}
      else{print $0,"@"}
      }'   > $tmp-shokuji_shurui
# 1:食事種類ID　2:食事種類

# Menu
[ -z "${Shokushu}" -o "${Shokushu}" = "_" ] && Shokushu="$(self 1 $tmp-shokuji_shurui | head -1)"

cat $tmp-data |
awk '$3=="'${Shokushu}'"{print $1,$2,$17=="_"?"999999":$17}' |
LANG=C sort -k3,3n |
delf 3             |
awk '{if($1=="'${Menu}'"){print $0,"selected"}
      else{print $0,"@"}
     }'  > $tmp-shokuji_menu

# 価格
[ -z "${Menu}" -o "${Menu}" = "_" ] && Menu="$(self 1 $tmp-shokuji_menu | head -1)"
#[ -z "${Taishousha}" -o "${Taishousha}" = "_" ] && Taishousha="$(self 1 $tmp-taishou | head -1)"

#if [ "${Taishousha}" = "4" ] ; then
#  Kakaku="$(awk '$1=="'${Menu}'"{print $7}' $tmp-data)"
#elif [ "${Taishousha}" = "3" ] ; then
#  Kakaku="$(awk '$1=="'${Menu}'"{print $6}' $tmp-data)"
#elif [ "${Taishousha}" = "2" ] ; then
#  Kakaku="$(awk '$1=="'${Menu}'"{print $5}' $tmp-data)"
#else

## 20140908追記
# 消費税率を取得
cat ${tbl_dir}/ZEIRITSU_GENGOU_MASTER/ZEIRITSU  |
# 1:ID 2:税率 3:適用開始日 4:適用終了日 5:削除フラグ 6:更新日時 7:userid
awk '$3<="'${Taishoubi_from}'"&&$4>="'${Taishoubi_to}'"{print $0}'   |
self 2                                               > ${tmp}-zeiritsu
zeiritsu=$(cat ${tmp}-zeiritsu | awk '{print $1+"1"}')

  NyuukyoshaKakakuZeinuki=$(awk '$1=="'${Menu}'"{print $6}' ${pompa_dir}/${Shisetsu}/SHOKUJI_MENU)
  Guest1KakakuZeinuki="$(awk '$1=="'${Menu}'"{print $7}' ${pompa_dir}/${Shisetsu}/SHOKUJI_MENU)"
  Guest2KakakuZeinuki="$(awk '$1=="'${Menu}'"{print $8}' ${pompa_dir}/${Shisetsu}/SHOKUJI_MENU)"
  StaffKakakuZeinuki="$(awk '$1=="'${Menu}'"{print $9}' ${pompa_dir}/${Shisetsu}/SHOKUJI_MENU)"

  NyuukyoshaKakaku="$(echo "${NyuukyoshaKakakuZeinuki}" | lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0)"
  Guest1Kakaku="$(echo "${Guest1KakakuZeinuki}" | lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0)"
  Guest2Kakaku="$(echo "${Guest2KakakuZeinuki}" | lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0)"
  StaffKakaku="$(echo "${StaffKakakuZeinuki}" |lcalc '$1 * '${zeiritsu}'' | marume -sage 1.0)"

# 対象者
cat << FINN > $tmp-taishousha_list
1 入居者 ${NyuukyoshaKakaku}円
2 ゲスト１ ${Guest1Kakaku}円
3 ゲスト２ ${Guest2Kakaku}円
4 スタッフ ${StaffKakaku}円
FINN

if [ "${Taishousha}" != "_" ] ; then
  cat $tmp-taishousha_list |
  awk '{if($1=="'${Taishousha}'"){print $0,"selected"}
        else{print $0,"@"}
       }'
else
  awk '{print $0,"@"}' $tmp-taishousha_list
fi  > $tmp-taishousha

###########################################################

# 嵌め込みデータの作成
cat << FIN | sed 's/ _$/ @/g' > $tmp-calsed
###SUURYOU### ${Suuryou}
###NYUUKYOSHAKAKAKU### ${NyuukyoshaKakaku}
###GUEST1KAKAKU### ${Guest1Kakaku}
###GUEST2KAKAKU### ${Guest2Kakaku}
###STAFFKAKAKU### ${StaffKakaku}
###SAKUJYO### ${SAKUJYO}
###NYUUKYOSHAKAKAKUZEINUKI### ${NyuukyoshaKakakuZeinuki}
###GUEST1KAKAKUZEINUKI### ${Guest1KakakuZeinuki}
###GUEST2KAKAKUZEINUKI### ${Guest2KakakuZeinuki}
###STAFFKAKAKUZEINUKI### ${StaffKakakuZeinuki}
FIN

###########################################################################

if [ "${MODE}" = "SHOKUJI_PATTERN" ] ; then

awk '$1=="1"' $tmp-taishousha > $tmp-taishou
awk '/\<shokuji_menu_nyuuryoku_tbl_start\>/,/\<shokuji_menu_nyuuryoku_tbl_end\>/' ${html_dir}/SHOKUJI_PATTERN_TOUROKU2.html

elif [ "${MODE}" = "StaffNyuuryoku" ] ; then

#  echo "###STAFFKAKAKUDISP### @"       >> ${tmp}-calsed
#  echo "###NYUUKYOSHAKAKAKUDISP### none"    >> ${tmp}-calsed
awk '$1=="4"' $tmp-taishousha >  $tmp-taishou

awk '/\<shokuji_menu_nyuuryoku_tbl_start\>/,/\<shokuji_menu_nyuuryoku_tbl_end\>/' ${html_dir}/SHOKUJI_JISSEKI_ICHIRAN2.html

else

awk '$1!="4"' $tmp-taishousha > $tmp-taishou
awk '/\<shokuji_menu_nyuuryoku_tbl_start\>/,/\<shokuji_menu_nyuuryoku_tbl_end\>/' ${html_dir}/SHOKUJI_YOYAKU2.html 

fi |
 #
 tee /home/hands/work/okuda/menuuuuokashii |
  mojihame -lshokuji_select - $tmp-shokuji              |
  mojihame -ltaishou_select - $tmp-taishou           |
  mojihame -lshokushu_select - $tmp-shokuji_shurui      |
  mojihame -lmenu_select - $tmp-shokuji_menu            |
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
