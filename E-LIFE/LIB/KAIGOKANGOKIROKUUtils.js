/**
 *
 * KAIGOKANGOKIROKUUtils.js
 * 介護看護記録カテゴリでの共通js
 *
 */

/**
 * 一行目の開始時間を設定した場合、それ以下の行の開始時間も同じ値で埋める
 */
function startTimeInput() {
	//「start」を含むテキスト要素取得
	var elm = $(".well").find($("input[type='time'][name*='start']")).get();
	if (elm.length > 0) {
		//一行目のname属性取得
		var elmDetail = $(elm).get(0);
		var nameAttr = elmDetail.getAttribute("name");
		//一行目の開始時間からフォーカスが外れたら
		$("input[type='time'][name ="+ nameAttr + "]").blur(function(){
			var startTime = $("input[type='time'][name ="+ nameAttr + "]").val();
			//取得したテキスト要素数ループ
			for (var i=1; i<elm.length; i++) {
				elmDetail = $(elm).get(i);
				var replaceNameAttr = elmDetail.getAttribute("name");
				//開始時間上書き
				$("input[type='time'][name ="+ replaceNameAttr + "]").val(startTime);
			}
		});
	}
}

/**
 * 一行目の終了時間を設定した場合、それ以下の行の終了時間も同じ値で埋める
 */
function endTimeInput() {
	//「shoyo」を含むテキスト要素取得
	var elmEn = $(".well").find($("input[type='time'][name*='shoyo']")).get();
	if (elmEn.length > 0) {
		//一行目のname属性取得
		var elmDetailEn = $(elmEn).get(0);
		var nameAttrEn = elmDetailEn.getAttribute("name");
		//一行目の終了時間からフォーカスが外れたら
		$("input[type='time'][name ="+ nameAttrEn + "]").blur(function(){
			var endTime = $("input[type='time'][name ="+ nameAttrEn + "]").val();
			//取得したテキスト要素数ループ
			for (var i=1; i<elmEn.length; i++) {
				elmDetailEn = $(elmEn).get(i);
				var replaceNameAttrEn = elmDetailEn.getAttribute("name");
				//開始時間上書き
				$("input[type='time'][name ="+ replaceNameAttrEn + "]").val(endTime);
			}
		});
	}
}

/**
 * 登録対象データ（チェックされた）があるかどうか確認
 * 
 * elmChecked:チェックされたチェックボックス
 */
function existRegistData(elmChecked){
	if (elmChecked.length == 0 || elmChecked.length == null) {
		return true;
	}
	return false;
}

/**
 * 渡された範囲に含まれる
 *「input type="number"」のバリデートチェックを実施する
 *
 */
function validateNumber(elements) {
	var elms = $(elements).find("input[type='number']").get();
	for (var i=0; i<elms.length; i++) {
		var numElm = $(elms).get(i);
		if (!checkValidate(numElm)) {
			return false;
		}
	}
	return true;
}
