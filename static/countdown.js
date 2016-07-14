
var date = new Date("June 08, 2016 14:00:00"); //Month Days, Year HH:MM:SS
var now = new Date();
var diff = (date.getTime()/1000) - (now.getTime()/1000);

var clock = $('#timer').FlipClock(diff, {
    "countdown":true
});

(function () {
    function checkTime(i) {
        return (i < 10) ? "0" + i : i;
    }

    function startTime() {
        var today = new Date(),
            h = checkTime(today.getHours()),
            m = checkTime(today.getMinutes()),
            s = checkTime(today.getSeconds());
        document.getElementById('time').innerHTML = h + ":" + m + ":" + s;
        t = setTimeout(function () {
            startTime()
        }, 500);
    }
    startTime();
})();