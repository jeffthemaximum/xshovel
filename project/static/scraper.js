$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);
    
    chatsock.onmessage = function(message) {
        var data = message.data;
        var chat = $("#chat")
        var ele = $('<tr></tr>')

        if (data === "COMPLETE!") {
            chat.prepend(
                '<img src="http://new2.fjcdn.com/gifs/Everyday+i+m+shuffling_7d4fe9_3215136.gif">'
            )
        }
        ele.append(
            $("<td></td>").text(data)
        )  
        chat.prepend(ele)
    };

    // $("#chatform").on("submit", function(event) {
    //     var message = {
    //         handle: $('#handle').val(),
    //         message: $('#message').val(),
    //     }
    //     chatsock.send(JSON.stringify(message));
    //     $("#message").val('').focus();
    //     return false;
    // });
});