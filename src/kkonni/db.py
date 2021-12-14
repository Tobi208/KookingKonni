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
    hashed_password = generate_password_hash(password)
    q = "INSERT INTO auth (username, password) VALUES (?, ?)"
    db.execute(q, (username, hashed_password))
    db.commit()

    click.echo(f'Registered new user: {username}')


@click.command('delete-user')
@click.option('--username', prompt='Username')
@with_appcontext
def init_delete_user_command(username):
    """
    Create new user.
    """
    db = get_db()
    q = "DELETE FROM auth WHERE username = ?"
    db.execute(q, (username,))
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
