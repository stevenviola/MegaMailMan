"""

Right now this just handles the requests

"""

import webapp2
from mailgun import Mailgun
from sendgrid import Sendgrid

class test_sending(webapp2.RequestHandler):
    def get(self):

        """
        mailgun = Mailgun()
        mailgun.send_mail(
            sender='stevenviola@gmail.com',
            to='stevenviola@gmail.com',
            subject='hello world',
            body='you fuckass',
            cc=['hello@yahoo.com','world@gmail.com']
        )
        """


        sendgrid = Sendgrid()
        sendgrid.send_mail(
            sender='stevenviola@gmail.com',
            to='stevenviola@gmail.com',
            subject='hello world',
            body='you fuckass',
            cc=['hello@yahoo.com','world@gmail.com']
        )

app = webapp2.WSGIApplication([
    ('/test', test_sending),
],
    debug=True
)
