from json import loads

from flask import Blueprint, render_template, session, redirect, url_for

from kkonni.auth import login_required
from kkonni.db import get_db

bp = Blueprint("book", __name__)

# https://flask.palletsprojects.com/en/2.0.x/quickstart/
# https://github.com/pallets/flask/tree/main/examples/tutorial
# https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/
# https://flask-assets.readthedocs.io/en/latest/index.html


@bp.route('/')
def index():
    cur = get_db().cursor()
    cur.execute("SELECT rid, name, image, rating, keywords FROM cookbook ORDER BY rid")
    recipes = cur.fetchall()

    return render_template('index.html', logged_in=session['is_logged_in'], recipes=recipes)


@bp.route('/<int:rid>')
def recipe(rid):
    cur = get_db().cursor()
    q = "SELECT * FROM cookbook WHERE rid = ?"
    cur.execute(q, (rid,))
    r = cur.fetchone()
    ingredients = loads(r['ingredients'])

    return render_template('recipe/recipe.html', logged_in=session['is_logged_in'], r=r, ings=ingredients)


@bp.route('/edit/<int:rid>')
@login_required
def edit_recipe(rid):
    cur = get_db().cursor()
    q = "SELECT * FROM cookbook WHERE rid = ?"
    cur.execute(q, (rid,))
    r = cur.fetchone()
    ingredients = loads(r['ingredients'])

    return render_template('recipe/edit_recipe.html', r=r, ings=ingredients)


@bp.route('/new')
@login_required
def new_recipe():

    return render_template('recipe/new_recipe.html')


@bp.route('/delete/<int:rid>')
@login_required
def delete_recipe(rid):

    # delete stuff

    return redirect(url_for('book.index'))
