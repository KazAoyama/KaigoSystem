#!/bin/bash
#
# APDATASET.MONTH.WEBEDI.SHIHARAI_MEISAI : 支払明細書をPOMPAにセットする
#
# Usage : APDATASET.MONTH.WEBEDI.SHIHARAI_MEISAI
#
# Written by Tomoaki.Imai / Date : 2012/03/29

source /home/hands/.bashrc &> /dev/null

#Functions{{{###################################################
function error_exit {
  touch ${semaphore_dir}/$(basename ${0}).${HOSTNAME}.ERROR.$(date "+%Y%m%d%H%M%S")
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions###################################################

# 走行ログの記録

exec 2> /home/hands/LOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d%H%M%S"); set -xv

# 開始
upcnt "${HOSTNAME} $(basename ${0}) START $(date "+%Y%m%d%H%M%S")"

# 本日設定
[ -n "$(awk --re-interval 'BEGIN{if("'"${1}"'" ~ /^[0-9]{8}$/){print "'"${1}"'"}}')" ] && today="${1}" || today="$(date "+%Y%m%d")"
current_time="$(date "+%Y%m%d%H%M%S")"

#DeclareVariables->{{{######################################
# 変数の宣言
tmp_dir="/dev/shm"
tmp="${tmp_dir}/${$}"
thismonth="${today:0:6}"
lastmonth="$(mdate ${thismonth}/-1)"
input_file_name="KAIKAKE_MOTOCHO"
output_file_name="SHIHARAI_MEISAI"

# ディレクトリの宣言
home_dir="/home/hands"
semaphore_dir="${home_dir}/SEMAPHORE"
app_dir="${home_dir}/WEBEDI"
sys_dir="${app_dir}/SYS"
pompa_dir="${app_dir}/POMPA"
data_dir="/DATA"
hands_data_dir="${data_dir}/HOST"
scl_data_dir="${data_dir}/HOST_SCL"
sz_data_dir="${data_dir}/HOST_SZ"
sa_data_dir="${data_dir}/HOST_SA"
txt_data_dir="KAIKAKE_MOTOCHOU/TXT"
hands_level3_data_dir="${hands_data_dir}/${txt_data_dir}/${lastmonth}"
scl_level3_data_dir="${scl_data_dir}/${txt_data_dir}/${lastmonth}"
sz_level3_data_dir="${sz_data_dir}/${txt_data_dir}/${lastmonth}"
sa_level3_data_dir="${sa_data_dir}/${txt_data_dir}/${lastmonth}"
# ファイルの宣言
download_list_name="SHIHARAI_DOWNLOAD_LIST"
#}}}<-DeclareVariables######################################

#MainProcess->{{{######################################

cat << FIN > ${tmp}-companies
HANDS ${hands_level3_data_dir}
SCL ${scl_level3_data_dir}
SZ ${sz_level3_data_dir}
SA ${sa_level3_data_dir}
FIN
# 1:会社 2:ディレクトリ

cat << FIN > ${tmp}-shiharai_meisai_list
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0079014 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0729302 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0731633 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0864439 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0924598 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0928313 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0932280 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0938823 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0942081 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0942324 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0946575 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0986305 HANDS
/DATA/HOST/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0988820 HANDS
/DATA/HOST_SCL/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0864439 SCL 
/DATA/HOST_SCL/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0924598 SCL 
/DATA/HOST_SCL/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0942081 SCL 
/DATA/HOST_SCL/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0986305 SCL 
/DATA/HOST_SCL/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0988820 SCL 
/DATA/HOST_SA/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0864439 SA
/DATA/HOST_SZ/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0864439 SZ
/DATA/HOST_SZ/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0924598 SZ
/DATA/HOST_SZ/KAIKAKE_MOTOCHOU/TXT/201206/KAIKAKE_MOTOCHO.0942081 SZ
FIN
# 1:ファイル 2:会社

# 各社の支払明細書をPOMPAにセットする
cat ${tmp}-shiharai_meisai_list |
while read file company; do
  base_name="$(basename ${file})"
  torihikisaki_code="${base_name#*.}"
  torihikisaki_dir="${pompa_dir}/${torihikisaki_code}00"
  download_list_file="${torihikisaki_dir}/${download_list_name}.${torihikisaki_code}"
  download_file="${torihikisaki_dir}/${output_file_name}_${company}_${lastmonth}_${torihikisaki_code}.pdf"
  torihikisaki_company_tmp="${tmp}-${torihikisaki_code}_${company}"
  # vimを使ってテキストファイルをHTMLファイルに変換するためのオプション定義
  echo -e \n:TOhtml"              \
          \n:w ${torihikisaki_company_tmp}-output_file \
          \n:qa! "                > ${torihikisaki_company_tmp}-vimoption
  # 取引先ごとのディレクトリを作成する
  mkdir -p ${torihikisaki_dir}
  # テキストからHTMLに変換する
  vim -n -s ${torihikisaki_company_tmp}-vimoption ${file} < /dev/null > /dev/null 2> /dev/null
  [ ${?} -eq 0 ] || error_exit
  cat ${torihikisaki_company_tmp}-output_file |
  # フォントの書き換え
  sed -e 's|monospace|IPA Gothic|'            |
  # タイトルの書き換え
  sed -e 's|買掛元帳|支払明細書|'             > ${torihikisaki_company_tmp}-html.html
  [ $(plus ${PIPESTATUS[@]}) -eq 0 ] || error_exit
  # HTMLからPDFに変換する
  ${app_dir}/TOOL/wkhtmltopdf-i386 -q ${torihikisaki_company_tmp}-html.html ${torihikisaki_company_tmp}-pdf
  [ ${?} -eq 0 ] || error_exit
  if [ -e "${download_list_file}" ]; then
    cat ${download_list_file} > ${torihikisaki_company_tmp}-download_list
  else
    touch ${torihikisaki_company_tmp}-download_list
  fi
  echo "${lastmonth} ${company} download ${current_time}" |
  # 1:年月 2:会社 3:表示方法 4:更新日時
  cat - ${torihikisaki_company_tmp}-download_list         |
  LANG=C sort -k1,2 -k4,4                                 |
  getlast 1 2                                             > ${torihikisaki_company_tmp}-new_download_list
  [ $(plus ${PIPESTATUS[@]}) -eq 0 ] || error_exit
  mv -f ${torihikisaki_company_tmp}-pdf ${download_file}
  [ ${?} -eq 0 ] || error_exit
  mv -f ${torihikisaki_company_tmp}-new_download_list ${download_list_file}
  [ ${?} -eq 0 ] || error_exit
done
[ ${?} -eq 0 ] || error_exit
#}}}<-MainProcess######################################

# 終了
upcnt "${HOSTNAME} $(basename ${0}) END $(date "+%Y%m%d%H%M%S")"
touch ${semaphore_dir}/$(basename ${0}).${HOSTNAME}.END.$(date +%Y%m%d%H%M%S)

rm -f ${tmp}-*
exit 0
