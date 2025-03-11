import json
import logging
import socket
from time import sleep
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from block_timer import BlockTimer
from config import config

from data.dto import DeviceDTO
from .metrics import Metrics
from .metric import CPUTimes, TemperatureInItaly, TemperatureFeelInItaly, RAMUsage, NetworkSend
from sdk.metrics_api import MetricsAPI

logger = logging.getLogger(__name__)

class MetricsCollector:
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

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        MetricsCollector.connect_local_metrics()
        MetricsCollector.connect_tp_metrics()
        self.scheduler.add_job(MetricsCollector.collect_local_metrics, 'interval', seconds=10, args=[True], max_instances=1)
        self.scheduler.add_job(MetricsCollector.collect_tp_metrics, 'interval', seconds=10, args=[True], max_instances=1)

    @staticmethod
    def connect_local_metrics():
        MetricsCollector.local_metrics.add_metric(CPUTimes())
        MetricsCollector.local_metrics.add_metric(RAMUsage())
        MetricsCollector.local_metrics.add_metric(NetworkSend())

    @staticmethod
    def connect_tp_metrics():
        MetricsCollector.third_party_metrics.add_metric(TemperatureInItaly())
        MetricsCollector.third_party_metrics.add_metric(TemperatureFeelInItaly())

    # PJ: PC Collector
    @staticmethod
    def collect_local_metrics(save_flag: bool = False):
        with BlockTimer("LOCAL Metrics"):
            data_list = MetricsCollector.local_metrics.measure_metrics()
            serialise_data_list = [data.serialize() for data in data_list]
            if save_flag:
                logger.debug('Sending LOCAL data to API')
                MetricsAPI.send_metrics(serialise_data_list)
                logger.debug('Data sent to LOCAL')
            return serialise_data_list

    # PJ: Third Party Collector
    @staticmethod
    def collect_tp_metrics(save_flag: bool = False):
        with BlockTimer("THIRD PARTY Metrics"):
            data_list = MetricsCollector.third_party_metrics.measure_metrics()
            serialise_data_list = [data.serialize() for data in data_list]
            if save_flag:
                logger.debug('Sending data from third party API')
                MetricsAPI.send_metrics(serialise_data_list)
                logger.debug('Data sent to third party API')
            return serialise_data_list

    def start_scheduler(self):
        self.scheduler.start()
        logger.info('Scheduler started')

    def stop_scheduler(self):
        self.scheduler.shutdown()
        logger.info('Scheduler stopped')