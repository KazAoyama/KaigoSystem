#!/bin/bash
#
# AJAX_NYUKYOSHA_KENSAKU.CGI:
#　カナ検索による対象者を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by K.Aoyama / 2014.01.02

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/CAREPLAN/CGI/CAREPLAN.INI &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv


#=== 初期化 ===
tmp=/var/tmp/${$}


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

Nyukyoshamei=$(nameread Nyukyoshamei $tmp-name)
CareManager=$(nameread CareManager $tmp-name)
Shisetsu=$(nameread Shisetsu $tmp-name)
KensakuDate=$(nameread KensakuDate $tmp-name)
Kaigo=$(nameread Kaigo $tmp-name)

cat ${home_dir}/TBL/JYUUGYOUIN_MASTER/USER_MASTER  > $tmp-user_mst

curdate=$KensakuDate

# 介護保険情報
cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_KAIGOHOKEN         |
if [ "$Kaigo" = "yobo" ] ; then
   awk '$23<="'$curdate'"&&"'$curdate'"<=$28&&$3>="1"&&$3<="2"'
else
   awk '$23<="'$curdate'"&&"'$curdate'"<=$28&&$3>="3"&&$3<="7"'
fi |
self 1                                         |
LANG=C sort -k1,1             > $tmp-taishou_kaigo

cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_KYOTAKU_JIGYOUSHO  |
awk '$3=="'$Shisetsu'"'                                   |
tee $tmp-service_riyousha                                 |
awk '$6<="'$curdate'"&&"'$curdate'"<$7{print $1,$4,$5}'   |
LANG=C sort -k2,2                                         |
join2 +_ key=2 $tmp-user_mst                              |
if [ -z "${CareManager}" -o "${CareManager}" = "_" -o "${CareManager}" = "0" ] ; then
cat -
else
awk '$2=="'${CareManager}'"' 
fi |
delf 2                                                    |
LANG=C sort -k1,1 > $tmp-user_caremanager



cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER |
awk '$(NF-2)!="9"'     |
join0 key=1 $tmp-service_riyousha |
join0 key=1 $tmp-taishou_kaigo    |
if [ -z "$Nyukyoshamei" -o "$Nyukyoshamei" = "_" ] ; then
  cat -
else
  awk '$2~/'$Nyukyoshamei'/'
fi |
# 1:利用者ID 2:利用者名
awk '{print $1,$2,$3}' |
LANG=C sort -k1,1       |
# 1:利用者ID 2:自事業所担当ケアマネ名 3:他事業所担当ケアマネ名 4:利用者名 5:利用者名カナ
if [ -z "${CareManager}" -o "${CareManager}" = "_" -o "${CareManager}" = "0" ] ; then
join2 +_ key=1 $tmp-user_caremanager
else
join1 key=1 $tmp-user_caremanager
fi |
tee $work_dir/caremane_kensaku  |
# 1:利用者ID 2:自事業所担当ケアマネ名 3:他事業所担当ケアマネ名 4:利用者名 5:利用者名カナ 6:ケアマネ名 
awk '{if($2=="_"){$5=$3}else{$5=$2};print $0}'          |
# 1:利用者ID 2:利用者名 3:ケアマネ名
LANG=C sort -k9,9   |
delf 2 3 9          |
rank                >  $tmp-kensaku_riyousha
# 1:利用者ID 2:利用者名 4:ケアマネージャ名

cp $tmp-kensaku_riyousha $work_dir/kensaku_riyousha

cat << FIN > $tmp-calsed_data
FIN

###########################################################################
# calsedデータの整形
cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result


awk '/\<nyukyosha_start\>/,/\<nyukyosha_end\>/' ${html_dir}/GEKKAN_RIYOU_KEIKAKU_IKKATSU_INSATSU.html |
tee $tmp-ajax_test |
calsed -f $tmp-calsed_data_result -                     |
mojihame -l###RIYOUSHA###  - $tmp-kensaku_riyousha |
sed 's/###SPACE###/ /'     > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
