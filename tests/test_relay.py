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
import src.relay as relay
from src.app import DB, JWT_SECRET_KEY
from src.__init__ import create_app


@pytest.fixture(autouse=True)
def reset_database():
    # resets the database before each test
    _drop_tables()
    _create_tables()


def test_sms_message_successfully_sent():
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

    app = create_app()
    payload = {"to": "9498149431", "message": "this is a test"}
    headers = {"X-API-Key": token}

    with app.test_client() as client:
        response = client.post("/iris/relay/send-sms/",
                               json=payload, headers=headers)

    assert response.status_code == 200
