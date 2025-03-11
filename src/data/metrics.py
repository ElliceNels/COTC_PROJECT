"""Metrics module to track metrics"""
from data.dto import DeviceDTO, MetricReadingDTO
from .metric import Metric

class Metrics:
    """Class to manage metrics."""

    def __init__(self, device_dto: DeviceDTO):
        """Initialize the Metrics class.

        Args:
            device_dto (DeviceDTO): The device DTO.
        """
        self.device_dto: DeviceDTO = device_dto
        self.metrics: set[Metric] = set()

    def add_metric(self, metric: Metric):
        """Add a metric to track.

        Args:
            metric (Metric): The metric to add.
        """
        self.metrics.add(metric)

    def remove_metric(self, metric: Metric):
        """Remove a metric to track.

        Args:
            metric (Metric): The metric to remove.
        """
        self.metrics.remove(metric)

    def get_metrics(self):
        """Return the metrics set to be tracked.

        Returns:
            list[str]: The list of metric types.
        """
        return [metric.get_metric_type() for metric in self.metrics]

    def measure_metrics(self) -> list[MetricReadingDTO]:
        """Measure all tracked metrics.

        Returns:
            list[MetricReadingDTO]: The list of measured metric readings.
        """
        list_data: list[MetricReadingDTO] = []
        for metric in self.metrics:
            data = metric.measure(self.device_dto)
            list_data.append(data)
        return list_data

    def measure_metric(self, metric_type: str) -> MetricReadingDTO:
        """Measure a specific tracked metric.

        Args:
            metric_type (str): The metric type to measure.

        Returns:
            MetricReadingDTO: The measured metric reading.
        """
        for metric in self.metrics:
            if metric.get_metric_type().lower() == metric_type.lower():
                data: MetricReadingDTO = metric.measure(self.device_dto)
                return data