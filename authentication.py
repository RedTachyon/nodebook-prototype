from os import path
import jwt
import datetime
import sqlite3 as sql
from flask import request

import config

ROOT = path.dirname(path.relpath(__file__))
DB_PATH = path.join(ROOT, 'nodedata.db')


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


def check_blacklist(auth_token, db_path=DB_PATH):
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


def check_email_exists(email, db_path=DB_PATH):
    con = sql.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT email FROM users WHERE email = ?", (email,))
    result = cur.fetchall()

    con.close()

    return True if len(result) > 0 else False


def recognize_user_logged_in():
    auth_token = request.headers.get('Authorization')

    if auth_token is None:
        response = {
            "status": "Failure",
            "message": "Need an Authorization header with the format: Bearer <token>",
            "role": None,
            "id": None,
            "user_id": None
        }
        return response

    try:
        token = auth_token.split(" ")[1]
    except IndexError:
        response = {
            "status": "Failure",
            "message": "Malformed auth token. Use the format: Bearer <token>",
            "role": None,
            "id": None,
            "user_id": None
        }
        return response

    user_id = decode_auth_token(token)
    if isinstance(user_id, str):
        response = {
            "status": "Failure",
            "message": "Wrong token",
            "role": None,
            "id": None,
            "user_id": None
        }
        return response

    response = {
        "status": "Success",
        "message": "Logged in",
        "user_id": user_id,
    }

    con = sql.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("SELECT student_id, teacher_id FROM users WHERE id = ?", (user_id,))
    ids = cur.fetchall()

    if len(ids) == 0:
        response = {
            "status": "Failure",
            "message": "No such user in the database",
        }

    return response
