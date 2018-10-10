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
   if [ -s ${kyoutsu_dir}/${Riyoushaid}/JISSEKI_SHOKAI ] ; then
       cat ${kyoutsu_dir}/${Riyoushaid}/JISSEKI_SHOKAI |
       awk '$3$4<"'${Nengetsu}'"' |
       ## 本番データを取り込む
       cat - ${kyoutsu_dir}/IKOU/HOUMONKAIGO/${Riyoushaid}/JISSEKI_SHOKAI  |
       LANG=C sort -k1,4 |
       getlast 1 4       > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/JISSEKI_SHOKAI
   else
       cat ${kyoutsu_dir}/IKOU/HOUMONKAIGO/${Riyoushaid}/JISSEKI_SHOKAI > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/JISSEKI_SHOKAI
   fi
#done

exit 0

