/*
Initialize the MegaMailMan API using gapi
*/
function init(){
    apiRoot = '//' + window.location.host + '/_ah/api';
    gapi.client.load('megamailman', 'v1',function() {
        console.log("MegaMailMan should be loaded now");
        $('#email-submit').removeAttr('disabled');
    }, apiRoot);
}

/*
This function takes the data from the form, and sends it to the API

The to, cc, and bcc fields are all arrays
Sender, subject and body are strings

If the request goes through without a hitch, then the 
form is emptied, and an alert is popped up

If there is an error, it will keep everything in the form and pop up an alert
*/
function send_mail(sender,to,cc,bcc,subject,body,services) {
    gapi.client.megamailman.mail.send({
        sender:sender,
        to:to,
        cc:cc,
        bcc:bcc,
        subject:subject,
        body:body,
        services:services
    }).then(function(resp) {
        if (!resp.code) {
            // Good Response from API
            // empty the form values
            console.log("Sent e-mail using: "+resp.result.service);
            $('.email-input').val('');
            $('#email-submit').removeAttr('disabled');
            add_alert('success',"Sent e-mail using "+resp.result.service);
        }
    }, function(reason) {
        console.log("Got an error");
        // We got an error
        // Undisable the submit button to try again
        $('#email-submit').removeAttr('disabled');
        console.log("Error sending e-mail. Reason is: "+reason.result.error.message);
        add_alert('danger',"Error sending e-mail. Got error: "+reason.result.error.message);
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
        var sender  = $('.mail-from').val();
        var subject = $('.mail-subject').val();
        var body    = $('.mail-body').val();
        var to      = $('.mail-to').map(make_array_from_fields).get();
        var cc      = $('.mail-cc').map(make_array_from_fields).get();
        var bcc     = $('.mail-bcc').map(make_array_from_fields).get();
        var services= $('input:checkbox:checked.service-selector').map(make_array_from_fields).get();
        send_mail(sender,to,cc,bcc,subject,body,services);
    } else {
        console.log('Form not valid');
    }
});

/*
Used for the map function on the form items that need to 
be converted to an array. Makes sure the values are not 
empty, and it not, returns them to map to become an array
*/
function make_array_from_fields() {
    var ret = this.value.trim()
    if ( ret != '' ) {
        return ret
    } 
}

/*
Renders an alert in the alert-popup div with the type
and message passed through to the function
*/
function add_alert(type,message) {
    alert = "<div class='alert alert-"+type+" alert-dismissible' role='alert'>"+
    "   <button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span></button>"+
        message+
    "</div>";
    $('#alert-popup').html(alert);
}

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
        var remove_button = "<button class='remove-field btn btn-default' type='button'><span class='glyphicon glyphicon-minus-sign' aria-hidden='true'></span></button>"
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
    /*
    Validate the Subject and From fields
    To, cc, and bcc difficult to validate 
    because there can be so many
    */
    $('#email-form').validate({
        rules: {
            subject: {
                minlength: 1,
                required: true
            },
            body: {
                required: true
            },
            from: {
                email: true,
                required: true
            },
        },
    });
});

