import sqlite3
from flask import g
import datetime

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            "newsdb" , detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db():
    db = get_db()
    db = g.pop("db", None)
    if db is not None:
        db.close()

def get_user(email):
    db = get_db()
    return db.execute('SELECT * FROM user where email="{}";'.format(email)).fetchone()

def registered_user(user):
    db = get_db()
    result = db.execute('SELECT * FROM user where email="{}";'.format(user.email)).fetchone()
    if not result:
        return False
    return True

def create_user(user):
    db = get_db()
    db.execute('INSERT INTO user VALUES ("{}", "{}", "{}");'.format(user.email, user.name, ''))
    db.commit()

def get_latest_news():
    db = get_db()
    result = db.execute('SELECT * FROM news ORDER BY time DESC LIMIT 10;').fetchall()
    print(result)
    for i in result:
        print("HI", i)
    return result

def create_news(user, news):
    db = get_db()
    time = datetime.datetime.isoformat(datetime.datetime.now())
    db.execute('INSERT INTO news (email, news, time) VALUES ("{}", "{}", "{}");'.format(user.email, news, time))
    db.commit()

def delete_news(news_id):
    db = get_db()
    db.execute('DELETE FROM news where newsid={};'.format(news_id))

def get_news(user):
    db = get_db()
    return db.execute('SELECT * FROM news WHERE email="{}";'.format(user.email)).fetchall()
