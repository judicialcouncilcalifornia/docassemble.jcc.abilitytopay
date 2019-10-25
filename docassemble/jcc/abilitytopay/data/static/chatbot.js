// CENSUS 2020 CHATBOT CODE
$(document).ready(function() {
    $(document.body).append($('<div name="chatbot" id="chatbot"></div>'));
    (function () {
        var deviceWidth = (window.innerWidth > 0) ? window.innerWidth : screen.width;
        var deviceHeight = (window.innerHeight > 0) ? window.innerHeight : screen.height;
        var frameWidth = (deviceWidth < 420) ? (deviceWidth - 30) : 500;
        var frameHeight = (deviceHeight < 830) ? (deviceHeight - 50) : 750;
        var IFrameDiv = document.createElement("div");
        var chatbotDiv = document.getElementById("chatbot");
        chatbotDiv.appendChild(IFrameDiv);
        IFrameDiv.outerHTML = "<div id='botDiv' style='z-index: 2000; height: 60px; position: fixed; bottom: 0; right: 10px;  background-color: #13293E'><div id='botTitleBar' style='height: 60px; width: " + frameWidth + "px; position:fixed; cursor: pointer;'></div><iframe width='" + frameWidth + "px' height='" + frameHeight + "px' src='https://jccatpchatbotwebprod.azurewebsites.net/chat.html'></iframe></div>";
        chatbotDiv.addEventListener('click', function (e) {
            e.target.matches = e.target.matches || e.target.msMatchesSelector;
            if (e.target.matches('#botTitleBar')) {
                var botDiv = document.querySelector('#botDiv');
                botDiv.style.height = botDiv.style.height == frameHeight + 'px' ? '60px' : frameHeight + 'px';
            };
        });
    }());
});