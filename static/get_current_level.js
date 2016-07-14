var current_level = 0;
var current_state = 0;
function get_current_level() {
    "use strict";
    $.getJSON('/_get_current_level', {current_level: current_level}, function (data) {
        current_level = data.level;
        current_state = data.state;
    });
    setTimeout("get_current_level()", 5000);
}
get_current_level();