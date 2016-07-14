$(function () {
    "use strict";
    $('button#live-button').bind('click', function () {
        manual_mode = 0;
        var new_level, state, state_text;
        state = current_state;
        new_level = current_level;

        $("#rect" + curr_level.toString()).removeClass('rect-curr');
        $("#tri" + curr_level.toString()).removeClass('tri-curr');
        $("#rect" + new_level.toString()).addClass('rect-curr');
        $("#tri" + new_level.toString()).addClass('tri-curr');

        state_text = '';
        if (state === 'schwarz') {
            state_text = 'Instruction';
        }
        if (state === 'weiss') {
            state_text = 'Playing';
        }
        $.getJSON('/_update_level', {current_level: new_level, current_state: state}, function (datas) {
            $("#level-title").html(state_text + "<img style=\"float:right;\" alt=\"Color\" src=\"static/images/instruction.png\" />");
            $("#instruction-text").text(datas.instruction);
            $("#mapper").html(datas.map);
        });
        $("#live-button").addClass('invisible-button');
        $("#rect" + current_level_chosen.toString()).removeClass('rect-chosen');
        $("#tri" + current_level_chosen.toString()).removeClass('tri-chosen');
        current_level_chosen = 0;
        return false;
    });
});