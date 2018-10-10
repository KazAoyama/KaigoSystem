#!/bin/bash
#
# RIYOUHYOUBEPPYOU_RECORD_YOBO_TOUGOU.CGI:
#      利用票別表レコード情報を統合する
#

kyoutsu_dir="/home/hands/E-LIFE/HOUMONKAIGO/POMPA/HOUMONKAIGO"

## 利用者ID
Riyoushaid=$1
Nengetsu=$2

#ls ${kyoutsu_dir}/IKOU/HOUMONKAIGO/ |
#while read dir ; do
   mkdir -p ${kyoutsu_dir}/TOUGOU/${Riyoushaid}
   if [ -s ${kyoutsu_dir}/${Riyoushaid}/HOUMONKAIGO_RIYOUHYOUBEPPYOU_YOBO ] ; then
       cat ${kyoutsu_dir}/${Riyoushaid}/HOUMONKAIGO_RIYOUHYOUBEPPYOU_YOBO |
       awk '$3$4<"'${Nengetsu}'"' |
       ## 本番データを取り込む
       cat - ${kyoutsu_dir}/IKOU/HOUMONKAIGO/${Riyoushaid}/HOUMONKAIGO_RIYOUHYOUBEPPYOU_YOBO  |
       LANG=C sort -k1,6 > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/HOUMONKAIGO_RIYOUHYOUBEPPYOU_YOBO
   else
       cat ${kyoutsu_dir}/IKOU/HOUMONKAIGO/${Riyoushaid}/HOUMONKAIGO_RIYOUHYOUBEPPYOU_YOBO > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/HOUMONKAIGO_RIYOUHYOUBEPPYOU_YOBO
   fi
#done

exit 0

