#!/bin/bash
#
# AJAX_KIHONJYOUHOU_ICHIRAN.CGI: 事業所、施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
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
userid=$(nameread "userid" $tmp-name)

  Shisetsu=$(nameread "Shisetsu" $tmp-name)
  Tateya=$(nameread "Tateya" $tmp-name)
  Floor=$(nameread "Floor" $tmp-name)
  Unit=$(nameread "Unit" $tmp-name)
  Kyoshitsu=$(nameread "Kyoshitsu" $tmp-name)
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)
  JIGYOUSHO=$(nameread "JIGYOUSHO" $tmp-name)
  shisetsu=$(nameread "shisetsu" $tmp-name)

  [ -z "${Shisetsu}" ] && Shisetsu="_"
  [ -z "${Tateya}" ] && Tateya="_"
  [ -z "${Floor}" ] && Floor="_"
  [ -z "${Unit}" ] && Unit="_"
  [ -z "${Kyoshitsu}" ] && Kyoshitsu="_"
  [ -z "${Nyuukyosha}" ] && Nyuukyosha="_"
  [ -z "${JIGYOUSHO}" ] && JIGYOUSHO="_"
  [ -z "${shisetsu}" ] && shisetsu="_"


# 施設だった場合
if [ "${JIGYOUSHO}" = "_" ] ; then
  # 施設名はログインユーザーの権限のある施設を取得
  cat ${kengen_dir}/USER_KENGEN/${userid}.USER_KENGEN    |
# 1:userid 2:SHISETSU_ID 3:KENGEN_GROUP 4:appID 5:MENU_NAME 6:DROPDOWN_STATUS 7:CGI_NAME 8:RINK_STATUS 9:CGI_STATUS 10:登録日時
  awk '$7=="'${cgi_name}'"{print $0}' |
  LANG=C sort -u -k2,2n               |
  self 1 2                            |
  join2 +"@" key=2 ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON - |
  awk '{if($1=="'${shisetsu}'"){print $2,3,"selected"}
      else{print $2,$3,"@"}
     }'                             > $tmp-shisetsu_name

  # 建屋一覧
  # 施設が空でなかったら

  cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR    |
# 1:施設ID 2:建屋ID 3:フロア
  awk '$1=="'${Shisetsu}'"{print $2}'                     |
  LANG=C sort |
  uniq |
  join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -    |
  self 1 3                                                > $tmp-tateya_name
# 1:建屋ID 2:建屋名
#-
# 建屋が選ばれていない、かつ建屋の選択肢が一つの場合はその建屋をセット
  [ -z "${Tateya}" -a "$(gyo $tmp-tateya_name)" -ge "1" ] && Tateya="$(awk '{print $1}' $tmp-tateya_name | head -1)"

  if [ -n "${Tateya}" -a "${Tateya}" != "_" ] ; then
    cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |
    awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"{print $3,$3}'  |
    sort  |
    uniq  >$tmp-floor_kari
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

  #--
  ## ユニット取得
  #--
  # フロア選択肢が全て以外で一個になる場合そのフロアを選択していると判断
  [ -z "${Floor}" -a "$(gyo $tmp-floor)" -ge "1" -a "$(self 1 $tmp-floor | head -1)" != "@" ] && Floor="$(awk '{print $1}' $tmp-floor)"

    # 建屋がケアの場合
    if [ "${Tateya}" = "02" ] ; then
    # フロアの指定がある場合
      if [ -n "${Floor}" -a "${Floor}" != "_" ] ; then
      cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS  |
      awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Floor}'"&&$(NF-2)!="9"{print $4}'  |
      LANG=C sort  |
      uniq |
      join1 key=1 ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME -  |
      self 1 2 > $tmp-unit_kari

        # 2つ以上ならば全てという選択肢
        if [ "$(gyo $tmp-unit_kari)" -gt "1"  ]; then
        cat $tmp-unit_kari |
        awk 'BEGIN{print "@ 全て"}{print $0}'
        else
        cat $tmp-unit_kari
        fi   > $tmp-unit_name
      else
       echo "@" "全て" > $tmp-unit_name
      fi
    # 建屋が2つ以上ある場合
    elif [ "$(gyo $tmp-tateya_name)" -gt "1" ] ; then
     echo "@" "全て" > $tmp-unit_name
    # 建屋がシニアの場合はユニットなし
    else
      echo "@" "@" > $tmp-unit_name
    fi


# 事業所だったら
else

#-------------------------------------------------------------------------------------

  cat ${pompa_dir}/RIYOUSHA/JIGYOUSHO_RIYOUSHA_STATUS |
  awk '$1=="'${JIGYOUSHO}'"&&$4>"'${today}'"&&$(NF-2)!="9"{print $2}' |
  LANG=C sort > $tmp-riyousha
# 1:入居者ID

  cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室
# 6:入居者ID 7:入居日 8:退去日
  self 6 1/5 7/NF   |
  LANG=C sort -k1,1 |
  join2 key=1 - $tmp-riyousha |
  self 2/6 1 7/NF > $tmp-riyousha_status
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室
# 6:入居者ID

#  施設
    cat $tmp-riyousha_status |
    self 1 |
    LANG=C sort |
    uniq |
    join1 key=1 ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON - |
    awk 'BEGIN{print "@","全て"}{print $0}' |
    if [ "${Shisetsu}" != "_" ] ; then
      awk '{if($1=="'${Shisetsu}'"){print $0,"selected"}
        else{print $0,"@"}
       }'      > $tmp-shisetsu_name
    else
      awk '{print $0,"@"}' > $tmp-shisetsu_name
    fi
# 建屋
  # 施設が選ばれていれば建屋を特定
  if [ "${Shisetsu}" != "_" ] ; then
    cat $tmp-riyousha_status |
    awk '$1=="'${Shisetsu}'"{print $2}'  |
    LANG=C sort |
    uniq  |
    join2 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME - |
    awk 'BEGIN{print "@","全て"}{print $1,$3}' |
    awk '{if($1=="'${Tateya}'"){print $0,"selected"}
      else{print $0,"@"}
    }'   > $tmp-tateya_name
  else
    echo "@" "全て" "@"  > $tmp-tateya_name
  fi

  if [ "${Tateya}" != "_" ] ; then
    cat $tmp-riyousha_status |
    awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"{print $3}'  |
    LANG=C sort |
    uniq |
    awk 'BEGIN{print "@","全て"}{print $1,$1}' |
    awk '{if($1=="'${Tateya}'"){print $0,"selected"}
      else{print $0,"@"}
    }'  > $tmp-floor
  else
    echo "@" "全て" "@" > $tmp-floor 
  fi 

  if [ "${Tateya}" = "02" -a "${Floor}" != "_" ] ; then
    cat $tmp-riyousha_status |
    awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Floor}'"{print $4}'  |
    LANG=C sort |
    uniq |
    awk 'BEGIN{print "@","全て"}{print $1,$2}' |
    awk '{if($1=="'${Unit}'"){print $0,"selected"}
      else{print $0,"@"}
    }'  > $tmp-unit_name
  elif [ "${Tateya}" = "02" -a "${Floor}" = "_" ] ; then
   echo "@" "全て" "@" > $tmp-unit_name
  elif [ "${Tateya}" = "_" ] ; then
   echo "@" "全て" "@" > $tmp-unit_name
  else
   : > $tmp-unit_name
  fi 

 
fi

#--
## 居室取得・入居者氏名取得
#--
# 施設の選択があれば施設内の、そうでなければ全入居者の居室を取得
if [ ${JIGYOUSHO} = "_" ] ; then
  cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS
else
  cat $tmp-riyousha_status
fi |

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
if [ -n "${Kyoshitsu}" -a "${Kyoshitsu}" != "_" ] ; then
  awk '$5=="'${Kyoshitsu}'"{print $0}'
else
  cat -
fi |
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室
# 6:入居者ID 7:入居日 8:退去日
#-

# 退去者表示のフラグがあれば
#if [ "${TaikyoshaHyouji}" = "1" ] ; then
  self 5 6 |
#else
# 入居期間中のものにする
#  awk '$8>"'${today}'"{print $5,$6}'
# 1:居室Ｎｏ 2:入居者Ｎｏ
#-
#fi |
LANG=C sort -k2,2 |
join1 key=2 ${pompa_dir}/RIYOUSHA/RIYOUSHA_MASTER -        |
LANG=C sort       |
uniq              > $tmp-kyoshitsu_kari
# 1:居室Ｎｏ 2:入居者Ｎｏ 3:入居者名

# 2人以上の場合のみ全てという選択をつける
if [ "$(gyo $tmp-kyoshitsu_kari)" -gt "1"  ]; then
  cat $tmp-kyoshitsu_kari  |
  awk 'BEGIN{print "@ 全て"}{print $1,$1}' |
  uniq                     > $tmp-kyoshitsu
  cat $tmp-kyoshitsu_kari  |
  awk 'BEGIN{print "@ 全て"}{print $2,$3}' > $tmp-nyuukyosha
# 1:居室Ｎｏ 2:居室Ｎｏ
else
  cat $tmp-kyoshitsu_kari |
  awk '{print $1,$0}'     |
  uniq                    > $tmp-kyoshitsu
  cat $tmp-kyoshitsu_kari |
  awk '{print $2,$3}' > $tmp-nyuukyosha
fi

 if [ -s $tmp-nyuukyosha -a "$(gyo $tmp-nyuukyosha)" -ge "300" ] ; then
   cat $tmp-nyuukyosha |
   head -300
 else
   cat $tmp-nyuukyosha
 fi > $tmp-nyuukyosha_name

# 1:入居者Ｎｏ 2:入居者名
# 施設選択されていない場合建屋以下は全てという選択肢のみ
###########################################################################
if [ -z "${GAMEN}" -o "${GAMEN}" = "_" ] ; then
  awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/KIHONJYOUHOU_ICHIRAN2.html 
elif [ "${GAMEN}" = "POPKOUZA" ] ; then
  awk '/\<shisetsu_tb_start\>/,/\<shisetsu_tb_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KOUZA.html
elif  [ "${GAMEN}" = "NYUUINGAIHAKU" ] ; then
  awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/NYUUINGAIHAKU_ICHIRAN2.html
fi |

tee $tmp-ajax_test |
 #
  mojihame -l"shisetsu_select"  - $tmp-shisetsu_name    |
  mojihame -l"tateya_select"     - $tmp-tateya_name     |
  mojihame -l"floor_select"    - $tmp-floor             |
  mojihame -l"unit_select"  - $tmp-unit_name            |
  mojihame -l"kyoshitsu_select"     - $tmp-kyoshitsu    |
  mojihame -l"nyuukyosha_select"    - $tmp-nyuukyosha_name   |
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
