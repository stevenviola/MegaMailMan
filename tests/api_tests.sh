#!/bin/bash

# This needs to be the URL for the send api
API='http://localhost:8888/_ah/api/megamailman/v1/send'

# Error message to be displayed upon error
# $1 is response code received
# $2 is expected response code
exit_message() {
        echo "FAILURE with: $1. Expecting response code of $2" >&2
        # Set the exit code to be 2 for scripting error checks
        exit 2
}

# $1 is the fields to send to our API
# $2 is the expected response code
# $3 is the service to use for the request
validate_response () {
	echo "Testing $API?$1&services=$3"

	# -X POST - Set the request method to POST
	# -f Fail silently on server errors. Returns 22 as exit code
	# -s Don't show progress meter or error messages.
	# -o Write  output to /dev/null instead of stdout.
	# -w Defines what to display on stdout.
	response_code=`curl -X POST -f -s -o /dev/null -w '%{http_code}' "$API?$1&services=$3"`
	if [[ $response_code != $2 ]]; then
		exit_message $response_code $2
	fi
}

# Loop through specifying each service
# We need to ensure that all services behave the same 
# through the API so that it is transparent to the user
for service in {'sendgrid','mailgun','mandrill'}; do    
    # Test for invalid situations that we expect a 400 error on
    # No request data
    validate_response "" 400 $service
    
    # Body tests
    echo "No body set"
    validate_response "sender=from@example.com&subject=Example+Test&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 400 $service
    echo "Body empty"
    validate_response "sender=from@example.com&subject=Example+Test&body=&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 400 $service
    
    # Sender tests
    echo "Sender not set"
    validate_response "subject=Example+Test&body=Test+Body&cc=cc@example.com&to=to1@example.com&to=to2@example.com&service=" 400 $service
    echo "Sender has no value"
    validate_response "sender=&subject=Example+Test&body=Test+Body&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 400 $service
    echo "Sender is not a valid e-mail address"
    validate_response "sender=example.com&subject=Example+Test&body=Test+Body&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 400 $service
    echo "Setting multiple senders"
    validate_response "sender=from1@afsdasdfasfd.com&sender=from2@example.com&subject=Example+Test&body=Test+Body&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 200 $service

    # To tests
    echo "To not set"
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&cc=cc@example.com" 400 $service
    echo "To not valid email"
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&cc=cc@example.com&to=example.com&to=to2@example.com" 400 $service
    echo "To is empty for one value"
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&cc=cc@example.com&to=&to=to2@example.com" 400 $service

    # CC Tests
    echo "CC field is empty"
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&cc=&to=to1@example.com&to=to2@example.com" 400 $service

    # BCC Tests
    echo "CC field is empty"
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&bcc=&to=to1@example.com&to=to2@example.com" 400 $service


    # Tests that should work
    # Generic test. Most valid requests should look like this
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 200 $service

    # Test Bogus fields
    echo "Testing bogus fields"
    validate_response "sender=from@example.com&subject=Example+Test&testing=will+this+work&body=Test+Body&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 200 $service

    #Test sending HTML in the body
    validate_response "sender=from@example.com&subject=Example+Test&body=<b>HELLO+WORLD</b>&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 200 $service
    
    echo "Sender domain doesn't exist but we don't know that. This should go through"
    validate_response "sender=from@afsdasdfasfd.com&subject=Example+Test&body=Test+Body&cc=cc@example.com&to=to1@example.com&to=to2@example.com" 200 $service
    echo "Sender weird but valid e-mail address. This should work"
    validate_response "subject=Example+Test&body=Test+Body&sender=c.c%2B1@example.co.uk&to=to1@example.com&to=to2@example.com" 200 $service
    echo "Multiple CC fields. This is supported"
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&cc=cc@example.com&cc=cc2@example.com&to=to1@example.com&to=to2@example.com" 200 $service
    echo "CC weird but valid e-mail address. This should work"
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&cc=c.c%2B1@example.co.uk&to=to1@example.com&to=to2@example.com" 200 $service
    echo "CC not set. This should work since we don't require cc"
    validate_response "sender=from@example.com&subject=Example+Test&body=Test+Body&to=to1@example.com&to=to2@example.com" 200 $service
done
