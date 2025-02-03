from app import register_routes
from flask import Flask
app = Flask(__name__)


def create_app():
    register_routes(app)
    return app
