#!/bin/bash
#
# AJAX_RIYOUSHA_JIKOHOU.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by E.Okuda / 2014.08.12

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
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null

#=== 初期化 ===
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

app_dir="${home_dir}/UNEI"
html_dir="${app_dir}/HTML"
kengen_dir="/home/hands/E-LIFE/TBL/KENGEN_KANRI"
data_dir="/DATA/E-LIFE"
riyousha_dir="${data_dir}/UNEI/RIYOUSHA"


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
  Kyoshitsu=$(nameread "Kyoshitsu" $tmp-name)
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)

  if [ "${MODE}" = "Nyuukyosha" ] ; then
    Kyoshitsu="_"
  elif [ "${MODE}" = "Kyoshitsu" -a "${Tateya}" ! = "00" ] ; then
#  elif [ "${MODE}" = "Kyoshitsu" ] ; then
    Nyuukyosha="_"
  else
    :
  fi

  [ -z "${Kyoshitsu}" ] && Kyoshitsu="_"
  [ -z "${Nyuukyosha}" ] && Nyuukyosha="_"

  Hasseibi=$(nameread "Hasseibi" $tmp-name)

  echo "${Hasseibi}"       |
  awk '$1~/^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$/'    > $tmp-hasseibi_check

  [ -s $tmp-hasseibi_check ] || Hasseibi="$(date +%Y%m%d)"


# モード関係なく最初の絞込み
#----------------------
# 施設選択されていない(初期状態)はログイン施設をセット
#----------------------
[ -z "${Shisetsu}" -o "${Shisetsu}" = "_" ] && Shisetsu="${SHISETSUID}"

## 建屋取得
#--
# 従業員所属テーブルに建屋があればデフォルト
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR  |
# 1:施設ID 2:建屋ID 3:フロア
awk '$1=="'${Shisetsu}'"{print $2}'                   |
LANG=C sort -u                                        |
join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -  |
self 1 3                                              > $tmp-tateya_kari
# 1:建屋ID 2:建屋名
#-
  cat $tmp-tateya_kari                   |
  awk 'BEGIN{print "00","@"}{print $0}'  |
  awk '{if($1=="'${Tateya}'"){print $0,"selected"}
        else{print $0,"@"}
       }'                                > $tmp-tateya_name

# cp $tmp-* /home/hands/work/okuda
#-------------------------------------
# モードのよる分岐

#-------------------------
# 建屋プルダウンの選択
#-------------------------

  # フロア一覧
  if [ -n "${Tateya}" -a "${Tateya}" != "_" ] ; then
    cat ${riyousha_dir}/SHISETSU_RIYOUSHA_STATUS |
    awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"{print $3,$3}'  |
    sort  |
    uniq  |
awk '{if($1=="'${Floor}'"){print $0,"selected"}
        else{print $0,"@"}
       }'  >$tmp-floor_kari
# 1:フロア 2:フロア
    # フロアが2つ以上の場合のみ全てという選択をつける
    if [ "$(gyo $tmp-floor_kari)" -gt "1"  ]; then
      cat $tmp-floor_kari |
      awk 'BEGIN{print "@ 全"}{print $0}'
    else
      cat $tmp-floor_kari
    fi  > $tmp-floor
  # 建屋が複数から未選択の場合
  else
    echo "@" "@"
  fi     > $tmp-floor
# 1:フロア番号 2:フロア番号

#--------------------------------------------------------------------------
# 居室・入居者の取得
#--------------------------------------------------------------------------
if [ -z "${Tateya}" -o "${Tateya}" = "_" -o "${Tateya}" = "00" ] ; then
#if [ -z "${Tateya}" -o "${Tateya}" = "_" ] ; then
 : > $tmp-kyoshitsu
  cat ${pompa_dir}/RIYOUSHA/JIGYOUSHO_RIYOUSHA_STATUS |
  awk '$(NF-2)!="9"' |
  awk '$1=="'${Shisetsu}'"' |
  LANG=C sort -k2,2 |
  cjoin1 key=2 ${pompa_dir}/RIYOUSHA/RIYOUSHA_MASTER -        |
  self 2 3 |
  sort -k1,1  |
  LANG=C sort |
  uniq |
  awk '{if($1=="'${Nyuukyosha}'"){print $0,"selected"}
        else{print $0,"@"}}' > $tmp-nyuukyosha

else

# 施設の選択があれば施設内の、そうでなければ全入居者の居室を取得
cat ${riyousha_dir}/SHISETSU_RIYOUSHA_STATUS  |
awk '$(NF-2)!="9"' |

if [ -n "${Shisetsu}" -a "${Shisetsu}" != "_" ] ; then
  awk '$1=="'${Shisetsu}'"{print $0}'    
# 1:施設ＩＤ 2:建屋ＩＤ 3:フロア 4:ユニットＩＤ 5:居室Ｎｏ
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
#tee $tmp-kyoshitsu_kari_kari |

# 居室の選択があった場合
#if [ -n "${Kyoshitsu}" -a "${Kyoshitsu}" != "_" ] ; then
#  awk '$5=="'${Kyoshitsu}'"{print $0}'
#else
#  cat -
#fi |
# 1:施設ＩＤ 2:建屋ＩＤ    3:フロア 4:ユニットＩＤ 5:居室Ｎｏ
# 6:入居者   7:入居開始日  8:退去日
#-
#-----
# 日付のチェック
#-----
# 対象期間に入居している人のみにする(入居開始日が該当月末より前かつ終わりが該当月はじめより後)
LANG=C sort -u      |
#awk '$7<="'${TaishouYear}'""'${TaishouMonth}'""31"&&$8>="'${TaishouYear}'""'${TaishouMonth}'""01"{print $5,$6}' |
if [ ! -z "${Hasseibi}" -a "${Hasseibi}" != "_" ] ; then
  awk '$7<="'${Hasseibi}'"&&$8>="'${Hasseibi}'"{print $0}' 
# 1:居室Ｎｏ 2:入居者Ｎｏ
#-
elif [ ! -z "${Houkakubi}" -a "${Houkokubi}" != "_"] ;then
  awk '$7<="'${Hasseibi}'"&&$8>="'${Houkokubi}'"{print $0}'
else
  cat -
fi |
tee $tmp-kyoshitsu_karimae |
self 5 6          |
LANG=C sort -k2,2 |
join1 key=2 ${riyousha_dir}/RIYOUSHA_MASTER -        |
LANG=C sort -k1,1                                    > $tmp-kyoshitsu_kari

  # 入居者が選択されていて居室が選択されていない場合居室を取得
  if [ "${Nyuukyosha}" != "_" -a "${Kyoshitsu}" = "_" ] ; then
    Kyoshitsu=$(awk '$6=="'${Nyuukyosha}'"&&$(NF-2)!="9"{print $5}' $tmp-kyoshitsu_karimae | head -1)
  else
   :
  fi


# 2人以上の場合のみ全てという選択をつける
if [ "$(gyo $tmp-kyoshitsu_kari)" -gt "1" ]; then
  cat $tmp-kyoshitsu_kari  |
#  awk 'BEGIN{print "@ 全て"}{print $1,$1}' |
  awk '{print $1,$1}'  |
  uniq |
    awk '{if($1=="'${Kyoshitsu}'"){print $0,"selected"}
        else{print $0,"@"}
       }'                  > $tmp-kyoshitsu

#  [ -z "${Kyoshitsu}" -o "${Kyoshitsu}" = "_" ] && Kyoshitsu="$(awk '$1!="@"{print $1}' $tmp-kyoshitsu | head -1)"
   Kyoshitsu_selected=$(awk '$3=="selected"{print $1}' $tmp-kyoshitsu)

  cat $tmp-kyoshitsu_kari  |
  self 1/3                 |
  if [ -n "${Kyoshitsu_selected}" -a "${Kyoshitsu_selected}" != "_" -a "${Kyoshitsu_selected}" != "@" ] ; then
    awk '{if($1=="'${Kyoshitsu_selected}'"){print $0,"selected"}else{print $0,"@"}
         }'
  else
    cat -
  fi |
  LANG=C sort -k2,2 |
  getfirst 2 2      |
  LANG=C sort       |
#  self 2 3          |
  delf 1            |
  if [ ! -z "${Nyuukyosha}" -a "${Nyuukyosha}" != "_" ] ; then
    awk '{if($1=="'${Nyuukyosha}'"){print $0,"selected"}
        else{print $0,"@"}}' 
  else
    cat -
  fi > $tmp-nyuukyosha
# 1:居室Ｎｏ 2:居室Ｎｏ
else
  cat $tmp-kyoshitsu_kari |
  awk '{print $1,$1}'     |
  uniq                    > $tmp-kyoshitsu

  cat $tmp-kyoshitsu_kari |
  self 1/3                |
  if [ -n "${Kyoshitsu_selected}" -a "${Kyoshitsu_selected}" != "_" -a "${Kyoshitsu_selected}" != "@" ] ; then
    awk '{if($1=="'${Kyoshitsu_selected}'"){print $0,"selected"}else{print $0,"@"}
         }'
  else
    cat -
  fi |
  LANG=C sort -k2,2 |
  getfirst 2 2      |
  LANG=C sort       |
  delf 1            |
#  self 2 3          |
#  awk '{print $2,$3}'     |
#  LANG=C sort -u          |
  if [ ! -z "${Nyuukyosha}" -a "${Nyuukyosha}" != "_" ] ; then
    awk '{if($1=="'${Nyuukyosha}'"){print $0,"selected"}
        else{print $0,"@"}}'
  else
    cat -
  fi > $tmp-nyuukyosha
fi
fi

awk '$NF=="selected"' $tmp-nyuukyosha > $tmp-nyuukyoshaselected
# selected 二人についてたら最初のほうの人だけにス
if [ "$(gyo $tmp-nyuukyoshaselected)" -lt "1" ] ; then
 :
else
 nyuukyoshaselected="$(cat $tmp-nyuukyoshaselected | head -1 | self 1)"
 awk '{if($1=="'${nyuukyoshaselected}'"){print $1,$2,"selected"}else{print $1,$2,"@"}
      }' $tmp-nyuukyosha  > $tmp-nyuukyosha_new
 mv $tmp-nyuukyosha_new $tmp-nyuukyosha
# 1:入居者Ｎｏ 2:入居者名
fi

  Nyuukyosha_selected=$(awk '$3=="selected"{print $1}' $tmp-nyuukyosha | head -1)
  [ -z ${Nyuukyosha_selected} ] && Nyuukyosha_selected=$(head -1 $tmp-nyuukyosha | self 1 | head -1)

# 入居者が洗濯されているならば
if [ ! -z "${Nyuukyosha_selected}" -a "${Nyuukyosha_selected}" != "_" -a "${Nyuukyosha_selected}" != "@" ] ;then

  # 発生日の時点の年齢と介護度を取得
  if [ ! -z "${Hasseibi}" -a "${Hasseibi}" != "_" ] ; then
  # 年齢準備
  cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KIHON  |
  awk '$1=="'${Nyuukyosha_selected}'"&&$(NF-2)!="9"{print $9}' > $tmp-birthday
  # 介護度準備
  cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KAIGOHOKEN  |
  awk '$1=="'${Nyuukyosha_selected}'"&&$23<="'${Hasseibi}'"&&$28>="'${Hasseibi}'"&&$(NF-2)!="9"{print $3}' > $tmp-kaigodo
    Nenrei="$(awk 'N="'${Hasseibi}'"-$1{print N/10000}' $tmp-birthday | marume -sage 1.0)"
    Kaigodo="$(cjoin1 key=1 $tmp-kaigodo ${tbl_dir}/CONFIG/KAIGODO_MASTER | self 2 | tail -1)"
  else
    Nenrei=""
    Kaigodo=""
  fi
else
  Nenrei=""
  Kaigodo=""
fi

[ -z "${Kaigodo}" ] && Kaigodo="介護認定なし"

# calsedデータの追記
cat << FIN > $tmp-calsed_data
###Nenrei### ${Nenrei}
###Kaigodo### ${Kaigodo}
FIN
###########################################################################
  awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/JIKOHOU_SHOUSAI2.html |
#tee /home/hands/work/okuda/ajax_test |
 #
  mojihame -l"tateya_select"     - $tmp-tateya_name     |
  mojihame -l"floor_select"    - $tmp-floor             |
  mojihame -l"kyoshitsu_select"     - $tmp-kyoshitsu    |
  mojihame -l"nyuukyosha_select"    - $tmp-nyuukyosha   |
calsed -f $tmp-calsed_data -                            |
  sed 's/###SPACE###/ /g'                               |
  sed 's/\\n/\n/g'                                      |
  sed 's/###KAIGYO###/\n/g'                             > $tmp-html
#tee $tmp-formhame_mae |
#  formhame -d"_"                - $tmp-name    > $tmp-html

cp $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
