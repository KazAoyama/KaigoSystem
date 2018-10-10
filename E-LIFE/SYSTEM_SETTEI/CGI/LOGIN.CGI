#!/bin/bash
#
# LOGIN.CGI : ログインチェック＆画面移動CGI
#
# Usage : LOGIN.CGI
#
# Written by Jun Aoyagi

source /home/hands/E-LIFE/SYSTEM_SETTEI/CGI/SYSTEM_SETTEI.INI &> /dev/null
source /home/hands/.bashrc &> /dev/null

mkdir -p ${log_dir}/$(date +%Y%m%d)
exec 2> ${log_dir}/$(date +%Y%m%d)/LOG.$(basename ${0}).${HOSTNAME}.$(date +%Y%m%d) ; set -xv

# 変数設定
tmp=/var/tmp/${$}

#ゴミtmpの消去
rm -f $tmp-*

# ディレクトリ設定
home_dir="/home/hands"
app_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI"
cgi_dir="${app_dir}/CGI"
html_dir="${app_dir}/HTML"
cgi_nisshi_dir="${home_dir}/E-LIFE/UNEI/CGI"
cgi_careplan_dir="${home_dir}/E-LIFE/CAREPLAN/CGI"
cgi_houmonkaigo_dir="${home_dir}/E-LIFE/HOUMONKAIGO/CGI"
tbl_dir="${home_dir}/E-LIFE/TBL"
ch_cgi_dir="${home_dir}/E-LIFE/SYSTEM_SETTEI/CGI"
# ケア施設
care_kaigokiroku_dir="${home_dir}/E-LIFE/CARE_KAIGOKIROKU/CGI"
care_kaigosakusei_dir="${home_dir}/E-LIFE/CARE_KAIGOSAKUSEI/CGI"

#}}}Functions#######################################

dd bs=${CONTENT_LENGTH} > ${tmp}-param
[ -s ${tmp}-param ] && cgi-name -d_ -i_ ${tmp}-param > ${tmp}-param_name || : > ${tmp}-param_name

eval $(name-source ${tmp}-param_name)
#MODEの確認
MODE="$(nameread "MODE" ${tmp}-param_name)"
[ -n "${MODE}" ] || MODE="init"

#cp -p ${tmp}-param_name param_name_kengen_kanri_test

# 画面、CGI紐付けテーブル取得
# 1:画面ID 2:パス 3:優先度
cat ${tbl_dir}/CONFIG/SCREEN_CGI |
LANG=C sort -k1,1                > $tmp-screen_cgi

# 処理の分岐
case "${MODE}" in
  #初期表示
  login )
    ${cgi_dir}/LOGIN.CHECK ${tmp}-param_name > ${tmp}-check
    # チェック内容を解析
    eval $(name-source ${tmp}-check)

    # パスワードの変更期間チェック
    today=$(date +%Y%m%d)
    awk '$6=="'${loginid}'"&&$(NF-2)!=9' ${pompa_dir}/JYUUGYOUIN/USER_KIHON |
    self 1 7 9 |
    LANG=C sort -k3,3 |
    getfirst 1 2 |
    awk '$2!="e-life-pass"' |
    tail -n1 |
    awk '{print substr($3,1,8)}' > $tmp-koushinbi
    koushinbi=$(cat $tmp-koushinbi)
    nissu=$(mdate $today $koushinbi)

    USRID=$(awk '$6=="'${loginid}'"&&$(NF-2)!=9{print $1}' ${pompa_dir}/JYUUGYOUIN/USER_KIHON)
    awk '$1=="'${USRID}'"&&$(NF-2)!=9{print $2}' ${pompa_dir}/JYUUGYOUIN/USER_PASS_KIKAN  |
    join1 key=1 ${app_dir}/TBL/HENKO_KIKAN |
    self 3 > $tmp-settei_kikan
    if [ $(gyo $tmp-settei_kikan) = 0 ];then
      echo "365" > $tmp-settei_kikan
    fi
    SETTEI_KIKAN=$(cat $tmp-settei_kikan)
    HENKOKANO_KIKAN=$(cat $tmp-settei_kikan | lcalc '$1-14')

    if [ "$status" = "success" ] ; then
      if [ "${password}" = "${INITIAL_PASSWORD}" ]; then
        ${ch_cgi_dir}/CHANGE_PASSWORD.DISPLAY ${tmp}-param_name ${tmp}-check > $tmp-html
        echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
        cat - ${tmp}-html
        rm -f ${tmp}-*
        exit 0
      elif [ $nissu -gt $SETTEI_KIKAN ];then
cat <<- FIN | sed 's/ _$/ @/g' > ${tmp}-calsed
###LOGINID### ${loginid}
FIN
        cat ${html_dir}/SIGN_IN.html |
        calsed -f $tmp-calsed - > $tmp-html

        message="パスワードの有効期間を過ぎました。システム管理者に連絡してください"
cat <<- FIN > $tmp-html2
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
        # HTMLファイルを表示する
        if [ -e "$tmp-html" ];then
          echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
          cat - ${tmp}-html $tmp-html2
        fi
        
        rm -f ${tmp}-*
        exit 0

      elif [ $nissu -gt $HENKOKANO_KIKAN ];then
        ${ch_cgi_dir}/CHANGE_PASSWORD.DISPLAY ${tmp}-param_name ${tmp}-check > $tmp-html
        echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
        cat - ${tmp}-html
        rm -f ${tmp}-*
        exit 0
      fi
      MODE="init"
# まずは施設建屋で画面遷移を制御　2015/06/29
      if [ "$tateya" == "99" ] ; then
          # テスト用（仮）
          echo "###LI_CCAREPLAN1### on" > ${tmp}-check2
          echo "###LI_CCAREPLAN3### on" >> ${tmp}-check2
          echo "###LI_CCAREPLAN4### on" >> ${tmp}-check2
          echo "###LI_CCAREPLAN5### on" >> ${tmp}-check2
          echo "###LI_CCAREPLAN6### on" >> ${tmp}-check2
          echo "###LI_CCAREPLAN7### on" >> ${tmp}-check2
          echo "###TOGGLE_SCHEDULE### dropdown" >> ${tmp}-check2
          echo "###TOGGLE_KOJIN### dropdown" >> ${tmp}-check2
          echo "###TOGGLE_RIYOU### dropdown" >> ${tmp}-check2
          echo "###TOGGLE_CAREPLAN### dropdown" >> ${tmp}-check2
          echo "###TOGGLE_KAIGO### dropdown" >> ${tmp}-check2
          echo "###TOGGLE_SHOKUJI### dropdown" >> ${tmp}-check2
          echo "###TOGGLE_SEIKYU### dropdown" >> ${tmp}-check2
          $care_kaigosakusei_dir/CARE_SHISETSU_ASSESSMENT.DISPLAY ${tmp}-check ${tmp}-check2 > $tmp-html
# ケア＋本社の時は一時的に気づきに行く(2015/08/31)
      elif [ "${shisetsu}" = "0007" -o "${shisetsu}" = "0008" -o "${shisetsu}" = "0009" -o "${shisetsu}" = "0010" -o "${shisetsu}" = "0011" -o "${shisetsu}" = "1000" ] ; then
          $ch_cgi_dir/KENGEN_CHECK.CGI ${tmp}-check > ${tmp}-check2
          if [ $(gyo ${tmp}-check2) -ne 0 ];then
             echo "MODE search" >> ${tmp}-check   
             echo "Shisetsu $shisetsu" >> ${tmp}-check
             $cgi_nisshi_dir/KIZUKI_ICHIRAN.SEARCH ${tmp}-check > ${tmp}-search
             $cgi_nisshi_dir/KIZUKI_ICHIRAN.DISPLAY ${tmp}-check ${tmp}-check2 ${tmp}-search > $tmp-html
          else
             ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-check
          fi
      else

          case "${shokushu}" in
        # ケアマネ
            1 )
            $ch_cgi_dir/KENGEN_CHECK.CGI ${tmp}-check > ${tmp}-check2
            if [ $(gyo ${tmp}-check2) -ne 0 ];then
                $cgi_careplan_dir/KYOTAKUSHIEN_MENU_KAIGO.DISPLAY ${tmp}-check ${tmp}-check2 > $tmp-html
            else
                ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-check
            fi
              ;;
        # 訪問介護
            2 )
            $ch_cgi_dir/KENGEN_CHECK.CGI ${tmp}-check > ${tmp}-check2
            if [ $(gyo ${tmp}-check2) -ne 0 ];then
               $cgi_houmonkaigo_dir/HOUMONKAIGO_MENU.DISPLAY ${tmp}-check ${tmp}-check2 > $tmp-html
            else
                ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-check
            fi
              ;;
            * )
            $ch_cgi_dir/KENGEN_CHECK.CGI ${tmp}-check > ${tmp}-check2
            [ "$tateya" = "_" ] && tateya="01"
            if [ $(gyo ${tmp}-check2) -ne 0 ];then
               # 権限ありの施設をセット
               cat ${tbl_dir}/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN    |
               awk '$2=="0000"||$2=="'$shisetsu'"'         |
               # リンクステータスがONのものを抽出
               awk '$8=="on"{print $7}' |
               LANG=C sort -k1,1 -u |
               join1 key=1 $tmp-screen_cgi |
               LANG=C sort -k3,3n           |
               head -1                     > $tmp-target_cgi
               target_cgi=$(self 2 $tmp-target_cgi)
               kakunin_cgi=$(self 1 $tmp-target_cgi)
     
               if [ "${kakunin_cgi}" = "NISSHI.CGI" ] ; then
                 # 所属している建屋が対象の施設にあるかどうかをチェック
                 cat /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR |
                 awk '$1=="'$shisetsu'"&&$(NF-2)!="9"' |
                 tee $tmp-tateya_select                |
    #             if [ "$tateya" = "_" ] ; then
    #               cat -
    #             else
                    awk '$2=="'$tateya'"'               |
    #             fi |
                 awk '{print $0}' > $tmp-tateya-check

               # 施設に所属建屋が無い場合は存在する建屋の日誌情報を表示
               if [ "$(gyo $tmp-tateya-check)" = "0" ] ; then
                 tateya=$(self 2 $tmp-tateya_select | LANG=C sort -k1,1 | tail -1)
               fi
    
               if [ "${tateya}" = "02" ] ; then
                 $cgi_nisshi_dir/NISSHI_CARE.DISPLAY ${tmp}-check ${tmp}-check2 > $tmp-html
               else
                 $cgi_nisshi_dir/NISSHI_SENIOR.DISPLAY ${tmp}-check ${tmp}-check2 > $tmp-html
               fi
             else
               echo $target_cgi > /home/hands/E-LIFE/SYSTEM_SETTEI/WORK/kengencgi
               : > $tmp-opt
               $target_cgi ${tmp}-check ${tmp}-check2 $tmp-opt > $tmp-html
             fi
           else
               ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-check
           fi
             ;;
         esac
      fi
    else 
      ${cgi_dir}/LOGIN_ERROR.DISPLAY ${tmp}-param_name > ${tmp}-html
    fi
    ;;
 #その他の場合
  * )
    MODE="init"
# 従業員情報取得
# 1:ユーザID         2:施設ID     3:建屋ID             4:フロアID 5:ユニットID
# 6:居宅訪問介護区分 7:管理者区分 8:介護支援専門員番号
    cat ${tbl_dir}/JYUUGYOUIN_MASTER/USER_SHISETSU          |
    cat - ${tbl_dir}/JYUUGYOUIN_MASTER/EXTRA_USER_SHISETSU  |
    awk '$(NF-2)!="9"'                                      |
    awk '$1=="'$userid'"&&$2=="'$shisetsu'"{print $3,$6}'            > $tmp-user_shokushu
    shokushu=$(self 2 $tmp-user_shokushu | tail -1)
    tateya=$(self 1 $tmp-user_shokushu | tail -1)

# まずは施設建屋で画面遷移を制御　2015/06/29
    awk '$1=="'$shisetsu'"&&$(NF-2)!="9"{print $2}' /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR |
    LANG=C sort -k1,1 > $tmp-care_shisetsu_check
    tateya_care_check=$(tail -1 $tmp-care_shisetsu_check)
#    if [ "$tateya_care_check" = "00" ] ; then
        # テスト用（仮）
#        echo "###LI_CSCHEDULE1### UNDER_CONSTRUCTION.CGI" > ${tmp}-check2
#        $care_kaigokiroku_dir/UNDER_CONSTRUCTION.DISPLAY ${tmp}-check > $tmp-html
#    else
# ケア＋本社の時は一時的に気づきに行く(2015/08/31)
     if [ "${shisetsu}" = "0007" -o "${shisetsu}" = "0008" -o "${shisetsu}" = "0009" -o "${shisetsu}" = "0010" -o "${shisetsu}" = "0011" -o "${shisetsu}" = "1000" ] ; then
          $ch_cgi_dir/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check2
          if [ $(gyo ${tmp}-check2) -ne 0 ];then
             echo "MODE search" >> ${tmp}-param_name
             echo "Shisetsu $shisetsu" >> ${tmp}-param_name
             $cgi_nisshi_dir/KIZUKI_ICHIRAN.SEARCH ${tmp}-param_name > ${tmp}-search
             $cgi_nisshi_dir/KIZUKI_ICHIRAN.DISPLAY ${tmp}-param_name ${tmp}-check2 ${tmp}-search > $tmp-html
          else
             ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
          fi
     else
        case "${shokushu}" in
        # ケアマネ
          1 )
           $ch_cgi_dir/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check2
           if [ $(gyo ${tmp}-check2) -ne 0 ];then
             # 選択された所属が施設かどうかをチェック
             cat /home/hands/E-LIFE/TBL/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
             awk '$1=="'${shisetsu}'"' > $tmp-jigyousho-check
             # 事業所ではない場合は日誌に遷移
             if [ "$(gyo $tmp-jigyousho-check)" = "0" ] ; then
               # 権限ありの施設をセット
               cat ${tbl_dir}/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN    |
               awk '$2=="0000"||$2=="'$shisetsu'"'         |
               # リンクステータスがONのものを抽出
               awk '$8=="on"{print $7}' |
               LANG=C sort -k1,1 -u |
               join1 key=1 $tmp-screen_cgi |
               LANG=C sort -k3,3n           |
               head -1                     > $tmp-target_cgi
               target_cgi=$(self 2 $tmp-target_cgi)
               kakunin_cgi=$(self 1 $tmp-target_cgi)
     
               if [ "${kakunin_cgi}" = "NISSHI.CGI" ] ; then
                 # 所属している建屋が対象の施設にあるかどうかをチェック
                 [ "$tateya" = "_" ] && tateya="01"
                 cat /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR |
                 awk '$1=="'$shisetsu'"&&$(NF-2)!="9"' |
                 tee $tmp-tateya_select                |
     #             if [ "$tateya" = "_" ] ; then
     #               cat -
     #             else
                  awk '$2=="'$tateya'"'                |
     #             fi |
                 awk '{print $0}' > $tmp-tateya-check
     
                 # 施設に所属建屋が無い場合は存在する建屋の日誌情報を表示
                 if [ "$(gyo $tmp-tateya-check)" = "0" ] ; then
                   tateya=$(self 2 $tmp-tateya_select | LANG=C sort -k1,1 | tail -1)
                 fi
     
                 if [ "${tateya}" = "02" ] ; then
                   $cgi_nisshi_dir/NISSHI_CARE.DISPLAY ${tmp}-param_name $tmp-check2 > $tmp-html
                 else
                   $cgi_nisshi_dir/NISSHI_SENIOR.DISPLAY ${tmp}-param_name $tmp-check2 > $tmp-html
                 fi
               else
                : > $tmp-opt
                $target_cgi ${tmp}-param_name ${tmp}-check2 $tmp-opt > $tmp-html
               fi
             else
                $cgi_careplan_dir/KYOTAKUSHIEN_MENU_KAIGO.DISPLAY ${tmp}-param_name ${tmp}-check2 > $tmp-html
             fi
           else
                ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
           fi
            ;;
        # 訪問介護
          2 )
           $ch_cgi_dir/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check2
           if [ $(gyo ${tmp}-check2) -ne 0 ];then
             # 選択された所属が施設かどうかをチェック
             cat /home/hands/E-LIFE/TBL/JIGYOUSHO_MASTER/JIGYOUSHO_GROUP_MASTER |
             awk '$1=="'${shisetsu}'"' > $tmp-jigyousho-check
             # 事業所ではない場合は日誌に遷移
             if [ "$(gyo $tmp-jigyousho-check)" = "0" ] ; then
               # 権限ありの施設をセット
               cat ${tbl_dir}/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN    |
               awk '$2=="0000"||$2=="'$shisetsu'"'         |
               # リンクステータスがONのものを抽出
               awk '$8=="on"{print $7}' |
               LANG=C sort -k1,1 -u |
               join1 key=1 $tmp-screen_cgi |
               LANG=C sort -k3,3n           |
               head -1                     > $tmp-target_cgi
               target_cgi=$(self 2 $tmp-target_cgi)
               kakunin_cgi=$(self 1 $tmp-target_cgi)
     
               if [ "${kakunin_cgi}" = "NISSHI.CGI" ] ; then
                 # 所属している建屋が対象の施設にあるかどうかをチェック
                 [ "$tateya" = "_" ] && tateya="01"
                 cat /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR |
                 awk '$1=="'$shisetsu'"&&$(NF-2)!="9"' |
                 tee $tmp-tateya_select                |
     #             if [ "$tateya" = "_" ] ; then
     #               cat -
     #             else
                  awk '$2=="'$tateya'"'                |
     #             fi |
                  awk '{print $0}' > $tmp-tateya-check

               # 施設に所属建屋が無い場合は存在する建屋の日誌情報を表示
                 if [ "$(gyo $tmp-tateya-check)" = "0" ] ; then
                   tateya=$(self 2 $tmp-tateya_select | LANG=C sort -k1,1 | tail -1)
                 fi
     
                 if [ "${tateya}" = "02" ] ; then
                   $cgi_nisshi_dir/NISSHI_CARE.DISPLAY ${tmp}-param_name $tmp-check2 > $tmp-html
                 else
                   $cgi_nisshi_dir/NISSHI_SENIOR.DISPLAY ${tmp}-param_name $tmp-check2 > $tmp-html
                 fi
               else
                : > $tmp-opt
                $target_cgi ${tmp}-param_name ${tmp}-check2 $tmp-opt > $tmp-html
               fi
             else
               $cgi_houmonkaigo_dir/HOUMONKAIGO_MENU.DISPLAY ${tmp}-param_name ${tmp}-check2 > $tmp-html
             fi
           else
             ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
           fi
            ;;
          * )
           $ch_cgi_dir/KENGEN_CHECK.CGI ${tmp}-param_name > ${tmp}-check2
           if [ $(gyo ${tmp}-check2) -ne 0 ];then
            # 選択された所属が施設かどうかをチェック
            cat /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_KIHON |
            awk '$1=="'${shisetsu}'"' > $tmp-shisetsu-check
            # 施設ではない場合はケアプランに遷移
            if [ "$(gyo $tmp-shisetsu-check)" = "0" ] ; then
              $cgi_careplan_dir/KYOTAKUSHIEN_MENU_KAIGO.DISPLAY ${tmp}-param_name ${tmp}-check2 > $tmp-html
            else
               # 権限ありの施設をセット
               cat ${tbl_dir}/KENGEN_KANRI/USER_KENGEN/${userid}.USER_KENGEN    |
               awk '$2=="0000"||$2=="'$shisetsu'"'         |
               # リンクステータスがONのものを抽出
               awk '$8=="on"{print $7}' |
               LANG=C sort -k1,1 -u |
               join1 key=1 $tmp-screen_cgi |
               LANG=C sort -k3,3n           |
               head -1                     > $tmp-target_cgi
               target_cgi=$(self 2 $tmp-target_cgi)
               kakunin_cgi=$(self 1 $tmp-target_cgi)
     
               if [ "${kakunin_cgi}" = "NISSHI.CGI" ] ; then
                 # 所属している建屋が対象の施設にあるかどうかをチェック
                 [ "$tateya" = "_" ] && tateya="01"
                 cat /home/hands/E-LIFE/TBL/SHISETSU_MASTER/SHISETSU_TATEYA_FLOOR |
                 awk '$1=="'$shisetsu'"&&$(NF-2)!="9"' |
                 tee $tmp-tateya_select                |
     #             if [ "$tateya" = "_" ] ; then
     #               cat -
     #             else
                  awk '$2=="'$tateya'"'                |
     #             fi |
                  awk '{print $0}' > $tmp-tateya-check

                # 施設に所属建屋が無い場合は存在する建屋の日誌情報を表示
                if [ "$(gyo $tmp-tateya-check)" = "0" ] ; then
                  tateya=$(self 2 $tmp-tateya_select | LANG=C sort -k1,1 | tail -1)
                fi
     
                if [ "${tateya}" = "02" ] ; then 
                  $cgi_nisshi_dir/NISSHI_CARE.DISPLAY ${tmp}-param_name $tmp-check2 > $tmp-html
                else
                  $cgi_nisshi_dir/NISSHI_SENIOR.DISPLAY ${tmp}-param_name $tmp-check2 > $tmp-html
                fi
              else
                : > $tmp-opt
                $target_cgi ${tmp}-param_name ${tmp}-check2 $tmp-opt > $tmp-html
              fi
            fi
           else
              ${ch_cgi_dir}/SIGN_IN.CGI ${tmp}-param_name
           fi
            ;;
        esac
     fi
   ;;
esac

# 返す？
if [ "$(gyo ${tmp}-check2)" -ne 0 ];then
  :
else
  message="権限がありません"
cat <<- FIN > $tmp-html2
     <script type="text/javascript" language="javascript">
       alert('${message}');
     </script>
FIN
fi


# HTMLファイルを表示する
if [ -e "$tmp-html" ];then
  echo -e 'Content-Type: text/html; charset=UTF-8; \n\n' |
  cat - ${tmp}-html
else
  cat $tmp-html2
fi

rm -f ${tmp}-*
exit 0
