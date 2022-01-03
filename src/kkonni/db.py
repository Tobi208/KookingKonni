import sqlite3
from os import remove
from os.path import join

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


@click.command('create-database')
@with_appcontext
def init_create_database():
    db = get_db()
    db.execute('''CREATE TABLE "comment" (
                "cid"	INTEGER,
                "rid"	INTEGER NOT NULL,
                "uid"	INTEGER NOT NULL,
                "time"	INTEGER NOT NULL,
                "comment"	TEXT NOT NULL,
                PRIMARY KEY("cid")
            )''')
    db.execute('''CREATE TABLE "rating" (
                "id"	INTEGER,
                "rid"	INTEGER NOT NULL,
                "uid"	INTEGER NOT NULL,
                "rating"	INTEGER NOT NULL,
                PRIMARY KEY("id")
            )''')
    db.execute('''CREATE TABLE "recipe" (
                "rid"	INTEGER,
                "uid"	INTEGER NOT NULL,
                "name"	TEXT NOT NULL,
                "rating"	INTEGER NOT NULL,
                "time"	INTEGER NOT NULL,
                "portions"	REAL NOT NULL,
                "ingredients"	TEXT NOT NULL,
                "instructions"	TEXT NOT NULL,
                "image"	TEXT,
                "tags"	TEXT NOT NULL,
                "keywords"	TEXT NOT NULL,
                PRIMARY KEY("rid")
            )''')
    db.execute('''CREATE TABLE "user" (
                "uid"	INTEGER,
                "username"	TEXT NOT NULL UNIQUE,
                "password"	TEXT NOT NULL,
                PRIMARY KEY("uid")
            )''')
    db.commit()
    click.echo('Database created')


@click.command('create-user')
@click.option('--username', prompt='Username')
@click.option('--password', prompt='Password')
@with_appcontext
def init_create_user_command(username, password):
    """
    Create new user.
    """

    # check if username is unique
    db = get_db()
    users = [u[0] for u in db.execute('SELECT username FROM user').fetchall()]
    if username in users:
        click.echo(f'Username already exists.')
        return

    # generate a hashed password and register user
    hashed_password = generate_password_hash(password)
    q = 'INSERT INTO user (username, password) VALUES (?, ?)'
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

    # check if user even exists
    db = get_db()
    users = [u[0] for u in db.execute('SELECT username FROM user').fetchall()]
    if username not in users:
        click.echo(f'User not found: {username}')
        return

    # gather the user's id and remove from user and user's comments
    uid = db.execute('SELECT uid FROM user WHERE username = ?', (username,)).fetchone()[0]
    db.execute('DELETE FROM user WHERE username = ?', (username,))
    db.execute('DELETE FROM comment WHERE uid = ?', (uid,))

    # remove the user's ratings
    rids = db.execute('SELECT rid FROM rating where uid = ?', (uid,)).fetchall()
    db.execute('DELETE FROM rating WHERE uid = ?', (uid,))
    db.commit()

    # recalculate rating of recipes the user rated
    for rid in [rid[0] for rid in rids]:
        ratings = db.execute("SELECT rating FROM rating WHERE rid = ?", (rid,)).fetchall()
        new_rating = round(sum(r[0] for r in ratings) / len(ratings))
        db.execute("UPDATE recipe SET rating = ? WHERE rid = ?", (new_rating, rid))
    db.commit()

    # remove user's recipes and other user's ratings and comments on them and the local image
    rids = db.execute('SELECT rid FROM recipe where uid = ?', (uid,)).fetchall()
    for rid in [rid[0] for rid in rids]:

        # delete image
        image = db.execute('SELECT image FROM recipe WHERE rid = ?', (rid,)).fetchone()[0]
        if len(image) > 0:
            remove(join(current_app.config['IMAGE_DIR'], image))

        # delete other user's ratings and comments
        db.execute('DELETE FROM rating WHERE rid = ?', (rid,))
        db.execute('DELETE FROM comment WHERE rid = ?', (rid,))

    # delete user's recipes
    db.execute('DELETE FROM recipe WHERE uid = ?', (uid,))
    db.commit()

    click.echo(f'Deleted user: {username}')


def init_app(app):
    """
    Register database functions with the Flask app.
    This is called by the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_create_database)
    app.cli.add_command(init_create_user_command)
    app.cli.add_command(init_delete_user_command)
