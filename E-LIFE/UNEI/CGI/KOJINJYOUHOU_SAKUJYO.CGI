#!/bin/bash
#
# KOJINJYOUHOU_SAKUJYO.CGI
# 個人情報削除
# 緊急時、登録された入居者(契約者)そのものを削除するためのCGI

#
# Written by E.Okuda (Tokyu-hands.co.jp) :20140420

#--------------------------------------------------------------
# ログ
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null

# 変数設定
tmp=/var/tmp/${$}

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/UNEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA/RIYOUSHA"
input_dir="${app_dir}/INPUT"
kanri_dir="/DATA/E-LIFE/UNEI/KANRI/RIYOUSHA"
data_dir="/DATA/E-LIFE/UNEI/RIYOUSHA"
#--------------------------------------------------------------

#--------------------------------------------------------------
rm -f $tmp-*
#--------------------------------------------------------------

#--------------------------------------------------------------
function error_exit {
  message="$1"
  echo "message ${message}"
  echo "result ng"
  cp -p $tmp-* /home/hands/work/okuda
  rm -f $tmp-*
  exit 1
}
function error_unlock {
  message="$1"
  cat $tmp-target-table |
  while read table base ;do
    rm -f $tmplock_dir/$base.lock
  : ;done
  error_exit ${message}
}
#--------------------------------------------------------------

#################################################################################################
# 変更するのはここから
#################################################################################################

#--------------------------------------------------------------
# 変数の定義
#namedata=$1
#checkdata=$2
RIYOUSHAID=$1
USERID=$2
# 必要な値の取得
eval $(name-source ${namedata})
#--------------------------------------------------------------
# チェックがNGだったら 
if [ $(awk '$1=="result"{print $2}' "${checkdata}") = "ng" ] ; then
  cat ${checkdata}
# チェックがokだったら
else
#--------------------------------------------------------------
##########################
# 入力データのチェック
##########################

# 利用者データがなければエラー
#  RIYOUSHAID="$(nameread "RIYOUSHAID" ${namedata})"
 [ -z "${RIYOUSHAID}" -o "${RIYOUSHAID}" != "_" ] && error_exit "利用者を指定してください。"

# 削除対象テーブル一覧
#
# 利用者テーブル
# 利用者基本
# 利用者契約
# 利用者契約金
# 利用者利用料
# 利用者特販
# 施設利用者テーブル

#--------------------------------------------------------------

# 利用者テーブル
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/RIYOUSHA_MASTER  |
delf NF-2/NF                                                        |
awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                  > $tmp-riyousha_master_input

# 利用者基本
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/RIYOUSHA_KIHON   |
delf NF-2/NF                                                        |
awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                  > $tmp-riyousha_kihon_input



# 利用者契約
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/RIYOUSHA_KEIYAKU            > $tmp-riyousha_keiyaku
if [ -s $tmp-riyousha_keiyaku ] ; then
  cat $tmp-riyousha_keiyaku                                                    |
  delf NF-2/NF                                                                 |
  awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                           > $tmp-riyousha_keiyaku_input
else
  :
fi

# 利用者特販
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/RIYOUSHA_TOKUHAN            > $tmp-riyousha_tokuhan
if [ -s $tmp-riyousha_tokuhan ] ; then 
  cat $tmp-riyousha_tokuhan                                                    |
  delf NF-2/NF                                                                 |
  awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                           > $tmp-riyousha_tokuhan_input
else
  :
fi

# 利用者利用料
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/RIYOUSHA_RIYOURYOU          > $tmp-riyousha_riyouryou
if [ -s $tmp-riyousha_riyouryou ] ; then
  cat $tmp-riyousha_riyouryou                                                  |
  delf NF-2/NF                                                                 |
  awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                           > $tmp-riyousha_riyouryou_input
else
  :
fi

# 利用者契約金
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/RIYOUSHA_KEIYAKUKIN         > $tmp-riyousha_keiyakukin
if [ -s $tmp-riyousha_keiyakukin ] ; then
  cat $tmp-riyousha_keiyakukin                                                 |
  delf NF-2/NF                                                                 |
  awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                           > $tmp-riyousha_keiyakukin_input
else
  :
fi

# 施設利用者テーブル
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/SHISETSU_RIYOUSHA_STATUS    > $tmp-shisetsu_riyousha_status
if [ -s $tmp-shisetsu_riyousha_status ] ; then
  cat $tmp-shisetsu_riyousha_status                                            |
  delf NF-2/NF                                                                 |
  awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                           > $tmp-shisetsu_riyousha_status_input
else
  :
fi

# 事業所利用者ステータス
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/JIGYOUSHO_RIYOUSHA_STATUS   > $tmp-jigyousho_riyousha_status
if [ -s $tmp-jigyousho_riyousha_status ] ; then
  cat $tmp-jigyousho_riyousha_status                                           |
  delf NF-2/NF                                                                 |
  awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                           > $tmp-jigyousho_riyousha_status_input
else
  :
fi

# 包括利用者ステータス
awk '$1=="'${RIYOUSHAID}'"{print $0}' ${pompa_dir}/HOUKATSU_RIYOUSHA_STATUS    > $tmp-houkatsu_riyousha_status
if [ -s $tmp-houkatsu_riyousha_status ] ; then
  cat $tmp-houkatsu_riyousha_status                                            |
  delf NF-2/NF                                                                 |
  awk '{print $0,"9","'${cur_time}'","'${USERID}'"}'                           > $tmp-houkatsu_riyousha_status_input
else
  :
fi

[ $(plus ${PIPESTATUS[@]}) -eq 0 ] || error_exit

### INPUTデータの作成
### 後で見てわかりやすいように書く
#echo "${INPUT_TEXT1} _"           |
### 加工済みのデータだけを元にして一旦selfする
#self NF 1  NF NF NF NF            |
# 1:ID         2:入力内容 3:入力者 4:入力者名 5:最終更新日時
# 6:最終更新者
# 最終的に更新情報を代入
#awk '{$1="'${data_id}'";
#      $3="'${USER_ID}'";
#      $4="'${USER_NAME}'";
#      $5="'${cur_time}'";
#      $6="'${USER_ID}'";
#      print}'                     > $tmp-sample_input
### ここでのtmpファイル名は更新時に使うので注意すること
#--------------------------------------------------------------
#--------------------------------------------------------------

# 更新対象ファイルのリスト化

# 1:ファイルのパス 2:ファイル名
## ロックファイル作成用テーブル
## POMPAファイルがPOMPA直下でなく、店などのサブディレクトリ配下にいる場合には
## 1フィールド目が「${TEN_CODE}/SAMPLE_DATA」などになる
cat <<- FIN | LANG=C sort -u > $tmp-target-table
RIYOUSHA_KIHON RIYOUSHA_KIHON
RIYOUSHA_MASTER RIYOUSHA_MASTER
FIN

[ -s $tmp-riyousha_keiyaku_input ] && echo "RIYOUSHA_KEIYAKU RIYOUSHA_KEIYAKU" >> $tmp-target-table
[ -s $tmp-riyousha_keiyakukin_input ] && echo "RIYOUSHA_KEIYAKUKIN RIYOUSHA_KEIYAKUKIN" >> $tmp-target-table
[ -s $tmp-riyousha_riyouryou_input ] && echo "RIYOUSHA_RIYOURYOU RIYOUSHA_RIYOURYOU" >> $tmp-target-table
[ -s $tmp-riyousha_tokuhan_input ] && echo "RIYOUSHA_TOKUHAN RIYOUSHA_TOKUHAN" >> $tmp-target-table
[ -s $tmp-shisetsu_riyousha_input ] && echo "SHISETSU_RIYOUSHA_STATUS SHISETSU_RIYOUSHA_STATUS" >> $tmp-target-table
[ -s $tmp-jigyousho_riyousha_input ] && echo "JIGYOUSHO_RIYOUSHA_STATUS JIGYOUSHO_RIYOUSHA_STATUS" >> $tmp-target-table
[ -s $tmp-houkatsu_riyousha_input ] && echo "HOUKATSU_RIYOUSHA_STATUS HOUKATSU_RIYOUSHA_STATUS" >> $tmp-target-table

# 1:tmpファイル名 2:更新ファイル名 3:キーフィールド 4:更新時間フィールド 5:全体列数
# 6:POMPA場所     7:INPUT場所

## 更新ファイルの作成とチェック用のテーブル
## 6/7フィールド目は、アプリ間連携で別アプリの配下にあるINPUTを更新する場合用
cat <<- FIN > $tmp-koushin_pompa
riyousha_master RIYOUSHA_MASTER 1 6 7 ${pompa_dir} ${input_dir}
riyousha_kihon RIYOUSHA_KIHON  1 20 21 ${pompa_dir} ${input_dir}
FIN

[ -s $tmp-riyousha_keiyaku_input ] && echo "riyousha_keiyaku RIYOUSHA_KEIYAKU 2 23 24 ${pompa_dir} ${input_dir}" >> $tmp-koushin_pompa
[ -s $tmp-riyousha_keiyakukin_input ] && echo "riyousha_keiyakukin RIYOUSHA_KEIYAKUKIN 5 23 24 ${pompa_dir} ${input_dir}" >> $tmp-koushin_pompa
[ -s $tmp-riyousha_riyouryou_input ] && echo "riyousha_riyouryou RIYOUSHA_RIYOURYOU 5 20 21 ${pompa_dir} ${input_dir}" >> $tmp-koushin_pompa
[ -s $tmp-riyousha_tokuhan_input ] && echo "riyousha_tokuhan RIYOUSHA_TOKUHAN 5 16 17 ${pompa_dir} ${input_dir}" >> $tmp-koushin_pompa
[ -s $tmp-shisetsu_riyousha_input ] && echo "shisetsu_riyousha SHISETSU_RIYOUSHA_STATUS 7 10 11 ${pompa_dir} ${input_dir}" >> $tmp-koushin_pompa
[ -s $tmp-jigyousho_riyousha_input ] && echo "jigyousho_riyousha JIGYOUSHO_RIYOUSHA_STATUS 3 6 7 ${pompa_dir} ${input_dir}" >> $tmp-koushin_pompa
[ -s $tmp-houkatsu_riyousha_input ] && echo "houkatsu_riyousha HOUKATSU_RIYOUSHA_STATUS 3 8 9 ${pompa_dir} ${input_dir}" >> $tmp-koushin_pompa

#--------------------------------------------------------------
cat $tmp-target-table |
awk '$1!~/*tbl_dir*/{print $0}' |
while read file_name base ;do
 cp ${pompa_dir}/${file_name} ${pompa_dir}/back/${file_name}.${today}
done

#################################################################################################
# 変更するのはここまで
#################################################################################################

#--------------------------------------------------------------
# データロック
$function_dir/FUNCTION.LOCK_CHECK $tmp-target-table
if [ $? -ne 0 ]; then
 # エラー（ロックに失敗）
  error_unlock "ロック処理失敗"
 ## error_exit ではなく error_unlock である点に注意！
fi
#--------------------------------------------------------------
#--------------------------------------------------------------
# 更新版作成
# POMPAと指定されたキー項目をつかってマージする
cat $tmp-koushin_pompa         |
while read input_name file_name sort_key time_key retu_no pompa_dir_name input_dir_name ; do
  cat $tmp-${input_name}_input |
  if [ -e ${pompa_dir_name}/${file_name} ] ; then
    cat ${pompa_dir_name}/${file_name} -
  else
    cat -
  fi |
  LANG=C sort -k1,${sort_key} -k${time_key},${time_key} |
  getlast 1 ${sort_key}        > $tmp-${input_name}_new
done
#--------------------------------------------------------------
#--------------------------------------------------------------
# 列数チェック
cat $tmp-koushin_pompa         |
while read input_name file_name sort_key time_key retu_no pompa_dir_name input_dir_name ; do
  [ "$(retu $tmp-${input_name}_new)" != "${retu_no}" ] && : > $tmp-err
  [ "$(retu $tmp-${input_name}_new | gyo)" != "1" ] && : > $tmp-err
  [ "$(awk 'NF!="'${retu_no}'"' $tmp-${input_name}_new | gyo)" != "0" ] && : > $tmp-err
done
[ -e $tmp-err ] && error_unlock "列数エラー"
## error_exit ではなく error_unlock である点に注意！
#--------------------------------------------------------------

#--------------------------------------------------------------
# バッチ側で処理中なら更新させずに落とす
#[ -e ${tmptmplock_dir}/BATCH.SAMPLE_LOCK ] && error_unlock "システム処理中"
#--------------------------------------------------------------

#--------------------------------------------------------------
# 更新
cat $tmp-koushin_pompa         |
while read input_name file_name sort_key time_key retu_no pompa_dir_name input_dir_name ; do
  mkdir -p ${pompa_dir_name}
  mkdir -p ${input_dir_name}
  mkdir -p ${input_dir_name}/${today}/RIYOUSHA

  mv -f $tmp-${input_name}_input ${input_dir_name}/${today}/RIYOUSHA/${file_name}.${cur_time}.$(basename $0).$$
  mv -f $tmp-${input_name}_new ${pompa_dir_name}/${file_name}
done
#--------------------------------------------------------------

#--------------------------------------------------------------
# ロックの解除
cat $tmp-target-table |
while read table base ;do
  rm -f $tmplock_dir/$base.lock
: ;done
#--------------------------------------------------------------
 cp -p ${pompa_dir}/RIYOUSHA_MASTER ${data_dir}/RIYOUSHA_MASTER
 cp -p ${pompa_dir}/RIYOUSHA_KIHON ${data_dir}/RIYOUSHA_KIHON
 cp -p ${pompa_dir}/RIYOUSHA_TOKUHAN ${data_dir}/RIYOUSHA_TOKUHAN
 cp -p ${pompa_dir}/RIYOUSHA_RIYOURYOU ${data_dir}/RIYOUSHA_RIYOURYOU
 cp -p ${pompa_dir}/RIYOUSHA_KEIYAKU ${data_dir}/RIYOUSHA_KEIYAKU
 cp -p ${pompa_dir}/RIYOUSHA_KEIYAKUKIN ${data_dir}/RIYOUSHA_KEIYAKUKIN
 cp -p ${pompa_dir}/SHISETSU_RIYOUSHA_STATUS ${data_dir}/SHISETSU_RIYOUSHA_STATUS
 cp -p ${pompa_dir}/JIGYOUSHO_RIYOUSHA_STATUS ${data_dir}/JIGYOUSHO_RIYOUSHA_STATUS
 cp -p ${pompa_dir}/HOUKATSU_RIYOUSHA_STATUS ${data_dir}/HOUKATSU_RIYOUSHA_STATUS
  echo "result sakujyo_ok" 
fi


## 終了
rm -f $tmp-*
exit 0
