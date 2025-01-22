"""
app.py allows devices running iris to make third party API calls, such as to
Twilio
"""
import os
from datetime import datetime, timedelta, time
import time
from collections import namedtuple
import uuid
import threading
import dotenv
import jwt
import psycopg2
import psycopg2.extras

from twilio.rest import Client
from flask import Flask, request, jsonify

dotenv.load_dotenv()

app = Flask(__name__)

DB = os.getenv("INTERNAL_DB_LINK")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_SID = os.getenv("TWILIO_AUTH_SID")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


@app.route("/iris/register/", methods=["POST"])
def register():
    _create_tables()
    # create tables here because this is theoretically the first time the
    # database will be accessed. If they're first accessed someone else, call
    # call this function there

    try:
        user_id = uuid.uuid4()
        # user_id = request.json.get("id")
        # as of right now, no devices don't have unique ids to provide, so we
        # will generate a uuid here

        expiration = time.time() + timedelta(days=30).total_seconds()

        # expiration is 30 days worth of seconds added to the current unix time
        # their token will expire in 30 days & a new one will need to be generated
        # todo: add check that their token hasn't expired
        # todo: also generate a new token with a new expiration date when it does expire
        # todo: also remove the old token from the table and add the new one
        token = jwt.encode(
            {"id": user_id, "expiration": expiration},
            JWT_SECRET_KEY,
            algorithm="HS256"
        )

        with psycopg2.connect(DB) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO tokens (token, expiration_date) VALUES (:token, :expiration_date);", {
                               "token": token, "expiration_date": expiration})

        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/iris/send_sms/", methods=["POST"])
def send_sms():
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_SID)

    data = request.get_json()
    recipient = data.get("to")
    message = data.get("message")
    token = request.headers.get('X-API-Key')

    if recipient == "" or message == "":
        # checks that all fields are filled
        return jsonify({"error": "recipient or message not provided!"}), 400
    elif not _validate_token(token):
        # checks if token is a valid token
        return jsonify({"error": "unauthorized token!"}), 401
    elif global_cache.contains_max(token):
        # checks if token is rate limited
        return jsonify({"error": "you've been rate limited"}), 
        # consider adding a "retry after" message (how to do?)
    else:
        try:
            global_cache.add_to_cache(token)
            message = twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=recipient
            )
            return jsonify({"status": "success", "sid": message.sid}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def _create_tables():
    schema_path = os.path.join(os.getcwd(), "schema.sql")
    schema_sql = ""
    with open(schema_path, "r+") as f:
        schema_sql = f.read()

    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)


def _validate_token(token):
    # this takes the token argument and checks the token table for a row that
    # contains this token. if one exists, then the token is valid.
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM tokens WHERE token = %s", (token,))
            if cursor.fetchone() is None:
                return False
            return True


def _get_all_tokens():
    rows = []
    with psycopg2.connect(DB) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM tokens")
            rows = cursor.fetchall()

    return rows  # returns a list of dictionaries


def start_updating_cache():
    # called in main to periodically update the cache in the background
    while True:
        time.sleep(60)
        global_cache.update_cache()


class Cache():
    Tokenlog = namedtuple("token", ["times_logged", "time_last_logged"])

    def __init__(self):
        # cache is a dictionary with tokens as keys and a tuple as a value.
        # the tuple contains how many calls the token has made and the time that
        # the last call was made.
        self.cache: dict[str, namedtuple] = {}
        self.lock = threading.Lock()

    def contains_max(self, token: str) -> bool:
        with self.lock:
            if self.cache_contains(token):
                return self.cache[token].times_logged == 10
            return False

    def add_to_cache(self, token: str):
        with self.lock:
            if self.cache_contains(token):
                self.cache[token] = self.Tokenlog(
                    self.cache[token].times_logged + 1, time.time())
            else:
                self.cache[token] = self.Tokenlog(1, time.time())

    def cache_contains(self, token: str) -> bool:
        with self.lock:
            return token in self.cache

    def update_cache(self):
        # this function must be periodically called to reset the cache
        with self.lock:
            self.cache = {
                token: token_log for token, token_log in self.cache.items() if (
                    token_log.time_last_logged + 1800) > time.time()
            }


global_cache = Cache()
# todo: put the Cache class in a separate .py file for interface purposes

if __name__ == "__main__":
    thread = threading.Thread(target=start_updating_cache, daemon=True)
    thread.start()

    app.run(debug=True)

# things to keep an eye on:
# - that passing in the db link as 1 argument will properly call it
# - that the SERIAL type in postgresql will act as a properly self-generating id
# - potentially, the Cache class won't be sufficient to handle a lot of traffic
# look into a caching library like redis in this case
