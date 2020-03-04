import datetime
from flask_mongoengine import MongoEngine
import uuid
import hashlib
import logging

db = MongoEngine()





class Doc(db.Document):
    title = db.StringField(default='')
    text = db.StringField(default='')
    source = db.StringField(default='')
    seq = db.IntField(default=0)
    created_at = db.DateTimeField(default=datetime.datetime.now)
    type = db.StringField(default='v1')  # v1, mturk, v2

    meta = {
        'indexes': [
            'seq',

        ]
    }

    def dump(self):
        return {
            'title': self.title,
            'text': self.text,
            'id': str(self.id),
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

################################################################################################################
class User(db.Document):
    username = db.StringField(unique=True)
    password = db.StringField()
    salt = db.StringField()
    
    first_name = db.StringField()
    last_name = db.StringField()
    student_id = db.IntField()
    
    is_active = db.BooleanField(default=True)
    is_admin = db.BooleanField(default=False)
    
    
    political_category = db.StringField()
    turker_id = db.StringField()
    
    
    last_ip = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    accessed_at = db.DateTimeField(default=datetime.datetime.now)

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
    def make_active(self):
        self.is_active=True

        
################################################################################################################
class DocLog(db.Document):
    doc = db.ReferenceField(Doc)
    user = db.ReferenceField(User)
    ip = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': [
            'user',
        ]
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

    ip = db.StringField(default='0.0.0.0')
    """
    ### format ###
    basket = {
        'attribute_key': {
            'initial_value': 'attribute_value',
            'value': 'attribute_value',
            'memo': '',
            'reason': '',
        },
    }
    """

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
            'target_text': self.target_text,
            'basket': self.basket,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'memo': self.memo,
        }


class AnnotationReview(db.Document):
    doc = db.ReferenceField(Doc)
    annotation = db.ReferenceField(Annotation)
    user = db.ReferenceField(User)
    basket = db.DictField()

    ip = db.StringField(default='0.0.0.0')

    created_at = db.DateTimeField(default=datetime.datetime.now)
    updated_at = db.DateTimeField(default=datetime.datetime.now)

    meta = {
        'indexes': [
            ('user'),
        ]
    }

    def dump(self):
        return {
            'id': str(self.id),
            'user': str(self.user.id),
            'basket': self.basket,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
        }

    
    
####################################

class Reactions(db.Document):
    sent_id = db.StringField()
    likes = db.DictField(default = {})
    most = db.StringField()
    total_reacts = db.IntField(default = 0)
    
    
    
class Sentence(db.Document):
    user = db.ReferenceField(User)
    text = db.StringField()
    created_at = db.DateTimeField(default=datetime.datetime.now)
    is_root = db.BooleanField(default=False)
    parent_id = db.StringField()
    children = db.ListField(db.ReferenceField('self'))
    reacts = db.ReferenceField(Reactions)
    depth = db.IntField()
    
    
    def dump(self):
        return {
            'user': str(self.user.username),
            'text': str(self.text),
            'id': str(self.id),
            'depth': str(self.depth)
        }
    


