import json
import socket
from .metrics import Metrics
from .metric import CPUUtilization, CPUTimes

class DataHandler:
    local_metrics: Metrics = Metrics(device=socket.gethostname())
    third_party_metrics: Metrics = Metrics(device="tHIRD paarty")
    
    def connect_local_metrics():
        DataHandler.local_metrics.add_metric(CPUUtilization())
        DataHandler.local_metrics.add_metric(CPUTimes())

    def connect_tp_metrics():
        # TODO: Add 3rd Party Measurements
        # DataHandler.third_party_metrics.add_metric(---)
        ...

    def collect_local_metrics(save_flag: bool = False):
        data_list: list[dict] = []
        data_list.append(DataHandler.local_metrics.measure_metric(metric_type="CPUUTILIZATION"))
        data_list.append(DataHandler.local_metrics.measure_metric(metric_type="CPUTimes"))
        if save_flag:
            with open('data.json', 'w') as f:
                json.dump(data_list, f, indent=2)

        return data_list

    def collect_tp_metrics(save_flag: bool = False):
        data_list: list[dict] = []
        # TODO: Add 3rd Party Measurements
        # data_list.append(DataHandler.third_party_metrics.measure_metric(metric_type="---"))
        if save_flag:
            with open('data.json', 'a') as f:
                json.dump(data_list, f, indent=2)
        return data_list
    
DataHandler.connect_local_metrics()
DataHandler.connect_tp_metrics()

