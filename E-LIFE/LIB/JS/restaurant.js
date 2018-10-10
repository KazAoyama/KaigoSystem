//レストランipadボタンクリック時の書式変更
var linkTouchEnd = function(){

//            var se = $('#btnsound');
//            se[0].currentTime = 0;
//            se[0].play();


    thisAnchor = $(this);
    hoverRemove = function(){
      $("button").removeClass("btn_hover");
    }
    setTimeout(hoverRemove,200);
}

$(document).on('touchend','button',linkTouchEnd);


// 20150930 ios9無音不具合対応　↓
var audioContext;
var audioNode;
var playable;

$(function () {

   audioContext = new (window.AudioContext || window.webkitAudioContext)();
   audioNode = document.querySelector(".btnsound");
   playable = false;

});


// 20150930 ios9無音不具合対応　↑


$(document).on('touchstart','button', function(){
/*
            var se = $('#btnsound');
            se[0].currentTime = 0;
            se[0].play();
*/
// 20150930 ios9無音不具合対応　↓

  if (playable) {
    audioNode.load();
    audioNode.currentTime = 0;
    audioNode.play();

  } else {
    audioNode.addEventListener("canplay", function(event) {
alert(1);

      if(playable == false){

        playable = true;
        audioContext.createMediaElementSource(audioNode).connect(audioContext.destination);

      }

      audioNode.currentTime = 0;
      audioNode.play();

    });
    audioNode.load();

  }


// 20150930 ios9無音不具合対応　↑


  $(this).addClass("btn_hover");

});



//クッキーにデータ格納(保持期間：セッション中)
function setCookieData(name,val){

  document.cookie = name + '=' + encodeURIComponent(val) +';';

}


//クッキーにデータ格納(長期保持)
//※２０３８年問題（2038年以降の日付が正しく処理されないケースがある）というのがあるので、
//　一旦、2035年まで保持にする。2035年以降は90日。期間内（90日）にこの関数を再実行すれば無期限に相当。
function setCookieData_longterm(name,val){

  var date1,date2;  //日付データを格納する変数
  var kigen = 90;   //cookieの保持期限（90日）

  //現在の日付データを取得
  date1 = new Date();

  date2035 = new Date("2035/1/1");

  if(date1 >= date2035){
    // 2035年以降は念のため、保持期限を90日後にしておく。
    // 2035年以降も使い続けてたら、2038年問題対策の内容に合わせて修正検討必要

    //kigen日後の日付データを作成
    date1.setTime(date1.getTime() + kigen*24*60*60*1000);

  }else{
     //2038年問題回避のため、2034年までは以下の日付を保持期限とする。
    date1 = new Date("2035/12/31");
  }

  //GMT形式に変換して変数date2に格納する
  date2 = date1.toGMTString();

  document.cookie = name + '=' + encodeURIComponent(val) +';' + 'expires=' + date2;

  $("#dummy").val(date2);

}





$(function ($) {

  //ボタン二重押し回避
  //AJAXで生成したボタンにも対応したイベント定義
  $(document).on("click", ".send", (function(){

    $("button").attr("disabled", true);
  }));

});
