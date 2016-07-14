var curr_level = 0;
function update() {
    "use strict";
    $.getJSON('/_get_current_level', {current_level: curr_level}, function (data) {
        var new_level, i;
        new_level = data.level;
        if (curr_level !== new_level) {
            if (curr_level !== 0) {
                $("#button" + curr_level.toString()).addClass('disabled');
                $("#button" + curr_level.toString()).addClass('btn-dis');
            } else {
                for (i = 1; i < 7; i += 1) {
                    $("#button" + i.toString()).addClass('disabled');
                }
            }
            if (new_level !== 0) {
                $("#button" + new_level.toString()).removeClass('disabled');
                $("#button" + new_level.toString()).removeClass('btn-dis');
            }
            curr_level = new_level;
        }
    });
    setTimeout("update()", 10000);
}
update();
