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

  JIGYOUSHO=$(nameread "JIGYOUSHO" $tmp-name)
  JigyoushoName=$(nameread "JIGYOUSHONAME" $tmp-name)
  ServiceShurui=$(nameread "ServiceShurui" $tmp-name)

# モード関係なく最初の絞込み
case "$MODE" in

# 居宅事業所
 KyotakuJigyousho)

  # 自事業所
  if [ "${JIGYOUSHO}" = "Jijigyousho" ] ; then
    cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
# 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
# 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名

    awk '$(NF-2)!="9"{print $1,$2}'         |
    awk '{if($1=="'${JigyoushoName}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousyo
  
  # 他事業所
  else
    cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_HIMODUKE_MASTER |
    awk '$(NF-2)!="9"{print $2}'         |
    LANG=C sort |
    uniq |
    join1 +ng key=1 - ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_MASTER  >$tmp-jijigyousho 2>$tmp-tajigyousho
# 1:事業所ＩＤ         2:サービス供給事業者番号 3:サービス供給事業者名 4:サービスコード種類 5:事業所区分
# 6:指定基準事業所区分 7:地域区分               8:生活保護指定         9:割引率  ...
#...
# 43:事業所評価加算（申出）の有無 44:生活機能向上グループ活動加算 45:24時間通報体制加算

  # 居宅事業所(43:居宅介護支援,46:居宅予防支援)に渋る
    cat $tmp-tajigyousho |
    awk '$(NF-2)!="9"{print $0}'   |
    awk '$4=="43"||$4=="46"{print $1,$3}' |
  # 1:事業所番号 2:事業所名
    awk '{if($1=="'${JigyoushoName}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousyo
  fi

;;

  ServiceJigyousho)

   # 自事業所
   if [ "${JIGYOUSHO}" = "Jijigyousho" ] ; then
     cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
# 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
# 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名
    awk '$(NF-2)!="9"{print $1,$2}'         |
    awk '{if($1=="'${JigyoushoName}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousyo
   # 他事業所
   else

    # サービス種類コード
    cat ${tbl_dir}/CONFIG/KAIGOHOKEN_SERVICE_TYPE |
    delf 2 |
    awk '{if($1=="'${ServiceShurui}'"){print $0,"selected"}
        else{print $0,"@"}
        }'    > $tmp-service_type

   [ -z "${ServiceShurui}" -o "${ServiceShurui}" = "_" ] && ServiceShurui=$(cat $tmp-service_type | head -1 | self 1)


    cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_HIMODUKE_MASTER |
    awk '$(NF-2)!="9"{print $2}'         |
    LANG=C sort |
    uniq |
    join1 +ng key=1 - ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_MASTER  >$tmp-jijigyousho 2>$tmp-tajigyousho
# 1:事業所ＩＤ         2:サービス供給事業者番号 3:サービス供給事業者名 4:サービスコード種類 5:事業所区分
# 6:指定基準事業所区分 7:地域区分               8:生活保護指定         9:割引率  ...
#...
# 43:事業所評価加算（申出）の有無 44:生活機能向上グループ活動加算 45:24時間通報体制加算

  # 居宅事業所(11:訪問介護,61:訪問介護(予防))に渋る
    cat $tmp-tajigyousho |
    awk '$4=="'${ServiceShurui}'"&&$(NF-2)!="9"{print $0}'   |
#    awk '$4=="11"||$4=="61"{print $1,$3}' |
    self 1 3 |
  # 1:事業所番号 2:事業所名
    awk '{if($1=="'${JigyoushoName}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousyo
   fi
;;

  ServiceShurui)

   # 自事業所
   if [ "${JIGYOUSHO}" = "Jijigyousho" ] ; then
     cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
# 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
# 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名
    awk '$(NF-2)!="9"{print $1,$2}'         |
    awk '{if($1=="'${JigyoushoName}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousyo

    # サービス種類コード
    cat ${tbl_dir}/CONFIG/KAIGOHOKEN_SERVICE_TYPE |
    delf 2 |
    awk '{if($1=="'${ServiceShurui}'"){print $0,"selected"}
        else{print $0,"@"}
        }'    > $tmp-service_type

   # 他事業所
   else

    # サービス種類コード
    cat ${tbl_dir}/CONFIG/KAIGOHOKEN_SERVICE_TYPE |
    delf 2 |
    awk '{if($1=="'${ServiceShurui}'"){print $0,"selected"}
        else{print $0,"@"}
        }'    > $tmp-service_type
   [ -z "${ServiceShurui}" -o "${ServiceShurui}" = "_" ] && ServiceShurui=$(cat $tmp-service_type | head -1 | self 1)


    cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_HIMODUKE_MASTER |
    awk '$(NF-2)!="9"{print $2}'         |
    LANG=C sort |
    uniq |
    join1 +ng key=1 - ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_MASTER  >$tmp-jijigyousho 2>$tmp-tajigyousho
# 1:事業所ＩＤ         2:サービス供給事業者番号 3:サービス供給事業者名 4:サービスコード種類 5:事業所区分
# 6:指定基準事業所区分 7:地域区分               8:生活保護指定         9:割引率  ...
#...
# 43:事業所評価加算（申出）の有無 44:生活機能向上グループ活動加算 45:24時間通報体制加算

  # 居宅事業所(11:訪問介護,61:訪問介護(予防))に渋る
    cat $tmp-tajigyousho |
    awk '$4=="'${ServiceShurui}'"&&$(NF-2)!="9"{print $0}'   |
#    awk '$4=="11"||$4=="61"{print $1,$3}' |
    self 1 3 |
  # 1:事業所番号 2:事業所名
    awk '{if($1=="'${JigyoushoName}'"){print $0,"selected"}
        else{print $0,"@"}
        }'  > $tmp-jigyousyo
   fi
;;


esac

###########################################################################

if [ "${MODE}" = "KyotakuJigyousho" ] ; then
 awk '/\<Jigyoushodiv_start\>/,/\<Jigyoushodiv_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KYOTAKUSHIENJIGYOUSHO.html  
elif [ "${MODE}" = "ServiceJigyousho" -o "${MODE}" = "ServiceShurui" ] ; then
 awk '/\<Jigyoushodiv_start\>/,/\<Jigyoushodiv_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_SERVICEJIGYOUSHO.html
fi |

#calsed -f $tmp-calsed_data - |
mojihame -l"jigyousho_select" -  $tmp-jigyousyo |

#tee $tmp-formhame_mae |
  formhame -d"_"  - $tmp-name    > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
