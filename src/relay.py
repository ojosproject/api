# relay.py
# Ojos Project
# 
# The aspect of the Iris API that sends notifications to people's devices.
import time
from flask import Blueprint, request, jsonify
from twilio.rest import Client
from .app import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from .auth import _validate_token, _log_token
from .cache import global_cache

bp = Blueprint('relay', __name__, url_prefix='/iris/relay/')

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
    elif global_cache.contains_max(token):
        # checks if token is rate limited
        return jsonify({"error": "you've been rate limited"}),
        # consider adding a "retry after" message, retry after 30 minutes (how to do?)
    else:
        try:
            global_cache.add_to_cache(token)
            message = twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=recipient
            )
            _log_token(token, time.time(), "SMS")
            return jsonify({"status": "success", "sid": message.sid}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
