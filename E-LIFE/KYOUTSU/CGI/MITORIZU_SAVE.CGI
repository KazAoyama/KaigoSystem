#!/bin/bash
#
# MITORIZU_SAVE.CGI 描画した住宅見取図の保存CGI
#
# written by AOI Daichi (d-aoi@usp-lab.com) 2015/4/28
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
   ASSESSMENT_KAIGO )
     save_dir=${home_dir}/CAREPLAN/POMPA/CAREPLAN_KAIGO/${riyoushaid}
     ;;
   ASSESSMENT_YOBO )
     save_dir=${home_dir}/CAREPLAN/POMPA/CAREPLAN_YOBO/${riyoushaid}
     ;;
   ASSESSMENT_HOUMONKAIGO )
     save_dir=${home_dir}/HOUMONKAIGO/POMPA/HOUMONKAIGO/ASSESSMENT/${riyoushaid}
     ;;
   KOBETSU_ENJO_KEIKAKU )
     save_dir=${home_dir}/HOUMONKAIGO/POMPA/HOUMONKAIGO/KOBETSU/${riyoushaid}
     ;;
   * )
     save_dir=${home_dir}/KYOUTSU/POMPA/${riyoushaid}
     ;;
esac

mkdir -p $save_dir

cat $tmp-name 	|
sed 's/,$//'	> ${save_dir}/mitorizu-$no

#######################################
# 終了処理
rm -f $tmp-*
exit 0
