#!/bin/bash -vx
#
# PUTPARTS_LOAD.CGI 描画した画像の呼び出しCGI
#
# written by AOI Daichi (d-aoi@usp-lab.com) 2015/3/9
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
	cgi-name  		> $tmp-name
else
	touch $tmp-name
fi

# データ番号の取得
no=$(nameread NO $tmp-name)
riyoushaid=$(nameread Riyoushaid $tmp-name)
riyoucgi=$(nameread RiyouCGI $tmp-name)

#######################################
# 出力
case "${riyoucgi}" in
   JIKOHOU_SHOUSAI )
     save_dir=${home_dir}/UNEI/POMPA/JIKOHOU/${riyoushaid}
     ;;
   *)
     save_dir=${home_dir}/KYOUTSU/POMPA/${riyoushaid}
     ;;
esac

echo "Content-type: text/plain"
echo ""
cat ${save_dir}/putparts-$no	

#######################################
# 終了処理
rm -f $tmp-*
exit 0
