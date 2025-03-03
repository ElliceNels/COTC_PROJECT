import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
from flask import Flask
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from config import config
from data.models import MetricReading, Device, MetricType
from dash.dependencies import Input, Output
from sqlalchemy.sql import func

def create_dash_app(flask_app: Flask):
    dash_app = dash.Dash(server=flask_app, name="Dashboard", url_base_pathname='/dashboard/', assets_folder='src/assets')
    
    engine = create_engine(config.database.db_engine)
    Session = sessionmaker(bind=engine)

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
                {'name': 'Timestamp', 'id': 'timestamp'},
                {'name': 'Value', 'id': 'value'},
                {'name': 'Unit', 'id': 'unit'}
            ],
            page_size=10,
            style_table={'width': '80%', 'margin': 'auto', 'font-size': '14px'}
        )
    ])

    @dash_app.callback(
        Output('gauge', 'figure'),
        Output('historical-plot', 'figure'),
        Output('data-table', 'data'),
        Input('interval-component', 'n_intervals'),
        Input('device-dropdown', 'value'),
        Input('metric-type-dropdown', 'value')
    )
    def update_metrics(n, selected_device, selected_metric_type):
        session = Session()

        query = session.query(MetricReading).options(joinedload(MetricReading.metric_type), joinedload(MetricReading.device), joinedload(MetricReading.unit))

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

        # Fetch all metric readings for the table
        all_metrics = query.order_by(MetricReading.timestamp.desc()).all()

        session.close()

        if latest_metric:
            max_value = average_value * 2
            gauge_figure = {
                'data': [
                    go.Indicator(
                        mode="gauge+number",
                        value=latest_metric.value,
                        title={'text': latest_metric.metric_type.name},
                        gauge={'axis': {'range': [None, max_value]}}
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
                    x=[metric.timestamp for metric in historical_metrics],
                    y=[metric.value for metric in historical_metrics],
                    mode='lines+markers'
                )
            ],
            'layout': go.Layout(
                title='Historical Data (Last 30 Entries)',
                xaxis={'title': 'Timestamp', 'autorange': 'reversed', 'tickformat': '%H:%M:%S'},
                yaxis={'title': 'Value'}
            )
        }

        table_data = [
            {
                'device': metric.device.name,
                'timestamp': metric.timestamp,
                'value': metric.value,
                'unit': metric.unit.name if metric.unit else ''
            } for metric in all_metrics
        ]

        # Updates the gauge, historical plot, and table
        return gauge_figure, historical_figure, table_data

    return dash_app
