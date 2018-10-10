#!/bin/bash
#
# AJAX_KANA_KENSAKU.CGI:
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

# ログインUSER名と施設の取得（仮）
self 1 2 ${home_dir}/TBL/JYUUGYOUIN_MASTER/USER_MASTER > $tmp-user_mst

#curdate=$(mdate today | self 1)
curdate=$(nameread "HDKENSAKUDATE" $tmp-name)
kensakudate=$(nameread "KENSAKUDATE" $tmp-name)
shisetsu=$(nameread "SHISETSU" $tmp-name)
caremanager=$(nameread "CAREMANAGER" $tmp-name)
jigyousho=$(nameread "JIGYOUSHO" $tmp-name)

# 施設
self 1 6 ${data_dir}/UNEI/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS |
if [ "$shisetsu" = "0" ] ; then
  cat -
else
  awk '$1=="'$shisetsu'"'
fi |
self 2 |
LANG=C sort -k1,1 > $tmp-shisetsu_riyousha

# 利用者のケアマネ情報
cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_KYOTAKU_JIGYOUSHO  |
awk '$(NF-2)!="9"'                     |
awk '$3=="'$jigyousho'"'                |
awk '"'$curdate'"<$7{print $1,$4,$5}'   |
if [ "$caremanager" = "0" ] ; then
  cat -
else
  awk '$2=="'$caremanager'"'
fi |
LANG=C sort -k2,2                                         |
join2 +_ key=2 $tmp-user_mst                              |
delf 2                                                    |
LANG=C sort -k1,1 > $tmp-user_caremanager

[ -s $tmp-user_caremanager ] || echo "_" "_" "_" > $tmp-user_caremanager

cp $tmp-user_caremanager $work_dir/user_caremanager

# ユーザ居宅支援事業所紐付け
cat ${data_dir}/UNEI/RIYOUSHA/JIGYOUSHO_RIYOUSHA_STATUS   |
awk '"'$curdate'"<$4&&$1=="'${jigyousho}'"{print $2}'  |
LANG=C sort -k1,1                      > $tmp-jigyousho_user

cp $tmp-jigyousho_user $work_dir/jigyousho_user

KAIGODO=$(nameread "KAIGODO" $tmp-name)
# 介護保険情報
cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_KAIGOHOKEN         |
if [ "$KAIGODO" = "YOBO" ] ; then
   awk '$23<="'$curdate'"&&"'$curdate'"<=$28&&$3>="1"&&$3<="2"'
else
   awk '$23<="'$curdate'"&&"'$curdate'"<=$28&&$3>="3"&&$3<="7"'
fi |
self 1                                         |
LANG=C sort -k1,1             > $tmp-taishou_kaigo

cp $tmp-taishou_kaigo $work_dir/taishoukaigo

# カナの取得
KANA=$(nameread "KANA" $tmp-name)

  [ -z "${KANA}" -o "${KANA}" = "_" ] && echo "@" "@" "@" >  $tmp-taishousha_name_select_head

#cat ${home_dir}/TBL/RIYOUSHA/RIYOUSHA_MASTER |
cat ${data_dir}/UNEI/RIYOUSHA/RIYOUSHA_MASTER |
awk '$(NF-2)!="9"'     |
join0 key=1 $tmp-taishou_kaigo |
join0 key=1 $tmp-jigyousho_user  |
awk '{print $1,$2,$3}'  |
LANG=C sort -k1,1       |
# ケアマネ検索
if [ "$caremanager" = "0" ] ; then
# 2014/6/27 外部ケアマネ外す対応
  join1 key=1 $tmp-user_caremanager
else
  join1 key=1 $tmp-user_caremanager
fi |
# 施設選択
if [ "$shisetsu" = "0" ] ; then
  cat -
else
  join1 key=1 $tmp-shisetsu_riyousha
fi |
awk '{if($2=="_"){$6=$3}else{$6=$2};print $0}'          |
delf 2 3                                      |
#LANG=C sort -k1,1 |
# 50音対応(2014/6/23)
LANG=C sort -k3,3 |
tee $work_dir/riyousha_kensaku |
# 1:利用者ID 2:利用者名 3:利用者名カナ 4:ケアマネージャ名

if [ "${KANA}" = "11" ] ; then
    awk '{print $1,$2,$4}'    > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE11### active
###CHECK11### checked
FIN

  elif [ "${KANA}" = "1" ] ; then
    awk '$3~/^ア/||$3~/^イ/||$3~/^ウ/||$3~/^エ/||$3~/^オ/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE1### active
###CHECK1### checked
FIN

  elif [ "${KANA}" = "2" ] ; then
    awk '$3~/^カ/||$3~/^キ/||$3~/^ク/||$3~/^ケ/||$3~/^コ/||$3~/^ガ/||$3~/^ギ/||$3~/^グ/||$3~/^ゲ/||$3~/^ゴ/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE2### active
###CHECK2### checked
FIN

  elif [ "${KANA}" = "3" ] ; then
    awk '$3~/^サ/||$3~/^シ/||$3~/^ス/||$3~/^セ/||$3~/^ソ/||$3~/^ザ/||$3~/^ジ/||$3~/^ズ/||$3~/^ゼ/||$3~/^ゾ/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE3### active
###CHECK3### checked
FIN

  elif [ "${KANA}" = "4" ] ; then
    awk '$3~/^タ/||$3~/^チ/||$3~/^ツ/||$3~/^テ/||$3~/^ト/||$3~/^ダ/||$3~/^ヂ/||$3~/^ヅ/||$3~/^デ/||$3~/^ド/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE4### active
###CHECK4### checked
FIN

  elif [ "${KANA}" = "5" ] ; then
    awk '$3~/^ナ/||$3~/^ニ/||$3~/^ヌ/||$3~/^ネ/||$3~/^ノ/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE5### active
###CHECK5### checked
FIN

  elif [ "${KANA}" = "6" ] ; then
    awk '$3~/^ハ/||$3~/^ヒ/||$3~/^フ/||$3~/^ヘ/||$3~/^ホ/||$3~/^バ/||$3~/^ビ/||$3~/^ブ/||$3~/^ベ/||$3~/^ボ/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE6### active
###CHECK6### checked
FIN

  elif [ "${KANA}" = "7" ] ; then
    awk '$3~/^マ/||$3~/^ミ/||$3~/^ム/||$3~/^メ/||$3~/^モ/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE7### active
###CHECK7### checked
FIN

  elif [ "${KANA}" = "8" ] ; then
    awk '$3~/^ヤ/||$3~/^ユ/||$3~/^ヨ/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE8### active
###CHECK8### checked
FIN

  elif [ "${KANA}" = "9" ] ; then
    awk '$3~/^ラ/||$3~/^リ/||$3~/^ル/||$3~/^レ/||$3~/^ロ/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE9### active
###CHECK9### checked
FIN

  elif [ "${KANA}" = "10" ] ; then
    awk '$3~/^ワ/||$3~/^ヲ/||$3~/^ン/{print $1,$2,$4}'   > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE10### active
###CHECK10### checked
FIN

  else
    awk '{print $1,$2,$4}'    > $tmp-taishousha_name_select_head

cat << FIN > $tmp-calsed_data
###KACTIVE0### active
###CHECK11### checked
FIN

  fi


###########################################################################
# calsedデータの整形
cat $tmp-calsed_data  |
sed 's/_/@/g' -        > $tmp-calsed_data_result

cat << FIN >> $tmp-calsed_data_resule
###HDKENSAKUDATE### $curdate
###KENSAKUDATE### $KensakuDate
FIN

awk '/\<kensaku_kana_start\>/,/\<kensaku_kana_end\>/' ${html_dir}/KYOTAKUSHIEN_MENU_KAIGO2.html |
tee $tmp-ajax_test |
calsed -f $tmp-calsed_data_result -                     |
mojihame -l###TAISHOUSHA###  - $tmp-taishousha_name_select_head |
sed 's/###SPACE###/ /'     > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
