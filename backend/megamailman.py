import endpoints
import json
import logging
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import ndb

from services.sendgrid import Sendgrid
from services.mailgun import Mailgun

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
Checks the request for common issues
Raises exceptions if there are issues
"""
def check_request(request):
    # Need to make sure there is a to 
    if not request.to or request.to is None:
        message = "No recipient in the too field"
        logging.error(message)
        raise endpoints.BadRequestException(message)

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
    These are all the fields required for sending mail
    """
    SEND_MAIL = endpoints.ResourceContainer(
        message_types.VoidMessage,
        to = messages.StringField(1, repeated=True),
        cc = messages.StringField(2, repeated=True),
        bcc = messages.StringField(3, repeated=True),
        sender = messages.StringField(4, required=True),
        subject = messages.StringField(5, required=True),
        body = messages.StringField(6)
    )
    
    """
    Endpoint for sending mail
    Takes the SEND_MAIL Fields and returns a SimpleResponse
    Adds the request to the database for processing later
    """
    @endpoints.method(SEND_MAIL, SimpleResponse,
        path='message', http_method='POST',
        name='mail.send')
    def send_email(self, request):
        # Check the request for common issues
        check_request(request)
        # Add the request to the DB
        mail_db = add_request_to_db(request)
        # Loop through the services and try to send a message
        services = {'sendgrid':Sendgrid(),'mailgun':Mailgun()}
        for service_name,service_obj in services.iteritems():
            mail_service = service_obj
            logging.info("Attempting to send mail using %s" % service_name)
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