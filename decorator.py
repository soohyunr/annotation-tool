from functools import wraps
from flask import g, session, request, redirect, url_for
import random

from libs import mongo


# reference: https://medium.com/@devsudhi/how-to-create-a-middleware-in-flask-4e757041a6aa


def defaults(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db = mongo.get_db()
        g.users = mongo.to_dicts(db['user'].find({}))
        if ('user' in session) is False:
            session['user'] = mongo.to_dict(g.users[0])
        g.random = random.randrange(0, 1000000)
        return f(*args, **kwargs)

    return decorated_function
