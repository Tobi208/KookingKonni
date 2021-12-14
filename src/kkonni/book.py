from json import loads

from flask import Blueprint, render_template, session

from kkonni.auth import login_required
from kkonni.db import get_db

bp = Blueprint("book", __name__)

# https://flask.palletsprojects.com/en/2.0.x/quickstart/
# https://github.com/pallets/flask/tree/main/examples/tutorial
# https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/
# https://flask-assets.readthedocs.io/en/latest/index.html


@bp.route('/')
def open_index():
    cur = get_db().cursor()
    cur.execute("SELECT rid, name, image, rating, keywords FROM cookbook ORDER BY rid")
    recipes = cur.fetchall()

    return render_template('index.html', logged_in=session['is_logged_in'], recipes=recipes)


@bp.route('/<int:rid>')
def open_recipe(rid):
    cur = get_db().cursor()
    q = "SELECT * FROM cookbook WHERE rid = ?"
    cur.execute(q, (rid,))
    recipe = cur.fetchone()
    ingredients = loads(recipe['ingredients'])

    return render_template('recipe/recipe.html', logged_in=session['is_logged_in'], r=recipe, ings=ingredients)


@bp.route('/edit/<int:rid>')
@login_required
def open_edit_recipe(rid):
    cur = get_db().cursor()
    q = "SELECT * FROM cookbook WHERE rid = ?"
    cur.execute(q, (rid,))
    recipe = cur.fetchone()
    ingredients = loads(recipe['ingredients'])

    return render_template('recipe/edit_recipe.html', r=recipe, ings=ingredients)


@bp.route('/new')
@login_required
def open_new_recipe():

    return render_template('recipe/new_recipe.html')
