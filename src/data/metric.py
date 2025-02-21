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
    DATA_INDEX = 0
    TIME_UPDATED_INDEX = 1

    def __init__(self):
        super().__init__()
        self.cache: tuple = (None, None)

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
    def measure(self, device: str) -> DataFrame:
        """Measure the metric."""
        if self.cache[self.DATA_INDEX] and self.cache[self.TIME_UPDATED_INDEX]:
            # Get time difference
            cache_time_str = self.cache[self.TIME_UPDATED_INDEX]
            cache_time = datetime.datetime.strptime(cache_time_str, '%H:%M:%S.%f').time()
            current_time = datetime.datetime.now().time()
            cache_age = datetime.datetime.combine(datetime.date.today(), current_time) - datetime.datetime.combine(datetime.date.today(), cache_time)
            
            if cache_age <= datetime.timedelta(minutes=config.third_party_api.cache_timeout_m):
                logger.debug('Returning cached data')
                return self.cache[self.DATA_INDEX]
            else:
                logger.debug('Cache expired')
                return None

class CPUUtilization(Metric):
    """Class to measure the CPU utilisation."""
    UNIT: str = 'percent'
    
    def measure(self, device: str):
        """Measure the CPU Utilisation."""
        if (cache := super().measure(device)):
            return cache
        
        value: float = psutil.cpu_percent(interval=1)
        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data

class CPUTimes(Metric):
    """Class to measure cpu times in user mode."""
    UNIT: str = 'seconds'

    def measure(self, device: str) -> DataFrame:
        """Measure the CPU user times."""
        if (cache := super().measure(device)):
            return cache

        value: float = psutil.cpu_times().user
        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data

class TemperatureInItaly(Metric):
    UNIT: str = 'Celsius'

    def measure(self, device: str) -> DataFrame:
        """Measure the temperature in Italy from a 3rd Party API."""
        if (cache := super().measure(device)):
            return cache

        # API to weather data
        all_weather_data = requests.get(config.third_party_api.url).json()
        value = all_weather_data["main"]["temp"]

        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data

class TemperatureFeelInItaly(Metric):
    UNIT: str = 'Celsius'

    def measure(self, device: str) -> DataFrame:
        """Measure the temperature feel in Italy from a 3rd Party API."""
        if (cache := super().measure(device)):
            return cache

        # API to weather data
        all_weather_data = requests.get(config.third_party_api.url).json()
        value = all_weather_data["main"]["feels_like"]

        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=self.get_timestamp(),
            value=value,
            unit=self.UNIT
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data
