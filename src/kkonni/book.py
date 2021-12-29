from datetime import datetime
from json import loads, dumps
from os import remove
from os.path import join
from re import sub, split

from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from werkzeug.utils import secure_filename

from kkonni.auth import login_required
from kkonni.db import get_db

bp = Blueprint("book", __name__)


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    cur = get_db().cursor()
    rs = cur.execute("SELECT rid, name, image, rating, keywords FROM recipe ORDER BY rid").fetchall()

    search_words = ''
    if request.method == 'POST' and 'search' in request.form:
        search_words = request.form['search']

    h = {'new': True, 'edit': False, 'delete': False, 'search_words': search_words}
    return render_template('index.html', h=h, rs=rs)


@bp.route('/<int:rid>', methods=('GET', 'POST'))
@login_required
def recipe(rid):
    cur = get_db().cursor()

    if request.method == 'POST' and 'user-rating' in request.form:
        uid = session['uid']
        rating = int(request.form['user-rating'])
        rating_id = cur.execute('SELECT id FROM rating WHERE (rid = ? AND uid = ?)', (rid, uid)).fetchall()
        if len(rating_id) == 0:
            cur.execute('INSERT INTO rating (rid, uid, rating) VALUES (?,?,?)', (rid, uid, rating))
        else:
            cur.execute('UPDATE rating SET rating = ? WHERE id = ?', (rating, rating_id[0][0]))
        get_db().commit()
        _update_rating(rid)

    if request.method == 'POST' and 'user-comment' in request.form:
        uid = session['uid']
        time = int(datetime.now().timestamp())
        comment = request.form['user-comment']
        cur.execute('INSERT INTO comment (rid, uid, time, comment) VALUES (?,?,?,?)', (rid, uid, time, comment))
        get_db().commit()

    r = cur.execute('SELECT * FROM recipe WHERE rid = ?', (rid,)).fetchone()
    ingredients = loads(r['ingredients'])
    author = _get_username(r['uid'])
    time = datetime.fromtimestamp(r['time']).strftime(current_app.config['DATE_FORMAT'])
    r = dict(r) | {'ingredients': ingredients, 'author': author, 'time': time}
    cs = cur.execute('SELECT * FROM comment WHERE rid = ?', (rid,)).fetchall()
    cs = [dict(c) | {'time': datetime.fromtimestamp(c['time']).strftime(current_app.config['DATE_FORMAT']),
                     'author': _get_username(c['uid'])}
          for c in sorted(cs, key=lambda c: c['time'] * -1)]
    u = {'comments': [c['cid'] for c in cs if c['uid'] == session['uid']]}
    u_rating = cur.execute('SELECT rating FROM rating WHERE rid = ? AND uid = ?', (rid, session['uid'])).fetchall()
    u['rating'] = u_rating[0][0] if len(u_rating) > 0 else 0

    h = {'new': True, 'edit': True, 'delete': True, 'search_words': ''}
    return render_template('recipe/recipe.html', h=h, u=u, r=r, cs=cs)


@bp.route('/edit/<int:rid>', methods=('GET', 'POST'))
@login_required
def edit_recipe(rid):
    if request.method == 'GET' or 'edit' in request.form:
        cur = get_db().cursor()
        r = cur.execute('SELECT * FROM recipe WHERE rid = ?', (rid,)).fetchone()
        r = dict(r) | {'ingredients': loads(r['ingredients'])}

        h = {'new': True, 'edit': False, 'delete': True, 'search_words': ''}
        return render_template('recipe/edit_recipe.html', h=h, r=r)

    if request.method == 'POST':
        form = request.form

        cur = get_db().cursor()
        uid, image = cur.execute('SELECT uid, image FROM recipe WHERE rid = ?', (rid,)).fetchone()
        name, portions, ings, instructions, tags, keywords = _parse_form_static(form, uid)

        q = 'UPDATE recipe SET name = ?, portions = ?, ingredients = ?, instructions = ?, ' \
            'image = ?, tags = ?, keywords = ? WHERE rid = ?'
        cur.execute(q, (name, portions, ings, instructions, image, tags, keywords, rid))
        _update_image(cur, rid, request.files)
        get_db().commit()

        return redirect(url_for('book.recipe', rid=rid))


@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new_recipe():
    if request.method == 'GET' or 'new' in request.form:
        h = {'new': True, 'edit': False, 'delete': False, 'search_words': ''}
        return render_template('recipe/new_recipe.html', h=h)

    if request.method == 'POST':
        form = request.form

        cur = get_db().cursor()
        uid = session['uid']
        name, portions, ings, instructions, tags, keywords = _parse_form_static(form, uid)
        image = ''
        rating = 0
        time = int(datetime.now().timestamp())

        q = 'INSERT INTO recipe (name, portions, ingredients, instructions, image, uid, tags, keywords, rating, time)' \
            'VALUES (?,?,?,?,?,?,?,?,?,?)'
        cur.execute(q, (name, portions, ings, instructions, image, uid, tags, keywords, rating, time))
        rid = cur.lastrowid
        _update_image(cur, rid, request.files)
        get_db().commit()

        return redirect(url_for('book.recipe', rid=rid))


@bp.route('/delete/<int:rid>', methods=['POST'])
@login_required
def delete_recipe(rid):
    cur = get_db().cursor()
    image = cur.execute('SELECT image FROM recipe WHERE rid = ?', (rid,)).fetchone()[0]
    if len(image) > 0:
        remove(join(current_app.config['IMAGE_DIR'], image))
    cur.execute('DELETE FROM recipe WHERE rid = ?', (rid,))
    cur.execute('DELETE FROM comment WHERE rid = ?', (rid,))
    cur.execute('DELETE FROM rating WHERE rid = ?', (rid,))
    get_db().commit()

    return redirect(url_for('book.index'))


@bp.route('/delete/<int:rid>/c/<int:cid>', methods=['POST'])
@login_required
def delete_comment(rid, cid):
    cur = get_db().cursor()
    cur.execute('DELETE FROM comment WHERE cid = ?', (cid,))
    get_db().commit()

    return redirect(url_for('book.recipe', rid=rid))


def _parse_form_static(form, uid):
    name = sub(r'[^\w\-]+', ' ', form['name']).strip()
    portions = int(form['portions'])
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
    author = _get_username(uid)

    keywords = ' '.join([name, tags, author, *[ing['name'] for ing in ings]])
    keywords = ' '.join(set(split(r'\s+|-', keywords))).lower()
    ings = dumps(ings)

    return name, portions, ings, instructions, tags, keywords


def _update_image(cur, rid, files):
    if 'image' in files and files['image'].filename != '':
        file = files['image']
        filename = str(rid) + '-' + secure_filename(file.filename)
        file.save(join(current_app.config['IMAGE_DIR'], filename))
        q = 'UPDATE recipe SET image = ? WHERE rid = ?'
        cur.execute(q, (filename, rid))


def _update_rating(rid):
    db = get_db()
    ratings = db.execute("SELECT rating FROM rating WHERE rid = ?", (rid,)).fetchall()
    new_rating = round(sum(r[0] for r in ratings) / len(ratings))
    db.execute("UPDATE recipe SET rating = ? WHERE rid = ?", (new_rating, rid))
    db.commit()


def _get_username(uid):
    return get_db().execute('SELECT username FROM user WHERE uid = ?', (uid,)).fetchone()[0]
