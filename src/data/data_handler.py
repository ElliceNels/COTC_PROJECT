import json
import logging
import socket
from time import sleep
import uuid
import requests
from config import config

from data.dto import DeviceDTO
from .metrics import Metrics
from .metric import CPUUtilization, CPUTimes, TemperatureInItaly, TemperatureFeelInItaly

logger = logging.getLogger(__name__)
class DataHandler:
    local_metrics: Metrics = Metrics(
        device_dto=DeviceDTO(
            id=uuid.uuid5(
                uuid.NAMESPACE_DNS,
                str(uuid.getnode())
            ),
            name=socket.gethostname()
        )
    )

    third_party_metrics: Metrics = Metrics(
        device_dto=DeviceDTO(
            id=uuid.uuid5(
                uuid.NAMESPACE_DNS,
                config.third_party_api.url
            ),
            name=config.third_party_api.name
        )
    )

    @staticmethod
    def connect_local_metrics():
        DataHandler.local_metrics.add_metric(CPUUtilization())
        DataHandler.local_metrics.add_metric(CPUTimes())

    @staticmethod
    def connect_tp_metrics():
        DataHandler.third_party_metrics.add_metric(TemperatureInItaly())
        DataHandler.third_party_metrics.add_metric(TemperatureFeelInItaly())

    # PJ: PC Collector
    @staticmethod
    def collect_local_metrics(save_flag: bool = False):
        data_list = DataHandler.local_metrics.measure_metrics()
        serialise_data_list = [data.serialize() for data in data_list]
        if save_flag:
            DataHandler.send_metrics_to_web_app(serialise_data_list)
        return serialise_data_list

    # PJ: Third Party Collector
    @staticmethod
    def collect_tp_metrics(save_flag: bool = False):
        data_list = DataHandler.third_party_metrics.measure_metrics()
        serialise_data_list = [data.serialize() for data in data_list]
        if save_flag:
            DataHandler.send_metrics_to_web_app(serialise_data_list)
        return serialise_data_list

    @staticmethod
    def data_collector():
        while True:
            DataHandler.collect_local_metrics(True)
            DataHandler.collect_tp_metrics(True)
            sleep(5)

    # PJ: Uploader Queue
    @staticmethod
    def send_metrics_to_web_app(data: list):
        url = 'https://ellicenelson.pythonanywhere.com/store_metrics'
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            return response.status_code
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to send metrics to web app: {e}")
            return None
    
DataHandler.connect_local_metrics()
DataHandler.connect_tp_metrics()

