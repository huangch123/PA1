function addPhoto() {
    var c = document.getElementById("photoCanvas");
    var ctxt = c.getContext("2d");
    ctxt.font = "30px Arial";
    ctxt.fillText("Photo goes here",10,50);
}

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