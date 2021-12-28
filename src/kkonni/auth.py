import functools

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash

from kkonni.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """
    View decorator that redirects anonymous users to the login page.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'uid' not in session:
            return redirect(url_for('auth.login', next=request.url))

        return view(**kwargs)

    return wrapped_view


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    Log in a registered user by adding the user id to the session.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM auth WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['uid'] = user['uid']
            next_url = request.args.get('next')
            next_url = next_url if next_url else url_for('book.index')
            return redirect(next_url)

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    """
    Clear the current session, including the stored user id.
    """
    session.clear()
    return redirect(url_for('auth.login'))
