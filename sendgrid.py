"""

Uses Sendgrid API to send e-mails

"""

import config
import logging
import urllib
from google.appengine.api import urlfetch

class Sendgrid():
    """
    Args:
    sender  | String - The e-mail address of the sender of the e-mail
    to      | String/List - The address to send the message to
    subject | String - The subject for the message
    body    | String - The body text of the message
    cc      | String/List - Optional - cc recipients to include on e-mail
    bcc     | String/List - Optional - bcc recipients to include on e-mail

    Returns:
    True on success
    False on failure
    """
    def send_mail(self,sender,to,subject,body,cc=None,bcc=None):
        # Define recipients that can be comma separated if a list
        recipents = {'to':to,'cc':cc,'bcc':bcc}
        url = "%s/mail.send.json" % (config.sendgrid['url'])
        payload_encoded = urllib.urlencode({
            'api_user':config.sendgrid['user'],
            'api_key':config.sendgrid['password'],
            'from':sender,
            'subject':subject,
            'text':body
        })
        for key,value in recipents.iteritems():
            if value is not None:
                # If we have a list, it need to be in this stupid weird format
                # Format is 'to[]=a@mail.com[]=b@mail.com' according to docs
                if type(value) is list:
                    append_string = '&'.join([key+"[]="+urllib.quote_plus(s) for s in value])
                elif type(value) is str:
                    append_string = urllib.urlencode({key:value})
                else:
                    logging.error("Got unknown type of variable for %s" % key)
                    return False
                logging.info("Appending %s to the payload" % append_string)
                payload_encoded += '&%s' % append_string
        logging.info("Sending mail with the following url: %s" % url)
        logging.info("Sending with the following payload: %s" % payload_encoded)
        try:
            result = urlfetch.fetch(url,
                payload=payload_encoded,
                method=urlfetch.POST,
            )
        except: # If we get an exception here, return false
            logging.error("Got exception when accessing API")
            return False
        if result.status_code == 200:
            logging.info("E-mail has been sent. Got back %s" % result.content)
            return True
        else:
            logging.error("Sent e-mail and got back a %s response and a body of %s" % (result.status_code,result.content))
            return False
        