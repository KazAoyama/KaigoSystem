#!/bin/bash
#
# AJAX_KIHONJYOUHOU_ICHIRAN_0.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
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
MODE=$(nameread "MODE" $tmp-name)
GAMEN=$(nameread "GAMEN" $tmp-name)
userid=$(nameread "userid" $tmp-name)

  Shisetsu=$(nameread "Shisetsu" $tmp-name)
  Tateya=$(nameread "Tateya" $tmp-name)
  Floor=$(nameread "Floor" $tmp-name)
  Unit=$(nameread "Unit" $tmp-name)
  Kyoshitsu=$(nameread "Kyoshitsu" $tmp-name)
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)
  JIGYOUSHO=$(nameread "JIGYOUSHO" $tmp-name)

  [ -z "${GAMEN}" ] && GAMEN="_"
  [ -z "${Shisetsu}" ] && Shisetsu="_"
  [ -z "${Tateya}" ] && Tateya="_"
  [ -z "${Floor}" ] && Floor="_"
  [ -z "${Unit}" ] && Unit="_"
  [ -z "${Kyoshitsu}" ] && Kyoshitsu="_"
  [ -z "${Nyuukyosha}" ] && Nyuukyosha="_"
  [ -z "${JIGYOUSHO}" ] && JIGYOUSHO="_"


# 施設だった場合
if [ "${JIGYOUSHO}" != "_" ] ; then
    # 自事業所
    cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
# 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
# 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名
    awk '$(NF-2)!="9"{print $1,$2}'         |
    awk 'BEGIN{print "9999","選択しない"}'  |
    awk '{if($1=="'${Jigyousho}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousho_name
  # 1:グループ事業所ＩＤ 2:グループ事業所名 3:Selected
fi

  # 施設名はログインユーザーの権限のある施設を取得
  cat ${kengen_dir}/USER_KENGEN/${userid}.USER_KENGEN    |
# 1:userid 2:SHISETSU_ID 3:KENGEN_GROUP 4:appID 5:MENU_NAME 6:DROPDOWN_STATUS 7:CGI_NAME 8:RINK_STATUS 9:CGI_STATUS 10:登録日時
  # APPIDが3のもの
  awk '$4=="3"{print $0}' |
  LANG=C sort -u -k2,2n               |
  self 2                            >  $tmp-kengenari-shisetsu
  
   # 施設名はログインユーザーの権限のある施設を取得
   if [ "$(head -1 $tmp-kengenari-shisetsu)" = "0000" ] ; then
    cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
    self 1 2 
   else
    cat $tmp-kengenari-shisetsu |
    join1 key=1 ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON -    |
    self 1 2 
   fi |

   if [ "${JIGYOUSHO}" = "9999" ] ; then
     awk 'BEGIN{print "@ 全て"}{print $0}' |
     awk '{if($1=="'${Shisetsu}'"){print $1,$2,"selected"}
          else{print $1,$2,"@"}
         }'  > $tmp-shisetsu_name
   else
     awk '{if($1=="'${Shisetsu}'"){print $1,$2,"selected"}
          else{print $1,$2,"@"}
          }'                      > $tmp-shisetsu_name
   fi

 if [ "${GAMEN}" != "_" ] ; then
   echo "${Shisetsu}" |
   join1 key=1 - ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
   self 1 2           > $tmp-shisetsu_name
 fi

#---
  # 建屋一覧
#---
  # 施設が空でなかったら
  if [ "${Shisetsu}" != "_" ] ; then

  shozokushisetsu=$(awk '$1=="'${userid}'"{print $2}' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU )
  shozokutateya=$(awk '$1=="'${userid}'"{print $3}' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU )
  [ "${Tateya}" = "_" -a "${shozokushisetsu}" -eq "${Shisetsu}" -a "${shozokutateya}" != "_" ] && Tateya="${shozokutateya}"

    cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR    |
# 1:施設ID 2:建屋ID 3:フロア
    awk '$1=="'${Shisetsu}'"{print $2}'                     |
    LANG=C sort |
    uniq |
    join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -    |
    self 1 3                                                |
    awk '{if($1=="'${Tateya}'"){print $1,$2,"selected"}
          else{print $1,$2,"@"}
          }' > $tmp-tateya_name
# 1:建屋ID 2:建屋名
#- 
  else
    echo "@ 全て @" >  $tmp-tateya_name
  fi

# 建屋が選ばれていない、かつ建屋の選択肢が一つの場合はその建屋をセット
  [ "${Tateya}" = "_" -a "$(awk '$1!="@"' $tmp-tateya_name | gyo)" -gt "1" ] && Tateya="$(awk '{print $1}' $tmp-tateya_name | head -1)"

  if [ "${Tateya}" != "_" ] ; then
    cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |
    awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"{print $3,$3}'  |
    sort  |
    uniq  >$tmp-floor_kari
# 1:フロア 2:フロア

    # フロアが2つ以上の場合のみ全てという選択をつける
    if [ "$(gyo $tmp-floor_kari)" -gt "1"  ]; then
      cat $tmp-floor_kari |
      awk 'BEGIN{print "@ 全て"}{print $0}' |
      awk '{if($1=="'${Floor}'"){print $1,$2,"selected"}
          else{print $1,$2,"@"}
          }' > $tmp-floor
    else
      cat $tmp-floor_kari
     fi  > $tmp-floor
  # 建屋が複数から未選択の場合

  else
    echo "@" "全て" "@"
  fi     > $tmp-floor
# 1:フロア番号 2:フロア番号

  #--
  ## ユニット取得
  #--
  # フロア選択肢が全て以外で一個になる場合そのフロアを選択していると判断
  [ "${Floor}" = "_" -a "$(awk '$1!="@"' $tmp-floor | gyo)" = "1" ] && Floor="$(awk '{print $1}' $tmp-floor | head -1)"

    # 建屋がケアの場合
    if [ "${Tateya}" = "02" ] ; then
    # フロアの指定がある場合
      if [ "${Floor}" != "_" ] ; then
      cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS  |
      awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Floor}'"&&$(NF-2)!="9"{print $4}'  |
      LANG=C sort  |
      uniq |
      join1 key=1 ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME -  |
      self 1 2 > $tmp-unit_kari

        # 2つ以上ならば全てという選択肢
        if [ "$(gyo $tmp-unit_kari)" -gt "1"  ]; then
        cat $tmp-unit_kari |
        awk 'BEGIN{print "@ 全て"}{print $0}' |
        awk '{if($1=="'${Unit}'"){print $1,$2,"selected"}
          else{print $1,$2,"@"}
          }' > $tmp-unit_name
        else
        cat $tmp-unit_kari
        fi   > $tmp-unit_name
      # フロアが選ばれていない場合
      else
       echo "@" "全て" > $tmp-unit_name
      fi
    # 建屋が選ばれておらず2つ以上ある場合
    elif [ "${Tateya}" =　"_" -a "$(gyo $tmp-tateya_name)" -gt "1" ] ; then
     echo "@" "全て" > $tmp-unit_name
    # 建屋がシニアの場合はユニットなし
    else
      echo "@" "@" > $tmp-unit_name
    fi

#--
## 居室取得・入居者氏名取得
#--
# 事業所
if [ "${JIGYOUSHO}" != "_" -a "${JIGYOUSHO}" != "9999" ] ; then
  cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |
# 1:事業所ID 2:入居者ID 3:契約開始日 4:契約終了日
  awk '$3<"'${today}'"&&$4>"'${today}'"{print $2}'   |
  LANG=C sort |
  cjoin1 key=6 - ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室
# 6:入居者ID 7:入居日 8:退去日
else
  cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS 
# 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室
# 6:入居者ID 7:入居日 8:退去日
fi |

# 施設
if [ "${Shisetsu}" != "_" -a "${Shisetsu}" != "@" ] ; then
  awk '$1=="'${Shisetsu}'"{print $0}'
# 1:施設ＩＤ 2:建屋ＩＤ 3:フロア 4:ユニットＩＤ 5:居室Ｎｏ
else
  cat -
fi |

# 建屋の選択があった場合
if [ "${Tateya}" != "_" -a "${Tateya}" != "@" ] ; then
  awk '$2=="'${Tateya}'"{print $0}'
else
  cat -
fi |
# 1:施設ＩＤ 2:建屋ＩＤ 3:フロア 4:ユニットＩＤ 5:居室Ｎｏ
#-
# フロアの選択があった場合
if [ "${Floor}" != "_" -a "${Floor}" != "@" ] ; then
  awk '$3=="'${Floor}'"{print $0}'
else
  cat -
fi |
#-

# ユニットの選択があった場合
if [ "${Unit}" != "_" -a "${Unit}" != "@" ] ; then
  awk '$4=="'${Unit}'"{print $0}'
else
  cat -
fi |

## 居室の選択があった場合
#if [ "${Kyoshitsu}" != "_" -a "${Kyoshitsu}" != "@" ] ; then
#  awk '$5=="'${Kyoshitsu}'"{print $0}'
#else
#  cat -
#fi |
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
  LANG=C sort              |
  awk 'BEGIN{print "@ 全て"}{print $1,$1}' |
  uniq                     |
  awk '{if($1=="'${Kyoshitsu}'"){print $1,$2,"selected"}
       else{print $1,$2,"@"}
          }'               > $tmp-kyoshitsu
  cat $tmp-kyoshitsu_kari  |
  # 居室の選択があった場合
  if [ "${Kyoshitsu}" != "_" -a "${Kyoshitsu}" != "@" ] ; then
    awk '$1=="'${Kyoshitsu}'"{print $0}'
  else
    cat -
  fi > $tmp-nyuukyosha_kari

  if [ "$(gyo $tmp-nyuukyosha_kari)" -gt "1"  ]; then
    cat $tmp-nyuukyosha_kari  |
    awk 'BEGIN{print "@ 全て"}{print $2,$3}' |
    uniq                     |
    awk '{if($1=="'${Nyuukyosha}'"){print $1,$2,"selected"}
       else{print $1,$2,"@"}
          }'                > $tmp-nyuukyosha
  # 1:居室Ｎｏ 2:居室Ｎｏ
  else
    cat $tmp-nyuukyosha_kari  |
    self 2 3                 > $tmp-nyuukyosha
  fi
else
  cat $tmp-kyoshitsu_kari |
  awk '{print $1,$1}'     |
  uniq                    > $tmp-kyoshitsu
  cat $tmp-kyoshitsu_kari |
  awk '{print $2,$3}' > $tmp-nyuukyosha
fi
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
