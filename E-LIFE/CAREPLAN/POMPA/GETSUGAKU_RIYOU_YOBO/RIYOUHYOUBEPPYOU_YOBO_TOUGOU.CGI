#!/bin/bash
#
# RIYOUHYOUBEPPYOU_YOBO_TOUGOU.CGI:
#      利用票別表情報を統合する
#

kyoutsu_dir="/home/hands/E-LIFE/CAREPLAN/POMPA/GETSUGAKU_RIYOU_YOBO"

Riyoushaid=$1
Nengetsu=$2

#ls ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/ |
#while read dir ; do
   mkdir -p ${kyoutsu_dir}/TOUGOU/${Riyoushaid}
   if [ -s ${kyoutsu_dir}/${Riyoushaid}/RIYOUHYOUBEPPYOU_YOBO ] ; then
       cat ${kyoutsu_dir}/${Riyoushaid}/RIYOUHYOUBEPPYOU_YOBO |
       awk '$2$3<"'${Nengetsu}'"' |
       ## 本番データを取り込む
       cat - ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/${Riyoushaid}/RIYOUHYOUBEPPYOU_YOBO  |
       LANG=C sort -k1,3 > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/RIYOUHYOUBEPPYOU_YOBO
   else
       cat ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/${Riyoushaid}/RIYOUHYOUBEPPYOU_YOBO > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/RIYOUHYOUBEPPYOU_YOBO
   fi
#done

exit 0

