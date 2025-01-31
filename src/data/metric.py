"""Metrics module. Collects data from the device and serializes the data"""
from abc import abstractmethod, ABC
import datetime
import psutil
import logging
import requests

from config import config

from .data_frame import DataFrame

logger = logging.getLogger(__name__)


class Metric(ABC):
    """Abstract class for metrics."""

    def __eq__(self, other_metric_type: str):
        """Check if the metric type is equal to another metric type."""
        return self.get_metric_type() == other_metric_type
    
    def __hash__(self):
        """Return the hash of the metric type."""
        return hash(self.get_metric_type())

    def get_metric_type(self):
        """Return the metric type."""
        return self.__class__.__name__.lower()

    def get_timestamp(self):
        """Return the current time."""
        return str(datetime.datetime.now().time())

    @abstractmethod
    def measure(self, device: str, timestamp: int, value: float):
        """Measure the metric."""
        pass

class CPUUtilization(Metric):
    """Class to measure the CPU utilisation."""
    UNIT: str = 'percent'
    
    def measure(self, device: str):
        """Measure the CPU Utilisation."""
        value: float = psutil.cpu_percent(interval=1)
        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        ).serialize()
        logger.debug(data)
        return data

class CPUTimes(Metric):
    """Class to measure cpu times in user mode."""
    UNIT: str = 'seconds'

    def measure(self, device: str):
        """Measure the CPU user times."""
        value: float = psutil.cpu_times().user
        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        ).serialize()
        logger.debug(data)
        return data

class CPUTimes(Metric):
    """Class to measure cpu times in user mode."""
    UNIT: str = 'seconds'

    def measure(self, device: str):
        """Measure the CPU user times."""
        value: float = psutil.cpu_times().user
        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        ).serialize()
        logger.debug(data)
        return data

class TemperatureInItaly(Metric):
    UNIT: str = 'Celsius'

    def measure(self, device: str):
        # API to weather data
        all_weather_data = requests.get(config.third_party_api.url).json()
        value = all_weather_data["main"]["temp"]

        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        ).serialize()
        logger.debug(data)
        return data

class TemperatureFeelInItaly(Metric):
    UNIT: str = 'Celsius'

    def measure(self, device: str):
        # API to weather data
        all_weather_data = requests.get(config.third_party_api.url).json()
        value = all_weather_data["main"]["feels_like"]

        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        ).serialize()
        logger.debug(data)
        return data
