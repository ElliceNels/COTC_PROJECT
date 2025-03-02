from dataclasses import dataclass, asdict
from typing import Optional
import uuid

def serialize_with_uuid(obj):
    """Custom serialization function to handle UUID objects."""
    def convert(value):
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, list):
            return [convert(v) for v in value]
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        return value

    return {k: convert(v) for k, v in asdict(obj).items()}

@dataclass
class DeviceDTO:
    id: int
    name: str

    def serialize(self):
        return serialize_with_uuid(self)


@dataclass
class MetricTypeDTO:
    id: int
    name: str

    def serialize(self):
        return serialize_with_uuid(self)


@dataclass
class UnitDTO:
    id: int
    name: str

    def serialize(self):
        return serialize_with_uuid(self)


@dataclass
class MetricReadingDTO:
    id: int
    device: DeviceDTO
    metric_type: MetricTypeDTO
    timestamp: str
    value: float
    unit: Optional[UnitDTO] = None

    def serialize(self):
        return serialize_with_uuid(self)