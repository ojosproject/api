# tests/test_relay.py
# Ojos Project
#
# Tests that relay methods function, such as sms messaging
# coverage run -m pytest tests/test_relay.py

import pytest
import time
import psycopg2
import jwt
from src.db import _create_tables, _drop_tables
from src.app import DB, JWT_SECRET_KEY
from src.auth import _log_token
from src.__init__ import create_app


@pytest.fixture(autouse=True)
def reset_database():
    # resets the database before each test
    _drop_tables()
    _create_tables()


def _add_a_token():
    expiration = time.time() + 10000
    token = jwt.encode(
        {"id": "user_id", "expiration": expiration},
        JWT_SECRET_KEY,
        algorithm="HS256"
    )
    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO tokens (token, expiration_date) VALUES (%s, %s) ON CONFLICT (token) DO UPDATE SET expiration_date = EXCLUDED.expiration_date;",
                           (token, expiration))

    return token


def test_sms_message_successfully_sent():
    token = _add_a_token()

    app = create_app(testing=True)
    payload = {"to": "9498149431", "message": "this is test 1"}
    headers = {"X-API-Key": token}

    with app.test_client() as client:
        response = client.post("/iris/relay/send-sms/",
                               json=payload, headers=headers)

    assert response.status_code == 200
    # can also verify this works if 9498149431 receives a text message


def test_sms_not_sent_if_no_message_provided():
    token = _add_a_token()

    app = create_app(testing=True)
    payload = {"to": "9498149431", "message": ""} # message is empty string
    headers = {"X-API-Key": token}

    with app.test_client() as client:
        response = client.post("/iris/relay/send-sms/",
                               json=payload, headers=headers)

    assert response.status_code == 400


def test_sms_not_sent_if_invalid_token_provided():
    token = 12345 # token not existing in db

    app = create_app(testing=True)
    payload = {"to": "9498149431", "message": "this won't send"}
    headers = {"X-API-Key": token}

    with app.test_client() as client:
        response = client.post("/iris/relay/send-sms/",
                               json=payload, headers=headers)

    assert response.status_code == 401


def test_sms_not_sent_if_over_ten_api_calls():
    token = _add_a_token()
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")
    _log_token(token, time.time(), "SMS")

    app = create_app(testing=True)
    payload = {"to": "9498149431", "message": "this won't send"}
    headers = {"X-API-Key": token}

    with app.test_client() as client:
        response = client.post("/iris/relay/send-sms/",
                               json=payload, headers=headers)

    assert response.status_code == 429
