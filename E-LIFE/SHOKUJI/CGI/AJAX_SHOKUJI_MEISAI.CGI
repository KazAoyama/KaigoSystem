#!/bin/bash
#
# 食事メニュー変更
#            食事メニュー登録画面から呼び出しにて
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
exec 2> /home/hands/E-LIFE/SHOKUJI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null

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
Shisetsu=$(nameread "Shisetsu" $tmp-name)
Tateya=$(nameread "Tateya" $tmp-name)
Taishousha=$(nameread "Taishousha" $tmp-name)
today=$(date +%Y%m%d)

#cat /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR |
#awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"'       |
#self 1 2 |
#LANG=C sort -u |

#検索対象プルダウン
cat <<FIN |
meisai 食事明細有り
kesshoku 欠食有り
FIN

awk '{if($1=="'${Taishousha}'"){print $0,"selected"}
      else{print $0}
     }'                       |
if [ "${Tateya}" != "02" ] ; then
  awk '$1!="kesshoku"'
else
  cat -
fi   > ${tmp}-taishousha
  

###########################################################################
#if [ "${MODE}" = "NyuukyoshaKakaku" ] ; then
#  awk '/\<nyuukyosya_zeikomi_start\>/,/\<nyuukyosya_zeikomi_end\>/' ${html_dir}/SHOKUJI_MENU_TOUROKU2.html 
#elif [ "${MODE}" = "Guest1Kakaku" ] ; then
#  awk '/\<guest1_zeikomi_start\>/,/\<guest1_zeikomi_end\>/' ${html_dir}/SHOKUJI_MENU_TOUROKU2.html
#elif [ "${MODE}" = "Guest2Kakaku" ] ; then
#  awk '/\<guest2_zeikomi_start\>/,/\<guest2_zeikomi_end\>/' ${html_dir}/SHOKUJI_MENU_TOUROKU2.html
#elif [ "${MODE}" = "StaffKakaku" ] ; then
#  awk '/\<staff_zeikomi_start\>/,/\<staff_zeikomi_end\>/' ${html_dir}/SHOKUJI_MENU_TOUROKU2.html
#fi |
  awk '/\<taishousha_select_start\>/,/\<taishousha_select_end\>/' ${html_dir}/SHOKUJI_MEISAI_IKKATSU_SHUTSURYOKU2.html |
 #
#  calsed -f $tmp-calsed -                               |
  mojihame -ltaishousha_select - ${tmp}-taishousha     |
  sed 's/###SPACE###/ /g'                               |
  sed 's/\\n/\n/g'                                      |
  sed 's/###KAIGYO###/\n/g'                              > $tmp-html
#tee $tmp-formhame_mae |
#  formhame -d"_" - $tmp-name    > $tmp-html
#cp $tmp-* /home/hands/work/okuda
# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
