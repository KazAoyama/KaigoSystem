#!/bin/bash
#
# SHOKUJI_SIGN.CGI :利用者サインCGI
# 
# 
# Written by K.Aoyama :2015/08/21

source  /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null
exec 2> /home/hands/E-LIFE/SHOKUJI/APLOG/$(date "+%Y%m%d")/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
app_dir="${home_dir}/SHOKUJI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
#-------------------------------------------------------------

dd bs=${CONTENT_LENGTH} > ${tmp}-param_work
sed 's/&sign_string=/ /g' ${tmp}-param_work |
tee $tmp-param_tmp |
self 1 > ${tmp}-param
self 2 $tmp-param_tmp > $tmp-param_sign_file

cp ${tmp}-param_work $work_dir/param_name_sign
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)

#-------------------------------------------------------------
#------------------------------------------------------------
# パラメーターの取得
#dd bs=${CONTENT_LENGTH}        |
#cgi-name -d_ -i_               |
#LANG=C sort                    > $tmp-name
#cookie-name                    |
#LANG=C sort                    > ${tmp}-cookie
#------------------------------------------------------------
#------------------------------------------------------------
# 処理モードの決定
#eval $(name-source ${tmp}-cookie)
#eval $(name-source $tmp-name)
#[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------


#------------------------------------------------------------
#upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
#cp -p $tmp-name $tmp-name_origin
#mv -f $tmp-name.new0 $tmp-name

#-------------------------------------------------------------
# 処理モードの決定
MODE="$(nameread "MODE" ${tmp}-param_name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#-------------------------------------------------------------

#--i-----------------------------------------------------------
# 処理の分岐
case "$MODE" in

  # -------------------------
  # 初期表示
  init)
    ${cgi_dir}/SHOKUJI_SIGN.DISPLAY ${tmp}-param_name > ${tmp}-html
  ;;
  regist)
    ${cgi_dir}/SHOKUJI_SIGN.TOUROKU ${tmp}-param_name $tmp-param_sign_file > ${tmp}-touroku
    ${cgi_dir}/SHOKUJI_SIGN.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  display)
    ${cgi_dir}/SHOKUJI_SIGN.DISPLAY ${tmp}-param_name > ${tmp}-html
  ;;

  #--------------------------

esac
#-------------------------------------------------------------

# HTMLファイルを表示する
echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
cat - ${tmp}-html

# 終了
rm -f $tmp-*
exit 0
