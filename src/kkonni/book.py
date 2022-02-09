from json import loads

from flask import Blueprint, render_template, session, redirect, url_for, request, escape, send_from_directory
from flask import current_app as ca

from kkonni import util
from kkonni.auth import login_required, recipe_author
from kkonni.db import get_db

bp = Blueprint("book", __name__)


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    """
    Shows all recipes and allows for dynamic filtering.
    """

    # gather all recipes
    cur = get_db().cursor()
    rs = cur.execute('SELECT rid, name, image, rating, keywords FROM recipe ORDER BY rid').fetchall()

    # can post search words to the page to pre-filter
    search_words = ''
    if request.method == 'POST' and 'search' in request.form:
        search_words = escape(request.form['search'])

    return render_template(
        'index.html',
        u=util.get_userdata(session['uid']),
        rs=rs,
        search_words=search_words
    )


@bp.route('/<int:rid>')
@login_required
def recipe(rid):
    """
    Shows all details of a recipe and allows for dynamic portions selection.
    """
    
    # gather all recipe details
    cur = get_db().cursor()
    r = cur.execute('SELECT * FROM recipe WHERE rid = ?', (rid,)).fetchone()
    if r is None:
        return redirect(url_for('book.index'))
    
    # convert raw data
    ingredients = loads(r['ingredients'])
    author = util.get_username(r['uid'])
    time = util.timestamp_to_date(r['time'])

    # complete recipe dict
    r = dict(r) | {'ingredients': ingredients, 'author': author, 'time': time}

    # gather all comments of the recipe
    # convert timestamp and author and sort by newest comments first
    cs = cur.execute('SELECT * FROM comment WHERE rid = ?', (rid,)).fetchall()
    cs = [dict(c) | {'time': util.timestamp_to_date(c['time']), 'author': util.get_username(c['uid'])}
          for c in sorted(cs, key=lambda c: c['time'] * -1)]

    # gather user id and their rating of the recipe
    u = dict(util.get_userdata(session['uid']))
    u_rating = cur.execute('SELECT rating FROM rating WHERE rid = ? AND uid = ?', (rid, session['uid'])).fetchall()
    u['rating'] = u_rating[0][0] if len(u_rating) > 0 else 0

    return render_template('recipe/recipe.html', u=u, r=r, cs=cs)


@bp.route('/edit/<int:rid>', methods=('GET', 'POST'))
@login_required
@recipe_author
def edit_recipe(rid):
    """
    GET  - show change recipe form and prefill it with recipe details.
    POST - process recipe changes. Only the author can change a recipe.
    """

    u = util.get_userdata(session['uid'])

    # simply gather recipe details
    if request.method == 'GET':
        cur = get_db().cursor()
        r = cur.execute('SELECT * FROM recipe WHERE rid = ?', (rid,)).fetchone()
        if r is None:
            return redirect(url_for('book.index'))

        r = dict(r) | {'ingredients': loads(r['ingredients'])}
        return render_template('recipe/edit_recipe.html', r=r)

    # process recipe changes and redirect to result
    if request.method == 'POST':

        # gather author and image file of the existing recipe
        cur = get_db().cursor()
        uid, image = cur.execute('SELECT uid, image FROM recipe WHERE rid = ?', (rid,)).fetchone()

        # parse the form, escape input
        name, portions, ings, instructions, tags, keywords = util.parse_form(request.form, uid)

        # write changes to database
        q = 'UPDATE recipe SET name = ?, portions = ?, ingredients = ?, instructions = ?, ' \
            'image = ?, tags = ?, keywords = ? WHERE rid = ?'
        cur.execute(q, (name, portions, ings, instructions, image, tags, keywords, rid))
        get_db().commit()

        # update image if applicable
        util.update_image(rid, request.files, image)

        ca.logger.info('User %s (%s) edited recipe %s (%s)', u['username'], u['uid'], name, rid)
        return redirect(url_for('book.recipe', u=u, rid=rid))


@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new_recipe():
    """
    GET  - show new recipe form.
    POST - process new recipe details.
    """
    u = util.get_userdata(session['uid'])

    # simply display form
    if request.method == 'GET':
        return render_template('recipe/new_recipe.html', u=u)

    # process new recipe details and redirect to result
    if request.method == 'POST':

        # gather details and set default values
        uid = session['uid']
        name, portions, ings, instructions, tags, keywords = util.parse_form(request.form, uid)
        image = ''
        rating = 0
        time = util.get_timestamp()

        # write changes to database
        cur = get_db().cursor()
        q = 'INSERT INTO recipe (name, portions, ingredients, instructions, image, uid, tags, keywords, rating, time)' \
            'VALUES (?,?,?,?,?,?,?,?,?,?)'
        cur.execute(q, (name, portions, ings, instructions, image, uid, tags, keywords, rating, time))
        get_db().commit()

        # if an image was uploaded, save it to static files and register in database
        rid = cur.lastrowid
        util.update_image(rid, request.files, image)

        ca.logger.info('User %s (%s) added recipe %s (%s)', u['username'], u['uid'], name, rid)
        return redirect(url_for('book.recipe', u=u, rid=rid))


@bp.route('/favicon.ico')
def favicon():
    """
    Route favicon.
    """
    return send_from_directory(ca.config['IMAGE_DIR'], 'favicon.png')
