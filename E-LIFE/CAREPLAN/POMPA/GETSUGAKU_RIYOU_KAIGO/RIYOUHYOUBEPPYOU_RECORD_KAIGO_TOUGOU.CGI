#!/bin/bash
#
# RIYOUHYOUBEPPYOU_RECORD_KAIGO_TOUGOU.CGI:
#      利用票別表レコード情報を統合する
#

kyoutsu_dir="/home/hands/E-LIFE/CAREPLAN/POMPA/GETSUGAKU_RIYOU_KAIGO"

Riyoushaid=$1
Nengetsu=$2

#ls ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_KAIGO/ |
#while read dir ; do
   mkdir -p ${kyoutsu_dir}/TOUGOU/${Riyoushaid}
   if [ -s ${kyoutsu_dir}/${Riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO ] ; then
       cat ${kyoutsu_dir}/${Riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO |
       awk '$3$4<"'${Nengetsu}'"' |
       ## 本番データを取り込む
       cat - ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_KAIGO/${Riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO  |
       LANG=C sort -k1,6 > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO
   else
       cat ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_KAIGO/${Riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/RIYOUHYOUBEPPYOU_RECORD_KAIGO
   fi
#done

exit 0

