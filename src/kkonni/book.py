from json import loads, dumps
from re import sub, split
from os.path import join
from os import remove

from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from werkzeug.utils import secure_filename

from kkonni.auth import login_required
from kkonni.db import get_db

bp = Blueprint("book", __name__)


@bp.route('/')
def index():
    cur = get_db().cursor()
    cur.execute("SELECT rid, name, image, rating, keywords FROM cookbook ORDER BY rid")
    recipes = cur.fetchall()

    return render_template('index.html', logged_in='uid' in session, recipes=recipes)


@bp.route('/<int:rid>')
def recipe(rid):
    cur = get_db().cursor()
    q = "SELECT * FROM cookbook WHERE rid = ?"
    cur.execute(q, (rid,))
    r = cur.fetchone()
    ingredients = loads(r['ingredients'])

    return render_template('recipe/recipe.html', logged_in='uid' in session, r=r, ings=ingredients)


@bp.route('/edit/<int:rid>', methods=('GET', 'POST'))
@login_required
def edit_recipe(rid):
    if request.method == 'GET':
        cur = get_db().cursor()
        q = "SELECT * FROM cookbook WHERE rid = ?"
        cur.execute(q, (rid,))
        r = cur.fetchone()
        ingredients = loads(r['ingredients'])

        return render_template('recipe/edit_recipe.html', r=r, ings=ingredients)

    if request.method == 'POST':

        form = request.form

        name, rating, portions, ings, instructions, tags = _parse_form_static(form)

        cur = get_db().cursor()
        author, image = cur.execute('SELECT author, image FROM cookbook WHERE rid = ?', (rid,)).fetchone()

        keywords = ' '.join([name, tags, author, *[ing['name'] for ing in ings]])
        keywords = ' '.join(set(split(r'\s+|-', keywords)))
        ings = dumps(ings)

        q = 'UPDATE cookbook SET name = ?, portions = ?, ingredients = ?, instructions = ?, ' \
            'image = ?, rating = ?, author = ?, tags = ?, keywords = ? WHERE rid = ?'
        cur.execute(q, (name, portions, ings, instructions, image, rating, author, tags, keywords, rid))
        _update_image(cur, rid, request.files)
        get_db().commit()

        return redirect(url_for('book.recipe', rid=rid))


@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new_recipe():
    if request.method == 'GET':
        return render_template('recipe/new_recipe.html')

    if request.method == 'POST':

        form = request.form

        name, rating, portions, ings, instructions, tags = _parse_form_static(form)

        cur = get_db().cursor()
        author = cur.execute('SELECT username FROM auth where uid = ?', (session['uid'],)).fetchone()[0]

        image = ''
        keywords = ' '.join([name, tags, author, *[ing['name'] for ing in ings]])
        keywords = ' '.join(set(split(r'\s+|-', keywords)))
        ings = dumps(ings)

        q = 'INSERT INTO cookbook (name, portions, ingredients, instructions, image, rating, author, tags, keywords)' \
            'VALUES (?,?,?,?,?,?,?,?,?)'
        cur.execute(q, (name, portions, ings, instructions, image, rating, author, tags, keywords))
        rid = cur.lastrowid
        _update_image(cur, rid, request.files)
        get_db().commit()

        return redirect(url_for('book.recipe', rid=rid))


def _parse_form_static(form):
    name = sub(r'[^\w\-]+', ' ', form['name']).strip()
    rating = int(form['rating'])
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

    return name, rating, portions, ings, instructions, tags


def _update_image(cur, rid, files):
    if 'image' in files and files['image'].filename != '':
        file = files['image']
        filename = str(rid) + '-' + secure_filename(file.filename)
        file.save(join(current_app.config['IMAGE_DIR'], filename))
        q = 'UPDATE cookbook SET image = ? WHERE rid = ?'
        cur.execute(q, (filename, rid))


@bp.route('/delete/<int:rid>')
@login_required
def delete_recipe(rid):
    cur = get_db().cursor()
    image = cur.execute('SELECT image FROM cookbook WHERE rid = ?', (rid,)).fetchone()[0]
    if len(image) > 0:
        remove(join(current_app.config['IMAGE_DIR'], image))
    q = 'DELETE FROM cookbook WHERE rid = ?'
    cur.execute(q, (rid,))
    get_db().commit()

    return redirect(url_for('book.index'))
