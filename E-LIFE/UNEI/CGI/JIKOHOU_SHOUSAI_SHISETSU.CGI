#!/bin/bash
#
# JIKOHOU_SHOUSAI_SHISETSU.CGI : 個人情報詳細(基本)CGI
# 
# 
#
# Written by E.Okuda :2013/12/3

exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xva

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
RIYOUSHAID             $(mime-read "RIYOUSHAID"         ${tmp}-param_mime)
USERID                 $(mime-read "USERID"             ${tmp}-param_mime)
USERNAME               $(mime-read "USERNAME"           ${tmp}-param_mime)
SHISETSUID             $(mime-read "SHISETSUID"         ${tmp}-param_mime)
SHISETSUNAME           $(mime-read "SHISETSUNAME"       ${tmp}-param_mime)
NYUUKYOTATEYAID        $(mime-read "NYUUKYOTATEYAID"    ${tmp}-param_mime)
NYUUKYOFLOOR           $(mime-read "NYUUKYOFLOOR"       ${tmp}-param_mime)
NYUUKYOUNITID          $(mime-read "NYUUKYOUNITID"      ${tmp}-param_mime)
NYUUKYOSHISETSUID      $(mime-read "NYUUKYOSHISETSUID"  ${tmp}-param_mime)
NYUUKYOKYOSHITSU       $(mime-read "NYUUKYOKYOSHITSU"   ${tmp}-param_mime)
NyuukyoShisetsu        $(mime-read "NyuukyoShisetsu"    ${tmp}-param_mime)
NyuukyoTateya          $(mime-read "NyuukyoTateya"      ${tmp}-param_mime)
NyuukyoUnit            $(mime-read "NyuukyoUnit"        ${tmp}-param_mime)
NyuukyoKyoshitsu       $(mime-read "NyuukyoKyoshitsu"   ${tmp}-param_mime)
userid                 $(mime-read "userid"             ${tmp}-param_mime)
shisetsu               $(mime-read "shisetsu"           ${tmp}-param_mime)
Shimei                 $(mime-read "Shimei"             ${tmp}-param_mime | sed 's/_/###SPACE###/g' )
Shimeikana             $(mime-read "Shimeikana"         ${tmp}-param_mime | sed 's/_/###SPACE###/g')
Seibetsu               $(mime-read "Seibetsu"           ${tmp}-param_mime)
SeinengappiGengou      $(mime-read "SeinengappiGengou"  ${tmp}-param_mime)
SeinengappiYear        $(mime-read "SeinengappiYear"    ${tmp}-param_mime)
SeinengappiMonth       $(mime-read "SeinengappiMonth"   ${tmp}-param_mime)
SeinengappiDay         $(mime-read "SeinengappiDay"     ${tmp}-param_mime)
Nenrei                 $(mime-read "Nenrei"             ${tmp}-param_mime)
Kansenshou             $(mime-read "Kansenshou"         ${tmp}-param_mime)
Shisetsu               $(mime-read "Shisetsu"           ${tmp}-param_mime)
Tateya                 $(mime-read "Tateya"             ${tmp}-param_mime)
Floor                  $(mime-read "Floor"              ${tmp}-param_mime)
Unit                   $(mime-read "Unit"               ${tmp}-param_mime)
Kyoshitsu              $(mime-read "Kyoshitsu"          ${tmp}-param_mime)
KeiyakuNenrei          $(mime-read "KeiyakuNenrei"      ${tmp}-param_mime)
KeiyakuShurui          $(mime-read "KeiyakuShurui"      ${tmp}-param_mime)
Keiyakubi              $(mime-read "Keiyakubi"          ${tmp}-param_mime)
KeiyakukikanFrom       $(mime-read "KeiyakukikanFrom"   ${tmp}-param_mime)
KeiyakuHikiwatashibi   $(mime-read "KeiyakuHikiwatashibi"   ${tmp}-param_mime)
NyuukyoMaeYuubinBangou $(mime-read "NyuukyoMaeYuubinBangou" ${tmp}-param_mime)
NyuukyoMaeJyuusho      $(mime-read "NyuukyoMaeJyuusho"      ${tmp}-param_mime)
YuubinBangou           $(mime-read "YuubinBangou"           ${tmp}-param_mime)
GenJyuusho             $(mime-read "GenJyuusho"             ${tmp}-param_mime)
Tel                    $(mime-read "Tel"                    ${tmp}-param_mime)
Email                  $(mime-read "Email"                  ${tmp}-param_mime)
Shumi                  $(mime-read "Shumi"                  ${tmp}-param_mime)
Bikou                  $(mime-read "Bikou"                  ${tmp}-param_mime)
GaijiKyuuji            $(mime-read "GaijiKyuuji"            ${tmp}-param_mime)
CHINRYOU               $(mime-read "CHINRYOU"               ${tmp}-param_mime)
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

#if ismime $tmp-param ; then
#mime-read "EDIT_IMAGE1_SELECT" ${tmp}-param
#fi

#-------------------------------------------------------------
# 処理モードの決定
MODE="$(grep "MODE" ${tmp}-param_name | self 2)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#-------------------------------------------------------------

#--i-----------------------------------------------------------
# 処理の分岐
case "$MODE" in

  # -------------------------
  # 初期表示
  init)
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.DISPLAY ${tmp}-param_name > $tmp-html
#  ;;
  # -------------------------

  #--------------------------
  #検索(初期表示で検索結果が出る)
#  init)
#    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.SEARCH ${tmp}-param_name               > ${tmp}-search
#    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.DISPLAY ${tmp}-param_name ${tmp}-search > ${tmp}-html
  ;;
  #--------------------------
  #--------------------------
  #登録(更新登録)
  touroku)
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.TOUROKU ${tmp}-param_name ${tmp}-param   > ${tmp}-touroku
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.DISPLAY ${tmp}-param_name ${tmp}-touroku > ${tmp}-html
  ;;

  #--------------------------
  #--------------------------
  #基本情報Excel出力
  KihonPrint)
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.SEARCH ${tmp}-param_name               > ${tmp}-search
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.EXCEL ${tmp}-param_name ${tmp}-search > ${tmp}-html
  ;;

  #--------------------------
  #--------------------------
  #登録(更新登録)
#  shinki)
#    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU_SHINKI.DISPLAY ${tmp}-param_name  > ${tmp}-html
#  ;;
  #--------------------------
  #登録(更新登録)
  edit_image1_upload)
   [ $MODE == "edit_image1_upload" ] && no="1"
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.UPDATE_IMAGE $tmp-param_name "$no" ${tmp}-param_mime > $tmp-data
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.DISPLAY $tmp-param_name $tmp-data > $tmp-html
  ;;

  #--------------------------
  #削除
  edit_image1_delete)
   [ $MODE == "edit_image1_delete" ] && no="1"
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.DELETE_IMAGE $tmp-param_name "$no" > $tmp-data
    ${cgi_dir}/JIKOHOU_SHOUSAI_SHISETSU.DISPLAY $tmp-param_name $tmp-data > $tmp-html

  ;;

esac
#-------------------------------------------------------------


# HTMLの出力
cat <<FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f ${tmp}-*
exit 0
