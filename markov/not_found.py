#!/usr/bin/env python

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from google.appengine.ext.webapp import template


def tpl(fn):
  return os.path.join(os.path.dirname(__file__), fn)

def geterr():
    #return template.render(tpl('err404.html'), {})
    return "<html><body><h2>Not found (Markov Tweet)"

class ErrorFourOhFour(webapp.RequestHandler):
  def get(self):
    self.response.out.write(geterr())


def main():
  application = webapp.WSGIApplication([
    ('/.*', ErrorFourOhFour),
    ], debug=True)

  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()

# vim: ts=2:sts=2:sw=2:et:
