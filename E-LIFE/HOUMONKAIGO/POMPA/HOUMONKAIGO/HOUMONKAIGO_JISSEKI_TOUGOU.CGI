#!/bin/bash
#
# TOUGOU_KAIGODO_INFO.CGI:
#      介護度情報を統合する
#

kyoutsu_dir="/home/hands/E-LIFE/HOUMONKAIGO/POMPA/HOUMONKAIGO"

## 利用者ID
Riyoushaid=$1
Nengetsu=$2

#ls ${kyoutsu_dir}/IKOU/HOUMONKAIGO/ |
#while read dir ; do
   mkdir -p ${kyoutsu_dir}/TOUGOU/${Riyoushaid}
   if [ -s ${kyoutsu_dir}/${Riyoushaid}/HOUMONKAIGO_JISSEKI ] ; then
       cat ${kyoutsu_dir}/${Riyoushaid}/HOUMONKAIGO_JISSEKI |
       awk '$2$3<"'${Nengetsu}'"' |
       ## 本番データを取り込む
       cat - ${kyoutsu_dir}/IKOU/HOUMONKAIGO/${Riyoushaid}/HOUMONKAIGO_JISSEKI  |
       LANG=C sort -k1,6 > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/HOUMONKAIGO_JISSEKI
   else
       cat ${kyoutsu_dir}/IKOU/HOUMONKAIGO/${Riyoushaid}/HOUMONKAIGO_JISSEKI > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/HOUMONKAIGO_JISSEKI
   fi
#done

exit 0

