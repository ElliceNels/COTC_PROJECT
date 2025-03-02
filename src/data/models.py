from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    __tablename__ = 'devices'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    metric_readings = relationship('MetricReading', back_populates='device')

class MetricType(Base):
    __tablename__ = 'metric_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    metric_readings = relationship('MetricReading', back_populates='metric_type')

class Unit(Base):
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    metric_readings = relationship('MetricReading', back_populates='unit')

class MetricReading(Base):
    __tablename__ = 'metric_readings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)
    metric_type_id = Column(Integer, ForeignKey('metric_types.id'), nullable=False)
    timestamp = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=True)

    device = relationship('Device', back_populates='metric_readings')
    metric_type = relationship('MetricType', back_populates='metric_readings')
    unit = relationship('Unit', back_populates='metric_readings')
