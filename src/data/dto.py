from dataclasses import dataclass, asdict
from typing import Optional
import uuid
from datetime import datetime

def serialize_with_uuid(obj):
    """Custom serialization function to handle UUID and datetime objects.

    Args:
        obj: The object to serialize.

    Returns:
        dict: The serialized object.
    """
    def convert(value):
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(value, list):
            return [convert(v) for v in value]
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        return value

    return {k: convert(v) for k, v in asdict(obj).items()}

@dataclass
class DeviceDTO:
    """Data Transfer Object for Device."""
    id: int
    name: str

    def serialize(self):
        """Serialize the DeviceDTO object.

        Returns:
            dict: The serialized DeviceDTO object.
        """
        return serialize_with_uuid(self)


@dataclass
class MetricTypeDTO:
    """Data Transfer Object for MetricType."""
    id: int
    name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def serialize(self):
        """Serialize the MetricTypeDTO object.

        Returns:
            dict: The serialized MetricTypeDTO object.
        """
        return serialize_with_uuid(self)


@dataclass
class UnitDTO:
    """Data Transfer Object for Unit."""
    id: int
    name: str
    symbol: Optional[str] = None

    def serialize(self):
        """Serialize the UnitDTO object.

        Returns:
            dict: The serialized UnitDTO object.
        """
        return serialize_with_uuid(self)


@dataclass
class MetricReadingDTO:
    """Data Transfer Object for MetricReading."""
    id: int
    device: DeviceDTO
    metric_type: MetricTypeDTO
    timestamp: datetime
    value: float
    unit: Optional[UnitDTO] = None
    utc_offset: Optional[float] = 0.0

    def serialize(self):
        """Serialize the MetricReadingDTO object.

        Returns:
            dict: The serialized MetricReadingDTO object.
        """
        return serialize_with_uuid(self)