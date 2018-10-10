#!/bin/bash -vx
#
# KAZOKUKOSEI_SAVE.CGI 描画した家族構成図の保存CGI
#
# written by AOI Daichi (d-aoi@usp-lab.com) 2015/3/19
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/KYOUTSU/CGI/KYOUTSU.INI &> /dev/null
mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

###########################################
# 変数の定義

#######################################
# POSTされたデータの読み込み
if [ ! -z "$CONTENT_LENGTH" ] ; then
	dd bs=$CONTENT_LENGTH	|
	cgi-name -d_ -i_        > $tmp-name
else
	touch $tmp-name
fi


# データ番号の取得
no=$(nameread NO $tmp-name)
riyoushaid=$(nameread Riyoushaid $tmp-name)
riyoucgi=$(nameread RiyouCGI $tmp-name)

#######################################
# データの出力
case "${riyoucgi}" in
   IKOU_ASSESSMENT )
     save_dir=${home_dir}/UNEI/POMPA/IKOU_ASSESSMENT/${riyoushaid}
     ;;
   KANGO_KAIGO_YOUYAKU )
     save_dir=${home_dir}/SHISETSU_KAIGOKIROKU/POMPA/KANGO_KAIGO_YOUYAKU/${riyoushaid}
     ;;
   RIYOUSHA_KIHON_JOUHOU )
     save_dir=${home_dir}/CAREPLAN/POMPA/CAREPLAN_YOBO/${riyoushaid}
     ;;
   * )
     save_dir=${home_dir}/KYOUTSU/POMPA/${riyoushaid}
     ;;
esac

mkdir -p $save_dir

cat $tmp-name 	|
sed 's/,$//'	> ${save_dir}/kazokukosei-$no

#######################################
# 終了処理
rm -f $tmp-*
exit 0
