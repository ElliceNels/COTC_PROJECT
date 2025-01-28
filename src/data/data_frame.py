"""Module to represent a data frame."""
from dataclasses import dataclass

@dataclass
class DataFrame:
    """Class to represent a data frame."""

    # Deserialised data
    device: str
    metric: str
    timestamp: str
    value: float
    unit: str = None

    # Serialised data
    def serialize(self):
        """Serialise the data frame."""
        return self.__dict__
