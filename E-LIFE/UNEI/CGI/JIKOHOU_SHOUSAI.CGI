#!/bin/bash
#
# JIKOHOU_SHOUSAI.CGI : 個人情報詳細(基本)CGI
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
ch_cgi_dir="${home_dir}/SYSTEM_SETTEI/CGI"
#-------------------------------------------------------------

# パラメーターの取得
dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)

#-------------------------------------------------------------
# 処理モードの決定
MODE="$(nameread "MODE" ${tmp}-param_name)"
[ -z "${MODE}" -o "${MODE}" = "_" ] && MODE="init"
#-------------------------------------------------------------

#--i-----------------------------------------------------------
# 処理の分岐
case "$MODE" in

  # -------------------------
  # 初期表示
#  init)
#    ${cgi_dir}/JIKOHOU_SHOUSAI.DISPLAY ${tmp}-param_name > $tmp-html
#  ;;
  # -------------------------

  #--------------------------
  #init(初期表示)
  init)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
    ${cgi_dir}/JIKOHOU_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-check > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  #検索
  search)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
    ${cgi_dir}/JIKOHOU_SHOUSAI.SEARCH ${tmp}-param_name        > $tmp-search
    ${cgi_dir}/JIKOHOU_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-check $tmp-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;
  #--------------------------
  #登録(更新登録)
  touroku | sakujyo)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
    ${cgi_dir}/JIKOHOU_SHOUSAI.TOUROKU ${tmp}-param_name ${tmp}-param   > ${tmp}-touroku
    ${cgi_dir}/JIKOHOU_SHOUSAI.SEARCH ${tmp}-param_name ${tmp}-touroku  > $tmp-search
    ${cgi_dir}/JIKOHOU_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-check $tmp-search ${tmp}-touroku > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
  ;;

  #--------------------------
  #--------------------------
  #PDF出力
  print)
    ${ch_cgi_dir}/KENGEN_CHECK.CGI ${tmp}-param_name          > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ];then
      ${cgi_dir}/JIKOHOU_SHOUSAI.SEARCH ${tmp}-param_name                          > ${tmp}-search
      ${cgi_dir}/JIKOHOU_SHOUSAI.PDF ${tmp}-param_name ${tmp}-check ${tmp}-search  > $tmp-html 
#    ${cgi_dir}/JIKOHOU_SHOUSAI.DISPLAY ${tmp}-param_name ${tmp}-check $tmp-search > ${tmp}-html
    else
      ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
    fi
#    ${cgi_dir}/JIKOHOU_SHOUSAI.PDF ${tmp}-param_name  > ${tmp}-html

  ;;

  #--------------------------
  #--------------------------
  #登録(更新登録)
#  shinki)
#    ${cgi_dir}/JIKOHOU_SHOUSAI_SHINKI.DISPLAY ${tmp}-param_name  > ${tmp}-html
#  ;;
  #--------------------------
#  #削除
#  edit_image1_delete)
#   [ $MODE == "edit_image1_delete" ] && no="1"
#    ${cgi_dir}/JIKOHOU_SHOUSAI.DELETE_IMAGE $tmp-param_name "$no" > $tmp-data
#    ${cgi_dir}/JIKOHOU_SHOUSAI.DISPLAY $tmp-param_name $tmp-data > $tmp-html
#
#  ;;
#
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

## HTMLの出力
#cat <<FIN | cat - $tmp-html
#Content-Type: text/html; charset=UTF-8;
#
#FIN

# 終了
rm -f ${tmp}-*
exit 0
