"""
app.py allows devices running iris to make third party API calls, such as to
Twilio
"""
import os
from datetime import datetime, timedelta, time
import time
import dotenv
import jwt
import psycopg2

from twilio.rest import Client
from flask import Flask, request, jsonify

dotenv.load_dotenv()

app = Flask(__name__)

# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_SID = os.getenv("TWILIO_AUTH_SID")
# TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_SID)

DB = os.getenv("INTERNAL_DB_LINK")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


@app.route("/iris/register/", methods=["POST"])
def register():
    _create_tables()
    # we create tables here because this is theoretically the first time the
    # database will be accessed. If they're first accessed someone else, call
    # call this function there

    try:
        user_id = request.json.get("id")
        # id_list = [] # GET VALID IDs FROM A LIST
        # if id in id_list:
        # if credentials are ever decided to be provided, validate here

        expiration = time.time() + timedelta(30).total_seconds()
        token = jwt.encode(
            {"id": user_id, "expiration": expiration},
            JWT_SECRET_KEY,
            algorithm="HS256"
        )

        # todo: store the token in the api's database here
        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _verify():
    ...


@app.route("/iris/send_sms/", methods=["POST"])
def send_sms():
    """
    data = request.get_json()
    recipient = data.get("to")
    message = data.get("message")

    if recipient == "" or message == "":
        return jsonify({"error" : "recipient or message not provided"}), 400
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
    """
    # UNCOMMENT WHEN TWILIO INTEGRATION/VERIFICATION IS CONFIRMED
    return jsonify({"status": "success", "sid": "SM1234"}), 200


def _create_tables():
    schema_path = os.path.join(os.getcwd(), "schema.sql")
    schema_sql = ""
    with open(schema_path, "r+") as f:
        schema_sql = f.read()

    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)


if __name__ == "__main__":
    app.run(debug=True)

# things to keep an eye on:
# - that passing in the db link as 1 argument will properly call it
# - that the SERIAL type in postgresql will act as a properly self-generating id
#
