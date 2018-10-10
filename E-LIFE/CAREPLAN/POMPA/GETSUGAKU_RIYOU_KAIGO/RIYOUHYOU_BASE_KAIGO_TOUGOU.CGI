#!/bin/bash
#
# RIYOUHYOUBEPPYOU_KAIGO_TOUGOU.CGI:
#      利用票別表情報を統合する
#

kyoutsu_dir="/home/hands/E-LIFE/CAREPLAN/POMPA/GETSUGAKU_RIYOU_KAIGO"

## 利用者ID
Riyoushaid=$1
Nengetsu=$2

#ls ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_KAIGO/ |
#while read dir ; do
   mkdir -p ${kyoutsu_dir}/TOUGOU/${Riyoushaid}
   if [ -s ${kyoutsu_dir}/${Riyoushaid}/RIYOUHYOU_BASE_KAIGO ] ; then
       cat ${kyoutsu_dir}/${Riyoushaid}/RIYOUHYOU_BASE_KAIGO |
       awk '$2$3<"'${Nengetsu}'"' |
       ## 本番データを取り込む
       cat - ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_KAIGO/${Riyoushaid}/RIYOUHYOU_BASE_KAIGO  |
       LANG=C sort -k1,3 > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/RIYOUHYOU_BASE_KAIGO
   else
       cat ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_KAIGO/${Riyoushaid}/RIYOUHYOU_BASE_KAIGO > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/RIYOUHYOU_BASE_KAIGO
   fi
#done

exit 0

