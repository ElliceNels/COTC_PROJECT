from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    """Model representing a device."""
    __tablename__ = 'devices'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    metric_readings = relationship('MetricReading', back_populates='device')

class MetricType(Base):
    """Model representing a type of metric."""
    __tablename__ = 'metric_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    metric_readings = relationship('MetricReading', back_populates='metric_type')

class Unit(Base):
    """Model representing a unit of measurement."""
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    symbol = Column(String, nullable=False, unique=False)
    metric_readings = relationship('MetricReading', back_populates='unit')

class MetricReading(Base):
    """Model representing a metric reading."""
    __tablename__ = 'metric_readings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)
    metric_type_id = Column(Integer, ForeignKey('metric_types.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)
    utc_offset = Column(Float, nullable=False, default=0.0)
    device = relationship('Device', back_populates='metric_readings')
    metric_type = relationship('MetricType', back_populates='metric_readings')
    unit = relationship('Unit', back_populates='metric_readings')
