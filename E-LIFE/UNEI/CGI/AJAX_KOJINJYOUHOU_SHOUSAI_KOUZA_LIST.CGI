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
app_dir="${home_dir}/UNEI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA"

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
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)
  NYUUKYOSHISETSUID=$(nameread "NYUUKYOSHISETSUID" $tmp-name)

  KouzaSentaku=$(nameread "KouzaSentaku" $tmp-name)

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
    awk '{if($1=="'${Unit}'"){print $0,"selected"}
     else{print $0,"@"}}'> $tmp-unit_name
    else
      echo "@ @"
    fi > $tmp-unit_name


#--------------------------------------------------------------------------
# 居室・入居者の取得
#--------------------------------------------------------------------------

# 施設の選択があれば施設内の、そうでなければ全入居者の居室を取得
 cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |

if [ -n "${Shisetsu}" -a "${Shisetsu}" != "_" ] ; then
  awk '$1=="'${Shisetsu}'"{print $0}' 
# 1:施設ＩＤ 2:建屋ＩＤ 3:フロア 4:ユニットＩＤ 5:居室Ｎｏ 6:入居者
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
# ユニットの選択があった場合
if [ -n "${Unit}" -a "${Unit}" != "_" ] ; then
  awk '$4=="'${Unit}'"{print $0}'
else
  cat -
fi |

# 居室の選択があった場合
if [ -n "${Kyoshitsu}" -a "${Kyoshitsu}" != "_" ] ; then
  awk '$5=="'${Kyoshitsu}'"{print $0}'
else
  cat -
fi |

# 居室の選択があった場合
if [ -n "${Nyuukyosha}" -a "${Nyuukyosha}" != "_" ] ; then
  awk '$6=="'${Nyuukyosha}'"{print $0}'
else
  cat -
fi |
self 6 |
### 201401001 退去者のも表示にしておきましょう
#awk '$8>"'${today}'"{print $6}' |
LANG=C sort       |
uniq              |
join1 key=1 ${pompa_dir}/RIYOUSHA/RIYOUSHA_MASTER -        |
self 1 2          > $tmp-nyuukyosha
# 1:入居者Ｎｏ

#----------------------------------------------------
# 入居者情報があれば口座の検索

if [ -s $tmp-nyuukyosha ] ;then

  # 入居者Ｎｏから口座情報を取得
  cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KOUZA |
  join1 key=1 $tmp-nyuukyosha - |
# 1:利用者(入居者)ID  2:利用者名 3:口座ID                4:金融機関コード    5:支店コード
# 6:請求内容コード    7:口座種類 8:口座番号              9:請求期間From      10:請求期間To
# 11:名義人           12:備考    13:他入居者との一括請求 14:一括請求入居者ID 15:一括請求書フラグ

# 誰かと一括にしていない人
awk '$13!="1"&&$(NF-2)!="9"{print $0}'        |
self 3/8 11 1 2 17                 > $tmp-takouza_data
#if [ -n "${Nyuukyosha}" -a "${Nyuukyosha}" != "_" ] ; then 
#  awk '$8=="'${Nyuukyosha}'"{print $0}'
#else
#  cat -
#fi  > $tmp-takouza_data
# 1:口座ID   2:金融機関コード 3:支店コード       4:請求内容コード 5:口座種類
# 6:口座番号 7:名義人         8:利用者(入居者)ID 9:利用者名

  # 該当データがあれば、金融機関名称、支店名を取得
  if [ -s "$tmp-takouza_data" ] ; then
   cat ${tbl_dir}/KINYUU_MASTER/KINYUUKIKAN_NAME |
   self 1 3 > $tmp-kinyuukikanmei

   cat ${tbl_dir}/KINYUU_MASTER/KINYUUKIKAN_SHITEN_NAME  |
   self 1 2 4 > $tmp-shitenmei

   cat $tmp-takouza_data   |
#   LANG=C sort -k2,3     |
   cjoin1 key=2/3 $tmp-shitenmei -  |
   cjoin1 key=2 $tmp-kinyuukikanmei - |
# 1:口座ID         2:金融機関コード 3:金融機関名 4:支店コード 5:支店名
# 6:請求内容コード 7:口座種類       8:口座番号   9:名義人     10:利用者(入居者)ID
# 11:利用者名

  # 口座
   awk '{if($7=="1"){print $0,"普通"}
         else if($7=="2"){print $0,"当座"}
         else{print $0,"@"}
       }'     |
   self 1/5 7 NF 8 NF-2 NF-3 NF-1  > $tmp-list_result
# 1:口座ID   2:金融機関コード 3:金融機関名 4:支店コード       5:支店名
# 6:口座種類 7:口座種類名     8:口座番号   9:利用者(入居者)ID 10:利用者名

  if [ "${NYUUKYOSHISETSUID}" = "${Shisetsu}" ] ; then
  # 他入居者口座(明細分割用)
    cat $tmp-list_result |
    self NF-1 NF-2       |
    awk '{print $0,"_"}' |
    LANG=C sort        |
    getlast 1 2   > $tmp-list_riyousha_result

    RIYOUSHALISTERRORMESSAGEDISP="none"
    RIYOUSHALISTERRORMESSAGE=""

  else
     : >  $tmp-list_riyousha_result

    RIYOUSHALISTERRORMESSAGEDISP=""
    RIYOUSHALISTERRORMESSAGE="＊一括請求では他施設の入居者を選択できません。"

  fi


  else
    : > $tmp-list_result
    : > $tmp-list_riyousha_result
  fi

else
  : > $tmp-list_result
  : > $tmp-list_riyousha_result
fi

: >$tmp-calsed_data
# 他入居者口座選択
if [ "${KouzaSentaku}" = "1" ]; then
  echo "###TAKOUZADISP###"          "@" >>$tmp-calsed_data
  echo "###IKKATSUDISP###"          "none" >>$tmp-calsed_data

# 他入居者一括請求
elif [ "${KouzaSentaku}" = "2" ]; then
  echo "###TAKOUZADISP###"          "none"  >>$tmp-calsed_data
  echo "###IKKATSUDISP###"          "@"     >>$tmp-calsed_data

# 0:新規
else
  echo "###TAKOUZADISP###"          "none"  >>$tmp-calsed_data
  echo "###IKKATSUDISP###"          "none"     >>$tmp-calsed_data
fi

[ -z "${RIYOUSHALISTERRORMESSAGE}" ] && RIYOUSHALISTERRORMESSAGE=""
if [ -z "${RIYOUSHALISTERRORMESSAGE}" ] ; then
  RIYOUSHALISTERRORMESSAGEDISP="none"
else
  RIYOUSHALISTERRORMESSAGEDISP=""
fi

  echo "###RIYOUSHALISTERRORMESSAGE###" "${RIYOUSHALISTERRORMESSAGE}"  >>$tmp-calsed_data
  echo "###RIYOUSHALISTERRORMESSAGEDISP###" "${RIYOUSHALISTERRORMESSAGEDISP}"  >>$tmp-calsed_data

#-
###########################################################################

awk '/\<list_table_start\>/,/\<list_table_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KOUZA.html |

calsed -f $tmp-calsed_data - |
mojihame -l"list_result"  -  $tmp-list_result |
mojihame -l"list_riyousha_result" - $tmp-list_riyousha_result |
#tee $tmp-formhame_mae |
  formhame -d"_"                - $tmp-name    > $tmp-html

#cp $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
