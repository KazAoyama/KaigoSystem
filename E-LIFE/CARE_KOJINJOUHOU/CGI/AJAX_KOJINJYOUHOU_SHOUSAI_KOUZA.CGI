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
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null

#=== 初期化 ===
tmp=/var/tmp/${$}
html_dir="${home_dir}/UNEI/HTML"
pompa_dir="${home_dir}/UNEI/POMPA"
kengen_dir="/home/hands/E-LIFE/TBL/KENGEN_KANRI"
cgi_name="KIHONJYOUHOU_ICHIRAN.CGI"

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
GAMEN=$(nameread "GAMEN" $tmp-name)
MODE=$(nameread "MODE" $tmp-name)

  Shisetsu=$(nameread "Shisetsu" $tmp-name)
  Tateya=$(nameread "Tateya" $tmp-name)
  Floor=$(nameread "Floor" $tmp-name)
  Unit=$(nameread "Unit" $tmp-name)
  Kyoshitsu=$(nameread "Kyoshitsu" $tmp-name)
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)

  [ -z "${Shisetsu}" -o "$(echo ${Shisetsu} | awk '{print substr($1,1,1)}')" = "1" ] && Shisetsu="_"
  [ -z "${Tateya}" ] && Tateya="_"
  [ -z "${Floor}" ] && Floor="_"
  [ -z "${Unit}" ] && Unit="_"
  [ -z "${Kyoshitsu}" ] && Kyoshitsu="_"
  [ -z "${Nyuukyosha}" ] && Nyuukyosha="_"


 cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON   |
  awk '{if($1=="'${Shisetsu}'"){print $1,$2,"selected"}
    else{print $1,$2,"@"}}'   >$tmp-shisetsu_name

[ "${Shisetsu}" = "_" ] && Shisetsu=$(head -1 $tmp-shisetsu_name | self 1)

  cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM |
  awk '$1=="'${Shisetsu}'"{print $2}'                     |
  sort  |
  uniq  |
  join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -           |
  self 1 3                                                |
  awk '{if($1=="'${Tateya}'"){print $0,"selected"}
       else {print $0,"@"}}'       > $tmp-tateya_name
# 1:建屋ID 2:建屋名

[ "${Tateya}" = "_" ] && Tateya=$(head -1 $tmp-tateya_name | self 1)

  # フロア一覧
  cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM |
  awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"{print $3,$3}'  |
  LANG=C sort |
  uniq |
  awk 'BEGIN{print "@","全て"}{print $0}' |
  awk '{if($1=="'${Floor}'"){print $0,"selected"}
     else {print $0,"@"}}' > $tmp-floor

  #--
  ## ユニット取得
  #--
  # フロア選択肢が全て以外で一個になる場合そのフロアを選択していると判断
  [ "${Floor}" = "_" -a "$(gyo $tmp-floor)" -ge "1" -a "$(self 1 $tmp-floor | head -1)" != "@" ] && Floor="$(head -1 $tmp-floor | self 1)"

    # 建屋がケアの場合
    if [ "${Tateya}" = "02" ] ; then
    cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM |
    awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Floor}'"{print $4}'  |
    LANG=C sort |
    uniq |
    join1 key=1 ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME -  |
    self 1 2    |
    awk 'BEGIN{print "@","全て"}{print $0}' |
    awk '{if($1=="'${Unit}'"){print $0,"selected"}
     else{print $0,"@"}}'> $tmp-unit_name
    else
      echo "@ @"
    fi > $tmp-unit_name

#--
## 居室取得・入居者氏名取得
#--
 cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS | 

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

# ユニットの選択があった場合
if [ -n "${Unit}" -a "${Unit}" != "_" ] ; then
  awk '$4=="'${Unit}'"{print $0}'
else
  cat -
fi |

# 居室の選択があった場合
#if [ -n "${Kyoshitsu}" -a "${Kyoshitsu}" != "_" ] ; then
#  awk '$5=="'${Kyoshitsu}'"{print $0}'
#else
#  cat -
#fi |
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室
# 6:入居者ID 7:入居日 8:退去日
#-

# 退去者表示のフラグがあれば
#if [ "${TaikyoshaHyouji}" = "1" ] ; then
#  self 5 6 |
#else
# 入居期間中のものにする
  awk '$8>"'${today}'"{print $5,$6}' |
# 1:居室Ｎｏ 2:入居者Ｎｏ
#-
#fi |
LANG=C sort -k2,2 |
join1 key=2 ${pompa_dir}/RIYOUSHA/RIYOUSHA_MASTER -        |
LANG=C sort       |
uniq              > $tmp-kyoshitsu_kari
# 1:居室Ｎｏ 2:入居者Ｎｏ 3:入居者名

if [ "$(self 1 $tmp-kyoshitsu_kari | LANG=C sort |uniq | gyo)" -gt "1" ] ; then
  cat $tmp-kyoshitsu_kari  |
  awk 'BEGIN{print "@ 全て"}{print $1,$1}' 
else
  cat $tmp-kyoshitsu_kari  |
  awk '{print $1,$1}'      
fi   |
uniq |
awk '{if($1=="'${Kyoshitsu}'"){print $0,"selected"}
        else{print $0,"@"}
       }'  > $tmp-kyoshitsu

cat $tmp-kyoshitsu_kari |
# 居室の選択があった場合
if [ -n "${Kyoshitsu}" -a "${Kyoshitsu}" != "_" ] ; then
  awk '$1=="'${Kyoshitsu}'"{print $0}'
else
  cat -
fi |
self 2 3    |
LANG=C sort |
uniq        > $tmp-nyuukyosha_kari

if [ "$(gyo $tmp-nyuukyosha_kari)" -gt "1" ] ; then
  cat $tmp-nyuukyosha_kari |
  awk 'BEGIN{print "@ 全て"}{print $0}' 
else
  cat $tmp-nyuukyosha_kari 
fi |
  awk '{if($1=="'${Nyuukyosha}'"){print $0,"selected"}
        else{print $0,"@"}
       }'  >$tmp-nyuukyosha
# 1:居室Ｎｏ 2:居室Ｎｏ
# 1:入居者Ｎｏ 2:入居者名
# 施設選択されていない場合建屋以下は全てという選択肢のみ
#cp $tmp-* /home/hands/work/okuda
###########################################################################
awk '/\<shisetsu_tb_start\>/,/\<shisetsu_tb_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KOUZA.html |

tee $tmp-ajax_test |
 #
  mojihame -l"shisetsu_select"  - $tmp-shisetsu_name    |
  mojihame -l"tateya_select"     - $tmp-tateya_name     |
  mojihame -l"floor_select"    - $tmp-floor             |
  mojihame -l"unit_select"  - $tmp-unit_name            |
  mojihame -l"kyoshitsu_select"     - $tmp-kyoshitsu    |
  mojihame -l"nyuukyosha_select"    - $tmp-nyuukyosha   |
  sed 's/###SPACE###/ /g'                               |
  sed 's/\\n/\n/g'                                      |
  sed 's/###KAIGYO###/\n/g'                             |
#tee $tmp-formhame_mae |
  formhame -d"_"                - $tmp-name    > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
