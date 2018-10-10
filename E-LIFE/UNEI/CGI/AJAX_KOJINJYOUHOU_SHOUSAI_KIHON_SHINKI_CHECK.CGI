#!/bin/bash
#
# KOJINJYOUHOU_SHOUSAI_SHINKI_CHECK.CGI : 個人情報重複チェックCGI
# 
# 
#
# Written by E.Okuda :2013/11/20

exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}
html_dir="${home_dir}/UNEI/HTML"
pompa_dir="${home_dir}/UNEI/POMPA"
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

MODE=$(nameread "MODE" $tmp-name)
Shimei=$(nameread "Shimei" $tmp-name)
Shimeikana=$(nameread "Shimeikana" $tmp-name)
SeinengappiGengou=$(nameread "SeinengappiGengou" $tmp-name)
SeinengappiYear=$(nameread "SeinengappiYear" $tmp-name)
SeinengappiMonth=$(nameread "SeinengappiMonth" $tmp-name)
SeinengappiDay=$(nameread "SeinengappiDay" $tmp-name)
RIYOUSHAID=$(nameread "RIYOUSHAID" $tmp-name)
#-------------------------------------------------------------
#--------------------------------------------------------------
function error_exit {
  message="$1"
  echo "message ${message}"
  echo "result ng"
  rm -f $tmp-*
  exit 1
}
function error_exit_choufuku {
  message="$1"
  echo "message ${message}"
  echo "result check_ng"
  cat $tmp-data
  rm -f $tmp-*
  exit 1
}

#-------------------------------------------------------------
# ファイルの取得
# 1:利用者(入居者)ID 2:利用者(入居者)氏名 3:利用者(入居者)氏名カナ 4:性別           5:和暦：元号
# 6:和暦：誕生年     7:和暦：誕生月       8:和暦：誕生日           9:西暦：生年月日 10:感染症
# 11:入居前郵便番号  12:入居前住所        13:現郵便番号            14:現住所        15:携帯電話番号
# 16:E-MAILアドレス  17:趣味特技          18:備考
if [ -s ${pompa_dir}/RIYOUSHA/RIYOUSHA_CHOUFUKU_OK ] ; then 
  awk '$(NF-2)!="9"{print $1}' ${pompa_dir}/RIYOUSHA/RIYOUSHA_CHOUFUKU_OK |
  LANG=C sort                  > $tmp-choufuku_nocheck
  if [ -s $tmp-choufuku_nocheck ] ; then
    cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KIHON  |
    cjoin1 +ng key=1 $tmp-choufuku_nocheck - >/dev/null 2>$tmp-riyousha_kihon
  else
    cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KIHON > $tmp-riyousha_kihon
  fi
else
    cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KIHON > $tmp-riyousha_kihon
fi



if [ "${MODE}" = "Shimei" ] ; then

  ShimeiNoSpace=$(echo "${Shimei}" | sed 's/_/　/g'| sed 's/　//g')

#  cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KIHON  |
  cat $tmp-riyousha_kihon        |
  awk '{gsub("　","");print $0}' |
#  awk '$2=="'${ShimeiNoSpace}'"&&$3=="'${ShimeikanaNoSpace}'"&&$4=="'${Seibetsu}'"&&$5=="'${SeinengappiGengou}'"&&$6=="'${SeinengappiYear}'"&&$7=="'${SeinengappiMonth}'"&&$8=="'${SeinengappiDay}'"&&$(NF-2)!="9"{print "choufuku",$0}' > $tmp-data
  awk '$2=="'${ShimeiNoSpace}'"&&$(NF-2)!="9"{print $0}' |
  if [ -z "${RIYOUSHAID}" -o "${RIYOUSHAID}" = "_" ] ; then
     cat - 
  else
     awk '$1!="'${RIYOUSHAID}'"'
  fi > $tmp-choufuku

  if [ -s $tmp-choufuku ] ; then
    ShimeiAlert="同じ名前のデータがあります。登録前に今一度基本情報一覧で重複していないか確認して下さい。"
  else
    ShimeiAlert=""
  fi

elif [ "${MODE}" = "Shimeikana" ] ; then

  ShimeikanaNoSpace=$(echo "${Shimeikana}" | sed 's/_/　/g' | sed 's/　//g')

#  cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KIHON  |
  cat $tmp-riyousha_kihon  |
  awk '{gsub("　","");print $0}' |
  awk '$3=="'${ShimeikanaNoSpace}'"&&$(NF-2)!="9"{print $0}' |
# > $tmp-choufuku
  if [ -z "${RIYOUSHAID}" -o "${RIYOUSHAID}" = "_" ] ; then
     cat -
  else
     awk '$1!="'${RIYOUSHAID}'"'
  fi > $tmp-choufuku

  if [ -s $tmp-choufuku ] ; then
    ShimeikanaAlert="同じ名前のデータがあります。登録前に今一度基本情報一覧で重複していないか確認して下さい。"
  else
    ShimeikanaAlert=""
  fi

elif [ "${MODE}" = "Seinengappi" ] ; then

#  cat ${pompa_dir}/RIYOUSHA/RIYOUSHA_KIHON  |
  cat $tmp-riyousha_kihon  |
  awk '$5=="'${SeinengappiGengou}'"&&$6=="'${SeinengappiYear}'"&&$7=="'${SeinengappiMonth}'"&&$8=="'${SeinengappiDay}'"&&$(NF-2)!="9"{print $0}'  |
#> $tmp-choufuku
  if [ -z "${RIYOUSHAID}" -o "${RIYOUSHAID}" = "_" ] ; then
     cat -
  else
     awk '$1!="'${RIYOUSHAID}'"'
  fi > $tmp-choufuku

  if [ -s $tmp-choufuku ] ; then
    SeinengappiAlert="同じ生年月日のデータがあります。登録前に今一度基本情報一覧で重複していないか確認して下さい。"
  else
    SeinengappiAlert=""
  fi

else
  :
fi

# -------------------------
# calsedファイル
cat << FIN > $tmp-calsed_data
###ShimeiAlert### ${ShimeiAlert}
###ShimeikanaAlert### ${ShimeikanaAlert}
###SeinengappiAlert### ${SeinengappiAlert}
FIN

cat $tmp-calsed_data |
sed 's/_/ /g'        > $tmp-calsed_result

#-------------------------------------------------------------
if [ "${MODE}" = "Shimei" ] ; then
 awk '/\<shimei_td_start\>/,/\<shimei_td_end\>/' ${html_dir}/KOJINJYOUHOU_SHOUSAI_SHINKI.html
elif [ "${MODE}" = "Shimeikana" ] ; then
 awk '/\<shimeikana_td_start\>/,/\<shimeikana_td_end\>/' ${html_dir}/KOJINJYOUHOU_SHOUSAI_SHINKI.html
elif [ "${MODE}" = "Seinengappi" ] ; then
 awk '/\<seinengappi_td_start\>/,/\<seinengappi_td_end\>/' ${html_dir}/KOJINJYOUHOU_SHOUSAI_SHINKI.html 
else
 :
fi |

calsed -f $tmp-calsed_result - > $tmp-html


cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

## 終了
rm -f $tmp-*
exit 0
