import datetime
from flask_mongoengine import MongoEngine
import uuid
import hashlib

db = MongoEngine()


class Doc(db.Document):
    title = db.StringField()
    text = db.StringField()
    source = db.StringField()
    seq = db.IntField()
    created_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': [
            'seq',
        ]
    }

    def dump(self):
        return {
            'title': self.title,
            'text': self.text,
            'seq': self.seq,
        }


class Sent(db.Document):
    doc = db.ReferenceField(Doc)
    index = db.IntField()
    text = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': [
            'doc',
        ]
    }

    def dump(self):
        return {
            'index': self.index,
            'text': self.text,
        }


class User(db.Document):
    username = db.StringField()
    password = db.StringField()
    salt = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    is_active = db.BooleanField(default=False)
    is_admin = db.BooleanField(default=False)
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


class Annotation(db.Document):
    doc = db.ReferenceField(Doc)
    sent = db.ReferenceField(Sent)
    user = db.ReferenceField(User)

    type = db.StringField(choices=('event', 'sentence'))

    index = db.IntField()
    anchor_offset = db.IntField()
    focus_offset = db.IntField()

    entire_text = db.StringField()
    target_text = db.StringField()

    basket = db.DictField()

    memo = db.StringField()

    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': [
            ('doc', 'user'),
            ('doc', 'user', 'type'),
        ]
    }

    def dump(self):
        return {
            'id': str(self.id),
            'doc': str(self.doc.id),
            'sent': str(self.sent.id),
            'user': str(self.user.id),
            'type': self.type,
            'index': self.index,
            'anchor_offset': self.anchor_offset,
            'focus_offset': self.focus_offset,
            'entire_text': self.entire_text,
            'target_text': self.target_text,
            'basket': self.basket,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'memo': self.memo,
        }
