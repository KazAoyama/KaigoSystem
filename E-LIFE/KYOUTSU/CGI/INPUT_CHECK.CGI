#!/bin/bash
#
# INPUT_CHECK.CGI
# 共通入力チェック用CGI
#
# Usage
# INPUT_CHECK.CGI param1 param2 param3
# param1:対象となる値
# param2:何のチェックをするか(現状 9 を入力すると数値チェック、sだと文字チェック*未実装)
# param3:文字数チェック(option)
# res:問題ない場合はOKを返す。エラーがある場合はエラーメッセージを返す
# Written by K.Aoyama :20140309

#--------------------------------------------------------------
# ログ
source /home/hands/E-LIFE/KYOUTSU/CGI/KYOUTSU.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).$HOSTNAME.$(date +%Y%m%d) ; set -xv
#--------------------------------------------------------------

#--------------------------------------------------------------
rm -f $tmp-*
#--------------------------------------------------------------

#--------------------------------------------------------------
function error_exit {
  rm -f $tmp-*
  exit 0
}
#--------------------------------------------------------------

#--------------------------------------------------------------
# 変数の定義
hensudata=$1
setteidata=$2
mojisudata=$3
shisetsu=$4

result="OK"

case "${setteidata}" in
  date )
    # 入力された8桁数字が日付かどうか
    isdate ${hensudata} || result="入力された値が日付ではありません"
  ;;
  kakutei )
    # 入力された8桁日付が請求確定後のデータかどうか
    kakutei_nengetsu="$(LANG=C sort -k1,1 /DATA/E-LIFE/SEIKYU/SHISETSU/SEIKYU_KAKUTEI/SEIKYU_KAKUTEI.${shisetsu} | getlast 1 1 | self 2)"
    kakunin_nengetsu="$(echo "${hensudata}" | self 1.1.6)"
    [ "${kakutei_nengetsu}" -lt "${kakunin_nengetsu}" ] || result="請求確定月以前のデータを入力することができません"
  ;;
  9 )
    # 数値チェック
    CHECK=$(echo "$hensudata" | awk '/[^0-9_-]/ {print $0}')
    if [ ! -z $CHECK ] ; then
       result="数値以外の値が入っています"
    fi
  ;;
  * )
    ## 文字数チェック
    if [ ! -z "$mojisudata" ]; then
       echo "$hensudata" | awk '{print length($1),"'$mojisudata'"}'   |
       awk '{if($1>$2){$3="文字数オーバーです"}else{$3="OK"};print $3}' > $tmp-result
       result=$(self 1 $tmp-result)
    fi
  ;;
esac

echo $result

## 終了
rm -f $tmp-*
exit 0
