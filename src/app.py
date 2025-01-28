"""Flask application module."""

import logging
from flask import Flask
from config import config

from data.data_handler import DataHandler

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""

    app: Flask = Flask(config.app_name)
    logger.debug('App "%s"created in %s', app.name, __name__)

    @app.route('/')
    def landing_page():
        """Landing page route."""

        logger.info('You have landed on the landing page')
        return 'Land!'

    @app.route('/data')
    def data():
        """Data Generation page route."""

        ...
        return DataHandler.collect_local_metrics(True)

    return app

def launch_app():
    """Launch the Flask application."""

    app: Flask = create_app()
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug,
    )