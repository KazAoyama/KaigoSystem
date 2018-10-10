#!/bin/bash
#
# AJAX_KIHONJYOUHOU_ICHIRAN.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by E.Okuda / 2013.11.21

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#=== ログ ===
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source  /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null

#=== 初期化 ===
tmp=/var/tmp/${$}
html_dir="${home_dir}/UNEI/HTML"
pompa_dir="${home_dir}/UNEI/POMPA"

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

  Shisetsu=$(nameread "Shisetsu" $tmp-name)
  Tateya=$(nameread "Tateya" $tmp-name)
  Floor=$(nameread "Floor" $tmp-name)
  Unit=$(nameread "Unit" $tmp-name)
  Kyoshitsu=$(nameread "Kyoshitsu" $tmp-name)
  KikanFrom=$(nameread "KikanFrom" $tmp-name)
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)

  if [ "${MODE}" = "riyousha_i" ] ; then
   Kyoshitsu=""
  elif [ "${MODE}" = "Tateya" ] ; then
   Floor=""
   Unit=""
   Kyoshitsu=""
   Nyuukyosha=""
  elif [ "${MODE}" = "Floor" ] ; then
   Unit=""
   Kyoshitsu=""
   Nyuukyosha=""
  elif [ "${MODE}" = "Unit" ] ; then
   Kyoshitsu=""
   Nyuukyosha=""
  elif [ "${MODE}" = "Kyoshitsu" ] ; then
   Nyuukyosha=""
  else
   : 
  fi

  [ -z "${Shisetsu}" ] && Shisetsu="_"
  [ -z "${Tateya}" ] && Tateya="_"
  [ -z "${Floor}" ] && Floor="_"
  [ -z "${Unit}" ] && Unit="_"
  [ -z "${Kyoshitsu}" ] && Kyoshitsu="_"
  [ -z "${Nyuukyosha}" ] && Nyuukyosha="_"
  [ -z "${KikanFrom}" ] && KikanFrom="_"

#--------------------------------------------------------------------------
# 施設～居室の取得
#--------------------------------------------------------------------------

echo "${Shisetsu}" |
join1 key=1 - ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
self 1 2           > $tmp-shisetsu_name
# 1:施設ＩＤ 2:施設名 3:Selected

#--
  # 建屋一覧
#---
  # 施設が選択されていたら絞込み
 if [ -n "${Shisetsu}" -a "${Shisetsu}" != "_" ] ; then
  cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR    |
# 1:施設ID 2:建屋ID 3:フロア
  awk '$1=="'${Shisetsu}'"&&$(NF-2)!="9"{print $2}'       |
  LANG=C sort  |
  uniq  |
  join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -    |
  self 1 3                                                |
  awk '{if($1=="'${Tateya}'"){print $0,"selected"}
       else {print $0,"@"}}'       > $tmp-tateya_name
# 1:建屋ID 2:建屋名

  # 施設が選ばれていない場合
 else
    echo "@ ←選択してください" > $tmp-tateya_name
 fi

##############################################
#いろいろやる前にまず期間で候補絞る
#入院期間の選択があったら、その期間の入居者
if [ "${KikanFrom}" != "_" ] ; then
  KikanFrom=$(echo ${KikanFrom} | tr -d "/")
  awk '$8>="'${KikanFrom}'" &&$(NF-2)!="9" ' ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS
#じゃなければ本日で限定
else
  awk '$7<="'${today}'"&&$8>="'${today}'" &&$(NF-2)!="9" ' ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS
fi                                                    > ${tmp}-filtered_riyousha
##################################################

  # 入居者が選択されていて居室が選択されていない場合居室を取得
  if [ "${Nyuukyosha}" != "_" -a "${Kyoshitsu}" = "_" ] ; then
    Kyoshitsu=$(awk '$6=="'${Nyuukyosha}'"&&$(NF-2)!="9"{print $5}' ${tmp}-filtered_riyousha | head -1)
  else
   :
  fi

#-------------------------------------
# 建屋がなかったら建屋リストの一番上をセット
[ -z "${Tateya}" -o "${Tateya}" == "_" ] && Tateya="$(head -1 $tmp-tateya_name | self 1)"
#--
# フロア一覧
#--
cat ${tmp}-filtered_riyousha  |
awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"{print $3,$3}'  |
LANG=C sort  |
uniq         |
awk 'BEGIN{print "_","全て"}{print $0}'         |
awk '{if($1=="'${Floor}'"){print $0,"selected"}
       else {print $0,"@"}}'                    > $tmp-floor

## フロアがなかったらフロアリストの一番上をセット
#[ -z "${Floor}" -o "${Floor}" = "_" ] && Floor="$(head -1 $tmp-floor | self 1)"

#上のリストで何かしら"selected"ならそれがUnit
if [ "$(awk '$3=="selected"' $tmp-floor | gyo)" = "1" ] ;then
  Floor=$(awk '$3=="selected"{print $1}' $tmp-floor)
else
#じゃなければ一番上がFloor
  Floor=$(head -1 $tmp-floor | self 1)
fi

#--
# ユニット一覧
#---
# ユニットは建屋がケアのときのみ
if [ "${Tateya}" = "02" ] ; then
  cat ${tmp}-filtered_riyousha  |
  awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Floor}'"&&$(NF-2)!="9"{print $4}'  |
  LANG=C sort |
  uniq |
  join1 key=1 ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME -  |
  self 1 2 |
  awk 'BEGIN{print "_","全て"}{print $0}'             |
  awk '{if($1=="'${Unit}'"){print $0,"selected"}
       else {print $0,"@"}}'
else
  echo "@ @"
fi > $tmp-unit_name


#上のリストで何かしら"selected"ならそれがUnit
if [ $(awk '$3=="selected"' $tmp-unit_name | gyo) = "1" ] ;then
  Unit=$(awk '$3=="selected"{print $1}' $tmp-unit_name)
else
#じゃなければ一番上がUnit
  Unit=$(head -1 $tmp-unit_name | self 1)
fi

# 居室取得
  cat ${tmp}-filtered_riyousha                  |
#if [ "${Tateya}" = "02" ] ; then
#  awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Floor}'"&&$4=="'${Unit}'"&&$(NF-2)!="9"{print $5,$5}'
#else
#  awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Floor}'"&&$(NF-2)!="9"{print $5,$5}'
#fi |
  awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"{print $0}' |

if [ "${Floor}" != "_" ] ; then
  awk '$3=="'${Floor}'"{print $0}'
else
  cat -
fi |

if [ ! -z "${Unit}" -a "${Unit}" != "_" -a "${Unit}" != "@" ] ; then
  awk '$3=="'${Unit}'"{print $0}'
else
  cat -
fi |
tee $tmp-kyoshitsu_kari |
self 5 5    |
LANG=C sort |
uniq        |
awk '{if($1=="'${Kyoshitsu}'"){print $0,"selected"}
       else {print $0,"@"}}' > $tmp-kyoshitsu

Kyoshitsu="$(awk '$3=="selected"{print $1}' $tmp-kyoshitsu | head -1)"
[ -z "${Kyoshitsu}" ] && Kyoshitsu="$(cat $tmp-kyoshitsu | self 1 | head -1)"


##上のリストで何かしら"selected"ならそれがKyoshitsu
#if [ $(awk '$3=="selected"' $tmp-kyoshitsu | gyo) = "1" ] ;then
#  Kyoshitsu=$(awk '$3=="selected"{print $1}' $tmp-kyoshitsu)
#else
#じゃなければ一番上がKyoshitsu
#  Kyoshitsu=$(head -1 $tmp-kyoshitsu | self 1)
#fi
#-------------------------------------------------------------------------
# 居室・入居者の取得
#--------------------------------------------------------------------------

# 施設の選択があれば施設内の、そうでなければ全入居者の居室を取得
cat ${tmp}-filtered_riyousha  |
if [ -n "${Shisetsu}" -a "${Shisetsu}" != "_" ] ; then
  awk '$1=="'${Shisetsu}'"{print $0}'    
# 1:施設ＩＤ 2:建屋ＩＤ 3:フロア 4:ユニットＩＤ 5:居室Ｎｏ 6:居室
# 7 入居日 8:退去日
else
  cat - 
fi |

# 建屋の選択があった場合
if [ -n "${Tateya}" -a "${Tateya}" != "_" ] ; then
  awk '$2=="'${Tateya}'"{print $0}'
else
  cat -
fi |
# 1:施設ＩＤ 2:建屋ＩＤ 3:フロア 4:ユニットＩＤ 5:居室Ｎｏ
#-
# フロアの選択があった場合
if [ -n "${Floor}" -a "${Floor}" != "_" ] ; then
  awk '$3=="'${Floor}'"{print $0}'
else
  cat -
fi |
#-

# ユニットの選択があった場合
if [ -n "${Unit}" -a "${Unit}" != "_" -a "${Unit}" != "@" ] ; then
  awk '$4=="'${Unit}'"{print $0}'
else
  cat -
fi |
tee $tmp-kyoshitsu_kari |

# 居室の選択があった場合
#if [ -n "${Kyoshitsu}" -a "${Kyoshitsu}" != "_" ] ; then
#  awk '$5=="'${Kyoshitsu}'"{print $0}'
#else
#  cat -
#fi |
self 5 6             |
# 入居期間中のものにする
#awk '{if($7<"'${today}'"&&$8>"'${today}'"&&$(NF-2)!="9"){print $5,$6}
#      else if($7<"'${today}'"&&$8=="_"&&$(NF-2)!="9"){print $5,$6}
#     }'    |
#awk '$8>"'${today}'"{print $5,$6}' | # 既に期間絞ってました
LANG=C sort -k2,2 |
getfirst 2 2                                                |
# 1:居室Ｎｏ 2:入居者Ｎｏ
#-
join1 key=2 ${pompa_dir}/RIYOUSHA/RIYOUSHA_MASTER -         |
self 1/3                                                    |
LANG=C sort -k1,1                                           |
# 1:居室Ｎｏ 2:入居者Ｎｏ 3:入居者名
# 居室の選択があった場合
if [ -n "${Kyoshitsu}" -a "${Kyoshitsu}" != "_" ] ; then
  awk '{if($1=="'${Kyoshitsu}'"){print $0,"selected"}
        else{print $0,"@"}
       }'
else
  awk '{print $1,$2,$3,"@"}'
fi |
delf 1   |
#self 2 3 |
uniq     |
if [ ! -z "${Nyuukyosha}" -a "${Nyuukyosha}" != "_" ] ; then
   awk '{if($1=="'${Nyuukyosha}'"){print $1,$2,"selected"}
       else {print $1,$2,"@"}}' 
else
  cat -
fi > $tmp-nyuukyosha

awk '$NF=="selected"' $tmp-nyuukyosha > $tmp-nyuukyoshaselected

if [ "$(gyo $tmp-nyuukyoshaselected)" -le "1" ] ; then
 :
else
 nyuukyoshaselected="$(cat $tmp-nyuukyoshaselected | head -1 | self 1)"
 awk '{if($1=="'${nyuukyoshaselected}'"){print $1,$2,"selected"}else{print $1,$2,"@"}
      }' $tmp-nyuukyosha  > $tmp-nyuukyosha_new
 mv $tmp-nyuukyosha_new $tmp-nyuukyosha
fi

###########################################################################

awk '/\<riyoushainit_select_start\>/,/\<riyoushainit_select_end\>/' ${html_dir}/NYUUINGAIHAKU_SHOUSAI.html |

 #
  mojihame -l"riyoushaname_select" - $tmp-nyuukyosha   |
#tee $tmp-formhame_mae |
#  formhame -d"_"   - $tmp-name    |
sed 's/###SPACE###/ /g'                                |
sed 's/\\n/\n/g'                                       |
sed 's/###KAIGYO###/\n/g'                              > $tmp-html

#cp $tmp-* /home/hands/work/okuda

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
