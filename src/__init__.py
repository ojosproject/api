from flask import Flask


def create_app(testing=False):
    app = Flask(__name__)

    from . import relay, auth
    app.register_blueprint(relay.bp)
    app.register_blueprint(auth.bp)
    return app
