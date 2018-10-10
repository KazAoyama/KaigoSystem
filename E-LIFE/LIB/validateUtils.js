/**
 *
 * validateUtils.js 
 * validationチェックに使用する共通js
 * true:エラーあり、false:エラーなしとする。
 * 
 */

/**
 * 時間比較（時：分を秒にして比較）
 * sTime：開始時間（形式：「00:00」）
 * eTime：終了時間（形式：「00:00」）
 *
 * 開始時間>終了時間の場合trueを返す。
 */

function timeCompare(sTime, eTime, separator){
	if ((sTime == "" || sTime == null) || 
		(eTime == "" || eTime == null)) {
		return false;
	}
	var sTimeArray = sTime.split(separator);
	var eTimeArray = eTime.split(separator);
	var sTimeSec = (sTimeArray[0] * 60) + (sTimeArray[1] - 0);
	var eTimeSec = (eTimeArray[0] * 60) + (eTimeArray[1] - 0);
	if (sTimeSec > eTimeSec) {
		return true;
	}
	return false;
}

var msgNumber = new Array();
	msgNumber["num"] = 0;
	msgNumber["pattern"] = 1;

/**
 * 数字チェック
 */
function isNumber(str) {
	if (str == "" || str == null) {
		return false;
	} else {
		if (str.match(/[^0-9*]/)) {
			return true;
		} else {
			return false;
		}
	}
}

/**
 * 数字チェック（カンマ含む）
 */
function isNumberWithComma(str) {
	if (str == "" || str == null) {
		return false;
	} else {
		if (str.match(/[^0-9.*]/)) {
			return true;
		} else {
			return false;
		}
	}
}

/**
 * 数字チェック（スラッシュ含む）
 */
function isNumberWithSrash(str) {
	if (str == "" || str == null) {
		return false;
	} else {
		if (str.match(/[^0-9\/*]/)) {
			return true;
		} else {
			return false;
		}
	}
}

/**
 * 数字チェック（ハイフン含む）
 */
function isNumberWithHaihun(str) {
	if (str == "" || str == null) {
		return false;
	} else {
		if (str.match(/[-0-9*]/)) {
			return false;
		} else {
			return true;
		}
	}
}
/**
 * ※バリデーションのフラグについて(ValidityState)
 * elm.validity.valueMissing	: 必須のフィールドにもかかわらず値を持たないならtrue を返し、そうでなければ false を返します。
 * elm.validity.typeMismatch	: 正しい構文でないなら true を返し、そうでなければ false を返します。
 * elm.validity.patternMismatch	: 指定のパターンに一致しないなら true を返し、そうでないなら false を返します。
 * elm.validity.tooLong			: 指定の最大長より長いなら true を返し、そうでなければ false を返します。
 * elm.validity.rangeUnderflow	: 指定の最小値より低いなら true を返し、そうでなければ false を返します。
 * elm.validity.rangeOverflow	: 指定の最大値より高ければ true を返し、そうでなければ false を返します。
 * elm.validity.stepMismatch	: step 属性で指定された規則に一致しないならtrue を返し、そうでなければ false を返します。
 * elm.validity.customError		: 独自エラーを持っているなら true を返し、そうでなければ false を返します。
 * elm.validity.valid			: 値の妥当性に問題がひとつもなければ true を返し、そうでなければ false を返します。
 */
var validityFlags = {
			"badInput" : false,
			"valueMissing" : false,
			"typeMismatch" : false,
			"patternMismatch" : false,
			"tooLong" : false,
			"rangeUnderflow" : false,
			"rangeOverflow" : false,
			"stepMismatch" : false,
			"customError" : false,
			"valid" : true,
};

/**
 * 指定項目（複数可）が何のエラーであるかフラグを返す。
 */
function idealValidateCheck(elements, msgFlag){
	resetFlags();
	var flags = validityFlags;
	var elms = $(elements).get();
	for (var i=0; i<elms.length; i++) {
		var elm = $(elms).get(i);
		//入力誤り
		if (elm.validity.badInput) {
			flags.badInput = true;
		}
		//必須エラー
		if (elm.validity.valueMissing) {
			flags.valueMissing = true;
		}
		//タイプミスマッチエラー
		if (elm.validity.typeMismatch) {
			flags.typeMismatch = true;
		}
		//パターンミスマッチエラー
		if (elm.validity.patternMismatch) {
			flags.patternMismatch = true;
		}
		//最大長エラー
		if (elm.validity.tooLong) {
			flags.tooLong = true;
		}
		//最小値エラー
		if (elm.validity.rangeUnderflow) {
			flags.rangeUnderflow = true;
		}
		//最大値エラー
		if (elm.validity.rangeOverflow) {
			flags.rangeOverflow = true;
		}
		//step属性エラー
		if (elm.validity.stepMismatch) {
			flags.stepMismatch = true;
		}
		//独自エラー
		if (elm.validity.customError) {
			flags.customError = true;
		}
		//その他のエラー
		if (!elm.validity.valid) {
			flags.valid = false;
		}
	}
	//メッセージ作成するなら、メッセージを返す。
	if (msgFlag) {
		return createMessage(flags);
	} else {
		return flags;
	}
}
function resetFlags() {
	validityFlags.badInput = false;
	validityFlags.valueMissing = false;
	validityFlags.typeMismatch = false;
	validityFlags.patternMismatch = false;
	validityFlags.tooLong = false;
	validityFlags.rangeUnderflow = false;
	validityFlags.rangeOverflow = false;
	validityFlags.stepMismatch = false;
	validityFlags.customError = false;
	validityFlags.valid = true;
}
/**
 * フラグ群より、メッセージを作成する。
 */
function createMessage(flags) {
	var message = "";
	//必須エラー
	//if (flags.valueMissing) {
	//	message += msgMst.num7 + "\n";
	//}
	//タイプミスマッチエラー
	if (flags.typeMismatch) {
		message += msgMst.num8 + "\n";
	}
	//パターンミスマッチエラー
	if (flags.patternMismatch) {
		message += msgMst.num6 + "\n";
	}
	//最大長エラー
	if (flags.tooLong) {
		message += msgMst.num9 + "\n";
	}
	//最小値エラー
	if (flags.rangeUnderflow) {
		message += msgMst.num10 + "\n";
	}
	//最大値エラー
	if (flags.rangeOverflow) {
		message += msgMst.num11 + "\n";
	}
	//step属性エラー
	if (flags.stepMismatch) {
		message += msgMst.num12 + "\n";
	}
	//独自エラー
	if (flags.customError) {
		message += msgMst.num13 + "\n";
	}
	//入力値あやまり
	//if (!flags.valueMissing || flags.badInput) {
	//	message += msgMst.num13 + "\n";
	//}
	//その他のエラー
	if (!flags.valid && flags.badInput) {
			message += msgMst.num13 + "\n";
	}
	return message;
}
/**
 * 指定項目（複数可）のエラーをメッセージ作成して返す。
 *
 * exp) elements = [{"elmId" : "対象要素のid", "itemName" : "対象項目名"},・・・];
 */
 /*
function idealValidateCheckAndMessage(elements){
	for (var cnt=0; cnt<elements.length; cnt++) {
		var elm = document.getElementById(validateCheckElements[cnt].elmId);
		//必須エラー
		if (elm.validity.valueMissing) {
			validityFlags.valueMissing = true;
		}
		//タイプミスマッチエラー
		if (elm.validity.typeMismatch) {
			validityFlags.typeMismatch = true;
		}
		//パターンミスマッチエラー
		if (elm.validity.patternMismatch) {
			validityFlags.patternMismatch = true;
		}
		//最大長エラー
		if (elm.validity.tooLong) {
			validityFlags.tooLong = true;
		}
		//最小値エラー
		if (elm.validity.rangeUnderflow) {
			validityFlags.rangeUnderflow = true;
		}
		//最大値エラー
		if (elm.validity.rangeOverflow) {
			validityFlags.rangeOverflow = true;
		}
		//step属性エラー
		if (elm.validity.stepMismatch) {
			validityFlags.stepMismatch = true;
		}
		//独自エラー
		if (elm.validity.customError) {
			validityFlags.customError = true;
		}
		//その他のエラー
		if (!elm.validity.valid) {
			validityFlags.valid = false;
		}
	}
	return flags;
}
*/
/**
 * htmlの機能によりバリデーションチェックを行う
 * エラーの分類はせず、該当要素がエラーであるかどうかのみ返す。
 * ※エラー：false
 *
 * element:チェック対象の「DOM要素」
 */
function checkValidate(element) {
	return element.checkValidity();
}

/**
 * 必須チェックを行い、メッセージを返す。
 *
 * element:チェック対象
 */
function isRequired(itemName, element) {
	var message = "";
	var elms = $(element).get();
	for (var i=0; i<elms.length; i++) {
		var elm = $(elms).get(i);
		if (elm.validity.valueMissing && !elm.validity.badInput) {
			message += msgMst.num0.replace("{0}", itemName) + "\n";
			break;
		}
	}
	return message;
}
/**
 * 必須チェックを行い、エラーであるか返す。
 * エラーの場合、trueを返す。
 * 
 * element:チェック対象
 */
function isRequiredReturnFlag(element) {
	var error = false;
	var elms = $(element).get();
	for (var i=0; i<elms.length; i++) {
		var elm = $(elms).get(i);
		if (elm.validity.valueMissing && !elm.validity.badInput) {
			error = true;
			break;
		}
	}
	return error;
}
/**
 * 必須チェックを行い、エラーであるか返す。
 * 指定した要素の内、一つでも必須エラーとならなかった場合、
 * その時点でfalseを返す。
 * 全て必須エラーの場合、trueを返す。
 * 
 * element:チェック対象
 */
function isRequiredReturnFlagEx(element) {
	var error = true;
	var elms = $(element).get();
	for (var i=0; i<elms.length; i++) {
		var elm = $(elms).get(i);
		if (elm.validity.valueMissing && !elm.validity.badInput) {
			//なにもしない
		} else {
			error = false
			break;
		}
	}
	return error;
}
/**
 * 時間入れ子チェック
 *
 * sTimes: 開始時間
 * eTimes: 終了時間
 * separator: 時分を区切るセパレーター
 * itemName1: 項目名１
 * itemName2: 項目名２
 */

function checkTime(sTimes, eTimes, separator, itemName1, itemName2) {
	var message = "";
	for (var i=0; i<sTimes.length; i++) {
		var sTime = $(sTimes).get(i);
		var eTime = $(eTimes).get(i);
		//開始・終了時間差分チェック
		var sTimeVal = $(sTime).val();
		var eTimeVal = $(eTime).val();
		//開始時間が23時台かつ終了時間が0時台の場合はチェック実施しない
		if (!(sTimeVal.match(/^23/) && eTimeVal.match(/^00/))) {
			if (timeCompare(sTimeVal, eTimeVal, separator)) {
				message += (msgMst.num5).replace("{0}", itemName1)
										.replace("{1}", itemName2) + "\n";
				break;
			}
		}
	}
	return message;
}

/**
 * 年チェック（和暦）
 *
 * 数字もしくは「元」のみOK
 */
function checkNen(str) {
	if (str.match(/\d*|元/)) {
		return 
	}
}

/**
 * 文字列のバイト数を返す
 *
 */
function getByte(str) {
	if (str == "" || str == null) {
		return 0;
	}
	var ue = "";
	var per = "";
	var bytes = 0;
	ue = encodeURI(str);
	per = ue.match(/%/g);
	if (per != "" && per != null) {
		bytes = ue.length - per.length * 2;
	} else {
		bytes = ue.length;
	}
	return bytes;
}

/**
 * 対象要素（群）のうち、指定したバイト数を超えたvalueを
 * もつ要素がある場合、エラーメッセージを返す。
 *
 * elms:対象要素（群）
 * byte:入力上限バイト数 ※"def"の場合、480とする。
 */
function checkByteLength(elms, byte) {
	var checkByte = 480;
	if (byte != 480 && byte != "def") {
		checkByte = byte;
	}
	var message = "";
	for (var i=0; i<elms.length; i++) {
		var elm = $(elms).get(i);
		if (getByte($(elm).val()) > checkByte) {
			message += msgMst.num16;
			break;
		}
	}
	return message;
}
