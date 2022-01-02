from os.path import dirname, realpath, join

from flask import Flask, session


def create_app():
    """
    Create and configure an instance of the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(join(dirname(realpath(__file__)), 'config.py'))

    # register the database commands
    from kkonni import db

    db.init_app(app)

    # apply the blueprints to the app
    from kkonni import auth, book, api

    app.register_blueprint(auth.bp)
    app.register_blueprint(book.bp)
    app.register_blueprint(api.bp)

    return app
