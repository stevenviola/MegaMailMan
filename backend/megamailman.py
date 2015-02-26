import endpoints
import json
import logging

import re
import config

from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.ext import ndb

from services.sendgrid import Sendgrid
from services.mailgun import Mailgun
from services.mandrill import Mandrill

"""
Define the Objects to be used for each Service.
"""
services = {
    'sendgrid':Sendgrid(),
    'mailgun' :Mailgun(),
    'mandrill':Mandrill()
}

"""
These are the fields of entities to store 
when we send an e-mail
"""
class MailEntity(ndb.Model):
    to = ndb.StringProperty(repeated=True)
    cc = ndb.StringProperty(repeated=True)
    bcc = ndb.StringProperty(repeated=True)
    sender = ndb.StringProperty()
    subject = ndb.StringProperty()
    body = ndb.TextProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    sent = ndb.BooleanProperty()
    service = ndb.StringProperty()

"""
This is the response to send back to the user 
with information about the API request they made
"""
class SimpleResponse(messages.Message):
    message= messages.StringField(1)
    service= messages.StringField(2)  

"""
Parses the email address passed and raises 
an exception if there is an issue
"""
def check_email(address,field):
    # Regex to check for email address
    # Regex by http://www.regular-expressions.info/email.html
    # Modified slightly for new TLD, including .co.uk
    parsed = re.search('^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z\.]{2,6}$',address,re.IGNORECASE)
    #logging.info("Parsed email field is %s" % parsed[1])
    if not parsed:
        # This isn't a valid e-mail address
        message = "The address %s in the %s field is invalid" % (address,field)
        logging.error(message)
        raise endpoints.BadRequestException(message)
    else:
        logging.info("Address %s is valid for %s field" % (address,field))

"""
Checks the request for common issues
Raises exceptions if there are issues
"""
def check_request(request):
    # Need to make sure these fields are present in the request
    required_fields = ['to','sender','subject','body']
    email_fields = ['to','cc','bcc']
    for req_field in required_fields:
        # Make sure the attribute is in the object
        # and is not none or empty string, else, raise exception
        attr = getattr(request, req_field,None)
        if not attr or attr is None or attr == "":
            message = "Nothing set for the %s field" % req_field
            logging.error(message)
            raise endpoints.BadRequestException(message)
        else:
            logging.info("Got field %s with value %s" % (req_field,attr))
    for email_field in email_fields:
        # Verify that these address follow the format for e-mails
        # Some e-mail providers accept non valid addresses and some don't
        # Need to conform with least common denominator
        attr = getattr(request, email_field,None)
        for address in attr:
            check_email(address,email_field)
    # The sender field is not repeatable, so 
    # need to check it separately here
    check_email(request.sender,'sender')
            

"""
Add the request to the DB before
trying to send the e-mail
"""
def add_request_to_db(request):
    mail = MailEntity(
        to      = request.to,
        cc      = request.cc,
        bcc     = request.cc,
        sender  = request.sender,
        subject = request.subject,
        body    = request.body,
        sent    = False,
    )
    mail.put()
    return mail


@endpoints.api(name='megamailman', version='v1')
class MegaMainMan(remote.Service):
    """
    These are all the fields we need for sending mail
    """
    SEND_MAIL = endpoints.ResourceContainer(
        message_types.VoidMessage,
        to       = messages.StringField(1, repeated=True),
        cc       = messages.StringField(2, repeated=True),
        bcc      = messages.StringField(3, repeated=True),
        sender   = messages.StringField(4, required=True),
        subject  = messages.StringField(5, required=True),
        body     = messages.StringField(6, required=True),
        services = messages.StringField(7, repeated=True)
    )
    
    """
    Endpoint for sending mail
    Takes the SEND_MAIL Fields and returns a SimpleResponse
    Adds the request to the database for processing later
    """
    @endpoints.method(SEND_MAIL, SimpleResponse,
        path='send', http_method='POST',
        name='mail.send')
    def send_email(self, request):
        # Check the request for common issues
        check_request(request)
        # Setting default value for services if it isn't set
        if not request.services or request.services is None:
            requested_services = config.enabled_services
        else:
            # Deduplicate any dups in user input data
            logging.info("Got request to process using certain services")
            requested_services = []
            for i in request.services:
                service_lower = i.lower()
                if service_lower in config.enabled_services:
                    if service_lower not in requested_services:
                        requested_services.append(service_lower)
                else:
                    logging.warning("Got requested service %s which we don't support" % service_lower)
        # Add the request to the DB
        # We currently don't use this, yet...
        mail_db = add_request_to_db(request)
        # Loop through the services and try to send a message
        for service_name in requested_services:
            logging.info("Going to try and send e-mail with %s" % service_name)
            # If the user requested a service that we don't support, skip
            if not service_name in services:
                logging.warning("We don't support %s. Skipping" % service_name)
                continue
            # Get the Object we need to call
            mail_service = services[service_name]
            ret = mail_service.send_mail(
                sender=request.sender,
                to=request.to,
                subject=request.subject,
                body=request.body,
                cc=request.cc,
                bcc=request.bcc
            )
            if ret:
                logging.info("Successfully sent e-mail using %s" % service_name)
                mail_db.sent=True
                mail_db.service=service_name
                mail_db.put()
                return SimpleResponse(
                    message="Sent Mail",
                    service=service_name
                )
            else:
                logging.warning("Couldn't send e-mail with %s. Will try with other services" % service_name)
        message = "Exhausted services to send email with"
        logging.error(message)
        raise endpoints.InternalServerErrorException(message);

api = endpoints.api_server([MegaMainMan])