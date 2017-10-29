function changeCharCounter() {
    var counter = document.getElementById("counter");
    var comment = document.getElementById("comment");
    var len = comment.value.length;
    var maxLen = comment.maxLength;

    if (len > maxLen) {
        comment.value = comment.value.substring(0, maxLen);
        len = comment.length;
    }

    counter.innerHTML = maxLen - len;
}

function submitComment() {
    var comment = document.getElementById("comment").value;

    /* Add comment to db and display it below comment box */
}

function likePhoto(myBtn) {
    var btn = document.getElementById(myBtn);

    var btnText = btn.innerHTML;

    if (btnText == "Like") {
        btn.innerHTML = "Unlike";
    }
    else {
        btn.innerHTML = "Like";
    }
}


/* Show/Hide buttons change text */
function showDiv(myBtn, id) {
    var btn = document.getElementById(myBtn);

    var btnText = btn.innerHTML;

    var indOfSpace = btnText.indexOf(" ");
    var firstWord = "";
    var theRest = "";

    if (indOfSpace == -1) {
        firstWord = btnText;
    }
    else {
        firstWord = btnText.substr(0, indOfSpace);
        theRest = btnText.substr(indOfSpace);
    }

    if (firstWord == "Show") {
        firstWord = "Hide";
        document.getElementById(id).style.display = "block";
    }
    else {
        firstWord = "Show";
        document.getElementById(id).style.display = "none";
    }
    btn.innerHTML = firstWord + theRest;
}

function addFriend(id) {
    document.getElementById(id).style.visibility = 'hidden';
    document.getElementById("invFriend").value = id;
    document.getElementById('search_form').submit();
}

function setSearchFriendInputs(info) {
    if (info[0] != "None") {
        document.getElementById("sfFName").value = info[0];
    }
    if (info[1] != "None") {
        document.getElementById("sfLName").value = info[1];
    }
    if (info[2] != "None") {
        document.getElementById("sfEmail").value = info[2];
    }
}

function showAlbumCreate(myBtn) {
    var btn = document.getElementById(myBtn);
    // btn.style.display = "none";
    var displayStyle = document.getElementById("albumCreate").style.display

    if (displayStyle == "block") {
        document.getElementById("albumCreate").style.display = "none";
    }
    else {
        document.getElementById("albumCreate").style.display = "block";
    }
}

function validateSelection() {
    var all = document.getElementById("rbAll");
    var my = document.getElementById("cbMy");
    var friends = document.getElementById("cbFriends");

    if (all.checked == true) {
        all.checked = false
        my.checked = false;
        friends.checked = false;
    }
    else {
        all.checked = false;
    }
}