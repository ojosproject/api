# relay.py
# Ojos Project
#
# The aspect of the Iris API that sends notifications to people's devices.
import time
from flask import Blueprint, request, jsonify
from twilio.rest import Client
import psycopg2
from .app import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, DB
from .auth import _validate_token, _log_token
from .cache import global_cache

bp = Blueprint('relay', __name__, url_prefix='/iris/relay')


@bp.route("/send-sms/", methods=["POST"])
def send_sms():
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
    elif calls_in_past_30_minutes(token, time.time()) > 10:
        # checks if token is rate limited
        return jsonify({"error": "you've been rate limited"}), 429
        # consider adding a "retry after" message, retry after 30 minutes (how to do?)
    else:
        try:
            message = twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=recipient
            )
            timestamp = time.time()
            _log_token(token, timestamp, "SMS")
            return jsonify({"status": "success", "sid": message.sid}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def calls_in_past_30_minutes(token : str, current_timestamp : int) -> int:
    """Returns the amount of times that a token has been logged within the
    past 30 minutes for the purposes of rate limiting

    Args:
        token (str): a user's token
        current_timestamp (int): the current time

    Returns:
        int: the number of times that a token was logged in the database in 
        the past 30 minutes 
    """
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT COUNT(token)
                   FROM token_log
                   WHERE %s = token
                   AND timestamp >= %s - 30 * 60;
                """, (token, current_timestamp)
            )
            return cursor.fetchone()[0]
