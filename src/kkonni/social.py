from flask import Blueprint, session, render_template

from kkonni.auth import login_required
from kkonni.db import get_db
from kkonni.util import get_userdata

bp = Blueprint("social", __name__, url_prefix="/social")


@bp.route('/user/<int:uid>')
@login_required
def profile(uid):
    """
    Show the profile page of a user.
    """

    cur = get_db().cursor()
    get = (uid,)

    username = cur.execute('SELECT username FROM user WHERE uid == ?', get).fetchone()[0]
    rs = cur.execute('SELECT rid, name, time, rating FROM recipe WHERE uid == ? ORDER BY name', get).fetchall()
    cs = cur.execute("""
        SELECT comment.cid, comment.rid, comment.comment, comment.time, recipe.name
        FROM comment
        INNER JOIN recipe
        ON comment.rid = recipe.rid
        WHERE comment.uid == ?
        ORDER BY comment.time DESC
    """, get).fetchall()
    ratings = cur.execute("""
        SELECT rating.rid, rating.rating, recipe.name
        FROM rating
        INNER JOIN recipe
        ON rating.rid = recipe.rid
        WHERE rating.uid == ?
        ORDER BY rating.rating DESC, recipe.name
    """, get).fetchall()

    ns = {}
    is_user = uid == session['uid']
    if is_user:
        ns = cur.execute(
            'SELECT nid, rid, cid, rating_id, time, message, seen FROM notification WHERE uid == ? ORDER BY time DESC',
            get).fetchall()
        cur.execute('UPDATE notification SET seen = 1 WHERE (uid == ? AND seen == 0)', get)
        get_db().commit()

    return render_template(
        'social/profile.html',
        u=get_userdata(session['uid']),
        username=username,
        is_user=is_user,
        ratings=ratings,
        rs=rs, cs=cs, ns=ns
    )


@bp.route('/users')
@login_required
def users():
    """
    Show list of all users.
    """

    cur = get_db().cursor()
    us = cur.execute("""
        SELECT 
          user.uid,
          user.username,
          (SELECT COUNT(recipe.rid) FROM recipe WHERE recipe.uid == user.uid) as recipes,
          (SELECT COUNT(comment.cid) FROM comment WHERE comment.uid == user.uid) as comments,
          (SELECT COUNT(rating.id) FROM rating WHERE rating.uid == user.uid) as ratings
        FROM user
        ORDER BY user.username
    """).fetchall()

    return render_template('social/users.html', u=get_userdata(session['uid']), us=us)
