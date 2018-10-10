#!/bin/bash
#
# AJAX_KIHONJYOUHOU_ICHIRAN.CGI: 施設、建屋、フロア、ユニット、居室のオプションタグ群を取得して返す。
#                                Ajax による使用を想定。
#
#
# Written by E.Okuda / 2013.11.21

#Functions{{{############################################################
# エラー終了
function error_exit {
  rm -f ${tmp}-*
  exit 1
}
#}}}Functions############################################################

#=== ログ ===
exec 2> /home/hands/E-LIFE/UNEI/APLOG/LOG.$(basename ${0}).${HOSTNAME}.$(date "+%Y%m%d"); set -xv

# 設定ファイル読込
source /home/hands/.bashrc &> /dev/null
source /home/hands/E-LIFE/UNEI/CGI/UNEI.INI &> /dev/null

#=== 初期化 ===
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*


html_dir="${home_dir}/UNEI/HTML"
pompa_dir="${home_dir}/UNEI/POMPA"
kengen_dir="/home/hands/E-LIFE/TBL/KENGEN_KANRI"

cgi_name="KIHONJYOUHOU_ICHIRAN.CGI"

work_dir="${home_dir}/UNEI/WORK"

# 渡ってきたデータを取得
if [ ${CONTENT_LENGTH:-0} -gt 0 ]; then
  dd bs=${CONTENT_LENGTH} |
  cgi-name -d_ -i_
else
  :
fi > $tmp-name
#---

# MODEの取得
MODE=$(nameread "MODE" $tmp-name)
GAMEN=$(nameread "GAMEN" $tmp-name)
userid=$(nameread "userid" $tmp-name)

  Shisetsu=$(nameread "Shisetsu" $tmp-name)
  Tateya=$(nameread "Tateya" $tmp-name)
  Floor=$(nameread "Floor" $tmp-name)
  Unit=$(nameread "Unit" $tmp-name)
  Kyoshitsu=$(nameread "Kyoshitsu" $tmp-name)
  Nyuukyosha=$(nameread "Nyuukyosha" $tmp-name)
  JIGYOUSHO=$(nameread "JIGYOUSHO" $tmp-name)
  shisetsu=$(nameread "shisetsu" $tmp-name)
  Caremaneger=$(nameread "Caremaneger" $tmp-name)
  NyuuingaihakuKikanFrom=$(nameread "NyuuingaihakuKikanFrom" $tmp-name)
  NyuuingaihakuKikanTo=$(nameread "NyuuingaihakuKikanTo" $tmp-name)
  JIGYOUSHODISP=$(nameread "JIGYOUSHODISP" $tmp-name)
  TaikyoshaHyouji=$(nameread "TaikyoshaHyouji" $tmp-name)

  [ -z "${GAMEN}" ] && GAMEN="_"
  [ -z "${Shisetsu}" ] && Shisetsu="_"
  [ -z "${Tateya}" ] && Tateya="_"
  [ -z "${Floor}" ] && Floor="_"
  [ -z "${Unit}" ] && Unit="_"
  [ -z "${Kyoshitsu}" ] && Kyoshitsu="_"
  [ -z "${Nyuukyosha}" ] && Nyuukyosha="_"
  [ -z "${JIGYOUSHO}" ] && JIGYOUSHO="_"
  [ -z "${shisetsu}" ] && shisetsu="_"
  [ -z "${Caremaneger}" ] && Caremaneger="_"
# 小文字のshisetsuは最上段でせんたくしたログイン施設

  # モードが変更になったら初期化
  [ "${MODE}" = "Shisetsu" ] && Kyoshitsu="_"
  [ "${MODE}" = "Shisetsu" ] && Nyuukyosha="_"

# 事業所に値が入っている、すなわち表示されている場合
#if [ "${MODE}" = "Jigyousho" -o "${JIGYOUSHO}" != "_" ] ; then
 if [ "${JIGYOUSHODISP}" != "none" ] ; then
    # 自事業所
    cat ${tbl_dir}/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
    # 1:グループ事業所ＩＤ 2:グループ事業所名 3:電話番号 4:住所   5:金融機関コード
    # 6:金融機関支店コード 7:口座区分         8:口座番号 9:口座名
    awk '$(NF-2)!="9"{print $1,$2}'         |
    awk 'BEGIN{print "_ 全て"}{print $0}'   |
    awk 'BEGIN{print "9999","選択しない"}{print $0}'  |
    awk '{if($1=="'${JIGYOUSHO}'"){print $0,"selected"}
        else{print $0,"_"}
        }'  > $tmp-jigyousho_name
    # 1:グループ事業所ＩＤ 2:グループ事業所名 3:Selected


    # ケアマネリスト用意--------------------------------------------------------------------------------
    # 事業所所属の人
    cat ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU ${tbl_dir}/JYUUGYOUIN_MASTER/EXTRA_USER_SHISETSU       |
    awk '$2=="'${JIGYOUSHO}'"&&$6=="1"&&$(NF-2)!="9"{print $0}'   |
    LANG=C sort -u |
    # 1:従業員ID   2:施設ID 3:建屋ID 4:フロア 5:ユニットID
    # 6:居宅or訪問 7:役職   8:なんとか番号

    # 従業員情報と紐付ける
    join1 key=1 <(awk '$(NF-2)!=9' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_KIHON) - |
    # 1:従業員ID 2:従業員名 3:従業員名カナ 4:勤務期間FROM 5:勤務期間TO
    # 6:ID       7:PASS     8:削除フラグ   9:更新日時     10:ユーザーID
    # 11:施設ID  12:建屋ID  13:フロア      14:ユニットID  15:事業所詳細
    # 16:役職'   17:ﾅﾝﾄｶ番号
   awk '$4<="'${today}'"&&$5>="'${today}'"&&$8!="9"{print $1,$2}' |
   awk 'BEGIN{print "_ 全て"}{print $0}'   |
   awk '{if($1=="'${Caremaneger}'"){print $0,"selected"}
        else{print $0,"_"}
        }' > $tmp-caremane_name 
   # 1:ケアマネID 2:ケアマネ名
   #-------------------------------------------------------------------------------------------------
   echo "###JIGYOUSHODISP### " > $tmp-calsed
else
   #事業所を非表示のままにする処理
   echo "###JIGYOUSHODISP### none" > $tmp-calsed
   : > $tmp-jigyousho_name
   : > $tmp-caremane_name
fi
#　これで事業所、ケアマネプルダウンは完成
#-------------------------------------------------------------------------------------------------



## 事業所名、ケアマネ名が入っているなら、それでまず入居者名を限定------------------------
# そうしてつくったリストから施設・建屋・フロア・ユニットでしぼることになる
# そのリスト作成
# 事業所の選択があったら以下の事業所利用者リストつくる(個別の事業所を選択しているなら)
if [ ${JIGYOUSHO} != "_" ] && [ ${JIGYOUSHO} != "9999" ] ;then
  awk '$1=="'${JIGYOUSHO}'"{print $0}' ${pompa_dir}/RIYOUSHA/JIGYOUSHO_RIYOUSHA_STATUS |
  if [ "${TaikyoshaHyouji}" == "0" ] ; then
    awk '$4>="'${today}'" && $(NF-2)!="9"{print $2}'  > ${tmp}-jigyousho_ari
  elif [ "${TaikyoshaHyouji}" == "2" ] ; then
    awk '$4<="'${today}'" && $(NF-2)!="9"{print $2}'  > ${tmp}-jigyousho_ari
  else
    awk '$(NF-2)!="9"{print $2}'  > ${tmp}-jigyousho_ari
  fi
  # ケアマネの選択があったらさらにしぼる
  if [ ${Caremaneger} != "_" ]  && [ ${Caremaneger} != "" ] ;then
     awk '$4=="'${Caremaneger}'"{print $1}'  ${pompa_dir}/RIYOUSHA/RIYOUSHA_KYOTAKU_JIGYOUSHO |
     LANG=C sort -u |
     join0 key=1 -  ${tmp}-jigyousho_ari
  else
     cat ${tmp}-jigyousho_ari
  fi                                       > ${tmp}-jigyousho_shozoku
  #これが事業所、ケアマネの選択があった場合に限定されるメンバー
  #このメンバーで絞る

  #事業所だけにしか所属がないメンバー求める
  self 6  ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS   |
  LANG=C sort -u                                           > ${tmp}-shisetsu_mem
  awk '{print $1,"_","_","_","_",$2,$3,$4,$5,$6,$7}'  ${pompa_dir}/RIYOUSHA/JIGYOUSHO_RIYOUSHA_STATUS |
  LANG=C sort -k6,6                                           |
  join0 +ng key=6 ${tmp}-shisetsu_mem  - 2>&1   > /dev/null   |
  #このメンバーと施設利用者マージ
  cat -   ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS      |
  LANG=C sort -k6,6                                           |
  join0 key=6 ${tmp}-jigyousho_shozoku -                      |
  LANG=C sort




#  LANG=C sort  -k6,6 ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS  |
#  join0 key=6 ${tmp}-jigyousho_shozoku -                                   |
#  LANG=C sort  


  # 事業所の選択がないか"選択しない"なら、事業所のみの利用者と施設利用者をマージ
else
  #事業所だけにしか所属がないメンバー求める
  self 6  ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS   |
  LANG=C sort -u                                           > ${tmp}-shisetsu_mem
  awk '{print $1,"_","_","_","_",$2,$3,$4,$5,$6,$7}'  ${pompa_dir}/RIYOUSHA/JIGYOUSHO_RIYOUSHA_STATUS |
  LANG=C sort -k6,6                                           |
  join0 +ng key=6 ${tmp}-shisetsu_mem  - 2>&1   > /dev/null    |
  #このメンバーと施設利用者マージ
  cat -   ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS      |
  tee /var/tmp/kikain_0 |
  LANG=C sort

fi   |
#有効時期に限定
#基本情報一欄の場合は本日の入居者
if [ "${GAMEN}" = "_" ] ;then
#  awk '$7<="'${today}'" && $8>="'${today}'" && $(NF-2)!="9"'  > ${tmp}-shisetsu_riyousha_status_filtered
# ajaxで事業所指定、事業所契約終了者のみにした際の制御を変更（2015/9/16）
  if [ "${TaikyoshaHyouji}" == "0" ] && [ "${JIGYOUSHO}" == "_" -o "${JIGYOUSHO}" == "9999" ] ; then
#  if [ "${TaikyoshaHyouji}" == "0" ] ; then
    awk '$8>="'${today}'" && $(NF-2)!="9"'  > ${tmp}-shisetsu_riyousha_status_filtered
# ajaxで事業所指定、事業所契約終了者のみにした際の制御を変更（2015/9/16）
  elif [ "${TaikyoshaHyouji}" == "2" ] && [ "${JIGYOUSHO}" == "_" -o "${JIGYOUSHO}" == "9999" ] ; then
#  elif [ "${TaikyoshaHyouji}" == "2" ] ; then
    awk '$8<="'${today}'" && $(NF-2)!="9"'  > ${tmp}-shisetsu_riyousha_status_filtered
  else
    awk '$(NF-2)!="9"'  > ${tmp}-shisetsu_riyousha_status_filtered
  fi

#入院外泊情報の場合は検索期間内の入居者

elif [ "${GAMEN}" = "NYUUINGAIHAKU" ] ;then
  from_day=$(echo ${NyuuingaihakuKikanFrom} | tr -d  "/" )
  [ "${from_day}" = "" -o "${from_day}" = "_" ] && from_day="00000000"
  to_day=$(echo ${NyuuingaihakuKikanTo} | tr -d  "/" )
  [ "${to_day}" = "" -o "${to_day}" = "_" ] && to_day="99999999"
  
  awk '$7<="'${to_day}'" && $8>="'${from_day}'"' > ${tmp}-shisetsu_riyousha_status_filtered  
fi

cp ${tmp}-shisetsu_riyousha_status_filtered $work_dir/shisetsu_riyousha_status_filtered

###############以下施設名以下の処理#############################################################################################
  

  # 施設名はログインユーザーの権限のある施設を取得
  cat ${kengen_dir}/USER_KENGEN/${userid}.USER_KENGEN    |
# 1:userid 2:SHISETSU_ID 3:KENGEN_GROUP 4:appID 5:MENU_NAME 6:DROPDOWN_STATUS 7:CGI_NAME 8:RINK_STATUS 9:CGI_STATUS 10:登録日時
  # APPIDが3のもの
  awk '$4=="3"{print $0}'             |
  LANG=C sort -u -k2,2n               |
  self 2                            >  $tmp-kengenari-shisetsu

   # すでにメンバーが限定されているなら、それに応じて施設も限定--------------------------------------
   cat ${tmp}-shisetsu_riyousha_status_filtered              |
   self 1                                                    |
   LANG=C sort -u                                            > ${tmp}-fitered_shisetsu
   #------------------------------------------------------------------------------------------------
   # 上位を選択していたらshisetsuは"_"
   [ "${MODE}" = "Jigyousho" -o  "${MODE}" = "Caremaneger" ] && Shisetsu="_"  
 
   # 施設名はログインユーザーの権限のある施設を取得
   if [ "$(head -1 $tmp-kengenari-shisetsu)" = "0000" -o "${JIGYOUSHO}" = "9999" ] ; then
    cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON              | 
    self 1 2 
   else
    cat $tmp-kengenari-shisetsu                                |
    join1 key=1 ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON -    |
    self 1 2 
   fi |
   #フィルターかかった施設があるなら絞り込む
   join0 key=1 ${tmp}-fitered_shisetsu -                       |
   #事業所が"選択しない"またはそもそも事業所の表示がないなら、選択肢に"全て"を追加
#   if [ ${JIGYOUSHO} = "_" ] || [ ${JIGYOUSHO} = "9999" ] ;then
#      cat -
#   else
      awk 'BEGIN{print "_ 全て"}{print $0}' |
#   fi      |
   #事業所選択しない(9999)以外なら施設外の表示を追加
   if [ "${JIGYOUSHO}" != "9999" ] ;then
     cat - <(echo "00 施設外")                             
   else
     cat -
   fi                                                         |
   #施設が選択されてたら"selected"  
   awk '{if($1=="'${Shisetsu}'"){print $1,$2,"selected"} 
         else{print $1,$2,"_"}
        }'                               > $tmp-shisetsu_name

 #基本情報一覧の表示画面じゃないならそんな面倒なことはしない(選択不可として上書きする)
 if [ "${GAMEN}" != "_" ] ; then
   echo "${Shisetsu}"                                      |
   join1 key=1 - ${tbl_dir}/SHISETSU_MASTER/SHISETSU_KIHON |
   self 1 2           > $tmp-shisetsu_name
 fi

   #候補リストが空欄だった場合（候補が存在しない場合）施設リストは空欄にする
  if [ ! -s ${tmp}-fitered_shisetsu  ] ;then
    : > $tmp-shisetsu_name
  fi

 #

#############################################################

     #事業所を選択しないを選ぶことで、強制的に施設名から「全て」が消えて、その時点の先頭の選択肢に移ることがある。
     #その場合Shisetsuを設定してやる必要がある。
     #その場合は上までの処理でselectedになっているものがないはず
     select_check=$(awk '$3=="selected"' $tmp-shisetsu_name | gyo)
     [ "${select_check}" -eq 0 ] && Shisetsu=$(head -1 $tmp-shisetsu_name | self 1)
#---
# 建屋一覧----------------------------------------------------------------------------------------------
#---
  # 施設が選択されていたら制限する
  if [ "${Shisetsu}" != "_" ] ; then



#    #ログイン者の所属施設と所属建屋
#    shozokushisetsu=$(awk '$1=="'${userid}'"{print $2}' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU )
#    shozokutateya=$(awk '$1=="'${userid}'"{print $3}' ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU )
#    # 今回変更したのが建屋より上位で、選択施設が所属施設と同じで、所属建屋が存在するならば、所属建屋を選択建屋とする
#    #　フロアはケア、シニアとも共通の数字があったりするから,上位をすべてチェック
#    [ "${MODE}" == "Jigyousho" -o "${MODE}" == "Caremaneger" -o "${MODE}" == "Shisetsu" ]  && [ "${shozokushisetsu}" -eq "${Shisetsu}" -a "${shozokutateya}" != "_" ] && Tateya="${shozokutateya}"
#  
      cat ${tbl_dir}/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR    |
    # 1:施設ID 2:建屋ID 3:フロア
      awk '$1=="'${Shisetsu}'"{print $2}'                     |
      LANG=C sort |
      uniq |
      join1 key=1 ${tbl_dir}/SHISETSU_MASTER/TATEYA_NAME -    |
      self 1 3                                               |
   #施設が選択されてたら"selected"
     awk '{if($1=="'${Tateya}'"){print $1,$2,"selected"}
           else{print $1,$2,"_"}
          }' > $tmp-tateya_name
    # 1:建屋ID 2:建屋名
    # 建屋が2つ以上の場合のみ全てという選択をつける←この処理なし！！
    
##    if [ "$(gyo $tmp-tateya_name_kari)" -gt "1"  ]; then
#      cat $tmp-tateya_name_kari |
#      awk 'BEGIN{print "@ 全て"}{print $0}' |
#      awk '{if($1=="'${Tateya}'"){print $1,$2,"selected"}
#          else{print $1,$2,"_"}
#          }'
#    else
#      cat $tmp-tateya_name_kari
#    fi       > $tmp-tateya_name



    #- 
    #施設が選択されていない場合
  else
    echo "_ 全て _" >  $tmp-tateya_name
  fi

   #施設リストが空欄だった場合（候補が存在しない場合）建屋リストは空欄にする  
  if [ ! -s $tmp-shisetsu_name ] ;then
    : > $tmp-tateya_name
  fi 

#---------------------------------------------------------------------------------------------------------------

#  フロア一覧----------------------------------------------------------------------------------------------
  # 今回変更したのがが建屋でなく、上位の変更により変更され建屋の選択肢が一つの場合はその建屋をセット(Tateyaを上書き)
  #
  #  [ "${Tateya}" = "_" -a "$(awk '$1!="@"' $tmp-tateya_name | gyo)" -gt "1" ] && Tateya="$(awk '{print $1}' $tmp-tateya_name | head -1)"
     [ "${MODE}" != "Tateya" -a "$(awk '$1!="_"' $tmp-tateya_name | gyo)" -eq "1" ] && Tateya="$(awk '{print $1}' $tmp-tateya_name | head -1)"
     
  # また、施設が全てだったら、建屋は全てをセット(施設を"全て"に変更したことで建屋が"全て"に変わっった時とか)
     [ "${Shisetsu}" = "_" ] && Tateya="_"

  # 建屋が選択されている（または上の処理で自動設定済み）のとき
  if [ "${Tateya}" != "_" ] ; then
    cat ${tmp}-shisetsu_riyousha_status_filtered                             |
    awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$(NF-2)!="9"{print $3,$3}'  |
    LANG=C sort  |
    uniq  >$tmp-floor_kari
  # 1:フロア 2:フロア

    # フロアが2つ以上の場合のみ全てという選択をつける
    if [ "$(gyo $tmp-floor_kari)" -gt "1"  ]; then
      cat $tmp-floor_kari |
      awk 'BEGIN{print "@ 全て"}{print $0}' |
      awk '{if($1=="'${Floor}'"){print $1,$2,"selected"}
          else{print $1,$2,"_"}
          }' 
    else
      cat $tmp-floor_kari
    fi  > $tmp-floor

  # 建屋が複数から未選択の場合
  else
    echo "_" "全て" "_"
  fi     > $tmp-floor
# 1:フロア番号 2:フロア番号

   #建屋リストが空欄だった場合（候補が存在しない場合）フロアリストは空欄にする
  if [ ! -s $tmp-tateya_name ] ;then
    : > $tmp-floor
  fi
#ー--------------------------------------------------------------------------------------------------------------------------
 
## ユニット取得-------------------------------------------------------------------------------------------------------------
  #--
  # 今回変更したのがフロアでなく、フロア選択肢が"全て"以外で一個になる場合そのフロアを選択していると判断
  [ "${MODE}" != "Floor" -a "$(awk '$1!="_"' $tmp-floor | gyo)" = "1" ] && Floor="$(awk '{print $1}' $tmp-floor | head -1)"
  [ "${Tateya}" = "_" ] && Floor="_"
    # 建屋がシニアの場合ユニットは「なし」
    if [ "${Tateya}" = "01" ] ; then
      echo "_" "なし" > $tmp-unit_name
    # すべてかケアなら判定
    else
    # フロアの指定がある場合(この時は上位の施設と建屋はかならず選択されているはず)
      if [ "${Floor}" != "_" ] ; then
        #cat ${pompa_dir}/RIYOUSHA/SHISETSU_RIYOUSHA_STATUS  |
        cat ${tmp}-shisetsu_riyousha_status_filtered                                            |
        awk '$1=="'${Shisetsu}'"&&$2=="'${Tateya}'"&&$3=="'${Floor}'"&&$(NF-2)!="9"{print $4}'  |
        LANG=C sort                                                                             |
        uniq                                                                                    | 
        join1 key=1  ${tbl_dir}/SHISETSU_MASTER/UNIT_NAME -  |
        self 1 2                                             > $tmp-unit_kari

        # 2つ以上ならば全てという選択肢加える
        if [ "$(gyo $tmp-unit_kari)" -gt "1"  ]; then
          cat $tmp-unit_kari |
          awk 'BEGIN{print "all 全て"}{print $0}' |
          awk '{if($1=="'${Unit}'"){print $1,$2,"selected"}
                else{print $1,$2,"_"}
               }' 
        else
          cat $tmp-unit_kari
        fi                                                                                  
      # フロアが選ばれていない場合
      else        
        echo "_" "全て"                                                             
      fi                                                                                  > $tmp-unit_name
    # 建屋が選ばれていない場合
#    elif [ "${Tateya}" =　"_"  ] ;then
#      echo "all 全て" > $tmp-unit_name

    fi
   #hフロアリストが空欄だった場合（候補が存在しない場合）ユニットは空欄にする
  if [ ! -s $tmp-floor ] ;then
    : > $tmp-unit_name
  fi



#-------------------------------------------------------------------------------------------------------
#   # 今回変更したのがユニットでなく、ユニット選択肢が"全て"以外で一個になる場合(あるいは選択肢なければユニットは全て"_"と判断)そのユニットを選択していると判断
  [ "${MODE}" != "Unit" -a "$(awk '$1!="_"' $tmp-unit_name | gyo)" -le 1 ] && Unit="$(awk '{print $1}' $tmp-unit_name | head -1)"
  [ -z "${Unit}" ] && Unit="_"
# ユニットを個別に選択していなければ
#if [ "${Unit}" = "_"  ] ;then
#   echo "_ 全て "      > ${tmp}-kyoshitsu
#   echo "_ 全て "      > ${tmp}-nyuukyosha
# 以下ユニットを個別に選択している場合（all 全て）の場合含む
#else
if [ ! -s $tmp-jigyousho_name -a "${Shisetsu}" = "_" ] ; then

  echo "_ 全て" > $tmp-kyoshitsu
  echo "_ 全て" > $tmp-nyuukyosha

else
  #　居室・入居者
  # 施設の選択があれば施設内の、そうでなければ全入居者の居室を取得
  cat ${tmp}-shisetsu_riyousha_status_filtered |
  awk '$(NF-2)!="9"' |
  # 施設
  if [ "${Shisetsu}" != "_" -a "${Shisetsu}" != "_" ] ; then
    awk '$1=="'${Shisetsu}'"{print $0}'
  # 1:施設ＩＤ 2:建屋ＩＤ 3:フロア 4:ユニットＩＤ 5:居室Ｎｏ 6:入居者ID
  else
    cat -
  fi |
  
  # 建屋の選択があった場合
  if [ "${Tateya}" != "_" -a "${Tateya}" != "_" ] ; then
    awk '$2=="'${Tateya}'"{print $0}'
  else
    cat -
  fi |
  # 1:施設ＩＤ 2:建屋ＩＤ 3:フロア 4:ユニットＩＤ 5:居室Ｎｏ
  #-
  # フロアの選択があった場合
  if [ "${Floor}" != "_" -a "${Floor}" != "_" ] ; then
    awk '$3=="'${Floor}'"{print $0}'
  else
    cat -
  fi |
  #-
  
  if [ "${Unit}" != "_" ] ; then
    awk '$4=="'${Unit}'"{print $0}'
  else
    cat -
  fi  |
  
  ## 居室の選択があった場合
  #if [ "${Kyoshitsu}" != "_" -a "${Kyoshitsu}" != "@" ] ; then
  #  awk '$5=="'${Kyoshitsu}'"{print $0}'
  #else
  #  cat -
  #fi  |
  # 1:施設ID   2:建屋ID 3:フロア 4:ユニットID 5:居室
  # 6:入居者ID 7:入居日 8:退去日
  self 5 6              |
  LANG=C sort -u -k2,2   >  ${tmp}-riyousha_name
  
  cp -p ${tmp}-riyousha_name $work_dir/riyousha_name

  self 1 2 ${pompa_dir}/RIYOUSHA/RIYOUSHA_MASTER > ${tmp}-riyousha_name_mas
  
  cp -p ${tmp}-riyousha_name_mas $work_dir/riyousha_name_mas

  #入居者名入れる
  join1 key=2 ${tmp}-riyousha_name_mas  ${tmp}-riyousha_name |
  LANG=C sort -u                                               > $tmp-kyoshitsu_kari
  # 1:居室Ｎｏ 2:入居者Ｎｏ 3:入居者名
  
  # 2人以上の場合のみ全てという選択をつける
  if [ "$(gyo $tmp-kyoshitsu_kari)" -gt "1"  ]; then
    cat $tmp-kyoshitsu_kari  |
    LANG=C sort              |
    awk 'BEGIN{print "_ 全て"}{print $1,$1}' |
    uniq                     |
    awk '{if($1=="'${Kyoshitsu}'"){print $1,$2,"selected"}
         else{print $1,$2,"_"}
            }'               > $tmp-kyoshitsu
  
    # 以下入居者リスト
    # 今回変更したのが居室でなく、居室選択肢が"全て"以外で一個になる場合(あるいは選択肢なければ居室は全て"_"と判断)その居室を選択していると判断
    [ "${MODE}" != "Kyoshitsu" -a "$(awk '$1!="_"' $tmp-kyoshitsu | gyo)" -le 1 ] && Kyoshitsu="$(awk '{print $1}' $tmp-kyoshitsu | head -1)"
    #居室のプルダウンで何も選択されていないなら、居室は"全て"として扱う
    [ $(awk '$3=="selected"' $tmp-kyoshitsu | gyo ) = "0" ] && Kyoshitsu="_"
    [ -z "${Kyoshitsu}" ] && Kyoshitsu="_"
    #今回変更したのが入居者より上位、つまり入居者以外の全てで、
    #居室が"_"になったのなら入居者は"_" 
　　[ "${MODE}" != "Kyoshitsu" ] && [ "${Kyoshitsu}" = "_" ] && Nyuukyosha="_"
  
    # 居室の選択があった場合絞り込む
    cat $tmp-kyoshitsu_kari  |
    if [ "${Kyoshitsu}" != "_" -a "${Kyoshitsu}" != "_" ] ; then
      awk '$1=="'${Kyoshitsu}'"{print $0}'
    else
      cat -
    fi > $tmp-nyuukyosha_kari
    #　選択肢あるなら"全て"を頭につける処理
    if [ "$(gyo $tmp-nyuukyosha_kari)" -gt "1"  ]; then
      cat $tmp-nyuukyosha_kari                 |
      awk 'BEGIN{print "_ 全て"}{print $2,$3}' |
      uniq                                     |
      awk '{if($1=="'${Nyuukyosha}'"){print $1,$2,"selected"}
         else{print $1,$2,"_"}
            }'                > $tmp-nyuukyosha
    # 1:居室Ｎｏ 2:居室Ｎｏ
    # 選択肢なければ(1行なら)そのまま表示で
    else
      cat $tmp-nyuukyosha_kari  |
      self 2 3                 > $tmp-nyuukyosha
    fi
  
  #居室の候補が１つならそのまま
  else
    cat $tmp-kyoshitsu_kari |
    awk '{print $1,$1}'     |
    uniq                    > $tmp-kyoshitsu
    cat $tmp-kyoshitsu_kari |
    awk '{print $2,$3}'     > $tmp-nyuukyosha
  fi
  
#fi
   #ユニットリストが空欄だった場合（候補が存在しない場合）居室、入居者は空欄にする
#  if [ ! -s $tmp-unit_name ] ;then
#    : > $tmp-kyoshitsu
#    : > $tmp-nyuukyosha
#  fi
#cp $tmp-* /home/hands/work/okuda
  #施設が「施設外」の場合は入居者リストのみ表示するので作り直し(上書き)
  if [ "${Shisetsu}" == "00" ] ;then
    #施設外のメンバーは建屋、フロア、ユニット、居室が空欄
    awk '$2=="_" && $3=="_" && $4=="_" && $5=="_"' ${tmp}-shisetsu_riyousha_status_filtered |
    self 6                                 | 
    LANG=C sort -k1,1 |
    join1 key=1 ${tmp}-riyousha_name_mas - > $tmp-nyuukyosha_kari
    #　選択肢あるなら"全て"を頭につける処理
    if [ "$(gyo $tmp-nyuukyosha_kari)" -gt "1"  ]; then
      cat $tmp-nyuukyosha_kari                 |
      awk 'BEGIN{print "_ 全て"}{print $1,$2}' |
      awk '{if($1=="'${Nyuukyosha}'"){print $1,$2,"selected"}
         else{print $1,$2,"_"}
            }'                > $tmp-nyuukyosha
    # 1:居室Ｎｏ 2:居室Ｎｏ
    # 選択肢なければ(1行なら)そのまま表示で
    else
      cat $tmp-nyuukyosha_kari   > $tmp-nyuukyosha
    fi   
  fi
fi
# 1:入居者Ｎｏ 2:入居者名
# 施設選択されていない場合建屋以下は全てという選択肢のみ
###########################################################################
if [ -z "${GAMEN}" -o "${GAMEN}" = "_" ] ; then
  awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/KIHONJYOUHOU_ICHIRAN2.html
elif [ "${GAMEN}" = "POPKOUZA" ] ; then
  awk '/\<shisetsu_tb_start\>/,/\<shisetsu_tb_end\>/' ${html_dir}/POP_KOJINJYOUHOU_SHOUSAI_KOUZA.html
elif  [ "${GAMEN}" = "NYUUINGAIHAKU" ] ; then
  awk '/\<shisetsu_tr_start\>/,/\<shisetsu_tr_end\>/' ${html_dir}/NYUUINGAIHAKU_ICHIRAN2.html
fi |

tee $tmp-ajax_test |
 
  mojihame -l"shisetsu_select"  - $tmp-shisetsu_name    |
  mojihame -l"jigyousho_select"  - $tmp-jigyousho_name  |
  mojihame -l"caremanager_select" - $tmp-caremane_name  |
  mojihame -l"tateya_select"     - $tmp-tateya_name     |
  mojihame -l"floor_select"    - $tmp-floor             |
  mojihame -l"unit_select"  - $tmp-unit_name            |
  mojihame -l"kyoshitsu_select"     - $tmp-kyoshitsu    |
  mojihame -l"nyuukyosha_select"    - $tmp-nyuukyosha   |
  calsed -f $tmp-calsed                                 |
  sed 's/###SPACE###/ /g'                               |
  sed 's/\\n/\n/g'                                      |
  sed 's/###KAIGYO###/\n/g'                             |
  tee $tmp-formhame_mae                                   > $tmp-html
#  formhame -d"_"                - $tmp-name    > $tmp-html

# HTML の出力
cat << FIN | cat - $tmp-html
Content-Type: text/html; charset=UTF-8;

FIN

# 終了
rm -f $tmp-*
exit 0
