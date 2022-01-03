import functools

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for, escape
from werkzeug.security import check_password_hash, generate_password_hash

from kkonni.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

"""
Handles all authentication processes.
"""


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


def recipe_author(view):
    """
    View decorator that ensures that the request is from the recipe's author.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        rid = kwargs['rid']
        cur = get_db().cursor()
        r_uid = cur.execute('SELECT uid FROM recipe WHERE rid = ?', (rid,)).fetchone()[0]
        if 'uid' not in session or r_uid != session['uid']:
            return redirect(url_for('book.recipe', rid=rid))

        return view(**kwargs)

    return wrapped_view


def api_login_required(view):
    """
    View decorator that ensures that the request is from authorized user.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'uid' not in session:
            return jsonify({'text': 'Unknown user'}), 401

        return view(**kwargs)

    return wrapped_view


def api_recipe_author(view):
    """
    View decorator that ensures that the request is from the recipe's author.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'uid' not in session:
            return jsonify({'text': 'Unknown user'}), 401
        rid = kwargs['rid']
        cur = get_db().cursor()
        r_uid = cur.execute('SELECT uid FROM recipe WHERE rid = ?', (rid,)).fetchone()[0]
        if r_uid != session['uid']:
            return jsonify({'text': f'User must be author'}), 403

        return view(**kwargs)

    return wrapped_view


def api_comment_author(view):
    """
    View decorator that ensures that the request is from the comment's author.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'uid' not in session:
            return jsonify({'text': 'Unknown user'}), 401
        cid = kwargs['cid']
        cur = get_db().cursor()
        c_uid = cur.execute('SELECT uid FROM comment WHERE cid = ?', (cid,)).fetchone()[0]
        if c_uid != session['uid']:
            return jsonify({'text': f'User must be author'}), 403

        return view(**kwargs)

    return wrapped_view


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in a registered user by adding the user id to the session.
    """

    # match form info with registered database info
    if request.method == 'POST':

        # gather data from form
        username = escape(request.form['username'])
        password = request.form['password']

        # attempt to find user in database
        cur = get_db().cursor()
        user = cur.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        # give hints on wrong login
        if user is None:
            return render_template('auth/login.html', error='Benutzer existiert nicht')
        # redirect to registration if user has not been confirmed
        if user['registered'] == 0:
            return redirect(url_for('auth.register'))
        if not check_password_hash(user['password'], password):
            return render_template('auth/login.html', error='Falsches Passwort')

        # store the user id in a new session
        # and redirect if applicable
        session.clear()
        session['uid'] = user['uid']
        next_url = request.args.get('next')
        next_url = next_url if next_url else url_for('book.index')
        return redirect(next_url)

    return render_template('auth/login.html')


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Clear the current session, including the stored user id.
    """
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Confirm user registration on first login by changing the password.
    """

    if request.method == 'POST':

        # gather data from form
        username = escape(request.form['username'])
        password = request.form['password']
        password1 = request.form['password1']
        password2 = request.form['password2']

        # attempt to find user in database
        cur = get_db().cursor()
        user = cur.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        # give hints on wrong registration
        if user is None:
            return render_template('auth/register.html', error='Benutzer existiert nicht')
        if user['registered'] == 1:
            return render_template('auth/register.html', error='Benutzer bereits registriert')
        if not check_password_hash(user['password'], password):
            return render_template('auth/register.html', error='Falsches Einmalpasswort')
        if password1 != password2:
            return render_template('auth/register.html', error='Neues Passwort stimmt nicht überein')
        if password == password1:
            return render_template('auth/register.html', error='Neues Passwort muss anders sein')

        # register user in database
        q = 'UPDATE user SET password = ?, registered = ? WHERE username = ?'
        cur.execute(q, (generate_password_hash(password1), 1, username))
        get_db().commit()

        # log user in and redirect to index
        session.clear()
        session['uid'] = user['uid']
        return redirect(url_for('book.index'))

    return render_template('auth/register.html')
