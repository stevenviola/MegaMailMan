"""
Displays the template for the static index page.

If we had templateable values, we could pass them to our templace
"""

import jinja2
import os
import webapp2

class index(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render())

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)
app = webapp2.WSGIApplication(
    [('/', index)],
    debug=True
)
