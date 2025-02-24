# tests/test_init.py
# Ojos Project
# 
# Tests the create_app() function. This is mostly to show how to run tests for
# the Iris Server.
from src import create_app

def test_init():
    assert bool(create_app(testing=True))
