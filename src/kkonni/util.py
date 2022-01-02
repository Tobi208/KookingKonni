from json import dumps
from os import remove
from os.path import join
from re import sub, split

from flask import current_app
from werkzeug.utils import secure_filename

from kkonni.db import get_db


def parse_form_static(form, uid):
    name = sub(r'[^\w\-]+', ' ', form['name']).strip()
    portions = int(float(form['portions']))
    ings = []
    i = 0
    while f'amount-{i}' in form:
        ings.append({
            'amount': float(form[f'amount-{i}']),
            'unit': sub(r'[^\w]+', ' ', form[f'unit-{i}']).strip(),
            'name': sub(r'[^\w\-]+', ' ', form[f'name-{i}']).strip(),
        })
        i += 1
    instructions = form['instructions']
    tags = sub(r'[^\w\-]+', ' ', form['tags']).strip()
    author = get_username(uid)

    keywords = ' '.join([name, tags, author, *[ing['name'] for ing in ings]])
    keywords = ' '.join(set(split(r'\s+|-', keywords))).lower()
    ings = dumps(ings)

    return name, portions, ings, instructions, tags, keywords


def update_image(cur, rid, files):
    if 'image' in files and files['image'].filename != '':
        file = files['image']
        filename = str(rid) + '-' + secure_filename(file.filename)
        file.save(join(current_app.config['IMAGE_DIR'], filename))
        q = 'UPDATE recipe SET image = ? WHERE rid = ?'
        cur.execute(q, (filename, rid))


def delete_image(image):
    if len(image) > 0:
        remove(join(current_app.config['IMAGE_DIR'], image))


def update_rating(rid):
    db = get_db()
    ratings = db.execute("SELECT rating FROM rating WHERE rid = ?", (rid,)).fetchall()
    new_rating = round(sum(r[0] for r in ratings) / len(ratings))
    db.execute("UPDATE recipe SET rating = ? WHERE rid = ?", (new_rating, rid))
    db.commit()
    return new_rating


def get_username(uid):
    return get_db().execute('SELECT username FROM user WHERE uid = ?', (uid,)).fetchone()[0]
