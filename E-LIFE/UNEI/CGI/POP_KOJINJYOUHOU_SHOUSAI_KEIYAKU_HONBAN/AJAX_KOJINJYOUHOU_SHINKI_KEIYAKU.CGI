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
GAMEN=$(nameread "GAMEN" $tmp-name)

  Shisetsu=$(nameread "Shisetsu" $tmp-name)
  KeiyakuShurui=$(nameread "KeiyakuShurui" $tmp-name)

cat ${tbl_dir}/KEIYAKU_MASTER/SHISETSU_KEIYAKU_MASTER |
# 1:施設/事業所名 2:契約ID 3:有効フラグ

# 施設番号が一致し、有効フラグが1:有効なもの
awk '$1=="'${Shisetsu}'"&&$(NF-2)!="9"&&(NF-2)!="2"{print $2}'  |
LANG=C sort |
join1 key=1 ${tbl_dir}/KEIYAKU_MASTER/KEIYAKU_NAME - |
awk '{if($1=="'${KeiyakuShurui}'"){print $1,$2,"selected"}
      else{print $1,$2,"@"}}'        > $tmp-keiyaku_shurui


[ ! -s $tmp-keiyaku_shurui ] && echo "@ @ @"  > $tmp-keiyaku_shurui


cat << FIN > $tmp-calsed_data
###Keiyakubi### @
###KeiyakukikanFrom### @
###KeiyakuHikiwatashibi### @
###KeiyakuNyuukyobi### @
###KeiyakuSeikyuuKikanFrom### @
FIN
# 事業所選択の表示
JIGYOUSHOHANTEI=$(echo ${Shisetsu} | awk '{print substr($1,1,1)}')

if [ "${JIGYOUSHOHANTEI}" = "1" ] ; then
  echo "###KEIYAKUDISP### none" >> $tmp-calsed_data
else
  echo "###KEIYAKUDISP### @" >> $tmp-calsed_data

fi

###########################################################################
if [ -z "${GAMEN}" -o "${GAMEN}" = "_" ] ; then
  awk '/\<keiyakushurui_tbl_start\>/,/\<keiyakushurui_tbl_end\>/' ${html_dir}/KOJINJYOUHOU_SHOUSAI_SHINKI.html

elif [ "${GAMEN}" = "KEIYAKU" ] ; then

  awk '/\<keiyakushurui_td_start\>/,/\<keiyakushurui_td_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KEIYAKU.html

fi |

tee $tmp-ajax_test |
 #
  mojihame -l"KEIYAKUSHURUI"  - $tmp-keiyaku_shurui   |
#  > $tmp-html
  calsed -f $tmp-calsed_data  >  $tmp-html
#formhame -d"_"                - $tmp-name    > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
