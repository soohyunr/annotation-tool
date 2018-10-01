from functools import wraps
from flask import g, session, request, redirect, url_for, render_template
import random


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('/login'))
        if not g.user.is_active:
            return render_template('403.html', g=g)
        return f(*args, **kwargs)

    return decorated_function


def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None or g.user.is_admin == False:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function
