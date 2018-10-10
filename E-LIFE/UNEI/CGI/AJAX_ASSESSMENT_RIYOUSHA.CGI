#!/bin/bash
#
# AJAX_ASSESSMENT_RIYOUSHA.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
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
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/SHOKUJI.INI &> /dev/null

#=== 初期化 ===
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

home_dir=/home/hands/E-LIFE
app_dir="${home_dir}/UNEI"
html_dir="${app_dir}/HTML"
data_dir="/DATA/E-LIFE"
riyousha_dir="${data_dir}/UNEI/RIYOUSHA"
kengen_dir="/home/hands/E-LIFE/TBL/KENGEN_KANRI"
tbl_dir="/home/hands/E-LIFE/TBL/"
pompa_dir="${app_dir}/POMPA"

cgi_name="KOJINJYOUHOU_SHOUSAI_ASSESSMENT.CGI"

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

  Shisetsu=$(nameread   "Shisetsu" $tmp-name)
  Tateya=$(nameread     "Tateya" $tmp-name)
  Floor=$(nameread      "Floor" $tmp-name)
  Unit=$(nameread       "Unit" $tmp-name)
  Kyoshitsu=$(nameread  "Kyoshitsu" $tmp-name)
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)
  Taikyo=$(nameread     "Taikyo" $tmp-name)
  Cgi=$(nameread        "Cgi" $tmp-name)

  if [ "${Taikyo}" = "1" ] ; then
    TAIKYOCHECK="checked"
  else
    TAIKYOCHECK="@"
  fi

  today=$(date +%Y%m%d)
# モード関係なく最初の絞込み
#----------------------
# 施設選択されていない(初期状態)はログイン施設をセット
#----------------------
[ -z "${Shisetsu}" -o "${Shisetsu}" = "_" -o "${Shisetsu}" = "###ROGINSHISETSU###" ] && Shisetsu="0001"
[ -z "${Tateya}" -o "${Tateya}" = "_" ] && Tateya="$(awk '$1=="'${USERID}'"&&$2=="'${Shisetsu}'"{print $3}' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU)" # 建屋がなければ 従業員マスタから
[ -z "${Tateya}" -o "${Tateya}" = "_" ] && Tateya=$(awk '$1=="'${Shisetsu}'"{print $2}' ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR | LANG=C sort |uniq |head -1) # 従業員マスタに指定がなければ施設建屋フロアマスタの上にある方(シニアがあればシニア)

  SHISETSUNAME=$(awk '$1=="'${Shisetsu}'"{print $2}' ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON)

## 建屋取得
#--
# 従業員所属テーブルに建屋があればデフォルト
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR  |
# 1:施設ID 2:建屋ID 3:フロア
awk '$1=="'${Shisetsu}'"{print $2}'                   |
LANG=C sort |
uniq |
join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -           |
self 1 3                                                > $tmp-tateya_kari
# 1:建屋ID 2:建屋名
#-
# 建屋が選択されていたらselected
if [ -z "${Tateya}"  -o "${Tateya}" = "_" ] ;then
  cat $tmp-tateya_kari
else
  cat $tmp-tateya_kari |
  awk '{if($1=="'${Tateya}'"){print $0,"selected"}
        else{print $0,"@"}
       }'
fi    > $tmp-tateya_name

# cp $tmp-* /home/hands/work/okuda
#-------------------------------------
# モードのよる分岐

#-------------------------
# 建屋プルダウンの選択
#-------------------------
#if [ "$MODE" = "Tateya" -o "$MODE" = "Shisetsu" ] ;then
  # 建屋が選ばれていない、かつ建屋の選択肢が一つの場合はその建屋をセット
  [ -z "${Tateya}" -a "$(gyo $tmp-tateya_name)" -ge "1" ] && Tateya="$(awk '{print $1}' $tmp-tateya_name)"

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
      awk 'BEGIN{print "@ 全て"}{print $0}'
    else
      cat $tmp-floor_kari
    fi  > $tmp-floor
  # 建屋が複数から未選択の場合
  else
    echo "@" "全て"
  fi     > $tmp-floor
# 1:フロア番号 2:フロア番号

#--------------------------------------------------------------------------
# 居室・入居者の取得
#--------------------------------------------------------------------------

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
LANG=C sort       |
uniq              |
#awk '$7<="'${TaishouYear}'""'${TaishouMonth}'""31"&&$8>="'${TaishouYear}'""'${TaishouMonth}'""01"{print $5,$6}' |
#awk '$8>="'${TaishouYear}'""'${TaishouMonth}'""01"{print $5,$6}' |
#awk '$8>="'${today}'"{print $5,$6}' |
# 1:居室Ｎｏ 2:入居者Ｎｏ
#-
if [ ! -z "${Taikyo}" -a "${Taikyo}" = "1" ] ; then
  self 5 6
else
  awk '$8>="'${today}'"{print $5,$6}'
fi   |

LANG=C sort -k2,2 |
join1 key=2 ${riyousha_dir}/RIYOUSHA_MASTER -        |
LANG=C sort -k1,1                                    |
self 1/3                                             > $tmp-kyoshitsu_kari
# 1:居室番号 2:利用者ID 3:利用者名

# 2人以上の場合のみ全てという選択をつける
if [ "$(gyo $tmp-kyoshitsu_kari)" -gt "1" ]; then
  cat $tmp-kyoshitsu_kari  |
  awk 'BEGIN{print "@ 全て"}{print $1,$1}' |
#  awk '{print $1,$1}'  |
  uniq |
  awk '{if($1=="'${Kyoshitsu}'"){print $0,"selected"}
        else{print $0,"@"}
       }'                  > $tmp-kyoshitsu

#  [ -z "${Kyoshitsu}" -o "${Kyoshitsu}" = "_" ] && Kyoshitsu="$(awk '$1!="@"{print $1}' $tmp-kyoshitsu | head -1)"
  Kyoshitsu_selected=$(awk '$3=="selected"{print $1}' $tmp-kyoshitsu)

  cat $tmp-kyoshitsu_kari  |
  if [ -n "${Kyoshitsu_selected}" -a "${Kyoshitsu_selected}" != "_" -a "${Kyoshitsu_selected}" != "@" ] ; then
    awk '$1=="'${Kyoshitsu_selected}'"{print $0}'
    LANG=C sort -k2,2       |
    getfirst 2 2
  else
    LANG=C sort -k2,2       |
    getfirst 2 2      
  fi |
  LANG=C sort |
  delf 1      |
#  uniq |
  awk '{if($1=="'${Nyuukyosha}'"){print $0,"selected"}
        else{print $0,"@"}}' > $tmp-nyuukyosha
# 1:居室Ｎｏ 2:居室Ｎｏ
else
  cat $tmp-kyoshitsu_kari |
  awk '{print $1,$1}'     |
  uniq                    > $tmp-kyoshitsu

  cat $tmp-kyoshitsu_kari |
#  awk '{print $2,$3}'     |
  LANG=C sort -k2,2       |
  getfirst 2 2            |
  LANG=C sort             |
  delf 1                  |
  awk '{if($1=="'${Nyuukyosha}'"){print $0,"selected"}
        else{print $0,"@"}}' > $tmp-nyuukyosha
fi
# 1:入居者Ｎｏ 2:入居者名
   if [ "$MODE" = "Nyuukyosha" -a -n "${Nyuukyosha}" -a "${Nyuukyosha}" != "_" ] ; then
     RIYOUSHAID=${Nyuukyosha}
   elif [ $(awk '$3=="selected"{print $0}' $tmp-nyuukyosha | gyo) -gt 0 ] ; then
     RIYOUSHAID=$(awk '$3=="selected"{print $0}' $tmp-nyuukyosha | self 1)
   else
     RIYOUSHAID=$(self 1 $tmp-nyuukyosha | head -1)
   fi
# シニアアセスメント履歴
if [ "${Cgi}" = "tsuika" ] ; then
  # 履歴リスト
  cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_ASSESSMENT/${RIYOUSHAID}/${RIYOUSHAID}_*_ASSESSMENT_JYOUHOUSHEET |
  awk '$(NF-2)!="9"'                                                                                  |
  self 2 NF-1  |
  LANG=C sort -k1r,1r |
  awk '{print $1,substr($2,1,4)"/"substr($2,5,2)"/"substr($2,7,2),"@"}'   > $tmp-rireki
elif [ "${Cgi}" = "base" ] ; then
  # 履歴リスト
  cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_ASSESSMENT/${RIYOUSHAID}/${RIYOUSHAID}_*_ASSESSMENT |
  awk '$(NF-2)!="9"'                                                                                  |
  self 2 NF-1  |
  LANG=C sort -k1r,1r |                                                                                                                                          awk '{print $1,substr($2,1,4)"/"substr($2,5,2)"/"substr($2,7,2),"@"}'   > $tmp-rireki
else
  :>  $tmp-rireki
fi

# calsedデータの追記
cat << FIN > $tmp-calsed_data
###SHISETSUNAME### ${SHISETSUNAME}
###TAIKYOCHECK### ${TAIKYOCHECK}
FIN


###########################################################################

awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/KOJINJYOUHOU_SHOUSAI_ASSESSMENT2.html |
#tee /home/hands/work/okuda/ajax_test |
 #

  calsed -f $tmp-calsed_data -                          |
  mojihame -l"tateya_select"     - $tmp-tateya_name     |
  mojihame -l"floor_select"    - $tmp-floor             |
  mojihame -l"kyoshitsu_select"     - $tmp-kyoshitsu    |
  mojihame -l"nyuukyosha_select"    - $tmp-nyuukyosha   |
  mojihame -l"rireki_select" - $tmp-rireki              |
  sed 's/###SPACE###/ /g'                               |
  sed 's/\\n/\n/g'                                      |
  sed 's/###KAIGYO###/\n/g'                             > $tmp-html
#tee $tmp-formhame_mae |
#  formhame -d"_"                - $tmp-name    > $tmp-html

#cp $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
