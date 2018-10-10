#!/bin/bash
#
# KOJINATESEIKYUSHO_SAKUSEI.CGI : 施設請求書発行CGI
#
# Usage : KOJINATESEIKYUSHO_SAKUSEI.CGI namefile
#
# Written by j.aoyagi(hands lab.inc)

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/KEIRI/CGI/KOJINATESEIKYUSHO_SAKUSEI.INI &> /dev/null

# ログ
[ ! -e /home/hands/E-LIFE/KEIRI/TRACE_LOG/${today} ] && mkdir /home/hands/E-LIFE/KEIRI/TRACE_LOG/${today}
exec 2> /home/hands/E-LIFE/KEIRI/TRACE_LOG/${today}/LOG.$(basename ${0}).${HOSTNAME}.${current_time}; set -xv

#ゴミtmpの消去
rm -f $tmp-*

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-param_name)"
[ -n "${MODE}" ] || MODE="init"

# -------------------------------------------------------------
# 処理の分岐
case "${MODE}" in
  # --------------
  # 初めてこの画面開いたときの(ドロップダウンのみ表示)
  init )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.DISPLAY ${tmp}-param_name ${tmp}-check /dev/null /dev/null /dev/null > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 表示ボタンを押したとき(繰越)
  kurikoshi_init )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search /dev/null /dev/null > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 表示ボタンを押したとき
  search )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search /dev/null /dev/null > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 計算(請求画面のみ)
  keisan )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.KOJINKAKUTEI.KEISAN ${tmp}-param_name > ${tmp}-result
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search /dev/null ${tmp}-result > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 請求選択更新(請求・繰越共通)
  seikyu_koushin | seikyu_koushin_kurikoshi )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.SEIKYU_SENTAKU ${tmp}-param_name > ${tmp}-result
        # 登録の結果がどうであれ画面更新をさせるのでサーチ
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search /dev/null ${tmp}-result > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 仮確定、仮確定解除 ボタンのみ更新
  karikakutei | karikakutei_kaijyo )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.KARIKAKUTEI ${tmp}-param_name > ${tmp}-result
        # 登録の結果がどうであれ画面更新をさせるのでサーチ
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search /dev/null ${tmp}-result > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 請求書出力(請求書のはきだし先は隠れたフレーム)
  print | print_ryosyu )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
      ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.PRINT ${tmp}-param_name > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
  # --------------
  # 当月確定
  tougetsukakutei )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.TOUGETSUKAKUTEI ${tmp}-param_name > ${tmp}-result
        # 登録の結果がどうであれ画面更新をさせるのでサーチ
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search /dev/null ${tmp}-result > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # 確定解除
  kakutei_kaijyo )
    ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check
    if [ $(gyo ${tmp}-check) -ne 0 ] ; then
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.KAIJO ${tmp}-param_name > ${tmp}-result
        # 登録の結果がどうであれ画面更新をさせるのでサーチ
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.SEARCH ${tmp}-param_name > ${tmp}-search
        ${cgi_dir}/KOJINATESEIKYUSHO_SAKUSEI.DISPLAY ${tmp}-param_name ${tmp}-check ${tmp}-search /dev/null ${tmp}-result > ${tmp}-html
    else
      ${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI/SIGN_IN.CGI ${tmp}-param_name > ${tmp}-html
    fi
  ;;
  # --------------
esac
# -------------------------------------------------------------

# -------------------------------------------------------------
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
# -------------------------------------------------------------


# -------------------------------------------------------------
# HTMLファイルを表示する
if [ -e "$tmp-html" ];then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
else
  cat $tmp-html2
fi
# -------------------------------------------------------------

rm -f ${tmp}-*
exit 0

