"""Configuration module."""

import json
from typing import ClassVar, Optional
from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Server configuration class."""
    host: str
    port: int

class LoggingConfig(BaseModel):
    """Logging configuration class."""
    level: str
    format: str
    file_path: str

class Config(BaseModel):
    """Singleton configuration class."""

    _instance: ClassVar[Optional["Config"]] = None

    app_name: str
    server: ServerConfig
    logging: LoggingConfig

    def __new__(cls, *args, **kwargs):
        """Singleton pattern enforcing on Config class creation."""

        if cls._instance is None:
            # Instantiate the Config class
            cls._instance = super(Config, cls).__new__(cls)
        # Else, return the existing instance
        return cls._instance

    def __init__(self, filepath: str = "../COTC_PROJECT/src/config.json"):
        """Load the configuration from a JSON file."""

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
