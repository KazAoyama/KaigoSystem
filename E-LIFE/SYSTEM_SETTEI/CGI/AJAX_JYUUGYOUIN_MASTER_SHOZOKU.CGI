#!/bin/bash
#
# AJAX_JYUUGYOUIN_MASTER_SHOUSAI.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
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
exec 2> /home/hands/E-LIFE/SYSTEM_SETTEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source  /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null

#=== 初期化 ===
tmp=/var/tmp/${$}
html_dir="${home_dir}/SYSTEM_SETTEI/HTML"
pompa_dir="${home_dir}/SYSTEM_SETTEI/POMPA"
kengen_dir="/home/hands/E-LIFE/SYSTEM_SETTEI/CGI"

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

  ShozokuShisetsu=$(nameread     "ShozokuShisetsu"    $tmp-name)
  ShozokuTateya=$(nameread       "ShozokuTateya"      $tmp-name)
  ShozokuFloor=$(nameread        "ShozokuFloor"       $tmp-name)
  ShozokuYakushoku1=$(nameread   "ShozokuYakushoku1"  $tmp-name)
  ShozokuYakushoku2=$(nameread   "ShozokuYakushoku2"  $tmp-name)
  SenmoninNumber=$(nameread      "SenmoninNumber"     $tmp-name)

  KenmuShisetsu=$(nameread       "KenmuShisetsu"        $tmp-name)
  KenmuTateya=$(nameread         "KenmuTateya"          $tmp-name)
  KenmuFloor=$(nameread          "KenmuFloor"           $tmp-name)
  KenmuYakushoku1=$(nameread     "KenmuYakushoku1"      $tmp-name)
  KenmuYakushoku2=$(nameread     "KenmuYakushoku2"      $tmp-name)
  KenmuSenmoninNumber=$(nameread "KenmuSenmoninNumber"  $tmp-name)


# モード関係なく最初の絞込み

 # 居宅・訪問介護事業所の準備
  cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
# 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
# 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名
  awk '$(NF-2)!="9"{print $1,$2}'   > $tmp-jigyousho_name


  # 施設一覧の取得
  cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON  |
  awk '$(NF-2)!="9"{print $1,$2}'                |
# 事業所情報をくっつける
  cat - $tmp-jigyousho_name |
  awk '{if($1=="'${ShozokuShisetsu}'"){print $0,"selected"}
        else{print $0,"@"}}'                   |
  LANG=C sort                                  |
  uniq       >$tmp-shisetsu_name

## 選択施設が事業所ではない場合
#if [ "$(echo "${Shisetsu}" | awk '{print substr($1,1,1)}')" != "1" ]; then
  # 建屋一覧
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR  |
awk '$1=="'${ShozokuShisetsu}'"&&$(NF-2)!="9"{print $2}'     |
LANG=C sort |
uniq |
join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -  |
self 1 3                                              |
awk 'BEGIN{print "@ @ @"}{print $0}'                  |
awk '{if($1=="'${ShozokuTateya}'"){print $1,$2,"selected"}
        else{print $1,$2,"@"}}' > $tmp-tateya_name
# 1:建屋ID 2:建屋名

###########################################################

#--
## フロア取得
#--
if [ ! -z "${ShozokuTateya}" -a "${ShozokuTateya}" != "_" ] ; then
  cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT_ROOM |
  awk '$1=="'${ShozokuShisetsu}'"&&$2=="'${ShozokuTateya}'"&&$(NF-2)!="9"{print $3,$3}'  |
  LANG=C sort  |
  uniq  |
  awk 'BEGIN{print "@ @ @"}{print $0}'      |
  awk '{if($1=="'${ShozokuFloor}'"){print $0,"selected"}
      else{print $0,"@"}
     }'  > $tmp-floor
else
  echo "@ @ @" > $tmp-floor
# 1:フロア 2:フロア
fi 

# フロアの指定がある場合
if [ ! -z "${ShozokuFloor}" -a "${ShozokuFloor}" != "_" ] ; then
  cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR_UNIT  |
  awk '$1=="'${ShozokuShisetsu}'"&&$2=="'${ShozokuTateya}'"&&$3=="'${ShozokuFloor}'"&&$(NF-2)!="9"{print $4}'  |
  LANG=C sort -k1,1 |
  uniq |
  join2 +"_" key=1 ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME -  |
  self 1 2 |
  sed 's/_/@/g' |
  awk 'BEGIN{print "@ @"}{print $0}'     |
  awk '{if($1=="'${ShozokuUnit}'"){print $0,"selected"}
        else{print $0,"@"}
       }'  |
  uniq  > $tmp-unit_name

else
  echo "@" "@" "@" > $tmp-unit_name
fi

# 選択したのが事業所の場合
#else

# 事業所番号の用意
cat ${tbl_dir}/CONFIG/JIGYOUSHO_BUNRUI_MASTER |
self 1 2 |
awk 'BEGIN{print "@","@"}{print $0}'     |
awk '{if($1=="'${ShozokuYakushoku1}'"){print $0,"selected"}
        else{print $0,"@"}
       }'   >  $tmp-jigyousho_shousai

# 事業所責任者

if [ ! -z "${ShozokuYakushoku1}" -a "${ShozokuYakushoku1}" = "1" ] ; then
  cat ${tbl_dir}/CONFIG/JIGYOUSHO_YAKUSHOKU_MASTER |
  self 1 2 3 |
  awk '$1=="1"{print $2,$3}' |
  awk 'BEGIN{print "@","@"}{print $0}'     |
  awk '{if($1=="'${ShozokuYakushoku2}'"){print $0,"selected"}
        else{print $0,"@"}
        }'
elif [ ! -z "${ShozokuYakushoku1}" -a "${ShozokuYakushoku1}" = "2" ] ; then
  cat ${tbl_dir}/CONFIG/JIGYOUSHO_YAKUSHOKU_MASTER |
  self 1 2 3 |
  awk '$1=="2"{print $2,$3}' |
  awk 'BEGIN{print "@","@"}{print $0}'   |
  awk '{if($1=="'${ShozokuYakushoku2}'"){print $0,"selected"}
        else{print $0,"@"}
        }'
else
  echo "@" "@" "@"
fi   >  $tmp-jigyousho_sekininsha
#fi

# 嵌め込みデータの作成
cat << FIN | sed 's/ _$/ @/g' > $tmp-calsed
###USERID### ${userid}
###SHISETSUID### ${shisetsu}
###PASSWORD### ${password}
###SenmoninNumber### ${SenmoninNumber}
FIN

#-------------------------------------------------------------
## 選択施設が事業所ではない場合、表示は施設
if [ "$(echo "${ShozokuShisetsu}" | awk '{print substr($1,1,1)}')" != "1" ]; then
  echo "###SHOZOKUTATEYADISP###" "@" >> $tmp-calsed
  echo "###SHOZOKUYAKUSHOKU1DISP###" "none"  >> $tmp-calsed
  echo "###SHOZOKUUNITDISP###" "@"  >> $tmp-calsed
  echo "###SENMONINNUMBERDISP###" "@" >> $tmp-calsed
  echo "###HeaderShozokuTateyaTblDISP###" "@" >> $tmp-calsed
  echo "###HeaderShozokuYakushokuTblDISP###" "none"  >> $tmp-calsed
  echo "###HeaderShozokuUnitTblDISP###" "@"  >> $tmp-calsed
  echo "###HeaderSenmoninNumberTblDISP##" "none" >> $tmp-calsed
else
  echo "###SHOZOKUTATEYADISP###" "none" >> $tmp-calsed
  echo "###SHOZOKUYAKUSHOKU1DISP###" "@"  >> $tmp-calsed
  echo "###SHOZOKUUNITDISP###" "none"  >> $tmp-calsed
  echo "###SENMONINNUMBERDISP###" "@" >> $tmp-calsed
  echo "###HeaderShozokuTateyaTblDISP###" "none" >> $tmp-calsed
  echo "###HeaderShozokuYakushokuTblDISP###" "@"  >> $tmp-calsed
  echo "###HeaderShozokuUnitTblDISP###" "none"  >> $tmp-calsed
  echo "###HeaderSenmoninNumberTblDISP###" "@"  >> $tmp-calsed
fi


###########################################################################
if [ "${MODE}" = "ShozokuShisetsu" ] ; then
  awk '/\<shozoku_tateya_td_start\>/,/\<shozoku_tateya_td_end\>/' ${html_dir}/JYUUGYOUIN_MASTER_SHOUSAI2.html | 
  mojihame -l"shozoku_tateya_select"  - $tmp-tateya_name    |
  mojihame -l"shozoku_floor_select"     - $tmp-floor        |
  mojihame -l"shozoku_jigyousho_select"  - $tmp-jigyousho_shousai |
  mojihame -l"shozoku_sekininsha_select"     - $tmp-jigyousho_sekininsha
elif [ "${MODE}" = "ShozokuTateya" ] ; then
  awk '/\<shozoku_tateya_td_start\>/,/\<shozoku_tateya_td_end\>/' ${html_dir}/JYUUGYOUIN_MASTER_SHOUSAI2.html  |
  mojihame -l"shozoku_tateya_select"  - $tmp-tateya_name    |
  mojihame -l"shozoku_floor_select"     - $tmp-floor        |
  mojihame -l"shozoku_jigyousho_select"  - $tmp-jigyousho_shousai |
  mojihame -l"shozoku_sekininsha_select"     - $tmp-jigyousho_sekininsha        
elif [ "${MODE}" = "ShozokuFloor" ] ; then
  awk '/\<shozoku_unit_td_start\>/,/\<shozoku_unit_td_end\>/' ${html_dir}/JYUUGYOUIN_MASTER_SHOUSAI2.html |
  mojihame -l"shozoku_unit_select"  - $tmp-unit_name            
fi |
tee $tmp-ajax_test |
 #
  sed 's/###SPACE###/ /g'                               |
  sed 's/\\n/\n/g'                                      |
  sed 's/###KAIGYO###/\n/g'                             |
  calsed -f $tmp-calsed - |
cat - > $tmp-html

#cp $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
