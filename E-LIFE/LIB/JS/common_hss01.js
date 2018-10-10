//クッキーにデータ格納(保持期間：セッション中)
// 引数１：名前　引数２：値
function setCookieData(name,val){

  document.cookie = name + '=' + encodeURIComponent(val) +';';

}

function setCookieRiyosha(val){
   setCookieData("ck_riyoshaid",val);
//   setCookieData("ck_room","");
}

/*
function setCookieRoom(val){
   setCookieData("ck_room",val);
   setCookieData("ck_riyoshaid","");
}
*/

$(function ($) {

  //ボタン二重押し回避
  //AJAXで生成したボタンにも対応
  $(document).on("click", ".send", (function(){
    $("button").attr("disabled", true);
  }));

});
