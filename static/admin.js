
"use strict";
$('button#submit-button').bind('click', function () {
    var max = document.getElementById("classSelector").selectedIndex;
    $.getJSON('/_admin_relative_submit', {
        class_num: max,
        points: $('input[name="points_relative"]').val()
    }, function (data) {
        $("#result").text(data.result);
    });
    return false;
});
