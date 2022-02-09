from datetime import datetime
from json import dumps
from os import remove
from os.path import join
from re import split, sub

from flask import current_app, escape
from werkzeug.utils import secure_filename

from kkonni.db import get_db

"""
Provides database, IO, parsing, and other utilities.
Not registered as an app.
"""


def update_image(rid, files, image):
    """
    Save an image file to the disk and register its path in the database.
    Remove old image if it is overwritten.
    """

    # check for existing image in form
    if 'image' in files and files['image'].filename != '':

        # secure name
        file = files['image']
        filename = str(rid) + '-' + secure_filename(file.filename)

        # delete old image first
        delete_image(image)

        # save to disk and register path in database
        file.save(join(current_app.config['IMAGE_DIR'], filename))
        cur = get_db().cursor()
        q = 'UPDATE recipe SET image = ? WHERE rid = ?'
        cur.execute(q, (filename, rid))
        get_db().commit()


def delete_image(image_file):
    """
    Delete an image from the disk.
    """
    if len(image_file) > 0:
        remove(join(current_app.config['IMAGE_DIR'], image_file))


def update_rating(rid):
    """
    Recalculate the rating of a recipe rounded to integer.
    """

    # calculate new rating
    db = get_db()
    ratings = db.execute("SELECT rating FROM rating WHERE rid = ?", (rid,)).fetchall()
    new_rating = int(round(sum(r[0] for r in ratings) / len(ratings)))

    # write changes to database
    db.execute("UPDATE recipe SET rating = ? WHERE rid = ?", (new_rating, rid))
    db.commit()

    return new_rating


def get_username(uid):
    """
    Fetch the username corresponding to a user id.
    """
    return get_db().execute('SELECT username FROM user WHERE uid = ?', (uid,)).fetchone()[0]


def parse_form(form, uid):
    """
    Parse the data from an edit/new recipe form.
    Sanitize input by escaping.
    """

    # recipe title
    name = escape(form['name']).strip()

    # number of portions the ingredients are for
    portions = int(float(escape(form['portions'])))

    # parse ingredients table containing amount, unit, and description
    ings = []
    ing_names = []
    i = 0
    while f'tb-ings-title-{i}' in form:
        title = escape(form[f'tb-ings-title-{i}'])
        data = []
        j = 0
        while f'amount-{i}-{j}' in form:
            ing_names.append(escape(form[f'name-{i}-{j}']).strip())
            data.append({
                'amount': escape(form[f'amount-{i}-{j}']),
                'unit': escape(form[f'unit-{i}-{j}']).strip(),
                'name': ing_names[-1],
            })
            j += 1
        ings.append({'title': title, 'data': data})
        i += 1

    # recipe instructions
    instructions = form['instructions']

    # tags that help to search for the recipe with words
    # that don't appear elsewhere
    tags = escape(form['tags']).strip()

    # author of the recipe never changes
    author = get_username(uid)

    # generate keywords to search the recipe by
    keywords = ' '.join([name, tags, author, *ing_names])
    keywords = sub(r'-|\(|\)|:|%|\d|,|\.|;|\?|=', '', keywords).lower()
    keywords = ' '.join(set(split(r'\s+|-', keywords)))

    # convert ingredients to json
    ings = dumps(ings)

    return name, portions, ings, instructions, tags, keywords


def timestamp_to_date(timestamp):
    """
    Convert an epoch timestamp to the configured date format.
    """
    return datetime.fromtimestamp(timestamp).strftime(current_app.config['DATE_FORMAT'])


def get_timestamp():
    """
    Returns the current epoch timestamp rounded.
    """
    return int(datetime.now().timestamp())


def get_userdata(uid):
    """
    Gather general data about a user.
    """

    cur = get_db().cursor()

    user_data = cur.execute("""
        SELECT user.uid,
               user.username,
               (SELECT COUNT(*)
                FROM notification
                WHERE notification.uid == ? AND notification.seen == 0)	as notifications
        FROM user
        WHERE user.uid == ?
    """, (uid, uid)).fetchone()

    return user_data
