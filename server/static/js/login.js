(function() {
    //bind get code
    $( "#get_code" ).bind( "click", function() {
        username = $('[name="username"]')[1].value;
        console.log(username)
        $("#get_code").prop('disabled', true);
        $.ajax({
            method: "POST",
            url: "/get_code",
            data: { username: username }
        })
        .done(function( msg ) {
            console.log(msg)
            $("#get_code").prop('disabled', false);
            if (msg.res == -1) alert("使用者名稱必須為學號");
            else if (msg.res == -2) alert("帳號已經存在");
            else if (msg.res == -3) alert("無法寄出認證信請聯絡管理員");
            else {
                $("#get_code").prop('disabled', true);
                alert("認證碼已經寄到您的信箱")
            }
        });
    });
})();
