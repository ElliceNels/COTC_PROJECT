"""Flask application module."""

import logging
from flask import Flask, request, jsonify, render_template
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from block_timer import BlockTimer
from config import config

from data.data_handler import DataHandler
from data.models import Base, MetricReading

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""

    app: Flask = Flask(config.app_name, template_folder="templates")
    logger.debug('App "%s"created in %s', app.name, __name__)

    engine = create_engine(config.database.db_engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    @app.route('/')
    def landing_page():
        """Landing page route."""
        logger.debug('Redirecting to /metrics')
        return metrics()

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

    @app.route('/metrics')
    def metrics():
        """Metrics page route."""
        session = Session()
        metric_types = session.query(MetricReading.metric_type).distinct().all()
        session.close()
        return render_template('metrics.html', metric_types=[mt[0] for mt in metric_types])

    @app.route('/metric/<metric_type>')
    def metric_detail(metric_type):
        """Individual metric detail page route."""
        session = Session()
        recent_metric = session.query(MetricReading).filter_by(metric_type=metric_type).order_by(MetricReading.timestamp.desc()).first()
        session.close()
        if recent_metric is None:
            logger.error('No metric found for type: %s', metric_type)
            return render_template('metric_detail.html', metric=None), 404
        return render_template('metric_detail.html', metric=recent_metric)

    @app.route('/metric/<metric_type>/history')
    def metric_history(metric_type):
        """Metric history page route."""
        session = Session()
        metrics = session.query(MetricReading).filter_by(metric_type=metric_type).order_by(MetricReading.timestamp.desc()).all()
        session.close()
        return render_template('metric_history.html', metrics=metrics, metric_type=metric_type)

    return app

def launch_app():
    """Launch the Flask application."""

    app: Flask = create_app()
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug,
    )