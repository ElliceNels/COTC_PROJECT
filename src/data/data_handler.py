import json
import socket
from time import sleep
import requests
from .metrics import Metrics
from .metric import CPUUtilization, CPUTimes, TemperatureInItaly, TemperatureFeelInItaly

class DataHandler:
    local_metrics: Metrics = Metrics(device=socket.gethostname())
    third_party_metrics: Metrics = Metrics(device="Third Party")
    
    def connect_local_metrics():
        DataHandler.local_metrics.add_metric(CPUUtilization())
        DataHandler.local_metrics.add_metric(CPUTimes())

    def connect_tp_metrics():
        DataHandler.third_party_metrics.add_metric(TemperatureInItaly())
        DataHandler.third_party_metrics.add_metric(TemperatureFeelInItaly())

    def collect_local_metrics(save_flag: bool = False):
        data_list = DataHandler.local_metrics.measure_metrics()
        serialise_data_list = [data.serialize() for data in data_list]
        if save_flag:
            DataHandler.send_metrics_to_web_app(serialise_data_list)
        return serialise_data_list

    def collect_tp_metrics(save_flag: bool = False):
        data_list = DataHandler.third_party_metrics.measure_metrics()
        serialise_data_list = [data.serialize() for data in data_list]
        if save_flag:
            DataHandler.send_metrics_to_web_app(serialise_data_list)
        return serialise_data_list
    
    def data_collector():
        while True:
            DataHandler.collect_local_metrics(True)
            DataHandler.collect_tp_metrics(True)
            sleep(5)

    def send_metrics_to_web_app(data: list):
        url = 'https://ellicenelson.pythonanywhere.com/store_metrics'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.status_code
    
DataHandler.connect_local_metrics()
DataHandler.connect_tp_metrics()

