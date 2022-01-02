from datetime import datetime

from flask import Blueprint, jsonify, session, request, current_app

from kkonni import util
from kkonni.auth import api_login_required, api_comment_author, api_recipe_author
from kkonni.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route('/add/c/<int:rid>', methods=['POST'])
@api_login_required
def add_comment(rid):
    data = request.get_json()
    comment = data['comment']
    uid = session['uid']
    time = int(datetime.now().timestamp())
    cur = get_db().cursor()
    cur.execute('INSERT INTO comment (rid, uid, time, comment) VALUES (?,?,?,?)', (rid, uid, time, comment))
    get_db().commit()
    cid = cur.lastrowid

    time = datetime.fromtimestamp(time).strftime(current_app.config['DATE_FORMAT'])
    author = util.get_username(uid)
    data = {'text': 'Comment was added', 'cid': cid, 'uid': uid, 'author': author, 'time': time, 'comment': comment}

    return jsonify(data), 200


@bp.route('/delete/c/<int:cid>', methods=['POST'])
@api_comment_author
def delete_comment(cid):
    cur = get_db().cursor()
    cur.execute('DELETE FROM comment WHERE cid = ?', (cid,))
    get_db().commit()

    return jsonify({'text': f'Comment {cid} was deleted'}), 200


@bp.route('/rate/r/<int:rid>', methods=['POST'])
@api_login_required
def add_rating(rid):
    cur = get_db().cursor()
    uid = session['uid']
    data = request.get_json()
    rating = int(data['rating'])
    rating_id = cur.execute('SELECT id FROM rating WHERE (rid = ? AND uid = ?)', (rid, uid)).fetchall()
    if len(rating_id) == 0:
        cur.execute('INSERT INTO rating (rid, uid, rating) VALUES (?,?,?)', (rid, uid, rating))
    else:
        cur.execute('UPDATE rating SET rating = ? WHERE id = ?', (rating, rating_id[0][0]))
    get_db().commit()
    new_rating = util.update_rating(rid)

    return jsonify({'rating': new_rating}), 200


@bp.route('/delete/r/<int:rid>', methods=['POST'])
@api_recipe_author
def delete_recipe(rid):
    cur = get_db().cursor()
    image = cur.execute('SELECT image FROM recipe WHERE rid = ?', (rid,)).fetchone()[0]
    util.delete_image(image)
    cur.execute('DELETE FROM recipe WHERE rid = ?', (rid,))
    cur.execute('DELETE FROM comment WHERE rid = ?', (rid,))
    cur.execute('DELETE FROM rating WHERE rid = ?', (rid,))
    get_db().commit()

    return jsonify({'text': f'Recipe {rid} was deleted'}), 200
