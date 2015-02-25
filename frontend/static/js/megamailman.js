/*
Initlize the MegaMailMan API
*/
function init(){
    apiRoot = '//' + window.location.host + '/_ah/api';
    gapi.client.load('megamailman', 'v1',function() {
        console.log("MegaMailMan should be loaded now");
    }, apiRoot);
}

/*
This function takes the data from the form, and sends it to the API
*/
function send_mail(sender,to,cc,bcc,subject,body) {
    gapi.client.megamailman.mail.send({
        sender:sender,
        to:to,
        cc:cc,
        bcc:bcc,
        subject:subject,
        body:body
    }).then(function(resp) {
        if (!resp.code) {
            // Good Response from API
            // empty the form values
            $('.email-input').val('');
        }
    }, function(reason) {
        console.log("Got an error");
        // We got an error
        // Undisable the submit button to try again
        $('#email-submit').removeAttr('disabled');
    });
}

/*
Handles when an e-mail form is submitted
*/
$("#email-form").submit(function(e){
    e.preventDefault();
    console.log("Intercepted Submit")
    var is_validate=$("#email-form").valid();
    if(is_validate) {
        console.log("Looks good to process");
        // Disable out the form
        $('#email-submit').attr('disabled','disabled');
        var sender = $('.mail-from').val();
        var subject = $('.mail-subject').val();
        var body = $('.mail-body').val();
        var to = $('.mail-to').map(function() {
            return this.value;
        }).get();
        var cc = $('.mail-cc').map(function() {
            return this.value;
        }).get();
        var bcc = $('.mail-bcc').map(function() {
            return this.value;
        }).get();
        send_mail(sender,to,cc,bcc,subject,body);
        console.log(body);
    } else {
        console.log("Form not valid");
    }
});

/*
jQuery delegation to find when the user clicks on the plus button
and will add clone the parent and add to the grandparent
Need to empty the value on the cloned value, and add remove buttons to the fields
*/
$( "body" ).delegate( ".add-field", "click", function() {
    // Get the grand parent of the button
    var field = $(this).parent().parent();
    var parent = field.parent();
    var new_field = field.clone().appendTo(parent)
    $(new_field).find('input').val('');
    if($(new_field).find('.remove-field').length == 0) {
        // Since the original field didn't have the remove sign, add it
        var remove_button = "<button class='remove-field btn btn-default' type='button'>-</button>"
        field.find('.add-remove-btns').prepend(remove_button);
        new_field.find('.add-remove-btns').prepend(remove_button);
    }
});

/*
jQuery delegation to remove the grandparent of 
an element that is being removed
If there is only one field left, remove the remove button
*/
$( "body" ).delegate( ".remove-field", "click", function() {
    // Get the grand parent of the button
    var grandparent = $(this).parent().parent()
    var greatgrandparent = grandparent.parent()
    $(grandparent).remove()
    var remove_fields = $(greatgrandparent).find('.remove-field')
    if(remove_fields.length <= 1) {
        $(remove_fields).remove()
    }
});

$(document).ready(function () {
    $('#email-form').validate({
        rules: {
            subject: {
                minlength: 1,
                required: true
            },
            from: {
                email: true,
                required: true
            },
        },
    });
});

