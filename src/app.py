"""Flask application module."""

import logging
from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from block_timer import BlockTimer
from config import config

from data.data_handler import DataHandler
from data.models import Base, MetricReading

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""

    app: Flask = Flask(config.app_name)
    logger.debug('App "%s"created in %s', app.name, __name__)

    engine = create_engine('sqlite:///metrics.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    @app.route('/')
    def landing_page():
        """Landing page route."""

        logger.info('You have landed on the landing page')
        return 'Land!'

    @app.route('/tpdata')
    def tp_data():
        """Third Party Data Generation page route."""

        with BlockTimer():
            data: list = DataHandler.collect_tp_metrics(False)
        return {'data': data}

    @app.route('/ldata')
    def l_data():
        """Local Data Generation page route."""

        with BlockTimer():
            data: list = DataHandler.collect_local_metrics(False)
        return {'data': data}

    @app.route('/store_metrics', methods=['POST'])
    def store_metrics():
        """Store metrics in the database."""
        session = Session()
        metrics_data = request.json
        for data in metrics_data:
            metric_reading = MetricReading(
                device=data['device'],
                metric_type=data['metric'],
                timestamp=data['timestamp'],
                value=data['value'],
                unit=data['unit']
            )
            session.add(metric_reading)
        session.commit()
        session.close()
        return jsonify({'status': 'success'}), 201

    @app.route('/get_metrics', methods=['GET'])
    def get_metrics():
        """Retrieve metrics from the database."""
        session = Session()
        metrics = session.query(MetricReading).all()
        metrics_list = [
            {
                'device': metric.device,
                'metric_type': metric.metric_type,
                'timestamp': metric.timestamp,
                'value': metric.value,
                'unit': metric.unit
            }
            for metric in metrics
        ]
        session.close()
        return jsonify(metrics_list), 200

    return app

def launch_app():
    """Launch the Flask application."""

    app: Flask = create_app()
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug,
    )