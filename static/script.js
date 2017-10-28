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
}