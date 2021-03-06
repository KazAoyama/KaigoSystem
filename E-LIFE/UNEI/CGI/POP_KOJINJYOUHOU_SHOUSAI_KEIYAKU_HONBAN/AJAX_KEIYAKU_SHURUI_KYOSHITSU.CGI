#!/bin/bash
#
# AJAX_KOJINJYOUHOU_SHINKI.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by E.Okuda / 2013.11.27

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
GAMEN=$(nameread "GAMEN" $tmp-name)

  KeiyakuShurui=$(nameread "KeiyakuShurui" $tmp-name)
  Shisetsu=$(nameread "Shisetsu" $tmp-name)
  Tateya=$(nameread "Tateya" $tmp-name)
  Floor=$(nameread "Floor" $tmp-name)
  Unit=$(nameread "Unit" $tmp-name)
  Kyoshitsu=$(nameread "Kyoshitsu" $tmp-name)
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)
  KeiyakuNenrei=$(nameread "KeiyakuNenrei" $tmp-name)
  RIYOUSHAID=$(nameread "RIYOUSHAID" $tmp-name)
  NENREIREAD="readonly"
  KeiyakukikanFrom=$(nameread "KeiyakukikanFrom" $tmp-name | sed 's/\///g' | awk '$1~/^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$/{print $0}' |awk '$1!="_"{print $0}')

[ -z "${KeiyakukikanFrom}" ] && KeiyakukikanFrom="_"
# モード関係なく最初の絞込み

  # 居宅・訪問介護事業所の準備
#cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
# 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
# 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名
awk '$1=="'${Shisetsu}'"{print $1,$2}' ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER  > $tmp-jigyousho_name

  # 施設一覧の取得
#  cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON $tmp-jigyousho_name  |
#  awk '$(NF-2)!="9"{print $1,$2}'                 |
#  awk '{if($1=="'${Shisetsu}'"){print $0,"selected"}
#    else{print $0,"@"}}'   >$tmp-shisetsu_name
# 1:施設ID 2:施設名
awk '$1=="'${Shisetsu}'"{print $0}' ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
self 1 2           > $tmp-shisetsu_name
# 1:施設ＩＤ 2:施設名 3:Selected

# 施設じゃなかったら事業所情報のみしゅとく
if [ ! -s $tmp-shisetsu_name ] ; then
 cat $tmp-jigyousho_name > $tmp-shisetsu_name
# 施設だったら
else
  # 建屋一覧
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
#-------------------------------------

  [ -z "${Tateya}" -o "${Tateya}" == "_" ] && Tateya="$(head -1 $tmp-tateya_name | self 1)"

# --------------------------
 # 定員以下の居室情報の取得
 if [ -z "${KeiyakukikanFrom}" -o "${KeiyakukikanFrom}" = "_" ] ; then
   # 退去日がキョウよいあと施設内の居室情報を取得
   awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$8>"'${today}'"&&$(NF-2)!="9"{print $0}' ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS   
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室
# 6:入居者ID 7:入居日 8:退去日
 else
  awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$8>"'${KeiyakukikanFrom}'"&&$(NF-2)!="9"{print $0}' ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS
 fi |
count 1 5   |
LANG=C sort -k1,5 > $tmp-shisetsu_riyousha
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室 6:人数

if [ -s $tmp-shisetsu_riyousha ] ; then
# 居室データ
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM    |
# 1:施設ID       2:建屋ID 3:フロア 4:ユニットID 5:居室NO
# 6:居室定員人数
awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"{print $0}'   |
self 1/6          |
LANG=C sort -k1,5 |
# 現状の入居者数と定員を比較し、定員以下の部屋のみとす
join2 +"_" key=1/5 $tmp-shisetsu_riyousha - |
awk '{if($6<$7){print $0}
      else if($6=="_"){print $0}
     }'           > $tmp-taisyou_data
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室 6:現人数
# 7:定員  
else
# 居室データ
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM    |
# 1:施設ID       2:建屋ID 3:フロア 4:ユニットID 5:居室NO
# 6:居室定員人数
awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"{print $0}'   |
self 1/6          |
LANG=C sort -k1,5 > $tmp-taisyou_data
fi
#---------------------
#--------------------
# 定員以下の居室 対象データあり
if [ -s $tmp-taisyou_data ] ; then
  # フロア
  cat $tmp-taisyou_data |
  self 3                |
  uniq |
  awk '{if($1=="'${Floor}'"){print $1,$1,"selected"}
       else {print $1,$1,"@"}}' > $tmp-floor
 
  [ -z "${Floor}" -o "${Floor}" == "_" ] && Floor="$(head -1 $tmp-floor | self 1)"

  # ユニット
  if [ "${Tateya}" = "02" ] ; then
    cat $tmp-taisyou_data |
    awk '$3=="'${Floor}'"{print $4}' |
#    self 4                |
    LANG=C sort  |
    uniq |
    join1 key=1 ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME -  |
    awk '{if($1=="'${Unit}'"){print $1,$2,"selected"}
       else {print $1,$2,"@"}}' > $tmp-unit_name
  else
    : > $tmp-unit_name
  fi

  [ -z "${Unit}" -o "${Unit}" == "_" ] && Unit="$(head -1 $tmp-unit_name | self 1)"

  # 居室
  if [ "${Floor}" != "_" ] ; then
    cat $tmp-taisyou_data |
    awk '$3=="'${Floor}'"{print $0}' 
  else
    cat $tmp-taisyou_data 
  fi |

  if [ "${Unit}" != "_" ] ; then
    awk '$4=="'${Unit}'"{print $5}'
  else
    self 5
  fi |

  uniq |
  awk '{if($1=="'${Kyoshitsu}'"){print $1,$1,"selected"}
       else {print $1,$1,"@"}}' > $tmp-kyoshitsu
 
  [ -z "${Kyoshitsu}" -o "${Kyoshitsu}" == "_" ] && Kyoshitsu="$(head -1 $tmp-kyoshitsu | self 1)"

# 対象データなし
else
 echo "@ 空きなし @" > $tmp-kyoshitsu
 echo "@ @ @" > $tmp-unit_name
 echo "@ @ @" > $tmp-floor
fi

[ ! -s $tmp-tateya_name ] && echo "@ @ @" > $tmp-tateya_name
[ ! -s $tmp-kyoshitsu ] && echo "@ 空居室なし @" > $tmp-kyoshitsu
[ ! -s $tmp-unit_name ] && echo "@ @ @" > $tmp-unit_name
[ ! -s $tmp-floor ] && echo "@ @ @" > $tmp-floor


# 賃料の取得
cat ${tbl_dir}/RIYOURYOU_MASTER/KYOSHITSU_CHINRYOU |
# 1:施設ID 2:建屋ID 3:居室ID 4:期間From 5:期間To 6:賃料

if [ ! -z "${KeiyakukikanFrom}" -a "${KeiyakukikanFrom}" != "_" ] ; then
# 施設建屋居室で絞込み、期間Fromの日付が今日以前のもののみとする
  awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Kyoshitsu}'"&&$4<="'${KeiyakukikanFrom}'"{print $5,$6}' 
else
  awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Kyoshitsu}'"&&$4<="'${today}'"{print $5,$6}'
fi |
# 期限TOが入っていないあるいは未来の日付であるものにする
awk '$1>="'${today}'"||$1=="_"{print $2}' > $tmp-chinryou

if [ ! -s $tmp-chinryou -o $(gyo $tmp-chinryou) != "1" ] ; then
 chinryou="$(echo "@")"
else
 chinryou="$(cat $tmp-chinryou)"
fi

fi # 施設だったらif終了

# 入居年齢

if [ -z "${KeiyakuNenrei}" -o "${KeiyakuNenrei}" = "_" ] ; then
  awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/RIYOUSHA/RIYOUSHA_KIHON  > $tmp-kihon
#  Birthday="$(awk '{print substr($9,5,4)}' $tmp-kihon)"
#  if [ "${Birthday}" -ge "${today}" ] ;then
    KeiyakuNenrei="$(awk 'N="'${today}'"-$9{print N/10000}' $tmp-kihon | marume -sage 1.0)"
  # 誕生日が来ていなければ
#  else
#    KeiyakuNenrei="$(awk 'N="'${today}'"-$9{print N/10000-1}' $tmp-kihon | marume -sage 1.0)"
#  fi
  NENREIREAD="@"
fi

# calsedファイル
cat << FIN > $tmp-calsed_data
###KeiyakuNenrei### ${KeiyakuNenrei}
###CHINRYOU### ${chinryou}
###NENREIREAD### ${NENREIREAD}
FIN

[ ! -s $tmp-tateya_name ] && echo "@ @ @" > $tmp-tateya_name
[ ! -s $tmp-kyoshitsu ] && echo "@ @ @" > $tmp-kyoshitsu
[ ! -s $tmp-unit_name ] && echo "@ @ @" > $tmp-unit_name
[ ! -s $tmp-floor ] && echo "@ @ @" > $tmp-floor

###########################################################################

if [ -z "${GAMEN}" -o "${GAMEN}" = "_" ] ; then
  awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/KOJINJYOUHOU_SHOUSAI_SHINKI.html 
elif [ "${GAMEN}" = "KEIYAKU" ] ; then
  awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KEIYAKU.html 
fi |
 #
  mojihame -l"shisetsu_select"  - $tmp-shisetsu_name    |
  mojihame -l"tateya_select"     - $tmp-tateya_name     |
  mojihame -l"floor_select"    - $tmp-floor             |
  mojihame -l"unit_select"  - $tmp-unit_name            |
  mojihame -l"kyoshitsu_select"  - $tmp-kyoshitsu       |
  calsed -f $tmp-calsed_data - > $tmp-html

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
