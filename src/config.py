"""Configuration module."""

import json
import os
from typing import ClassVar, Optional
from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Server configuration class."""
    host: str
    port: int
    debug: bool

class DatabaseConfig(BaseModel):
    """Database configuration class."""
    db_engine: str

class LoggingConfig(BaseModel):
    """Logging configuration class."""
    level: str
    format: str
    file_path: str

class ThirdPartyAPIConfig(BaseModel):
    """Third Party API configuration class."""
    name: str
    url: str
    cache_timeout_m: float

class Config(BaseModel):
    """Singleton configuration class."""

    _instance: ClassVar[Optional["Config"]] = None

    app_name: str
    server: ServerConfig
    logging: LoggingConfig
    third_party_api: ThirdPartyAPIConfig
    database: DatabaseConfig

    def __new__(cls, *args, **kwargs):
        """Singleton pattern enforcing on Config class creation."""

        if cls._instance is None:
            # Instantiate the Config class
            cls._instance = super(Config, cls).__new__(cls)
        # Else, return the existing instance
        return cls._instance

    def __init__(self, filepath: str = "src/config.json"):
        """Load the configuration from a JSON file."""

        # Walk through directories to find the config file
        current_dir = os.path.abspath(os.path.dirname(filepath))
        while not os.path.isfile(filepath):
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                raise FileNotFoundError(f'File not found: {filepath}')
            current_dir = parent_dir
            filepath = os.path.join(current_dir, os.path.basename(filepath))


        # Load the JSON config file
        try:
            with open(filepath, 'r') as file:
                data: dict = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f'File not found: {filepath}')
        except json.JSONDecodeError:
            raise ValueError(f'Invalid JSON file: {filepath}')
        
        # Initialize the configuration
        super().__init__(**data)

# Create a singleton instance of the Config class to be used throughout the application
config = Config()
