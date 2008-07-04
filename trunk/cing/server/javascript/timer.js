// First used by JFD in Aqua web server

<!-- don't bother with this code when timer is absent -->
if (! document.getElementsByName('theTimer').item(0)) {
    return
}

var seconds = 0
var minutes = 0
var hours = 0
var timerID = setTimeout("showTime()",1000);

function showTime() { 
  seconds ++;
  if (seconds == 60) {
   seconds=0;
   minutes ++;
  }
  if (minutes == 60){
    minutes=0;
    hours ++;
  }
  if (hours == 24){
    hours = 0;
  }
  var timeValue =""+(hours)
  timeValue +=((minutes < 10) ? ":0" : ":")+minutes
  timeValue +=((seconds < 10) ? ":0":":")+seconds
  document.theTimer.theTime.value = timeValue;
  timerID = setTimeout("showTime()",1000);
}

function startTimer() { 
  timerID = setTimeout("showTime()",1000);
}

function stopTimer() {
    if (timerID) {
        clearTimeout(timerID);
        timerID  = 0;
    }
}

function resetTimer() {
   tStart = null;
   document.theTimer.theTime.value = "0:00:00";
}
