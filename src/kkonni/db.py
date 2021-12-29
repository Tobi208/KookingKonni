import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    """
    Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DB_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    If this request connected to the database, close the connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('create-user')
@click.option('--username', prompt='Username')
@click.option('--password', prompt='Password')
@with_appcontext
def init_create_user_command(username, password):
    """
    Create new user.
    """
    db = get_db()
    users = [u[0] for u in db.execute("SELECT username FROM user").fetchall()]
    if username in users:
        click.echo(f'Username already exists.')
    else:
        hashed_password = generate_password_hash(password)
        q = "INSERT INTO user (username, password) VALUES (?, ?)"
        db.execute(q, (username, hashed_password))
        db.commit()
        click.echo(f'Registered new user: {username}')


@click.command('delete-user')
@click.option('--username', prompt='Username')
@with_appcontext
def init_delete_user_command(username):
    """
    Delete a user.
    """
    db = get_db()
    users = [u[0] for u in db.execute("SELECT username FROM user").fetchall()]
    if username not in users:
        click.echo(f'User not found: {username}')
    else:
        uid = db.execute("SELECT uid FROM user WHERE username = ?", (username,)).fetchone()[0]
        db.execute("DELETE FROM user WHERE username = ?", (username,))
        db.execute("DELETE FROM comment WHERE uid = ?", (uid,))
        rids = db.execute("SELECT rid FROM rating where uid = ?", (uid,)).fetchall()
        db.execute("DELETE FROM rating WHERE uid = ?", (uid,))
        db.commit()

        for rid in [rid[0] for rid in rids]:
            ratings = db.execute("SELECT rating FROM rating WHERE rid = ?", (rid,)).fetchall()
            new_rating = round(sum(r[0] for r in ratings) / len(ratings))
            db.execute("UPDATE recipe SET rating = ? WHERE rid = ?", (new_rating, rid))
        db.commit()

        click.echo(f'Deleted user: {username}')


def init_app(app):
    """
    Register database functions with the Flask app.
    This is called by the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_create_user_command)
    app.cli.add_command(init_delete_user_command)
