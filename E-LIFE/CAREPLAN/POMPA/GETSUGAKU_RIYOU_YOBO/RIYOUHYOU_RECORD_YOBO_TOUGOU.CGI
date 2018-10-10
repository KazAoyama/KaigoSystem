#!/bin/bash
#
# RIYOUHYOUBEPPYOU_RECORD_YOBO_TOUGOU.CGI:
#      利用票別表レコード情報を統合する
#

kyoutsu_dir="/home/hands/E-LIFE/CAREPLAN/POMPA/GETSUGAKU_RIYOU_YOBO"

Riyoushaid=$1
Nengetsu=$2

#ls ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/ |
#while read dir ; do
   mkdir -p ${kyoutsu_dir}/TOUGOU/${Riyoushaid}
   if [ -s ${kyoutsu_dir}/${Riyoushaid}/RIYOUHYOU_RECORD_YOBO ] ; then
       cat ${kyoutsu_dir}/${Riyoushaid}/RIYOUHYOU_RECORD_YOBO |
       awk '$3$4<"'${Nengetsu}'"' |
       ## 本番データを取り込む
       cat - ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/${Riyoushaid}/RIYOUHYOU_RECORD_YOBO  |
       LANG=C sort -k1,4 > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/RIYOUHYOU_RECORD_YOBO
   else
       cat ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/${Riyoushaid}/RIYOUHYOU_RECORD_YOBO > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/RIYOUHYOU_RECORD_YOBO
   fi
#done

exit 0

