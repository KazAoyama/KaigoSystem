#!/bin/bash
#
# KESSHOKU_KAKUTEI.CGI
# 欠食確定CGI
#
# Written by E.Okuda  : 2014/3/25

#--------------------------------------------------------------
# ログ
exec 2> /home/hands/E-LIFE/SHOKUJI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv
# 設定ファイル読込
source  /home/hands/E-LIFE/SHOKUJI/CGI/SHOKUJI.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null
#--------------------------------------------------------------
#--------------------------------------------------------------
# 変数の定義
tmp=/var/tmp/${$}
#namedatai=$1
KakuteiNengetsu=$1
Shisetsu=$2

#KakuteiNengetsu="201401"
#Shisetsu="0001"

#ゴミtmpの消去
rm -f $tmp-*

#--------------------------------------------------------------
#--------------------------------------------------------------
function error_exit {
  rm -f $tmp-*
  exit 0
}
#--------------------------------------------------------------
#--------------------------------------------------------------
# ディレクトリ設定
app_dir="${home_dir}/SHOKUJI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
pompa_dir="${app_dir}/POMPA"
today=$(date +%Y%m%d)
data_dir="/DATA/E-LIFE"
seikyuu_dir=${data_dir}/SEIKYU/SHISETSU/SHOKUJI
#--------------------------------------------------------------

#------------------------------------------------------------
# 検索対象者の絞込み
#----------------------
: > $tmp-riyousha_kesshoku

# 1:シニア
cat ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/01/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU |
# 1:利用者(入居者)ID 2:施設ID     3:建屋 4:居室 5:欠食年月日
# 6:欠食食事         7:入院外泊ID
awk '$2=="'${Shisetsu}'"&&$3=="02"&&$(NF-2)!="9"{print "01",$1}'  |
LANG=C sort -u  >> $tmp-riyousha_kesshoku

# 2:ケア
cat ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/02/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU |
# 1:利用者(入居者)ID 2:施設ID     3:建屋 4:居室 5:欠食年月日
# 6:欠食食事         7:入院外泊ID
awk '$2=="'${Shisetsu}'"&&$3=="02"&&$(NF-2)!="9"{print "02",$1}'   |
LANG=C sort -u  >> $tmp-riyousha_kesshoku

 [ $(plus ${PIPESTATUS[@]}) -eq 0 ] || : > $tmp-err

# 欠食データがあれば欠食確定の処理をする
if [ -s $tmp-riyousha_kesshoku ] ; then
  cat $tmp-riyousha_kesshoku |
  while read TATEYA NYUUKYOSHA ; do

    [ ! -s $tmp-${TATEYA}_result ] && : > $tmp-${TATEYA}_result
    #---------------
    # 前月確定済みの欠食データ
    #----------------
     last_month=$(mdate "${KakuteiNengetsu}"/-1)
    if [ -s ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/${TATEYA}/${last_month}/RIYOUSHA_KESSHOKU_KAKUTEI ] ; then
       cat ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/${TATEYA}/${last_month}/RIYOUSHA_KESSHOKU_KAKUTEI |
       awk '$1=="'${NYUUKYOSHA}'"{print $0}'  |
# 1:入居者ID 2:年月日 3:食事番号(朝 昼 夜) 4:欠食情報
  # 欠食情報フィールドにて1や2だったらKSへ置き換え
       awk '{if($4=="1"||$4=="2"){print $2,$3,"KS","@"}
        else if($4~/KESSHOKU/){print $2,$3,"KESSHOKU_3","@"}
        else{print $2,$3,"@","@"}
            }' > $tmp-kakutei_nengetsu_kakutei_kesshoku_${NYUUKYOSHA}
# 1:年月日 2:食事番号 3:欠食情報 4:"@"
    else
       : > $tmp-kakutei_nengetsu_kakutei_kesshoku_${NYUUKYOSHA}
    fi
 
   #------------------
   # 確定する月の欠食データ
   #------------------

    if [ -s ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/${TATEYA}/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU ] ; then
       cat ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/${TATEYA}/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU |
# 1:利用者(入居者)ID 2:施設ID     3:建屋 4:居室 5:欠食年月日
# 6:欠食食事         7:入院外泊ID
       # 入居者データの絞り込み
       awk '$1=="'${NYUUKYOSHA}'"&&$2=="'${Shisetsu}'"&&$3=="'${TATEYA}'"&&$(NF-2)!="9"{print $5,$6,"KS",$7}' |
       LANG=C sort -k1,1 > $tmp-kesshoku_data_before_${NYUUKYOSHA}
# 1:欠食年月日 2:欠食食事  3:KS 4:入院外泊有無

          if [ -s $tmp-kesshoku_data_before_${NYUUKYOSHA} ] ; then
            # 月データの取得
            mdate "${KakuteiNengetsu}"m |
            tarr  |
            awk '{print $1,"1"}' > $tmp-month_asa_${NYUUKYOSHA}
# 1:年月日 2:"1"
            awk '{print $1,"2"}' $tmp-month_asa_${NYUUKYOSHA} > $tmp-month_hiru_${NYUUKYOSHA}
            awk '{print $1,"3"}' $tmp-month_asa_${NYUUKYOSHA} > $tmp-month_yoru_${NYUUKYOSHA}

            cat $tmp-month_asa_${NYUUKYOSHA} $tmp-month_hiru_${NYUUKYOSHA} $tmp-month_yoru_${NYUUKYOSHA} |
            LANG=C sort  |
# 1:年月日 2:食事(1～3)
            loopj -d"@" num=2 - $tmp-kesshoku_data_before_${NYUUKYOSHA}  > $tmp-kesshoku_mikakutei_data_${NYUUKYOSHA}
          
            # 欠食データがあれば欠食処理
            if [ -s $tmp-kesshoku_mikakutei_data_${NYUUKYOSHA} -a -s $tmp-kakutei_nengetsu_kakutei_kesshoku_${NYUUKYOSHA} ] ; then
              cat $tmp-kesshoku_mikakutei_data_${NYUUKYOSHA} $tmp-kakutei_nengetsu_kakutei_kesshoku_${NYUUKYOSHA} |
              LANG=C sort -u
            elif [ -s $tmp-kesshoku_mikakutei_data_${NYUUKYOSHA} ] ; then
              cat $tmp-kesshoku_mikakutei_data_${NYUUKYOSHA}
            fi |
            delf 4 |
            tateyoko      |
            # KSが3つで欠食1回とカウント
            sed 's/KS KS KS/1 2 KESSHOKU_3/g' |
            sed 's/KS KS/1 2/g' |
            sed 's/KS/1/g' > $tmp-data_2_${NYUUKYOSHA}

            # 検索月データだけにする
            cat $tmp-data_2_${NYUUKYOSHA} |
            tateyoko        |
            awk '$1~/^'${search_month}'/{print $0}'   |
            tateyoko        > $tmp-data_3_${NYUUKYOSHA}
          fi

          if [ -s $tmp-data_3_${NYUUKYOSHA} ] ; then
            kesshoku_kaisuu=$(sed 's/[ \t]/\n/g' $tmp-data_3_${NYUUKYOSHA} | grep KESSHOKU_3 | wc -l)

            for i in $(seq 1 $kesshoku_kaisuu) ;do
              cat $tmp-data_3_${NYUUKYOSHA} |
              sed 's/KESSHOKU_3/KESSHOKU'${i}'/'${i}'' |
              tateyoko  > $tmp-data_for${i}_${NYUUKYOSHA}
            done
            cat $tmp-data_for*_${NYUUKYOSHA} |
            LANG=C sort -k1,2  |
            getfirst 1 2        |
            awk '{print "'${NYUUKYOSHA}'",$0}' >> $tmp-${TATEYA}_result
          fi
     fi
   done
fi

 [ $(plus ${PIPESTATUS[@]}) -eq 0 ] || : > $tmp-err

#--------------------------------------------
# データ更新

  mkdir -p ${pompa_dir}/${Shisetsu}/01/${KakuteiNengetsu}
  mkdir -p ${pompa_dir}/${Shisetsu}/02/${KakuteiNengetsu}
  mkdir -p ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/01/${KakuteiNengetsu} 
  mkdir -p ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/02/${KakuteiNengetsu} 

# 更新する対象があったら
if [ -s $tmp-01_result ] ; then
  # 既にファイルがあったらバックアップとる
  [ -s ${pompa_dir}/${Shisetsu}/01/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU_KAKUTEI ] && cp -p ${pompa_dir}/${Shisetsu}/01/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU_KAKUTEI ${pompa_dir}/${Shisetsu}/01/${KakuteiNengetsu}/bk.RIYOUSHA_KESSHOKU_KAKUTEI
else
  : > $tmp-01_result
fi

# 更新する対象があったら
if [ -s $tmp-02_result ] ; then
  [ -s ${pompa_dir}/${Shisetsu}/02/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU_KAKUTEI ] && cp -p ${pompa_dir}/${Shisetsu}/02/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU_KAKUTEI ${pompa_dir}/${Shisetsu}/02/${KakuteiNengetsu}/bk.RIYOUSHA_KESSHOKU_KAKUTEI
else
  : > $tmp-02_result
fi

  [ -e $tmp-01_result ] && cp -p $tmp-01_result ${pompa_dir}/${Shisetsu}/01/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU_KAKUTEI
  [ -e $tmp-01_result ] && cp -p $tmp-01_result ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/01/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU_KAKUTEI
  [ -e $tmp-02_result ] && cp -p $tmp-02_result ${pompa_dir}/${Shisetsu}/02/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU_KAKUTEI
  [ -e $tmp-02_result ] && cp -p $tmp-02_result ${data_dir}/SEIKYU/SHISETSU/SHOKUJI/${Shisetsu}/02/${KakuteiNengetsu}/RIYOUSHA_KESSHOKU_KAKUTEI

#cp $tmp-* /home/hands/work/okuda

## 終了
rm -f $tmp-*
exit 0
