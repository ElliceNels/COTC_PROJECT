from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MetricReading(Base):
    __tablename__ = 'metric_readings'

    id = Column(Integer, primary_key=True)
    device = Column(String, nullable=False)
    metric_type = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
