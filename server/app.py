from flask import Flask, request, make_response, abort, send_from_directory
from flask_redis import FlaskRedis
import configparser
import pathlib
parent_dir = pathlib.Path(__file__).parent.parent.absolute()
config = configparser.ConfigParser()
print(config.read(parent_dir.joinpath('config.ini')))

import os
import json

redis_client = FlaskRedis()

def create_app(outreach_existing=None, SQLALCHEMY_DATABASE_URI=None, **kwargs):
    app = Flask(__name__)
    app.config["REDIS_URL"] = "redis://{}".format(config["DEFAULT"]["REDIS_URL"])
    print(app.config)
    redis_client.init_app(app)
    if "FLASK_SECRET_KEY" in os.environ:
        app.secret_key = os.environ["FLASK_SECRET_KEY"]
        app.config['SECRET_KEY'] = os.environ["FLASK_SECRET_KEY"]
    else:
        app.secret_key = "TESTING"
        app.config['SECRET_KEY'] = "TESTING"

    for key, value in kwargs.items():
        app.config[key] = value

    configure_blueprints(app)
    return app

def configure_blueprints(app):
    from misc import bp as misc_bp
    app.register_blueprint(misc_bp)

