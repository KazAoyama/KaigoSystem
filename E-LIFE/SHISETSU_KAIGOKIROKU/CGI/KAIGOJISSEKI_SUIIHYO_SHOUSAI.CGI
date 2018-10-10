#!/bin/bash
#
# KAIGOJISSEKI_SUIIHYO.CGI : 介護実績推移表CGI
#
# Usage : KAIGOJISSEKI_SUIIHYO.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)


# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

#--------------------ログ出力--------------------
mkdir -p /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/APLOG/$(date +%Y%m%d)
exec 2> /home/hands/E-LIFE/SHISETSU_KAIGOKIROKU/APLOG/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv


# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/SHISETSU_KAIGOKIROKU"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
ch_cgi_dir="${home_dir}/E-LIFE/TEST/CGI"
riyosha_dir="/DATA/E-LIFE/UNEI/RIYOUSHA"
tbl_dir="${home_dir}/E-LIFE/TBL"

#}}}Functions#######################################

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-param_name)"
[ -n "${MODE}" ] || MODE="init"


# 処理の分岐
case "${MODE}" in
  # 詳細表示する場合
  shosai )
    ${cgi_dir}/KAIGOJISSEKI_SUIIHYO_SHOUSAI.SEARCH ${tmp}-param_name   > ${tmp}-search
    ${cgi_dir}/KAIGOJISSEKI_SUIIHYO_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
  #その他の場合
  * )
    ${cgi_dir}/KAIGOJISSEKI_SUIIHYO_SHOUSAI.SEARCH ${tmp}-param_name   > ${tmp}-search
    ${cgi_dir}/KAIGOJISSEKI_SUIIHYO_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-search  > ${tmp}-html
  ;;
esac

# 返す？
if [ "$(gyo ${tmp}-search)" -ne 0 ];then
  :
else
  message="その日はデータがありません"
cat <<- FIN > $tmp-html2
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
fi


# HTMLファイルを表示する
if [ -e "${tmp}-html2" ];then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html ${tmp}-html2
else
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
fi

rm -f ${tmp}-*
exit 0

