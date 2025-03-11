"""Flask application module."""

import logging
from flask import Flask, request, jsonify, redirect
from sqlalchemy.orm import sessionmaker, joinedload  # Add joinedload import
from sqlalchemy import create_engine
from block_timer import BlockTimer
from config import config
from datetime import datetime
from threading import Lock

from data.dto import DeviceDTO, MetricTypeDTO, UnitDTO
from data.models import Base, MetricReading, Device, MetricType, Unit
from dash import dcc, html, dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from flask_caching import Cache
from sqlalchemy.sql import func
import dash
import requests

logger = logging.getLogger(__name__)

# Global variable to store the message with a lock for thread safety
stored_message = None
message_lock = Lock()

def create_app():
    """Create and configure the Flask application."""

    app: Flask = Flask(config.app_name)
    logger.debug('App "%s" created in %s', app.name, __name__)
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    engine = create_engine(config.database.db_engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
 
    # Create Dash app
    dash_app = dash.Dash(server=app, name="Dashboard", url_base_pathname='/dashboard/', assets_folder='src/assets')
    
    session = Session()
    devices = session.query(MetricReading.device_id, Device.name).join(Device).distinct().all()
    metric_types = session.query(MetricReading.metric_type_id, MetricType.name).join(MetricType).distinct().all()
    session.close()

    # Layout for the Dash app
    dash_app.layout = html.Div([
        html.H1("Metrics Dashboard"),
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # Update every 5 seconds
            n_intervals=0
        ),
        dcc.Dropdown(
            id='device-dropdown',
            options=[{'label': device.name, 'value': device.device_id} for device in devices],
            placeholder="Select a device",
            className='dash-dropdown'
        ),
        dcc.Dropdown(
            id='metric-type-dropdown',
            options=[{'label': metric_type.name, 'value': metric_type.metric_type_id} for metric_type in metric_types],
            value=metric_types[0].metric_type_id if metric_types else None,  # Default to the first metric type
            placeholder="Select a metric type",
            className='dash-dropdown'
        ),
        dcc.Graph(id='gauge', className='dash-graph'),
        dcc.Graph(id='historical-plot', className='dash-graph'),
        dash_table.DataTable(
            id='data-table',
            columns=[
                {'name': 'Device', 'id': 'device'},
                {'name': 'Timestamp', 'id': 'timestamp', 'type': 'datetime'},
                {'name': 'Value', 'id': 'value'},
                {'name': 'Unit', 'id': 'unit'}
            ],
            page_size=10,
            style_table={'width': '80%', 'margin': 'auto', 'font-size': '14px'}
        ),
        dcc.Input(id='message-input', type='text', placeholder='Enter a message'),
        html.Button('Send Message', id='send-message-button'),
        html.Div(id='message-output')
    ])

    @dash_app.callback(
        Output('gauge', 'figure'),
        Output('historical-plot', 'figure'),
        Output('data-table', 'data'),
        Input('interval-component', 'n_intervals'),
        Input('device-dropdown', 'value'),
        Input('metric-type-dropdown', 'value')
    )
    @cache.memoize(timeout=5)
    def update_metrics(n, selected_device, selected_metric_type):
        session = Session()

        query = session.query(MetricReading).options(joinedload(MetricReading.metric_type), joinedload(MetricReading.device), joinedload(MetricReading.unit))

        # Refresh device fields
        devices = session.query(MetricReading.device_id, Device.name).join(Device).distinct().all()

        if selected_device:
            query = query.filter(MetricReading.device_id == selected_device)
        if selected_metric_type:
            query = query.filter(MetricReading.metric_type_id == selected_metric_type)
        else:
            selected_metric_type = metric_types[0].metric_type_id if metric_types else None
            query = query.filter(MetricReading.metric_type_id == selected_metric_type)

        # Fetch the latest metric reading for the gauge
        latest_metric = query.order_by(MetricReading.timestamp.desc()).first()

        # Calculate the average value for the selected metric type
        average_value = query.with_entities(func.avg(MetricReading.value)).scalar() if latest_metric else 50

        # Fetch the last 20 metric readings for the historical plot
        historical_metrics = query.order_by(MetricReading.timestamp.desc()).limit(20).all()
        historical_metrics.reverse()  # Reverse to have the oldest first

        # Fetch all metric readings for the table
        all_metrics = query.order_by(MetricReading.timestamp.desc()).all()

        session.close()

        if latest_metric:
            min_value = latest_metric.metric_type.min_value if latest_metric.metric_type.min_value is not None else 0
            max_value = latest_metric.metric_type.max_value if latest_metric.metric_type.max_value is not None else average_value * 2
            unit_name = latest_metric.unit.name if latest_metric.unit else ''
            unit_symbol = latest_metric.unit.symbol if latest_metric.unit else ''
            gauge_figure = {
                'data': [
                    go.Indicator(
                        mode="gauge+number",
                        value=latest_metric.value,
                        title={'text': f"{latest_metric.metric_type.name} ({unit_name})"},
                        gauge={'axis': {'range': [min_value, max_value]}},
                        number={'suffix': f" {unit_symbol}"}
                    )
                ]
            }
        else:
            gauge_figure = {
                'data': [
                    go.Indicator(
                        mode="gauge+number",
                        value=0,
                        title={'text': 'No Data'},
                        gauge={'axis': {'range': [None, 100]}}
                    )
                ]
            }

        historical_figure = {
            'data': [
                go.Scatter(
                    x=[metric.timestamp.isoformat() if metric.timestamp else '' for metric in historical_metrics],
                    y=[metric.value for metric in historical_metrics],
                    mode='lines+markers'
                )
            ],
            'layout': go.Layout(
                title='Historical Data (Last 20 Entries)',
                xaxis={'title': 'Timestamp', 'tickformat': '%Y-%m-%d %H:%M:%S'},
                yaxis={'title': 'Value'}
            )
        }

        table_data = [
            {
                'device': metric.device.name,
                'timestamp': metric.timestamp.isoformat() if metric.timestamp else '',
                'value': metric.value,
                'unit': metric.unit.name if metric.unit else ''
            } for metric in all_metrics
        ]

        # Updates the gauge, historical plot, and table
        return gauge_figure, historical_figure, table_data

    @dash_app.callback(
        Output('message-output', 'children'),
        Input('send-message-button', 'n_clicks'),
        State('message-input', 'value')
    )
    def send_message_to_server(n_clicks, message):
        if n_clicks:
            logger.debug(f"Attempting to send message: {message}")
            response = requests.post(f"{config.server.url}/send_message", json={'message': message})
            if response.status_code == 200:
                logger.debug("Message sent successfully!")
                return 'Message sent successfully!'
            else:
                logger.error(f"Failed to send message. Status code: {response.status_code}")
                return 'Failed to send message.'
        return ''

    @app.route('/send_message', methods=['POST'])
    def send_message():
        with BlockTimer("send_message"):
            global stored_message
            data = request.get_json()
            message = data.get('message') if data else None
            if not message:
                return jsonify({'error': 'No message provided'}), 400

            with message_lock:
                stored_message = message
            logger.info("Sent message: %s", stored_message)
            return jsonify({"status": "success"}), 200

    @app.route('/poll_message', methods=['GET'])
    def poll_message():
        with BlockTimer("poll_message"):
            global stored_message
            with message_lock:
                message = stored_message
                stored_message = None  # Reset the stored message after a successful poll
            return jsonify({'message': message}), 200

    @app.route('/')
    def landing_page():
        """Landing page route."""
        return redirect('/dashboard/')

    # PJ: Aggregator API (Stores in the DB)
    @app.route('/store_metrics', methods=['POST'])
    def store_metrics():
        """Store metrics in the database."""
        with BlockTimer("store_metrics"):
            metrics_data = request.json
            if not metrics_data:
                logger.error('No data provided for storing metrics')
                return jsonify({'error': 'No data provided'}), 400

            session = Session()
            try:
                for data in metrics_data:
                    # Map incoming data into DTOs
                    device_dto = DeviceDTO(id=data['device']['id'], name=data['device']['name'])
                    metric_type_dto = MetricTypeDTO(id=data['metric_type']['id'], name=data['metric_type']['name'], min_value=data['metric_type'].get('min_value'), max_value=data['metric_type'].get('max_value'))
                    unit_dto = UnitDTO(id=data['unit']['id'], name=data['unit']['name'], symbol=data['unit'].get('symbol')) if data.get('unit') else None

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
                        metric_type = MetricType(name=metric_type_dto.name, min_value=metric_type_dto.min_value, max_value=metric_type_dto.max_value)
                        session.add(metric_type)
                    
                    session.flush()
                    session.commit()
                    
                    # Check if Unit exists or create it
                    if unit_dto:
                        unit = session.query(Unit).filter_by(name=unit_dto.name).first()
                        if not unit:
                            unit = Unit(name=unit_dto.name, symbol=unit_dto.symbol)
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