"""
app.py allows devices running iris to make third party API calls, such as to
Twilio
"""
import os
import threading
import dotenv
from flask import Flask

dotenv.load_dotenv(override=True)

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
DB = os.getenv("INTERNAL_DB_LINK")

if __name__ == "__main__":
    app.run(debug=True)

# things to keep an eye on:
# - that passing in the db link as 1 argument will properly call it
# - that the SERIAL type in postgresql will act as a properly self-generating id
# - potentially, the Cache class won't be sufficient to handle a lot of traffic
# look into a caching library like redis in this case
