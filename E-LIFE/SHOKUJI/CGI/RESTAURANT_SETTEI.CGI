#!/bin/bash
#
# RESTAURANT_SETTEI.CGI : レストラン設定CGI
#
# Usage : RESTAURANT_SETTEI.CGI
#
# Written by R.Suzuki Date:2015/08/27

# ログ
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


rm -f $tmp-*


# パラメーターの取得
#アイコン起動時はPOSTデータがないため上記でエラーになるのを回避。
if [ "${CONTENT_LENGTH}" != "" ] ; then
dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name
else
:> $tmp-name
fi

#------------------------------------------------------------

eval $(name-source $tmp-name)

#------------------------------------------------------------
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#------------------------------------------------------------


# 処理の分岐
case "${MODE}" in
  #初期表示
  init )

    ${cgi_dir}/RESTAURANT_SETTEI.DISPLAY ${tmp}-name > ${tmp}-html
    ;;

  #その他の場合
  * )
    ${cgi_dir}/RESTAURANT_SETTEI.DISPLAY ${tmp}-name > ${tmp}-html
    ;;
esac

#--------------------------------------------------------------

# HTMLファイルを表示する
if [ -e "$tmp-html" ];then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
fi

#--------------------------------------------------------------

## 終了
rm -f ${tmp}-*
exit 0

