#!/bin/bash
#
# AJAX_JIGYOUSHO.CGI:
#　事業所を取得。
# Ajax による使用を想定。
#
#
# Written by K.Aoyama / 2013.12.27

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

#=== 初期化 ===
tmp=/var/tmp/${$}

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name
#---

# POSTパラメータの取得
ServiceType=$(nameread "ServiceType" $tmp-name)

: > tmp-jigyousho_master_html
# 事業所マスター
cat ${home_dir}/TBL/JIGYOUSHO/JIGYOUSHO_MASTER |
LANG=C sort -k1,1 |
# 1:事業所ID 2:事業所名
awk '$4=="'${ServiceType}'"{print "<option value=\""$1"\">"$3"</option>"}'    > $tmp-jigyousho_master_html

cp $tmp-jigyousho_master_html $work_dir/html_jigyousho

# HTML の出力
cat << FIN | cat - $tmp-jigyousho_master_html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
