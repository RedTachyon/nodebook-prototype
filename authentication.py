from os import path
import jwt
import datetime
import sqlite3 as sql

import config

ROOT = path.dirname(path.relpath(__file__))


def encode_auth_token(user_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=90),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            config.SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e


def check_blacklist(auth_token, db_path=path.join(ROOT, 'nodedata.db')):
    con = sql.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT * FROM blacklist WHERE token = ?", (auth_token,))
    result = cur.fetchall()

    con.close()

    return True if len(result) > 0 else False


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, config.SECRET_KEY)
        is_blacklisted_token = check_blacklist(auth_token)
        if is_blacklisted_token:
            return 'Token blacklisted. Please log in again.'
        else:
            return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


def check_email_exists(email, db_path=path.join(ROOT, 'nodedata.db')):
    con = sql.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT email FROM users WHERE email = ?", (email,))
    result = cur.fetchall()

    con.close()

    return True if len(result) > 0 else False

