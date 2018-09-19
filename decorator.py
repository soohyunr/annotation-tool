from functools import wraps
from flask import g, session, request, redirect, url_for
import random


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function
