"""
app.py allows devices running iris to make third party API calls, such as to
Twilio
"""
import os
from datetime import datetime, timedelta, time
import time
import uuid
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
    # we create tables here because this is theoretically the first time the
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
        return jsonify({"error": "recipient or message not provided!"}), 400
    elif not _validate_token(token):
        return jsonify({"error": "unauthorized token!"}), 401
    else:
        try:
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


if __name__ == "__main__":
    app.run(debug=True)

# things to keep an eye on:
# - that passing in the db link as 1 argument will properly call it
# - that the SERIAL type in postgresql will act as a properly self-generating id
#
