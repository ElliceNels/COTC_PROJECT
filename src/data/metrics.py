"""Metrics module to track metrics"""
from data.dto import DeviceDTO, MetricReadingDTO
from .metric import Metric

class Metrics:
    """Class to manage metrics."""

    def __init__(self, device_dto: DeviceDTO):
        """Initialise the metrics."""
        self.device_dto: DeviceDTO = device_dto
        self.metrics: set[Metric] = set()

    def add_metric(self, metric: Metric):
        """Add a metric to track."""
        self.metrics.add(metric)

    def remove_metric(self, metric: Metric):
        """Remove a metric to track."""
        self.metrics.remove(metric)

    def get_metrics(self):
        """Return the metrics set to be track."""
        return [metric.get_metric_type() for metric in self.metrics]

    def measure_metrics(self) -> list[MetricReadingDTO]:
        """Measure all tracked metrics."""
        list_data: list[MetricReadingDTO] = []
        for metric in self.metrics:
            data = metric.measure(self.device_dto)
            list_data.append(data)
        return list_data

    def measure_metric(self, metric_type: str) -> MetricReadingDTO:
        """Measure a specific tracked metric."""
        for metric in self.metrics:
            if metric.get_metric_type() == metric_type.lower():
                data: MetricReadingDTO = metric.measure(self.device_dto)
                return data