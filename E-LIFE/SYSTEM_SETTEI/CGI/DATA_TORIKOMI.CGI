#!/bin/bash
#
# DATA_TORIKOMI.CGI : 欠食表CGI
# 
# 
# Written by E.Okuda :2014/01/08

source  /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null
exec 2> /home/hands/E-LIFE/SYSTEM_SETTEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
app_dir="${home_dir}/SYSTEM_SETTEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"
#-------------------------------------------------------------

dd bs=${CONTENT_LENGTH} > ${tmp}-param

if [ -s ${tmp}-param ]; then
  # 入力データは MIME 形式か？
  if ismime ${tmp}-param; then
    # MIME 形式なので、そのまま。
    cat ${tmp}-param > ${tmp}-param_mime
    # NAME 形式のファイルも準備
tr -s " " <<- FIN > ${tmp}-param_name
MODE       $(mime-read "MODE"        ${tmp}-param_mime)
Shisetsu   $(mime-read "Shisetsu"    ${tmp}-param_mime)
NUMBER     $(mime-read "NUMBER"      ${tmp}-param_mime)
FIN

  # アップロードファイルは別ファイルに保存
  mime-read FILE1 ${tmp}-param            > ${tmp}-upload_file
  mime-read FILE2 ${tmp}-param            > ${tmp}-upload_file2
  mime-read FILE3 ${tmp}-param            > ${tmp}-upload_file3
  mime-read FILE4 ${tmp}-param            > ${tmp}-upload_file4
  mime-read FILE5 ${tmp}-param            > ${tmp}-upload_file5
  mime-read FILE6 ${tmp}-param            > ${tmp}-upload_file6
  mime-read FILE7 ${tmp}-param            > ${tmp}-upload_file7
  mime-read FILE8 ${tmp}-param            > ${tmp}-upload_file8
  mime-read FILE9 ${tmp}-param            > ${tmp}-upload_file9
  mime-read FILE10 ${tmp}-param            > ${tmp}-upload_file10
  mime-read FILE11 ${tmp}-param            > ${tmp}-upload_file11

 else
    # MIME 形式ではないので、name 形式に変換。
    cgi-name -d"_" -i"_" ${tmp}-param > ${tmp}-param_name
    : > ${tmp}-param_mime
  fi
else
  # ファイルがないか、空ファイルなので、空ファイル作成。
  : | tee ${tmp}-param_name ${tmp}-param_mime
fi


eval $(name-source ${tmp}-param_name)
#-------------------------------------------------------------
#------------------------------------------------------------
# 処理モードの決定
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------
#-------------------------------------------------------------
# 処理モードの決定
MODE="$(nameread "MODE" ${tmp}-param_name)"
Shisetsu="$(nameread "Shisetsu" ${tmp}-param_name)"
[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#-------------------------------------------------------------

#--i-----------------------------------------------------------
# 処理の分岐
case "$MODE" in

  # -------------------------
  # 初期表示
  init)
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name  > $tmp-html
  ;;
  # -------------------------
  #--------------------------
  #利用者取込する場合
  touroku)
      ${cgi_dir}/DATA_TORIKOMI_RIYOUSHA.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #口座取込
  kyoshitsu)
      ${cgi_dir}/DATA_TORIKOMI_ROOM.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file2    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #口座取込
  kouza)
      ${cgi_dir}/DATA_TORIKOMI_KOUZA.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file3    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #連絡先取込
  renrakusaki)
      ${cgi_dir}/DATA_TORIKOMI_RENRAKUSAKI.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file4    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #入院外泊取込
  nyuuingaihaku)
      ${cgi_dir}/DATA_TORIKOMI_NYUUINGAIHAKU.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file11    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------


  #--------------------------
  #利用料取込
  riyouryou)
      ${cgi_dir}/DATA_TORIKOMI_RIYOURYOU.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file7    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #利用料取込
  keiyakukin)
      ${cgi_dir}/DATA_TORIKOMI_KEIYAKUKIN.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file8    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #食事メニュー取込
  shokuji_menu)
      ${cgi_dir}/DATA_TORIKOMI_SHOKUJI_MENU.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file6    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #食事取込
  shokuji)
      ${cgi_dir}/DATA_TORIKOMI_SHOKUJI.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file5    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------

  #--------------------------
  #食事取込
  service)
      ${cgi_dir}/DATA_TORIKOMI_SERVICE_RIYOURYOU.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file9    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
      ${cgi_dir}/DATA_TORIKOMI_SERVICE_RIYOURYOU.DATASET ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file9    > ${tmp}-ok
  ;;
  #--------------------------
  #--------------------------
  #食事取込
  tatekaekin)
      ${cgi_dir}/DATA_TORIKOMI_TATEKAEKIN.UPLOAD ${tmp}-param_name ${tmp}-param_mime ${tmp}-upload_file10    > ${tmp}-touroku
      ${cgi_dir}/DATA_TORIKOMI.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;
  #--------------------------



esac
#-------------------------------------------------------------

# HTMLファイルを表示する
if [ -e "$tmp-html" ];then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
else
  cat $tmp-html2
fi

#終了
rm $tmp-*
exit 0 
