from flask import Blueprint, jsonify, session, request, url_for
from flask import current_app as ca

from kkonni import util
from kkonni.auth import api_login_required, api_comment_author, api_recipe_author
from kkonni.db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")

"""
Handle Fetch API requests during session for more responsive UX
"""


@bp.route('/add/c/<int:rid>', methods=['POST'])
@api_login_required
def add_comment(rid):
    """
    Add a new comment to a recipe from the user in session.
    """

    # gather data from request and other
    data = request.get_json()
    comment = data['comment']
    uid = session['uid']
    time = util.get_timestamp()

    # write changes to database
    cur = get_db().cursor()
    cur.execute('INSERT INTO comment (rid, uid, time, comment) VALUES (?,?,?,?)', (rid, uid, time, comment))
    get_db().commit()

    # gather data for response
    cid = cur.lastrowid
    time = util.timestamp_to_date(time)
    comment_author = util.get_username(uid)
    data = {
        'text': 'Comment was added',
        'cid': cid, 'uid': uid,
        'author': comment_author, 'time': time, 'comment': comment,
        'profile_url': url_for('social.profile', uid=uid)
    }

    # create notification for recipe author
    recipe = cur.execute('SELECT uid, name FROM recipe WHERE rid == ?', (rid,)).fetchone()[0]
    if uid != recipe['uid']:
        message = f"{comment_author} hat '{recipe['name']}' kommentiert:\n\n{comment}"
        cur.execute("INSERT INTO notification (uid, rid, cid, time, message, seen) VALUES (?, ?, ?, ?, ?, ?)",
                    (recipe['uid'], rid, cid, time, message, 0))
        get_db().commit()

    ca.logger.info('User %s (%s) added a comment (%s) to recipe %s (%s)', comment_author, uid, cid, recipe['name'] ,rid)
    return jsonify(data), 200


@bp.route('/delete/c/<int:cid>', methods=['POST'])
@api_comment_author
def delete_comment(cid):
    """
    Delete a comment from the user in session.
    """

    # write changes to database
    cur = get_db().cursor()
    cur.execute('DELETE FROM comment WHERE cid = ?', (cid,))
    cur.execute('DELETE FROM notification WHERE cid = ?', (cid,))
    get_db().commit()

    ca.logger.info('Deleted comment %s', cid)
    return jsonify({'text': f'Comment {cid} was deleted'}), 200


@bp.route('/rate/r/<int:rid>', methods=['POST'])
@api_login_required
def add_rating(rid):
    """
    Add or change a rating of a recipe from the user in session.
    """

    # gather data from request and other
    uid = session['uid']
    rating_author = util.get_username(uid)
    data = request.get_json()
    rating = int(data['rating'])
    cur = get_db().cursor()
    rating_id = cur.execute('SELECT id FROM rating WHERE (rid = ? AND uid = ?)', (rid, uid)).fetchall()

    # write changes to database, check if insert or update
    if len(rating_id) == 0:
        cur.execute('INSERT INTO rating (rid, uid, rating) VALUES (?,?,?)', (rid, uid, rating))
        get_db().commit()
        rating_id = cur.lastrowid
    else:
        rating_id = rating_id[0][0]
        cur.execute('UPDATE rating SET rating = ? WHERE id = ?', (rating, rating_id[0][0]))
        get_db().commit()

    # create notification for recipe author
    recipe = cur.execute('SELECT uid, name FROM recipe WHERE rid == ?', (rid,)).fetchone()[0]
    if uid != recipe['uid']:
        message = f"{rating_author} hat '{recipe['name']}' mit {rating}/10 bewertet"
        cur.execute("INSERT INTO notification (uid, rid, rating_id, time, message, seen) VALUES (?, ?, ?, ?, ?, ?)",
                    (recipe['uid'], rid, rating_id, util.get_timestamp(), message, 0))
        get_db().commit()

    # gather data for response
    new_rating = util.update_rating(rid)

    ca.logger.info('User %s (%s) rated recipe %s with rating %s', rating_author, uid, rid, rating)
    return jsonify({'rating': new_rating}), 200


@bp.route('/delete/r/<int:rid>', methods=['POST'])
@api_recipe_author
def delete_recipe(rid):
    """
    Delete a recipe from the user in session.
    """

    # get the image path and delete the file
    cur = get_db().cursor()
    image = cur.execute('SELECT image FROM recipe WHERE rid = ?', (rid,)).fetchone()[0]
    util.delete_image(image)

    # write changes to database
    cur.execute('DELETE FROM recipe WHERE rid = ?', (rid,))
    cur.execute('DELETE FROM comment WHERE rid = ?', (rid,))
    cur.execute('DELETE FROM rating WHERE rid = ?', (rid,))
    cur.execute('DELETE FROM notification WHERE rid = ?', (rid,))
    get_db().commit()

    ca.logger.info('Deleted recipe %s', rid)
    return jsonify({'text': f'Recipe {rid} was deleted'}), 200
