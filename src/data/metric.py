"""Metrics module. Collects data from the device and serializes the data"""
from abc import abstractmethod, ABC
import datetime
import psutil
import logging

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
        timestamp: str = str(datetime.datetime.now().time())
        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=timestamp,
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
        timestamp: str = str(datetime.datetime.now().time())
        data: DataFrame = DataFrame(
            device=device,
            metric=self.get_metric_type(),
            timestamp=timestamp,
            value=value,
            unit=self.UNIT
        ).serialize()
        logger.debug(data)
        return data
