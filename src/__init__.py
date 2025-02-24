from . import relay, auth
from .cache import start_threading
from flask import Flask


def create_app(testing=False):
    app = Flask(__name__)
    start_threading(testing)
    app.register_blueprint(relay.bp)
    app.register_blueprint(auth.bp)
    return app
