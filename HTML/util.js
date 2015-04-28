// Mostly Tested with recent versions of Safari 3.2.3, Firefox 3.0.8 on Mac &
// MS IE 8.0.6001.xx and Google Chrome 1.0.154.xx on Windows Vista on 2009-06-08

// Id is always unique within document tree so no list needed.
// Use pretty long names since there is no additional namespace set up in javascript.

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

function toggleShowHideByCheckBox(id1, id2, box) {
    // If checkbox is checked the element with id1 is visible and id2 not and vice versa.
    if (box.checked) {
        showById(id1)
        hideById(id2)
    } else {
        showById(id2)
        hideById(id1)
    }
    // var vis = (box.checked) ? "block" : "none";
    // document.getElementById(id).style.display = vis;
}

