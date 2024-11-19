from flask import Flask, request, jsonify
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_SID = os.getenv("TWILIO_AUTH_SID")
# TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_SID)


@app.route("/send_sms", methods=["POST"])
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
    return jsonify({"status": "success", "sid": 1234}), 200
