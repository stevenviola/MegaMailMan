"""

Uses Mailgun API to send e-mails

"""

import config
import base64
import logging
import urllib
from google.appengine.api import urlfetch

class Mailgun():
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
        base64creds = base64.b64encode("%s:%s" % (config.mailgun['user'],config.mailgun['password']))
        url = "%s/%s/messages" % (config.mailgun['url'],config.mailgun['domain'])
        headers={"Authorization": 
            "Basic %s" % base64creds
        }
        payload = {
            'from':sender,
            'subject':subject,
            'text':body
        }
        for key,value in recipents.iteritems():
            if value is not None:
                # If we have a list, it need to be comma delimited
                if type(value) is list:
                    payload[key] = ','.join(value)
                elif type(value) is str:
                    payload[key] = value
                else:
                    logging.warning("Got unknown type of variable for %s" % key)
        payload_encoded = urllib.urlencode(payload)
        logging.info("Sending mail with the following url: %s" % url)
        logging.info("Adding the following payload: %s" % payload_encoded)
        try:
            result = urlfetch.fetch(url,
                payload=payload_encoded,
                method=urlfetch.POST,
                headers=headers,
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
		