import datetime
from flask_mongoengine import MongoEngine

db = MongoEngine()


class Doc(db.Document):
    title = db.StringField()
    text = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
