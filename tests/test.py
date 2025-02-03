# use python -m tests.test to run

import unittest
from unittest.mock import patch
import time
from datetime import timedelta
import dotenv
import os
import jwt
import psycopg2
import requests
import psycopg2.extras
from flask import Flask
import app
from __init__ import create_app


dotenv.load_dotenv(override=True)


class TestDatabaseCalls(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.test_client = cls.app.test_client()

        cls.localhost = "http://127.0.0.1:5000"
        cls.register_url = "/iris/register/"
        cls.update_token_url = "/iris/update-token/"
        cls.send_sms_url = "/iris/send-sms/"

    def setUp(self):
        ...
        # self.not_expired_expiration = time.time() + 10000
        # self.not_expired_test_token = jwt.encode(
        #     {"id": "test_id", "expiration": self.not_expired_expiration},
        #     JWT_SECRET_KEY,
        #     algorithm="HS256"
        # )
        # with psycopg2.connect(DB) as conn:
        #     with conn.cursor() as cursor:
        #         cursor.execute(
        #             "INSERT INTO tokens (token, expiration_date) VALUES (%s, %s) ON CONFLICT (token) DO UPDATE SET expiration_date = EXCLUDED.expiration_date;", (self.not_expired_test_token, self.not_expired_expiration))

        # self.expiration = time.time() + timedelta(days=30).total_seconds()
        # self.test_token = jwt.encode(
        #     {"id": "test_id", "expiration": self.expiration},
        #     JWT_SECRET_KEY,
        #     algorithm="HS256"
        # )
        # with psycopg2.connect(DB) as conn:
        #     with conn.cursor() as cursor:
        #         cursor.execute(
        #             "INSERT INTO tokens (token, expiration_date) VALUES (%s, %s) ON CONFLICT (token) DO UPDATE SET expiration_date = EXCLUDED.expiration_date;", (self.test_token, self.expiration))

        # inserting an expired token into the db
        # self.expired_expiration = time.time() - 10000
        # self.expired_test_token = jwt.encode(
        #     {"id": "test_id", "expiration": self.expired_expiration},
        #     JWT_SECRET_KEY,
        #     algorithm="HS256"
        # )
        # with psycopg2.connect(DB) as conn:
        #     with conn.cursor() as cursor:
        #         cursor.execute(
        #             "INSERT INTO tokens (token, expiration_date) VALUES (%s, %s) ON CONFLICT (token) DO UPDATE SET expiration_date = EXCLUDED.expiration_date;", (self.expired_test_token, self.expired_expiration))

        # # inserting an unexpired token into the db
        # self.not_expired_expiration = time.time() + 10000
        # self.not_expired_test_token = jwt.encode(
        #     {"id": "test_id", "expiration": self.not_expired_expiration},
        #     JWT_SECRET_KEY,
        #     algorithm="HS256"
        # )
        # with psycopg2.connect(DB) as conn:
        #     with conn.cursor() as cursor:
        #         cursor.execute(
        #             "INSERT INTO tokens (token, expiration_date) VALUES (%s, %s) ON CONFLICT (token) DO UPDATE SET expiration_date = EXCLUDED.expiration_date;", (self.not_expired_test_token, self.not_expired_expiration))

    def test_correctly_registers_tokens(self):
        response = self.test_client.post(self.register_url)
        print(response.status_code)
        print(response.text)

        self.assertEqual(response.status_code, 200)
        # would add verification w/ response.text to check that token is what we
        # expected, but no way to test without retrieving the token

    # def test_correctly_checks_if_token_is_expired(self):
    #     # manually inserted an expired token
    #     self.assertTrue(app._token_is_expired(self.expired_test_token))
    #     # manually inserted a not expired token
    #     self.assertFalse(app._token_is_expired(self.not_expired_test_token))

    # def test_correctly_updates_tokens(self):
    #     # correctly updates expired tokens
    #     data = {"token": self.expired_test_token}
    #     response = requests.post(self.update_token_url, json=data)
    #     print(response.status_code)
    #     print(response.text)

    # def test_able_to_retrieve_tokens(self):
    #     ...

    @patch("app._validate_token")
    @patch("app._log_token")
    def test_send_sms(self, mock_validate_token, mock_log_token):
        mock_log_token.return_value = None
        mock_validate_token.return_value = True

        data = {"to": "9498149431", "message": "this is a TEST message"}
        headers = {"X-API-KEY": "TEST_TOKEN"}

        response = self.test_client.post(
            self.send_sms_url, json=data, headers=headers)

        print(response.status_code)
        print(response.text)
        self.assertEqual(response.status_code, 200)


        mock_log_token.return_value = None
        mock_validate_token.return_value = True

        data = {"to": "9498149431", "message": "this is a TEST message"}
        headers = {"X-API-KEY": "TEST_TOKEN"}

        response = self.test_client.post(
            self.send_sms_url, json=data, headers=headers)

        print(response.status_code)
        print(response.text)
        self.assertEqual(response.status_code, 200)

    #     # def test_generate_token(self):
    #     #     received_token = app._generate_token("test_id")

    #     #     print(received_token)


if __name__ == "__main__":
    unittest.main()
