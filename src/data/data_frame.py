"""Module to represent a data frame."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class DataFrame:
    """Class to represent a data frame."""

    # Deserialised data
    device: str
    metric: str
    timestamp: str
    value: float
    unit: Optional[str] = None

    # Serialised data
    def serialize(self):
        """Serialise the data frame."""
        return self.__dict__
