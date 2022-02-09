import sqlite3
import json
import re


con = sqlite3.connect('kkonni.sqlite3')
cur = con.cursor()

# ingredients
recipes = [{'rid': t[0], 'ingredients': t[1]} for t in cur.execute('SELECT rid, ingredients FROM recipe').fetchall()]
for r in recipes:
    ingredients = json.loads(r['ingredients'])
    new_ingredients = [{'title': '', 'data': []}]
    for i in ingredients:
        all_empty = True
        for k, v in i.items():
            if (isinstance(v, float) and v == 0) or\
                    (isinstance(v, str) and (v == len(v) * '0' or any(s in v.lower() for s in ['stck', 'stück']))):
                i[k] = ''
            else:
                all_empty = False
        if all_empty:
            new_ingredients.append({'title': '', 'data': []})
        else:
            new_ingredients[-1]['data'].append(i)
    cur.execute('UPDATE recipe SET ingredients = ? WHERE rid = ?', (json.dumps(new_ingredients), r['rid']))
con.commit()

# keywords
recipes = [{'rid': t[0], 'keywords': t[1]} for t in cur.execute('SELECT rid, keywords FROM recipe').fetchall()]
for r in recipes:
    new_keywords = re.sub(r'-|\(|\)|:|%|\d|,|\.|;|\?|=', '', r['keywords'])
    new_keywords = re.sub(r'\s+', ' ', new_keywords).strip()
    cur.execute('UPDATE recipe SET keywords = ? WHERE rid = ?', (new_keywords, r['rid']))
con.commit()

# ratings
ratings = [{'id': t[0], 'rid': t[1], 'rating': t[2]} for t in cur.execute('SELECT id, rid, rating FROM rating').fetchall()]
for r in ratings:
    new_rating = r['rating'] * 2
    cur.execute('UPDATE rating SET rating = ? WHERE id = ?', (new_rating, r['id']))
con.commit()
ratings = [{'id': t[0], 'rid': t[1], 'rating': t[2]} for t in cur.execute('SELECT id, rid, rating FROM rating').fetchall()]
rids = set(r['rid'] for r in ratings)
for rid in rids:
    r_ratings = [r['rating'] for r in ratings if r['rid'] == rid]
    new_rating = int(round(sum(r_ratings) / len(r_ratings)))
    cur.execute('UPDATE recipe SET rating = ? WHERE rid = ?', (new_rating, rid))
con.commit()

# notifications
cur.execute('''CREATE TABLE "notification" (
        "nid"	INTEGER,
        "uid"	INTEGER NOT NULL,
        "rid"	INTEGER NOT NULL,
        "cid"	INTEGER,
        "rating_id"	INTEGER,
        "time"	INTEGER NOT NULL,
        "message"	TEXT NOT NULL,
        "seen"	INTEGER NOT NULL,
        PRIMARY KEY("nid")
    )''')
con.commit()
users = {t[0]: {'username': t[1]} for t in cur.execute('SELECT uid, username FROM user').fetchall()}
ratings = {t[0]: {'rid': t[1], 'uid': t[2], 'rating': t[3]} for t in cur.execute('SELECT * FROM rating').fetchall()}
comments = {t[0]: {'rid': t[1], 'uid': t[2], 'time': t[3], 'comment': t[4]} for t in cur.execute('SELECT * FROM comment').fetchall()}
recipes = {t[0]: {'uid': t[1], 'name': t[2], 'time': t[3]} for t in cur.execute('SELECT rid, uid, name, time FROM recipe').fetchall()}
notifications = []
for k, r in ratings.items():
    rid = r['rid']
    uid = recipes[rid]['uid']
    if uid == r['uid']:
        continue
    time = recipes[rid]['time']
    message = f"{users[r['uid']]['username']} hat '{recipes[rid]['name']}' mit {r['rating']} bewertet"
    n = {
        'uid': uid,
        'rid': rid,
        'rating_id': k,
        'time': time,
        'message': message
    }
    notifications.append(n)
for k, c in comments.items():
    rid = c['rid']
    uid = recipes[rid]['uid']
    if uid == c['uid']:
        continue
    time = c['time']
    message = f"{users[c['uid']]['username']} hat '{recipes[rid]['name']}' kommentiert:\n\n{c['comment']}"
    n = {
        'uid': uid,
        'rid': rid,
        'cid': k,
        'time': time,
        'message': message
    }
    notifications.append(n)
notifications.sort(key=lambda x: x['time'])
for n in notifications:
    special = 'rating_id' if 'rating_id' in n else 'cid'
    query = f'INSERT INTO notification (uid, rid, {special}, time, message, seen) VALUES (?, ?, ?, ?, ?, ?)'
    values = (n['uid'], n['rid'], n[special], n['time'], n['message'], 0)
    cur.execute(query, values)
con.commit()
