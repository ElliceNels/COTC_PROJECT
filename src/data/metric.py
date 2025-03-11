"""Metrics module. Collects data from the device and serializes the data"""
from abc import abstractmethod, ABC
import datetime
import psutil
import logging
import requests

from config import config

from .dto import DeviceDTO, MetricReadingDTO, UnitDTO, MetricTypeDTO

logger = logging.getLogger(__name__)

class Metric(ABC):
    """Abstract class for metrics."""
    DATA_INDEX = 0
    TIME_UPDATED_INDEX = 1

    def __init__(self):
        """Initialize the Metric class."""
        super().__init__()
        self.cache: tuple = (None, None)
        self.metric_type = None

    def __eq__(self, other_metric_type: str):
        """Check if the metric type is equal to another metric type.

        Args:
            other_metric_type (str): The other metric type to compare.

        Returns:
            bool: True if the metric types are equal, False otherwise.
        """
        return self.get_metric_type() == other_metric_type
    
    def __hash__(self):
        """Return the hash of the metric type.

        Returns:
            int: The hash of the metric type.
        """
        return hash(self.get_metric_type())

    def get_metric_type(self):
        """Return the metric type.

        Returns:
            str: The metric type.
        """
        return self.__class__.__name__

    def get_timestamp(self):
        """Return the current datetime.

        Returns:
            datetime: The current datetime.
        """
        return datetime.datetime.now()

    def get_utc_offset(self, timestamp):
        """Calculate the UTC offset for the given timestamp.

        Args:
            timestamp (datetime): The timestamp to calculate the UTC offset for.

        Returns:
            float: The UTC offset in hours.
        """
        offset = timestamp.utcoffset() if timestamp.utcoffset() else datetime.timezone.utc.utcoffset(timestamp)
        return offset.total_seconds() / 3600

    @abstractmethod
    def measure(self, device: DeviceDTO) -> MetricReadingDTO | None:
        """Measure the metric.

        Args:
            device (DeviceDTO): The device to measure the metric for.

        Returns:
            MetricReadingDTO | None: The measured metric reading or None if cache is expired.
        """
        if self.cache[self.DATA_INDEX] and self.cache[self.TIME_UPDATED_INDEX]:
            # Get time difference
            cache_time = self.cache[self.TIME_UPDATED_INDEX]
            current_time = datetime.datetime.now()
            cache_age = current_time - cache_time
            if cache_age <= datetime.timedelta(minutes=config.third_party_api.cache_timeout_m):
                logger.debug('Returning cached data')
                return self.cache[self.DATA_INDEX]
            else:
                logger.debug('Cache expired')
                return None

class RAMUsage(Metric):
    """Class to measure the RAM usage."""
    UNIT_DTO: UnitDTO = UnitDTO(id=-1, name='Percent', symbol='%')

    def __init__(self):
        """Initialize the RAMUsage class."""
        super().__init__()
        self.metric_type = MetricTypeDTO(id=-1, name=self.get_metric_type(), min_value=0, max_value=100)

    def measure(self, device: DeviceDTO) -> MetricReadingDTO:
        """Measure the RAM usage.

        Args:
            device (DeviceDTO): The device to measure the RAM usage for.

        Returns:
            MetricReadingDTO: The measured RAM usage.
        """
        if (cache := super().measure(device)):
            return cache

        value: float = psutil.virtual_memory().percent
        timestamp = self.get_timestamp()
        data = MetricReadingDTO(
            id=-1,
            device=device,
            metric_type=self.metric_type,
            timestamp=timestamp,
            value=value,
            unit=self.UNIT_DTO,
            utc_offset=self.get_utc_offset(timestamp)
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data

class CPUTimes(Metric):
    """Class to measure CPU times in user mode."""
    UNIT_DTO: UnitDTO = UnitDTO(id=-1, name='Seconds', symbol='s')

    def __init__(self):
        """Initialize the CPUTimes class."""
        super().__init__()
        self.metric_type = MetricTypeDTO(id=-1, name=self.get_metric_type(), min_value=0, max_value=90000)

    def measure(self, device: DeviceDTO) -> MetricReadingDTO:
        """Measure the CPU user times.

        Args:
            device (DeviceDTO): The device to measure the CPU user times for.

        Returns:
            MetricReadingDTO: The measured CPU user times.
        """
        if (cache := super().measure(device)):
            return cache

        value: float = psutil.cpu_times().user
        timestamp = self.get_timestamp()
        data = MetricReadingDTO(
            id=-1,
            device=device,
            metric_type=self.metric_type,
            timestamp=timestamp,
            value=value,
            unit=self.UNIT_DTO,
            utc_offset=self.get_utc_offset(timestamp)
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data

class NetworkSend(Metric):
    """Class to measure the network send bytes."""
    UNIT_DTO: UnitDTO = UnitDTO(id=-1, name='Bytes', symbol='B')

    def __init__(self):
        """Initialize the NetworkSend class."""
        super().__init__()
        self.metric_type = MetricTypeDTO(id=-1, name=self.get_metric_type(), min_value=0, max_value=1000000000)

    def measure(self, device: DeviceDTO) -> MetricReadingDTO:
        """Measure the network send bytes.

        Args:
            device (DeviceDTO): The device to measure the network send bytes for.

        Returns:
            MetricReadingDTO: The measured network send bytes.
        """
        if (cache := super().measure(device)):
            return cache

        value: float = psutil.net_io_counters().bytes_sent
        timestamp = self.get_timestamp()
        data = MetricReadingDTO(
            id=-1,
            device=device,
            metric_type=self.metric_type,
            timestamp=timestamp,
            value=value,
            unit=self.UNIT_DTO,
            utc_offset=self.get_utc_offset(timestamp)
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data

class TemperatureInItaly(Metric):
    """Class to measure the temperature in Italy from a 3rd Party API."""
    UNIT_DTO: UnitDTO = UnitDTO(id=-1, name='Celsius', symbol='°C')

    def __init__(self):
        """Initialize the TemperatureInItaly class."""
        super().__init__()
        self.metric_type = MetricTypeDTO(id=-1, name=self.get_metric_type(), min_value=-50, max_value=50)

    def measure(self, device: DeviceDTO) -> MetricReadingDTO:
        """Measure the temperature in Italy from a 3rd Party API.

        Args:
            device (DeviceDTO): The device to measure the temperature for.

        Returns:
            MetricReadingDTO: The measured temperature.
        """
        if (cache := super().measure(device)):
            return cache

        # API to weather data
        all_weather_data = requests.get(config.third_party_api.url, params=config.third_party_api.params).json()
        value = all_weather_data["main"]["temp"]

        timestamp = self.get_timestamp()
        data = MetricReadingDTO(
            id=-1,
            device=device,
            metric_type=self.metric_type,
            timestamp=timestamp,
            value=value,
            unit=self.UNIT_DTO,
            utc_offset=self.get_utc_offset(timestamp)
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data

class TemperatureFeelInItaly(Metric):
    """Class to measure the temperature feel in Italy from a 3rd Party API."""
    UNIT_DTO: UnitDTO = UnitDTO(id=-1, name='Celsius', symbol='°C')

    def __init__(self):
        """Initialize the TemperatureFeelInItaly class."""
        super().__init__()
        self.metric_type = MetricTypeDTO(id=-1, name=self.get_metric_type(), min_value=-50, max_value=50)

    def measure(self, device: DeviceDTO) -> MetricReadingDTO:
        """Measure the temperature feel in Italy from a 3rd Party API.

        Args:
            device (DeviceDTO): The device to measure the temperature feel for.

        Returns:
            MetricReadingDTO: The measured temperature feel.
        """
        if (cache := super().measure(device)):
            return cache

        # API to weather data
        all_weather_data = requests.get(config.third_party_api.url, params=config.third_party_api.params).json()
        value = all_weather_data["main"]["feels_like"]

        timestamp = self.get_timestamp()
        data = MetricReadingDTO(
            id=-1,
            device=device,
            metric_type=self.metric_type,
            timestamp=timestamp,
            value=value,
            unit=self.UNIT_DTO,
            utc_offset=self.get_utc_offset(timestamp)
        )
        logger.debug(data)
        self.cache = (data, self.get_timestamp())
        return data
