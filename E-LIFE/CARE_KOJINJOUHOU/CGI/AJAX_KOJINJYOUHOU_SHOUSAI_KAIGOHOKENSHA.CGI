#!/bin/bash
#  AJAX_KOJINJYOUHOU_SHOUSAI_KAIGOHOKENSHA.CGI 
#       介護保険者名称取得      Ajax による使用を想定。
#
# Written by E.Okuda / 2014.03.05

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
home_dir="/home/hands/E-LIFE"
tbl_dir="/home/hands/E-LIFE/TBL"

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


  KaigoHokenshaBangou=$(nameread "KaigoHokenshaBangou" $tmp-name)

# 保険者マスタから保険者名をとってくる
  cat ${tbl_dir}/HOKENJA/HOKENJA_TABLE |
  awk '$2=="'${KaigoHokenshaBangou}'"&&$(NF-2)!="9"{print $4}' > $tmp-hokensha_name

  if [ -s $tmp-hokensha_name ] ; then
    KaigoHokenshaName="$(cat $tmp-hokensha_name)"
  else
    KaigoHokenshaName="マスタに該当する保険者がありません。"
  fi
###########################################################################
awk '/\<hokensha_name_start\>/,/\<hokensha_name_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KAIGOHOKEN.html |
tee $tmp-ajax_html |
calsed "###KaigoHokenshaName###" "${KaigoHokenshaName}" - > $tmp-html
#mojihame -l"###KaigoHokenshaName###" "${KaigoHokenshaName}" |

#tee $tmp-formhame_mae |
#  formhame -d"_"  - $tmp-name    > $tmp-html

#cp $tmp-* /home/hands/work/okuda

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
