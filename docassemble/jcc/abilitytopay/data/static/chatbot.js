// CENSUS 2020 CHATBOT CODE
$(document).ready(function() {
    var frame = null;

    (function () {
        var deviceWidth = (window.innerWidth > 0) ? window.innerWidth : screen.width;
        var deviceHeight = (window.innerHeight > 0) ? window.innerHeight : screen.height;
        var frameWidth = (deviceWidth < 420) ? (deviceWidth - 20) : 440;
        var frameHeight = (deviceHeight < 830) ? (deviceHeight - 50) : 750;

        var div = document.createElement("div");
        document.getElementsByTagName('body')[0].appendChild(div);
        div.outerHTML = "<iframe class='iframeBot' id='iframeBot' width='"+frameWidth+"px' height='"+frameHeight+"px' style='position:fixed; bottom: 0; right: 10px; border-radius: 20px; border: 0; background: unset; z-index: 2000;' src='https://jccatpchatbotwebprod.azurewebsites.net/chat.html'></iframe>";
    }());

    function changeLanguageSelected(e) {
        var languageSelected = e.options[e.selectedIndex].value;
        var postMessageData = { type: 'state', language: languageSelected, county: '', questionId: '' };
        if (frame == null) {
            frame = document.getElementById('iframeBot').contentWindow;
        }

        if (frame != null) {
            frame.postMessage(JSON.stringify(postMessageData), window.location.href);
        }
    }
});
