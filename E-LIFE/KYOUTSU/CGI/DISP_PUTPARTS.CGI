#!/bin/bash
#
# PUTPARTS.CGI : 身体図CGI
#
# Usage : PUTPARTS.CGI
#
# Written by K.AOYAMA(HANDS LAB)

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/KYOUTSU/CGI/KYOUTSU.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


rm -f $tmp-*


#------------------------------------------------------------
# パラメーターの取得
dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name
cookie-name                    |
LANG=C sort                    > ${tmp}-cookie
#------------------------------------------------------------


#------------------------------------------------------------
# 処理モードの決定
eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
#------------------------------------------------------------

#------------------------------------------------------------
upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
cp -p $tmp-name $tmp-name_origin
mv -f $tmp-name.new0 $tmp-name

#MODEの確認
USERID="$(nameread "userid" ${tmp}-name)"

${cgi_dir}/DISP_PUTPARTS.DISPLAY ${tmp}-name > ${tmp}-html


## 終了
rm -f ${tmp}-*
exit 0

