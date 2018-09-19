import datetime
from flask_mongoengine import MongoEngine
import uuid
import hashlib

db = MongoEngine()


class Doc(db.Document):
    title = db.StringField()
    text = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)


class User(db.Document):
    username = db.StringField()
    password = db.StringField()
    salt = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)

    def set_password(self, password):
        self.salt = uuid.uuid4().hex
        self.password = hashlib.sha256(self.salt.encode() + password.encode()).hexdigest()

    def check_password(self, password):
        return self.password == hashlib.sha256(self.salt.encode() + password.encode()).hexdigest()

    def dump(self):
        return {
            'id': self.id,
            'username': self.username,
        }
