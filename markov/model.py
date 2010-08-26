from google.appengine.ext import db

class MarkovUserV1(db.Model):
    atName = db.StringProperty()
    userSecret = db.StringProperty()
    userToken = db.StringProperty()
    pictureUrl = db.StringProperty()
    name = db.StringProperty()
    tweets = db.BlobProperty()
    generated = db.StringProperty(multiline=True)
