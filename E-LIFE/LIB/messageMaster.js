/**
 * messageMaster.js
 * 
 * メッセージマスタ、項目名マスタ
 */
var msgMst = {
"num0" : "{0}は必須です。",
"num1" : "数字を入力するべきところに数字以外が入力されています。",
"num2" : "登録対象データを入力してください。",
"num3" : "登録対象データを選択してください。",
"num4" : "{0}を選択してください。",
"num5" : "{0}が{1}より後になっています。",
"num6" : "指定された形式で入力されていない箇所があります。",
"num7" : "必須項目が入力されていません。",
"num8" : "正しい構文で入力されていない箇所があります。",
"num9" : "入力値が長すぎる箇所があります。",
"num10" : "入力値が小さすぎる箇所があります。",
"num11" : "入力値が大きすぎる箇所があります。",
"num12" : "入力可能な小数桁と異なる箇所があります。",
"num13" : "入力値に誤りがある箇所があります。",
"num14" : "修正内容を登録しましたか？",
"num15" : "更新対象のデータがありません。",
"num16" : "入力文字列が長すぎる箇所があります。",
"num17" : "上書きしてよろしいですか？",
"num18" : "取り消しました。",
"num19" : "登録してよろしいですか？",
"num20" : "削除してもよろしいですか？",
"num21" : "上書き登録してよろしいですか？",
"num22" : "更新対象データを選択してください。",
"num23" : "{0}を登録する場合、{1}は必須です。",
"num24" : "登録対象の都道府県を選択してください。",
"num25" : "更新対象の権限を選択してください。",
"num26" : "削除対象の権限を選択してください。",
"num27" : "追加対象のメンバーを選択してください。",
"num28" : "削除対象のメンバーを選択してください。",
"num29" : "登録済の{0}は削除できません。",
"num30" : "賃料を変更する場合、{0}は必須です。",
"num31" : "修正対象の項目を選択してください。（{0}）",
"num32" : "削除対象の項目を選択してください。（{0}）",
"num33" : "検索を実行して、登録対象を表示してください。",
};

var KAIGOKANGOKIROKU_Item = {
"num0" : "介助分類",
"num1" : "開始時間",
"num2" : "終了時間",
"num3" : "時刻",
"num4" : "登録対象者",
"num5" : "対象者",
};

var HOUMONKAIGO_Item = {
"num0" : "派遣時間（開始）",
"num1" : "派遣時間（終了）",
"num2" : "提供時間（開始）",
"num3" : "提供時間（終了）",
"num4" : "サービス提供日の開始時間",
"num5" : "終了時間",
"num6" : "サービス時間（開始）",
"num7" : "サービス時間（終了）",
};

var CAREPLAN_Item = {
"num0" : "提供時刻（開始）",
"num1" : "提供時刻（終了）",
"num2" : "提供時刻",
"num3" : "表示順",
"num4" : "時間（開始）",
"num5" : "時間（終了）",
"num6" : "時間",
"num7" : "開催時間（開始）",
"num8" : "開催時間（終了）",
"num9" : "提供時間帯（開始）",
"num10" : "提供時間帯（終了）",
};

var SYSTEM_SETTEI_Item = {
"num0" : "スケジュール名",
"num1" : "参加費",
"num2" : "スケジュールタイプ",
"num3" : "色設定",
"num4" : "施設名称",
"num5" : "略称",
"num6" : "電話番号",
"num7" : "FAX",
"num8" : "郵便番号",
"num9" : "住所",
"num10" : "ユニット名",
"num11" : "居室番号",
"num12" : "定員",
"num13" : "居室タイプ1",
"num14" : "居室タイプ2",
"num15" : "ユニット名",
"num16" : "領収書表示名称",
"num17" : "金融機関",
"num18" : "支店名",
"num19" : "口座番号",
"num20" : "口座名義",
"num21" : "委託者番号",
"num22" : "委託者名",
"num23" : "委託者カナ",
"num24" : "問合せ先名称",
"num25" : "問合せ先郵便番号",
"num26" : "問合せ先住所",
"num27" : "問合せ先電話番号",
"num28" : "問合せ先FAX番号",
"num29" : "従業員名",
"num30" : "従業員名カナ",
"num31" : "勤務期間",
"num32" : "id",
"num33" : "パスワード",
"num34" : "所属施設・事業所",
"num35" : "契約種別",
"num36" : "集計グループ",
"num37" : "入金項目",
"num38" : "出金項目",
"num39" : "立替対象項目（入居者以外）",
"num40" : "税率",
"num41" : "元号",
"num42" : "適用開始日",
"num43" : "適用終了日",
"num44" : "事業所番号",
"num45" : "事業所名称",
"num46" : "表示順",
"num47" : "サービス項目名",
"num48" : "単価",
"num49" : "保険者番号",
"num50" : "保険者名",
"num51" : "保険者カナ",
"num52" : "権限",
"num53" : "追加する契約種別名",
"num54" : "契約種別名",
"num55" : "契約金種別名",
"num56" : "項目名、税区分、金額、支払区分、費用算出方法",
"num57" : "項目名",
"num58" : "グループ事業所名",
"num59" : "事業所",
"num60" : "現賃料有効期間(至)",
"num61" : "新賃料",
"num62" : "新賃料有効期間(自)",
"num63" : "容量（主食）",
"num64" : "容量(副食・おやつ共通)",
"num65" : "主食形態",
"num66" : "介助場所",
"num67" : "副食形態",
"num68" : "おやつ種類",
"num69" : "水分種類",
"num70" : "排尿量",
"num71" : "排尿形状",
"num72" : "排便量",
"num73" : "排便形状",
"num74" : "介助区分（上）",
"num75" : "介助区分（下）",
"num76" : "下剤種類",
"num77" : "入浴その他",
"num78" : "入浴区分",
"num79" : "詳細",
"num80" : "種目",
"num81" : "場所",
"num82" : "内服薬用法",
"num83" : "内服薬容量",
"num84" : "介助場所",
"num85" : "処置(用法)",
"num86" : "医療(用法)",
"num87" : "医療(容量)",
"num88" : "頓用(用法)",
"num89" : "頓用(容量)",
"num90" : "外用薬(用法)",
"num91" : "測定・観察(用法)",
"num92" : "通院介助・入院中の面会(用法)",
"num93" : "通院介助(容量)",
"num94" : "往診(用法)",
"num95" : "介助区分",
"num96" : "金額",
"num97" : "月額利用料種別",
};