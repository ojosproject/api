from . import relay, auth
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.register_blueprint(relay.bp)
    app.register_blueprint(auth.bp)
    return app
