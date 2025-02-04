# auth.py
# Ojos Project
# 
# The aspect of the Iris API that works with authentication.
import uuid
import time
import psycopg2
import jwt
from flask import Blueprint
from .db import _create_tables
from flask import jsonify, request
from datetime import timedelta, time
from .app import DB, JWT_SECRET_KEY

bp = Blueprint('auth', __name__, url_prefix="/iris/auth")

@bp.route("/register/", methods=["POST"])
def register():
    _create_tables()
    # create tables here because this should be the first time the database will
    # be accessed. If they're first accessed someone else, call this function there

    try:
        user_id = uuid.uuid4()
        # user_id = request.json.get("id")
        # as of right now, no devices don't have unique ids to provide, so we
        # will generate a uuid here
        # todo: I REALLY THINK WE SHOULD BE GENERATING DEVICE IDS BY NOW

        token = _generate_token(str(user_id))

        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/update-token/", methods=["POST"])
def update_token():
    try:
        # user_id = request.json.get("id")
        user_id = uuid.uuid4()

        token = request.json.get("token")

        print("PURPLE")
        if _token_is_expired(token):
            print("RED")
            token = _generate_token(str(user_id))
            print(token)

        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _generate_token(user_id: str):
    # inserts the provided token into the tokens table. If it already exists,
    # it will simply update the token's expiration date
    expiration = time.time() + timedelta(days=30).total_seconds()
    # expiration is 30 days worth of seconds added to the current unix time
    # their token will expire in 30 days & a new one will need to be generated
    token = jwt.encode(
        {"id": user_id, "expiration": expiration},
        JWT_SECRET_KEY,
        algorithm="HS256"
    )

    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tokens (token, expiration_date) VALUES (%s, %s) ON CONFLICT (token) DO UPDATE SET expiration_date = EXCLUDED.expiration_date;", (token, expiration))

    return token


def _validate_token(token) -> bool:
    # this takes the token argument and checks the token table for a row that
    # contains this token. if one exists, then the token is valid.
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM tokens WHERE token = %s", (token,))
            if cursor.fetchone() is None:
                return False
            return True


def _token_is_expired(token) -> bool:
    # this takes the token argument and checks its expiration_date field,
    # returning true if it is greater than the current time (expired) and false
    # otherwise
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT expiration_date FROM tokens WHERE token = %s", (token,))
            expiration_date = cursor.fetchone()[0]
            return float(expiration_date) < time.time()


def _get_all_tokens():
    rows = []
    with psycopg2.connect(DB) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM tokens")
            rows = cursor.fetchall()

    return rows  # returns a list of dictionaries


def _log_token(token: str, timestamp: float, message_type: str):
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO token_log (token, timestamp, message_type) VALUES (%s, %s, %s)",
                           (token, timestamp, message_type))
