(function() {
    //bind send request
    $("#add_user").bind( "click", function() {
        username = $("#new_user")[0].value;
        console.log(username)
        $("#add_user").prop('disabled', true);
        $.ajax({
            method: "POST",
            url: "/friend_request",
            data: { username: username }
        })
        .done(function( msg ) {
            $("#add_user").prop('disabled', false);
            if (msg.res == -1) alert("[錯誤] 你們目前已經為朋友");
            else if (msg.res == -2) alert("[錯誤] 你已經向用戶送出交友邀請");
            else if (msg.res == -3) alert("[錯誤] 用戶已經向你送出過交友邀請");
            else if (msg.res == -4) alert("[錯誤] 帳號不存在");
            else {
                alert("成功送出交友邀請");
            }
            location.reload();
        });
    });
    //bind update friend
    $('.update_friend').bind( "click", function() {
        var username = this.parentElement.getAttribute("user");
        var type_str = this.value;
        this.parentElement.remove();
        var type = -1;
        if (type_str == "Confirm") type = 0;
        if (type_str == "Delete Request") type = 1;
        if (type_str == "Cancel Request") type = 2;
        if (type_str == "Unfriend") type = 3;
        console.log(type_str);
        console.log(type);
        $.ajax({
            method: "POST",
            url: "/friend_update",
            data: { username: username, request_type: type }
        })
        .done(function( msg ) {
            console.log(msg)
            if (msg.res == -1) alert("[錯誤] 請重新整理");
            else {
                if (type_str == "Confirm") alert("以確認好友邀請");
                if (type_str == "Delete Request") alert("已刪除好友邀請");
                if (type_str == "Cancel Request") alert("已取消好友請求");
                if (type_str == "Unfriend") alert("已刪除好友");
            }
            location.reload();
        });
    });
})();
