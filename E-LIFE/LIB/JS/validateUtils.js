/**
 *
 * validateUtils.js 
 * validation�`�F�b�N�Ɏg�p���鋤��js
 * true:�G���[����Afalse:�G���[�Ȃ��Ƃ���B
 * 
 */

/**
 * ���Ԕ�r�i���F����b�ɂ��Ĕ�r�j
 * sTime�F�J�n���ԁi�`���F�u00:00�v�j
 * eTime�F�I�����ԁi�`���F�u00:00�v�j
 *
 * �J�n����>�I�����Ԃ̏ꍇtrue��Ԃ��B
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
/**
 * �N����r�i�N�E�����r�j
 * sKikan�F�J�n�N���i�`���F�uyyyymm�v�j
 * eKikan�F�I���N���i�`���F�uyyyymm�v�j
 *
 * �J�n�N��>�I���N���̏ꍇtrue��Ԃ��B
 */

function kikanCompare(sKikan, eKikan){
	if ((sKikan == "" || sKikan == null) || 
		(eKikan == "" || eKikan == null)) {
		return false;
	}
	if (sKikan > eKikan) {
		return true;
	}
	return false;
}
var msgNumber = new Array();
	msgNumber["num"] = 0;
	msgNumber["pattern"] = 1;

/**
 * �����`�F�b�N
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
 * �����`�F�b�N�i�J���}�܂ށj
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
 * �����`�F�b�N�i�X���b�V���܂ށj
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
 * �����`�F�b�N�i�n�C�t���܂ށj
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
 * ���o���f�[�V�����̃t���O�ɂ���(ValidityState)
 * elm.validity.valueMissing	: �K�{�̃t�B�[���h�ɂ�������炸�l�������Ȃ��Ȃ�true ��Ԃ��A�����łȂ���� false ��Ԃ��܂��B
 * elm.validity.typeMismatch	: �������\���łȂ��Ȃ� true ��Ԃ��A�����łȂ���� false ��Ԃ��܂��B
 * elm.validity.patternMismatch	: �w��̃p�^�[���Ɉ�v���Ȃ��Ȃ� true ��Ԃ��A�����łȂ��Ȃ� false ��Ԃ��܂��B
 * elm.validity.tooLong			: �w��̍ő咷��蒷���Ȃ� true ��Ԃ��A�����łȂ���� false ��Ԃ��܂��B
 * elm.validity.rangeUnderflow	: �w��̍ŏ��l���Ⴂ�Ȃ� true ��Ԃ��A�����łȂ���� false ��Ԃ��܂��B
 * elm.validity.rangeOverflow	: �w��̍ő�l��荂����� true ��Ԃ��A�����łȂ���� false ��Ԃ��܂��B
 * elm.validity.stepMismatch	: step �����Ŏw�肳�ꂽ�K���Ɉ�v���Ȃ��Ȃ�true ��Ԃ��A�����łȂ���� false ��Ԃ��܂��B
 * elm.validity.customError		: �Ǝ��G���[�������Ă���Ȃ� true ��Ԃ��A�����łȂ���� false ��Ԃ��܂��B
 * elm.validity.valid			: �l�̑Ó����ɖ�肪�ЂƂ��Ȃ���� true ��Ԃ��A�����łȂ���� false ��Ԃ��܂��B
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
 * �w�荀�ځi�����j�����̃G���[�ł��邩�t���O��Ԃ��B
 */
function idealValidateCheck(elements, msgFlag){
	resetFlags();
	var flags = validityFlags;
	var elms = $(elements).get();
	for (var i=0; i<elms.length; i++) {
		var elm = $(elms).get(i);
		//���͌��
		if (elm.validity.badInput) {
			flags.badInput = true;
		}
		//�K�{�G���[
		if (elm.validity.valueMissing) {
			flags.valueMissing = true;
		}
		//�^�C�v�~�X�}�b�`�G���[
		if (elm.validity.typeMismatch) {
			flags.typeMismatch = true;
		}
		//�p�^�[���~�X�}�b�`�G���[
		if (elm.validity.patternMismatch) {
			flags.patternMismatch = true;
		}
		//�ő咷�G���[
		if (elm.validity.tooLong) {
			flags.tooLong = true;
		}
		//�ŏ��l�G���[
		if (elm.validity.rangeUnderflow) {
			flags.rangeUnderflow = true;
		}
		//�ő�l�G���[
		if (elm.validity.rangeOverflow) {
			flags.rangeOverflow = true;
		}
		//step�����G���[
		if (elm.validity.stepMismatch) {
			flags.stepMismatch = true;
		}
		//�Ǝ��G���[
		if (elm.validity.customError) {
			flags.customError = true;
		}
		//���̑��̃G���[
		if (!elm.validity.valid) {
			flags.valid = false;
		}
	}
	//���b�Z�[�W�쐬����Ȃ�A���b�Z�[�W��Ԃ��B
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
 * �t���O�Q���A���b�Z�[�W���쐬����B
 */
function createMessage(flags) {
	var message = "";
	//�K�{�G���[
	//if (flags.valueMissing) {
	//	message += msgMst.num7 + "\n";
	//}
	//�^�C�v�~�X�}�b�`�G���[
	if (flags.typeMismatch) {
		message += msgMst.num8 + "\n";
	}
	//�p�^�[���~�X�}�b�`�G���[
	if (flags.patternMismatch) {
		message += msgMst.num6 + "\n";
	}
	//�ő咷�G���[
	if (flags.tooLong) {
		message += msgMst.num9 + "\n";
	}
	//�ŏ��l�G���[
	if (flags.rangeUnderflow) {
		message += msgMst.num10 + "\n";
	}
	//�ő�l�G���[
	if (flags.rangeOverflow) {
		message += msgMst.num11 + "\n";
	}
	//step�����G���[
	if (flags.stepMismatch) {
		message += msgMst.num12 + "\n";
	}
	//�Ǝ��G���[
	if (flags.customError) {
		message += msgMst.num13 + "\n";
	}
	//���͒l����܂�
	//if (!flags.valueMissing || flags.badInput) {
	//	message += msgMst.num13 + "\n";
	//}
	//���̑��̃G���[
	if (!flags.valid && flags.badInput) {
			message += msgMst.num13 + "\n";
	}
	return message;
}
/**
 * �w�荀�ځi�����j�̃G���[�����b�Z�[�W�쐬���ĕԂ��B
 *
 * exp) elements = [{"elmId" : "�Ώۗv�f��id", "itemName" : "�Ώۍ��ږ�"},�E�E�E];
 */
 /*
function idealValidateCheckAndMessage(elements){
	for (var cnt=0; cnt<elements.length; cnt++) {
		var elm = document.getElementById(validateCheckElements[cnt].elmId);
		//�K�{�G���[
		if (elm.validity.valueMissing) {
			validityFlags.valueMissing = true;
		}
		//�^�C�v�~�X�}�b�`�G���[
		if (elm.validity.typeMismatch) {
			validityFlags.typeMismatch = true;
		}
		//�p�^�[���~�X�}�b�`�G���[
		if (elm.validity.patternMismatch) {
			validityFlags.patternMismatch = true;
		}
		//�ő咷�G���[
		if (elm.validity.tooLong) {
			validityFlags.tooLong = true;
		}
		//�ŏ��l�G���[
		if (elm.validity.rangeUnderflow) {
			validityFlags.rangeUnderflow = true;
		}
		//�ő�l�G���[
		if (elm.validity.rangeOverflow) {
			validityFlags.rangeOverflow = true;
		}
		//step�����G���[
		if (elm.validity.stepMismatch) {
			validityFlags.stepMismatch = true;
		}
		//�Ǝ��G���[
		if (elm.validity.customError) {
			validityFlags.customError = true;
		}
		//���̑��̃G���[
		if (!elm.validity.valid) {
			validityFlags.valid = false;
		}
	}
	return flags;
}
*/
/**
 * html�̋@�\�ɂ��o���f�[�V�����`�F�b�N���s��
 * �G���[�̕��ނ͂����A�Y���v�f���G���[�ł��邩�ǂ����̂ݕԂ��B
 * ���G���[�Ffalse
 *
 * element:�`�F�b�N�Ώۂ́uDOM�v�f�v
 */
function checkValidate(element) {
	return element.checkValidity();
}

/**
 * �K�{�`�F�b�N���s���A���b�Z�[�W��Ԃ��B
 *
 * element:�`�F�b�N�Ώ�
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
 * �K�{�`�F�b�N���s���A�G���[�ł��邩�Ԃ��B
 * �G���[�̏ꍇ�Atrue��Ԃ��B
 * 
 * element:�`�F�b�N�Ώ�
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
 * �K�{�`�F�b�N���s���A�G���[�ł��邩�Ԃ��B
 * �w�肵���v�f�̓��A��ł��K�{�G���[�ƂȂ�Ȃ������ꍇ�A
 * ���̎��_��false��Ԃ��B
 * �S�ĕK�{�G���[�̏ꍇ�Atrue��Ԃ��B
 * 
 * element:�`�F�b�N�Ώ�
 */
function isRequiredReturnFlagEx(element) {
	var error = true;
	var elms = $(element).get();
	for (var i=0; i<elms.length; i++) {
		var elm = $(elms).get(i);
		if (elm.validity.valueMissing && !elm.validity.badInput) {
			//�Ȃɂ����Ȃ�
		} else {
			error = false
			break;
		}
	}
	return error;
}
/**
 * ���ԓ���q�`�F�b�N
 *
 * sTimes: �J�n����
 * eTimes: �I������
 * separator: ��������؂�Z�p���[�^�[
 * itemName1: ���ږ��P
 * itemName2: ���ږ��Q
 */

function checkTime(sTimes, eTimes, separator, itemName1, itemName2) {
	var message = "";
	for (var i=0; i<sTimes.length; i++) {
		var sTime = $(sTimes).get(i);
		var eTime = $(eTimes).get(i);
		//�J�n�E�I�����ԍ����`�F�b�N
		var sTimeVal = $(sTime).val();
		var eTimeVal = $(eTime).val();
		//�J�n���Ԃ�23���䂩�I�����Ԃ�0����̏ꍇ�̓`�F�b�N���{���Ȃ�
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
 * �N�`�F�b�N�i�a��j
 *
 * �����������́u���v�̂�OK
 */
function checkNen(str) {
	if (str.match(/\d*|��/)) {
		return 
	}
}

/**
 * ������̃o�C�g����Ԃ�
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
 * �Ώۗv�f�i�Q�j�̂����A�w�肵���o�C�g���𒴂���value��
 * ���v�f������ꍇ�A�G���[���b�Z�[�W��Ԃ��B
 *
 * elms:�Ώۗv�f�i�Q�j
 * byte:���͏���o�C�g�� ��"def"�̏ꍇ�A480�Ƃ���B
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
