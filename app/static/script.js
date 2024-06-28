function change(val) {
    if (val == "username") {
        document.getElementById("username_div").style.display = "block";
        document.getElementById("email_div").style.display = "none";
    } else {
        document.getElementById("email_div").style.display = "block";
        document.getElementById("username_div").style.display = "none";
    }
}