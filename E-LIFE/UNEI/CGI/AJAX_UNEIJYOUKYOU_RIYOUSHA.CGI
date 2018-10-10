#!/bin/bash
#
# AJAX_UNEIJYOUKYOU_RIYOUSHA.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
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
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/SHOKUJI.INI &> /dev/null

#=== 初期化 ===
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

home_dir=/home/hands/E-LIFE
app_dir="${home_dir}/UNEI"
html_dir="${app_dir}/HTML"
data_dir="/DATA/E-LIFE"
riyousha_dir="${data_dir}/UNEI/RIYOUSHA"
kengen_dir="/home/hands/E-LIFE/TBL/KENGEN_KANRI"
tbl_dir="/home/hands/E-LIFE/TBL/"

cgi_name="KOJINJYOUHOU_SHOUSAI_ASSESSMENT.CGI"

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

  Shisetsu=$(nameread   "Shisetsu" $tmp-name)
  Tateya=$(nameread     "Tateya" $tmp-name)
  today=$(date +%Y%m%d)

## 建屋取得
#--
# 従業員所属テーブルに建屋があればデフォルト
cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR  |
# 1:施設ID 2:建屋ID 3:フロア
awk '$1=="'${Shisetsu}'"{print $2}'                   |
LANG=C sort -u |
join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -  |
self 1 3                                                > $tmp-tateya_kari
# 1:建屋ID 2:建屋名
#-
# 建屋が選択されていたらselected
if [ -z "${Tateya}"  -o "${Tateya}" = "_" ] ;then
  cat $tmp-tateya_kari
else
  cat $tmp-tateya_kari |
  awk '{if($1=="'${Tateya}'"){print $0,"selected"}
        else{print $0,"@"}
       }'
fi    > $tmp-tateya_name

# cp $tmp-* /home/hands/work/okuda

###########################################################################

awk '/\<tateya_select_start\>/,/\<tateya_select_end\>/' ${html_dir}/UNEIJYOUKYOU_HOUKOKUSHO2.html |
#tee /home/hands/work/okuda/ajax_test |
 #

  mojihame -l"tateya_select"     - $tmp-tateya_name     |
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
