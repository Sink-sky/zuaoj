from flask import Flask
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler


def create_app(config):
    app = Flask(__name__)
    app.config.update(config)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=app.config['SESSION_LIFETIME'])

    if not app.debug:
        file_handler = RotatingFileHandler(app.config['LOGGER_PATH'])
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .manager import manager as manager_blueprint
    app.register_blueprint(manager_blueprint, url_prefix='/manager')

    return app
