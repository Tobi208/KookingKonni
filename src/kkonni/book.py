from datetime import datetime
from json import loads
from os import remove
from os.path import join

from flask import Blueprint, render_template, session, redirect, url_for, request, current_app

from kkonni import util
from kkonni.auth import login_required, recipe_author
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

    return render_template('index.html', h={'search_words': search_words}, rs=rs)


@bp.route('/<int:rid>')
@login_required
def recipe(rid):
    cur = get_db().cursor()
    r = cur.execute('SELECT * FROM recipe WHERE rid = ?', (rid,)).fetchone()
    ingredients = loads(r['ingredients'])
    author = util.get_username(r['uid'])
    time = datetime.fromtimestamp(r['time']).strftime(current_app.config['DATE_FORMAT'])
    r = dict(r) | {'ingredients': ingredients, 'author': author, 'time': time}
    cs = cur.execute('SELECT * FROM comment WHERE rid = ?', (rid,)).fetchall()
    cs = [dict(c) | {'time': datetime.fromtimestamp(c['time']).strftime(current_app.config['DATE_FORMAT']),
                     'author': util.get_username(c['uid'])}
          for c in sorted(cs, key=lambda c: c['time'] * -1)]
    u = {'uid': session['uid']}
    u_rating = cur.execute('SELECT rating FROM rating WHERE rid = ? AND uid = ?', (rid, session['uid'])).fetchall()
    u['rating'] = u_rating[0][0] if len(u_rating) > 0 else 0

    return render_template('recipe/recipe.html', h={'search_words': ''}, u=u, r=r, cs=cs)


@bp.route('/edit/<int:rid>', methods=('GET', 'POST'))
@login_required
@recipe_author
def edit_recipe(rid):
    if request.method == 'GET':
        cur = get_db().cursor()
        r = cur.execute('SELECT * FROM recipe WHERE rid = ?', (rid,)).fetchone()
        r = dict(r) | {'ingredients': loads(r['ingredients'])}

        return render_template('recipe/edit_recipe.html', h={'search_words': ''}, r=r)

    if request.method == 'POST':
        form = request.form

        cur = get_db().cursor()
        uid, image = cur.execute('SELECT uid, image FROM recipe WHERE rid = ?', (rid,)).fetchone()
        name, portions, ings, instructions, tags, keywords = util.parse_form_static(form, uid)

        q = 'UPDATE recipe SET name = ?, portions = ?, ingredients = ?, instructions = ?, ' \
            'image = ?, tags = ?, keywords = ? WHERE rid = ?'
        cur.execute(q, (name, portions, ings, instructions, image, tags, keywords, rid))
        util.update_image(cur, rid, request.files)
        get_db().commit()

        return redirect(url_for('book.recipe', rid=rid))


@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new_recipe():
    if request.method == 'GET':
        return render_template('recipe/new_recipe.html', h={'search_words': ''})

    if request.method == 'POST':
        form = request.form

        cur = get_db().cursor()
        uid = session['uid']
        name, portions, ings, instructions, tags, keywords = util.parse_form_static(form, uid)
        image = ''
        rating = 0
        time = int(datetime.now().timestamp())

        q = 'INSERT INTO recipe (name, portions, ingredients, instructions, image, uid, tags, keywords, rating, time)' \
            'VALUES (?,?,?,?,?,?,?,?,?,?)'
        cur.execute(q, (name, portions, ings, instructions, image, uid, tags, keywords, rating, time))
        rid = cur.lastrowid
        util.update_image(cur, rid, request.files)
        get_db().commit()

        return redirect(url_for('book.recipe', rid=rid))
