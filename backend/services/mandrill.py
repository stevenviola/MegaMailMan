"""

Uses Mandrill API to send e-mails

"""

import config
import logging
import json
from google.appengine.api import urlfetch

class Mandrill():
    """
    Args:
    sender  | String | Required | The e-mail address of the sender of the e-mail
    to      | List   | Required | The address to send the message to
    subject | String | Required | The subject for the message
    body    | String | Required | The body text of the message
    cc      | List   | Optional | cc recipients to include on e-mail
    bcc     | List   | Optional | bcc recipients to include on e-mail

    Returns:
    True on success
    False on failure
    """
    def send_mail(self,sender,to,subject,body,cc=None,bcc=None):
        # Define recipients that can be comma separated if a list
        recipents = {'to':to,'cc':cc,'bcc':bcc}
        url = "%s/messages/send.json" % (config.mandrill['url'])
        payload = {
            'key':config.mandrill['key'],
            'message':{
                'from_email':sender,
                'subject':subject,
                'text':body,
                'to':[]
            }
        }
        for key,value in recipents.iteritems():
            # Ensure the value is set and not None
            if value and value is not None:
                # Append the payloads with an array of the recipients
                for recipients in value:
                    payload['message']['to'].append({'email':recipients,'type':key})
        payload_encoded = json.dumps(payload)
        logging.info("Sending mail with the following url: %s" % url)
        logging.info("Adding the following payload: %s" % payload_encoded)
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
            return_array = json.loads(result.content)
            for email in return_array:
                # If the e-mail is not sent, we need to return False
                if email['status'] != 'sent':
                    logging.warning("Email to %s encountered an issue. The status is %s and the reason for rejection is %s" % (
                        email['email'],
                        email['status'],
                        email['reject_reason'])
                    )
                    return False
            # If all of the returned status messages are sent, then we're good
            return True
        else:
            logging.error("Sent e-mail and got back a %s response and a body of %s" % (result.status_code,result.content))
            return False
        