from functools import wraps
from flask import g, session, request, redirect, url_for, render_template
import random


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect('/login')
        if not g.user.is_active:
            return redirect('/403')
        return f(*args, **kwargs)

    return decorated_function


def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None or g.user.is_admin == False:
            return redirect('/403')
        return f(*args, **kwargs)

    return decorated_function
