"""Flask application module."""

import logging
from flask import Flask, request, jsonify, redirect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import config
from datetime import datetime

from data.dto import DeviceDTO, MetricTypeDTO, UnitDTO
from data.models import Base, MetricReading, Device, MetricType, Unit
from dash_app import create_dash_app

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""

    app: Flask = Flask(config.app_name)
    logger.debug('App "%s"created in %s', app.name, __name__)

    engine = create_engine(config.database.db_engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
 
    # Create Dash app
    create_dash_app(app)

    @app.route('/')
    def landing_page():
        """Landing page route."""
        return redirect('/dashboard/')

    # PJ: Aggregator API (Stores in the DB)
    @app.route('/store_metrics', methods=['POST'])
    def store_metrics():
        """Store metrics in the database."""
        metrics_data = request.json
        if not metrics_data:
            logger.error('No data provided for storing metrics')
            return jsonify({'error': 'No data provided'}), 400

        session = Session()
        try:
            for data in metrics_data:
                # Map incoming data into DTOs
                device_dto = DeviceDTO(id=data['device']['id'], name=data['device']['name'])
                metric_type_dto = MetricTypeDTO(id=data['metric_type']['id'], name=data['metric_type']['name'])
                unit_dto = UnitDTO(id=data['unit']['id'], name=data['unit']['name']) if data.get('unit') else None

                # Check if Device exists or create it
                device = session.query(Device).filter_by(id=device_dto.id).first() or \
                         session.query(Device).filter_by(name=device_dto.name).first()
                if not device:
                    device = Device(name=device_dto.name, id=device_dto.id)
                    session.add(device)
                
                session.flush()
                session.commit()

                # Check if MetricType exists or create it
                metric_type = session.query(MetricType).filter_by(name=metric_type_dto.name).first()
                if not metric_type:
                    metric_type = MetricType(name=metric_type_dto.name)
                    session.add(metric_type)
                
                session.flush()
                session.commit()
                
                # Check if Unit exists or create it
                if unit_dto:
                    unit = session.query(Unit).filter_by(name=unit_dto.name).first()
                    if not unit:
                        unit = Unit(name=unit_dto.name)
                        session.add(unit)
                
                session.flush()
                session.commit()

                # Create MetricReading record using DTO data
                metric_reading = MetricReading(
                    device_id=device.id,
                    metric_type_id=metric_type.id,
                    timestamp=datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S'),
                    value=data['value'],
                    unit_id=unit.id if unit else None
                )
                session.add(metric_reading)

            # Commit the session
            session.commit()
            logger.debug('Metrics stored successfully')
            return jsonify({'status': 'success'}), 201
        except Exception as e:
            session.rollback()
            logger.error('Error storing metrics: %s', e)
            return jsonify({'error': 'Failed to store metrics'}), 500
        finally:
            session.close()

    return app

def launch_app():
    """Launch the Flask application."""

    app: Flask = create_app()
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug,
    )