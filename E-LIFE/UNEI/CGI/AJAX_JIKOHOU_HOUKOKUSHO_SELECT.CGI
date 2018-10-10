#!/bin/bash
#
# AJAX_JIKOHOU_HOUKOKUSHO_SELECT.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by E.Okuda / 2014.08.12

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

app_dir="${home_dir}/UNEI"
html_dir="${app_dir}/HTML"
kengen_dir="/home/hands/E-LIFE/TBL/KENGEN_KANRI"
data_dir="/DATA/E-LIFE"
riyousha_dir="${data_dir}/UNEI/RIYOUSHA"


# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name
#---

  Houkokusho=$(nameread "Houkokusho" $tmp-name)

 cat /home/hands/E-LIFE/TBL/JIKOHOU/HOUKOKUSHO_NAME_TBL |
 awk '$1=="'${Houkokusho}'"{print $1,$2}'                  > $tmp-houkokusho_name

HOUKOKUSHONAME="$(self 2 $tmp-houkokusho_name)"
HOUKOKUSHOTYPE="$(self 1 $tmp-houkokusho_name)"
# calsedデータの追記
cat << FIN > $tmp-calsed_data
###HOUKOKUSHONAME### ${HOUKOKUSHONAME}
###HOUKOKUSHOTYPE### ${HOUKOKUSHOTYPE}
FIN

###########################################################################
  awk '/\<houkokusho_header_start\>/,/\<houkokusho_header_end\>/' ${html_dir}/JIKOHOU_SHOUSAI2.html |
#tee /home/hands/work/okuda/ajax_test |
 #
calsed -f $tmp-calsed_data -                            |
  sed 's/###SPACE###/ /g'                               |
  sed 's/\\n/\n/g'                                      |
  sed 's/###KAIGYO###/\n/g'                             > $tmp-html
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
