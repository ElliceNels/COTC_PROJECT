"""Configuration module."""

from pathlib import Path
import json
import os
from typing import ClassVar, Optional
from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Server configuration class."""
    host: str
    port: int
    debug: bool
    url: str

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
    params: dict[str, str]
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

    def __init__(self, rel_path: str = "config.json"):
        """Load the configuration from a JSON file.

        Args:
            rel_path (str): Relative path to the configuration file.
        """
        script_dir = Path(__file__).parent
        filepath = script_dir / rel_path

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
