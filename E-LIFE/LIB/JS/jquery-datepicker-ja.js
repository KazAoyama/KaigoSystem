/* Japanese initialisation for the jQuery UI date picker plugin. */
$(function(){
    $.datepicker.regional['ja'] = {
        closeText: '閉じる',
        prevText: '<前',
        nextText: '次>',
        currentText: '今日',
        monthNames: ['1月','2月','3月','4月','5月','6月',
        '7月','8月','9月','10月','11月','12月'],
        monthNamesShort: ['1月','2月','3月','4月','5月','6月',
        '7月','8月','9月','10月','11月','12月'],
        dayNames: ['日曜日','月曜日','火曜日','水曜日','木曜日','金曜日','土曜日'],
        dayNamesShort: ['日','月','火','水','木','金','土'],
        dayNamesMin: ['日','月','火','水','木','金','土'],
        weekHeader: '週',
        dateFormat: 'yy-mm-dd',
        firstDay: 0, // 週の最初の曜日を設定（0〜6 : 日曜日〜土曜日）
        isRTL: false,
        showMonthAfterYear: true, // 西暦年の後に月を出力
        yearSuffix: '年'}; // 西暦年の接尾語
});
 
/**
 * 和暦変換
 * @param int year
 * @param bool setting
 * @returns int | string
 */
function convert_wareki(year, setting){
    var result;
    if(setting === false){
        return year;
    } else if (year > 1988) {
        result = year - 1988;
        result = '平成 ' + result;
        return result;
    } else if (year > 1925) {
        result = year - 1925;
        result = '昭和 ' + result;
        return result;
    } else if (year > 1911) {
        result = y - 1911;
        result = '大正 ' + result;
        return result;
    } else if (year > 1867) {
        result = year - 1867;
        result = '明治 ' + result;
        return result;
    }
}
