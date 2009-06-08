// Id is always unique within document tree so no list needed.
function setDisplayById(id, displayAttribute) {
    var d = document.getElementById(id);
    if (d) {
        d.style.display = displayAttribute;
    }
}

function hideById(id) {
    setDisplayById(id, 'none');
}

function showById(id) {
    // alert('DEBUG: now in showDiv with argument: ' + divId)
    setDisplayById(id, '');
}

function showHideByCheckBox(id, box) {
    if (box.checked) {
        showById(id)
    } else {
        hideById(id)
    }
    // var vis = (box.checked) ? "block" : "none";
    // document.getElementById(id).style.display = vis;
}

// From http://www.tek-tips.com/faqs.cfm?fid=6620
// Trim function, trims all leading and trailing spaces:
String.prototype.trim = function() {
    return (this.replace(/^[\s\xA0]+/, "").replace(/[\s\xA0]+$/, ""))
}

// startsWith to check if a string starts with a particular character sequence:
String.prototype.startsWith = function(str) {
    return (this.match("^" + str) == str)
}

// endsWith to check if a string ends with a particular character sequence:
String.prototype.endsWith = function(str) {
    return (this.match(str + "$") == str)
}

// <!-- <table id="y" style='display:none'> -->
