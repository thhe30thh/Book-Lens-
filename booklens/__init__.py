import os

from flask import Flask

from booklens.config import get_config
from booklens.database import init_app as init_database


def create_app(config_name=None, test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True
    )

    app.config.from_object(get_config(config_name))

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    init_database(app)

    from booklens.api import api_bp
    from booklens.api.errors import register_error_handlers
    from booklens.web import web_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp)

    register_error_handlers(app)

    return app
