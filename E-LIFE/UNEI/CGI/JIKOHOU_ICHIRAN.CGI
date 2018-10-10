#!/bin/bash
#
# JIKOHOU_ICHIRAN.CGI : 基本情報一覧CGI
# 
# 
#
# Written by E.Okuda :2013/11/20

exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null
# 変数設定
tmp=/var/tmp/${$}

# ディレクトリ設定
home_dir="/home/hands"
sys_dir="${home_dir}/E-LIFE"
app_dir="${home_dir}/E-LIFE/UNEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
ch_cgi_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI"
#-------------------------------------------------------------

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)

#-------------------------------------------------------------
#------------------------------------------------------------
# パラメーターの取得
dd bs=${CONTENT_LENGTH}        |
cgi-name -d_ -i_               |
LANG=C sort                    > $tmp-name
cookie-name                    |
LANG=C sort                    > ${tmp}-cookie
#------------------------------------------------------------
#------------------------------------------------------------
# 処理モードの決定
eval $(name-source ${tmp}-cookie)
eval $(name-source $tmp-name)
[ -z "${MODE}" ] && MODE="init"
#------------------------------------------------------------


#------------------------------------------------------------
upl key=1 ${tmp}-cookie $tmp-name > $tmp-name.new0
cp -p $tmp-name $tmp-name_origin
mv -f $tmp-name.new0 $tmp-name

#-------------------------------------------------------------
# 処理モードの決定
MODE="$(nameread "MODE" ${tmp}-param_name)"

[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
[ ! -z "${NYUUINGAIHAKUID}" ] &&  MODE="search"
#-------------------------------------------------------------

#--i-----------------------------------------------------------
# 処理の分岐
case "$MODE" in

  # -------------------------
  # 初期表示
  init)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
     ${cgi_dir}/JIKOHOU_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check > $tmp-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  # -------------------------

  #--------------------------
  #検索する場合
  search)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/JIKOHOU_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/JIKOHOU_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------

  #身元引受人情報エクセル出力
  mimoto_print)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/JIKOHOU_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/JIKOHOU_ICHIRAN.EXCEL ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;

  #加算給付同意情報エクセル出力
  kasankyuufu_print)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/JIKOHOU_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KIHONJYOUHOU_KASANKYUUHU.EXCEL ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;

    #認定期間情報エクセル出力
  nintei_print)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/JIKOHOU_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KIHONJYOUHOU_NINTEI.EXCEL ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;

    #感染症情報エクセル出力
  kansenshou_print)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/JIKOHOU_ICHIRAN.SEARCH ${tmp}-param_name               > ${tmp}-search
      ${cgi_dir}/KIHONJYOUHOU_KANSENSHOU.EXCEL ${tmp}-param_name ${tmp}-check ${tmp}-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
esac
#-------------------------------------------------------------

# 返す？
if [ "$(gyo ${tmp}-check)" -ne 0 ];then
  :
else
  message="権限がありません"
cat <<- FIN > $tmp-html2
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
fi


# HTMLファイルを表示する
if [ -e "$tmp-html" ];then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
else
  cat $tmp-html2
fi


#終了
rm -f $tmp-*

exit 0
