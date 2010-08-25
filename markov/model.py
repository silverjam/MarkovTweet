from google.appengine.ext import db

class MarkovUserV1(db.Model):
    atName = db.StringProperty()
    userSecret = db.StringProperty()
    userToken = db.StringProperty()
    pictureUrl = db.StringProperty()
    name = db.StringProperty()
    tweets = db.BlobProperty()
    generated = db.StringProperty()

"""
class V1_ValidEmail(db.Model):
    email = db.StringProperty()

class V1_TokenCounter(db.Model):
    counter = db.IntegerProperty()

class V1_Reminder(db.Model):
    token = db.StringProperty()
    message = db.TextProperty() 
    time  = db.DateTimeProperty()
"""
