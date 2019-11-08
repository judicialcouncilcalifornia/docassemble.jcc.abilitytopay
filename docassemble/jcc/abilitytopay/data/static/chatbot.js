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
        div.outerHTML = "<div id='botDiv' style='z-index: 2000; border-radius: 20px; height: 60px; position: fixed; bottom: 0; right: 10px;  background: rgb(36, 79, 114, 0.95);'>" +
            "<div id='botTitleBar' style='height: 60px; width: " + frameWidth + "px; position:fixed; cursor: pointer;'></div>" +
            "<iframe id='iframeBot' width='" + frameWidth + "px' height='" + frameHeight + "px' src='https://jccatpchatbotwebprod.azurewebsites.net/chat.html'></iframe></div>";

        document.querySelector('body').addEventListener('click', function (e) {
            e.target.matches = e.target.matches || e.target.msMatchesSelector;
            if (e.target.matches('#botTitleBar')) {
                var botDiv = document.querySelector('#botDiv');
                frame = document.getElementById('iframeBot').contentWindow;
                if (botDiv.style.height == frameHeight + 'px') {
                    botDiv.style.height = '60px';
                    var postMessageData = { 'event': 'resize', 'action': 'minimize' };
                    frame.postMessage(JSON.stringify(postMessageData), window.location.href);
                } else {
                    botDiv.style.height = frameHeight + 'px';
                    var postMessageData = { 'event': 'resize', 'action': 'maximize' };
                    frame.postMessage(JSON.stringify(postMessageData), window.location.href);
                }
                botDiv.style.overflow = "hidden";
            };
        });
    }());
});