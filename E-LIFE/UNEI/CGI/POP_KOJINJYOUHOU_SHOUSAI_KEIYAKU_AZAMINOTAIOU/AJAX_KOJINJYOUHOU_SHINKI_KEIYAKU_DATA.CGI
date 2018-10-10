#!/bin/bash
#
# AJAX_KOJINJYOUHOU_SHINKI_KEIYAKU.CGI: 
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
  KeiyakuShurui=$(nameread "KeiyakuShurui" $tmp-name)

# 契約金・利用料・特販
cat ${tbl_dir}/RIYOURYOU_MASTER/KEIYAKUKIN_MASTER        |
awk '$1=="'${Shisetsu}'"&&$(NF-2)!="9"&&$(NF-2)!="2"{print $0}' |
LANG=C sort -k4,4n  |
self 2 3            |
awk 'BEGIN{print "@ @"}{print $0}' > $tmp-keiyakukin
cat ${tbl_dir}/RIYOURYOU_MASTER/RIYOURYOU_MASTER         |
awk '$1=="'${Shisetsu}'"{print $2,$3}' |
awk 'BEGIN{print "@ @"}{print $1,$2}' > $tmp-riyouryou
cat ${tbl_dir}/RIYOURYOU_MASTER/TOKUHAN_SHUBETSU           |
awk '$1=="'${Shisetsu}'"&&$(NF-2)!="9"&&$(NF-2)!="2"{print $2,$3}' |
awk 'BEGIN{print "@ @"}{print $0}' > $tmp-tokuhan
cat ${tbl_dir}/RIYOURYOU_MASTER/RIYOURYOU_MASTER          |
awk '$1=="'${Shisetsu}'"{print $2,$5}' |
awk '$2!="001"{print $0}'       > $tmp-riyouryou_master

###########################################################################

awk '/\<KeiyakuData_start\>/,/\<KeiyakuData_end\>/' ${html_dir}/KOJINJYOUHOU_SHOUSAI_SHINKI.html |
tee $tmp-ajax_test |
 #
  mojihame -l"KEIYAKUKINMASTER"  - $tmp-keiyakukin   |
  mojihame -l"RIYOURYOUMASTER"  - $tmp-riyouryou   |
  mojihame -l"TOKUHANMASTER"  - $tmp-tokuhan   |
  mojihame -l"RIYOURYOUKINGAKU"  - $tmp-riyouryou_master   > $tmp-html
#  > $tmp-html
#  calsed -f $tmp-calsed_data  > $tmp-html
#formhame -d"_"                - $tmp-name    > $tmp-html

#cp  $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
