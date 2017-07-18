//For getting CSRF token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//When submit is clicked
// $("#pasteAreaSubmitButton").click(function(e) {
function submitForm() {

    //Prevent default submit
    // e.preventDefault();

    // show the loading bar - change color just in case it was resubmitted after error
    document.getElementById("pasteAreaSubmitButtonText").style.display = "none";
    document.getElementById("pasteAreaSubmitButtonLoading").style.display = "block";
    document.getElementById("pasteAreaSubmitButton").style.background = "#000021";
    // prepare csrf token
    var csrftoken = getCookie('csrftoken');
    // get the data
    var records = $('#records').val();

    // clear old messages if this is a resubmit
    $("#errors_body").empty();
    $("#submissions_body").empty();

    //Send data  
    $.ajax({
        url: "thesisSubmission/",
        type: "POST", // http method
        data: {
            csrfmiddlewaretoken: csrftoken,
            // recaptcha:grecaptcha.getResponse(),
            records: records
        },
        // handle a successful response
        success: function(response) {
            // stop the loading circle
            document.getElementById("pasteAreaSubmitButtonText").style.display = "block";
            document.getElementById("pasteAreaSubmitButtonLoading").style.display = "none";

            // parse the json 
            my_response = JSON.parse(response);
            // // TODO check the response here and do something with it
            console.log(my_response);



            if (my_response.status == 1) {
                // recaptcha successful
                localStorage.setItem('canlink_submission', JSON.stringify(my_response));
                window.location.replace("/thesisSubmission")
            } else {
                // recaptcha error - someone tampered with the recaptcha code
                console.log("recaptcha error")
            }


        },

        // handle a non-successful response
        error: function(xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
            alert("SERVER ERROR"); // not related to recaptcha - just some other error
            // stop the loading circle
            document.getElementById("pasteAreaSubmitButtonText").style.display = "block";
            document.getElementById("pasteAreaSubmitButtonLoading").style.display = "none";
        }
    });
};


