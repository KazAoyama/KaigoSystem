#!/bin/bash
#
# TOUGOU_KAIGODO_INFO.CGI:
#      介護度情報を統合する
#

kyoutsu_dir="/home/hands/E-LIFE/CAREPLAN/POMPA/GETSUGAKU_RIYOU_YOBO"

## 利用者ID
Riyoushaid=$1
Nengetsu=$2

#ls ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/ |
#while read dir ; do
   mkdir -p ${kyoutsu_dir}/TOUGOU/${Riyoushaid}
   if [ -s ${kyoutsu_dir}/${Riyoushaid}/KAIGODO_INFO ] ; then
       cat ${kyoutsu_dir}/${Riyoushaid}/KAIGODO_INFO |
       awk '$2$3<"'${Nengetsu}'"' |
       ## 本番データを取り込む
       cat - ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/${Riyoushaid}/KAIGODO_INFO  |
       LANG=C sort -k1,4 > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/KAIGODO_INFO
   else
       cat ${kyoutsu_dir}/IKOU/GETSUGAKU_RIYOU_YOBO/${Riyoushaid}/KAIGODO_INFO > ${kyoutsu_dir}/TOUGOU/${Riyoushaid}/KAIGODO_INFO
   fi
#done

exit 0

