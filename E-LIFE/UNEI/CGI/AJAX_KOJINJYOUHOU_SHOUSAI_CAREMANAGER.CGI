#!/bin/bash
#  AJAX_KOJINJYOUHOU_SHOUSAI_JIGYOUSHO.CGI 
#           事業所       Ajax による使用を想定。
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

  JigyoushoName=$(nameread "JIGYOUSHONAME" $tmp-name)

# モード関係なく最初の絞込み
case "$MODE" in

# 居宅事業所
 KyotakuJigyousho)

  if [ "${JigyoushoName}" = "_" -o "$(echo "${JigyoushoName}" | awk '{print substr($1,1,1)}')" != "1" ] ; then

    cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
# 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
# 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名

    awk '$(NF-2)!="9"{print $1,$2}'         |
    awk '{if($1=="'${JigyoushoName}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousyo

   JigyoushoName="$(awk '{print $1}' $tmp-jigyousyo | head -1)"

  fi

  # 自事業所
  cat ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU ${tbl_dir}/JYUUGYOUIN_MASTER/EXTRA_USER_SHISETSU |
# 1:従業員ID   2:施設ID 3:建屋ID             4:フロア 5:ユニットID
# 6:事業所詳細 7:役職   8:介護支援専門員番号

  # 指定事業所所属の訪問介護でない、介護支援専門員番号のある人
#  awk '$2=="'${JigyoushoName}'"&&$6!="2"&&$8!="_"{print $0}' |
  # 指定事業所所属の訪問介護でない、介護支援専門番号はなくておｋ
  awk '$2=="'${JigyoushoName}'"&&$6!="2"{print $0}' |
  LANG=C sort -u |
  join1 key=1 <(awk '$(NF-2)!=9' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_KIHON) - |
  awk '$5>="'${today}'"&&$(NF-2)!="9"{print $1,$2}'     |
# 1:従業員ID    2:従業員名    3:従業員名カナ 4:勤務期間FROM        5:勤務期間TO
# 6:ID          7:PAS         8:施設ID       9:建屋ID              10:フロア
# 11:ユニットID 12:事業所詳細 13:役職        14:介護支援専門員番号
  awk 'BEGIN{print "@ @"}{print $0}'   |
  awk '{if($1=="'${CareManagerName}'"){print $0,"selected"}
        else{print $0,"@"}
        }' > $tmp-caremanager

  [ ! -s $tmp-caremanager ] &&  : > $tmp-caremanager

;;

  ServiceJigyousho)

  if [ "${JigyoushoName}" = "_" -o "$(echo "${JigyoushoName}" | awk '{print substr($1,1,1)}')" != "1" ] ; then

    cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
# 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
# 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名

    awk '$(NF-2)!="9"{print $1,$2}'         |
    awk '{if($1=="'${JigyoushoName}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousyo

   JigyoushoName="$(awk '{print $1}' $tmp-jigyousyo | head -1)"
  fi

# 従業員マスタから担当者情報をもってくる
  cat ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU ${tbl_dir}/JYUUGYOUIN_MASTER/EXTRA_USER_SHISETSU  |
# 1:従業員ID   2:施設ID 3:建屋ID             4:フロア 5:ユニットID
# 6:事業所詳細 7:役職   8:介護支援専門員番号
  # 指定事業所所属の居宅でない人
  awk '$2=="'${JigyoushoName}'"&&$6!="1"{print $0}' |
  LANG=C sort -u |
  join1 key=1 <(awk '$(NF-2)!=9' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_KIHON) - |
  awk '$5>="'${today}'"&&$(NF-2)!="9"{print $1,$2}'     |
# 1:従業員ID    2:従業員名    3:従業員名カナ 4:勤務期間FROM        5:勤務期間TO
# 6:ID          7:PAS         8:施設ID       9:建屋ID              10:フロア
# 11:ユニットID 12:事業所詳細 13:役職        14:介護支援専門員番号
  awk 'BEGIN{print "@ @"}{print $0}'   |
  awk '{if($1=="'${TantoushaName}'"){print $0,"selected"}
        else{print $0,"@"}
        }' > $tmp-tantousha

;;
esac

###########################################################################

if [ "${MODE}" = "KyotakuJigyousho" ] ; then
 awk '/\<CareManagerdiv_start\>/,/\<CareManagerdiv_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KYOTAKUSHIENJIGYOUSHO.html  |
 mojihame -l"caremanager_select" -  $tmp-caremanager
elif [ "${MODE}" = "ServiceJigyousho" ] ; then
 awk '/\<Tantoushadiv_start\>/,/\<Tantoushadiv_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_SERVICEJIGYOUSHO.html |
 mojihame -l"tantousha_select" -  $tmp-tantousha
fi |

#calsed -f $tmp-calsed_data - |

#tee $tmp-formhame_mae |
  formhame -d"_"  - $tmp-name    > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
