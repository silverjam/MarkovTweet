#!/usr/bin/env python

import os
import sys
import logging
import zlib
import pickle

from pprint import pformat

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor-libs.zip'))

import AppEngineOAuth
from lilcookies import LilCookies
from twitter import Twitter
from twitter import OAuth

import mrkvtwt
import not_found
import model
import secrets
import cfg

consumer_key = "xLIRlOkGfNMtuJjkiTT8kw"
callback_url = "%s/oauth_callback"

def buildTemplatePath(name):
  return os.path.join(os.path.dirname(__file__), name)

class TemplatedMixin(object):

  def renderTemplate(self, name, **kwArgs):
    from google.appengine.ext.webapp import template
    fullPath = buildTemplatePath(name)
    kwArgs.update({'KEY' : consumer_key})
    self.response.out.write(template.render(fullPath, kwArgs))

head = """
  <head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8">
    <title>MarkovTweet</title>
    <script src="http://platform.twitter.com/anywhere.js?id=%(KEY)s&v=1" type="text/javascript"></script>
  <script type="text/javascript"> twttr.anywhere(function (T) { T.hovercards(); }); </script>
  </head>
""" % { 'KEY' : consumer_key }

template = "<!DOCTYPE html>\n<html>" + head + "<body>%(BODY)s</body></html>"

def getOAuth(url):
    return AppEngineOAuth.TwitterClient(consumer_key, secrets.consumer_secret, callback_url % url)

class OAuthCallbackHandler(webapp.RequestHandler, TemplatedMixin):

  def get(self):

    auth_token = self.request.get("oauth_token")
    auth_verifier = self.request.get("oauth_verifier")

    oauth_client = getOAuth(self.request.host_url)
    user_info = oauth_client.get_user_info(auth_token, auth_verifier=auth_verifier)

    username = user_info['username']

    d = model.MarkovUserV1(key_name=username)
    d.atName = username
    d.pictureUrl = user_info['picture']
    d.userSecret = user_info['secret']
    d.userToken = user_info['token']
    d.name = user_info['name']

    self.renderTemplate(cfg.OAUTH_TEMPLATE, USER=username)

    cookies = LilCookies(self, secrets.cookie_secret)
    cookies.set_secure_cookie('markov_twitter_username', username)

    d.put()

class AuthHandler(webapp.RequestHandler):
  def get(self):
    oauth_client = getOAuth(self.request.host_url)
    self.redirect(oauth_client.get_authorization_url())

def getStatuses(twitter, count):
  return reversed(twitter.statuses.user_timeline(count=count))

def setStatus(twitter, status):
  return twitter.statuses.update(status=status)

def fetch_tweets(userToken, userSecret):
  auth = OAuth(userToken, userSecret, consumer_key, secrets.consumer_secret)
  twitter = Twitter(auth=auth)
  return [ S['text'] for S in getStatuses(twitter, 1000) ]

class GenerateHandler(webapp.RequestHandler, TemplatedMixin):

  def get(self):

    cookies = LilCookies(self, secrets.cookie_secret)
    username = cookies.get_secure_cookie('markov_twitter_username')

    if username is None:
      self.error(404)
      self.response.out.write(not_found.geterr())
      return

    d = model.MarkovUserV1.get_by_key_name(username)
    if not d:
      self.error(404)
      self.response.out.write(not_found.geterr())
      return

    stored_tweets = d.tweets
    if not stored_tweets:
      texts = fetch_tweets(d.userToken, d.userSecret)
      d.tweets = zlib.compress(pickle.dumps(texts))
      d.put()
    else:
      texts = pickle.loads(zlib.decompress(stored_tweets))

    order, table = 7, {}

    for text in texts:
        table = mrkvtwt.makeTableN(order, text, table)

    for generated in mrkvtwt.markov(order, table):
      continue

    tweet = ''.join(generated)[:140]

    d.generated = tweet
    d.put()

    self.renderTemplate(cfg.GENERATE_DONE_TEMPLATE, POST=d.generated)


class PostHandler(webapp.RequestHandler):
  def get(self):

    cookies = LilCookies(self, secrets.cookie_secret)
    username = cookies.get_secure_cookie('markov_twitter_username')

    if not username:
      self.error(404)
      self.response.out.write(not_found.geterr())
      return

    d = model.MarkovUserV1.get_by_key_name(username)
    if not d:
      self.error(404)
      self.response.out.write(not_found.geterr())
      return

    if d.generated is None:
      self.response.out.write(template % { 'BODY' : '''<p>Nothing to post!</p>
<p><a href="/generate">Regenerate</a></p>
<p><a href="/">Go home</a></p>'''})
      return

    auth = OAuth(d.userToken, d.userSecret, consumer_key, secrets.consumer_secret)
    twitter = Twitter(auth=auth)
    result = setStatus(twitter, d.generated)

    self.response.out.write(template % { 'BODY' :
"""
<p>%(TIME)s</p>
<p>Cool, I went ahead and posted your <a href="http://twitter.com/%(USER)s/status/%(ID)s">tweet</a>:</p>
<blockquote>%(POST)s</blockquote>
<p><a href="/generate">Regenerate</a></p>
<p><a href="/">Go home</a></p>
""" % { 
  'TIME' : result['created_at'], 
  'USER' : username, 
  'ID' : result['id'], 
  'POST' : d.generated,
  }
})

    d.generated = None
    d.put()


class MainHandler(webapp.RequestHandler, TemplatedMixin):

  def get(self):

    cookies = LilCookies(self, secrets.cookie_secret)
    username = cookies.get_secure_cookie('markov_twitter_username')

    if username is None:
      self.renderTemplate(cfg.INDEX_TEMPLATE)
      return

    d = model.MarkovUserV1.get_by_key_name(username)
    if d is None:
      cookies.clear_cookie('markov_twitter_username')
      self.response.out.write(default)
      return

    self.renderTemplate(cfg.AUTHED_INDEX_TEMPLATE, USER=username)


def main():

  application = webapp.WSGIApplication([
      ('/', MainHandler),
      ('/authorize', AuthHandler),
      ('/oauth_callback', OAuthCallbackHandler),
      ('/generate', GenerateHandler),
      ('/post', PostHandler),
    ],
    debug=True)

  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()

# vim: ts=2:sts=2:sw=2:et:nocp:tw=999:bs=2:
