#!/bin/bash
#
# KOJINJYOUHOU_SHOUSAI_KEIYAKU.CGI : 個人情報詳細(契約)CGI
# 
# 
#
# Written by E.Okuda :2013/12/9

exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
cgi_dir="${home_dir}/UNEI/CGI"

#-------------------------------------------------------------

dd bs=${CONTENT_LENGTH} > ${tmp}-param

if [ -s ${tmp}-param ]; then
  # 入力データは MIME 形式か？
  if ismime ${tmp}-param; then
    # MIME 形式なので、そのまま。
    cat ${tmp}-param > ${tmp}-param_mime
    # NAME 形式のファイルも準備
tr -s " " <<- FIN > ${tmp}-param_name
MODE                   $(mime-read "MODE"               ${tmp}-param_mime)
KEIYAKU_SHURUI         $(mime-read "KEIYAKU_SHURUI"     ${tmp}-param_mime)
KEIYAKUID              $(mime-read "KEIYAKUID"          ${tmp}-param_mime)
RIYOUSHAID             $(mime-read "RIYOUSHAID"         ${tmp}-param_mime)
RIYOUSHANAME           $(mime-read "RIYOUSHANAME"       ${tmp}-param_mime)
USERID                 $(mime-read "USERID"             ${tmp}-param_mime)
USERNAME               $(mime-read "USERNAME"           ${tmp}-param_mime)
SHISETSUID             $(mime-read "SHISETSUID"         ${tmp}-param_mime)
SHISETSUNAME           $(mime-read "SHISETSUNAME"       ${tmp}-param_mime)
NYUUKYOTATEYAID        $(mime-read "NYUUKYOTATEYAID"    ${tmp}-param_mime)
NYUUKYOTATEYANAME      $(mime-read "NYUUKYOTATEYANAME"  ${tmp}-param_mime)
NYUUKYOFLOOR           $(mime-read "NYUUKYOFLOOR"       ${tmp}-param_mime)
NYUUKYOUNITID          $(mime-read "NYUUKYOUNITID"      ${tmp}-param_mime)
NYUUKYOUNITNAME        $(mime-read "NYUUKYOUNITNAME"    ${tmp}-param_mime)
NYUUKYOSHISETSUID      $(mime-read "NYUUKYOSHISETSUID"  ${tmp}-param_mime)
NYUUKYOSHISETSUNAME    $(mime-read "NYUUKYOSHISETSUNAME" ${tmp}-param_mime)
NYUUKYOKYOSHITSU       $(mime-read "NYUUKYOKYOSHITSU"   ${tmp}-param_mime)
TOUROKUDISP            $(mime-read "TOUROKUDISP"        ${tmp}-param_mime)
PRINTDISP              $(mime-read "PRINTDISP"          ${tmp}-param_mime)
userid                 $(mime-read "userid"             ${tmp}-param_mime)
shisetsu               $(mime-read "shisetsu"           ${tmp}-param_mime)
FIN
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
#-------------------------------------------------------------


#IsLogon{{{################################################

#-------------------------------------------------------------
# 処理モードの決定
MODE="$(nameread "MODE" ${tmp}-param_name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#-------------------------------------------------------------

#--i-----------------------------------------------------------
# 処理の分岐
case "$MODE" in

  #--------------------------
  #検索(初期表示で検索結果が出る)
  init)
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
  ;;
  #--------------------------
  edit_keiyakusho_upload)
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.UPDATE_KEIYAKUSHO ${tmp}-param_name ${tmp}-param_mime    > ${tmp}-kikakusho
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.SEARCH ${tmp}-param_name                                 > ${tmp}-search
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.DISPLAY ${tmp}-param_name ${tmp}-search ${tmp}-kikakusho > ${tmp}-html
  ;;
  #--------------------------

  keiyaku_sakujyo)
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.SAKUJYO ${tmp}-param_name                                > ${tmp}-sakujyo
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.SEARCH ${tmp}-param_name                                 > ${tmp}-search
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.DISPLAY ${tmp}-param_name ${tmp}-search ${tmp}-sakujyo > ${tmp}-html
  ;;
  #--------------------------

  keiyakusho_sakujyo)
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.IMAGE_SAKUJYO ${tmp}-param_name                          > ${tmp}-kikakusho
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.SEARCH ${tmp}-param_name                                 > ${tmp}-search
    ${cgi_dir}/KOJINJYOUHOU_SHOUSAI_KEIYAKU.DISPLAY ${tmp}-param_name ${tmp}-search ${tmp}-kikakusho > ${tmp}-html
  ;;
  #--------------------------

esac
#-------------------------------------------------------------


# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0

