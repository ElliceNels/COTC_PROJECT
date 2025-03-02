"""This module contains the logger setup function."""

import logging
from config import config
import os

logger = logging.getLogger(__name__)

def setup_logger():
    """Setup the logger."""
    # Walk through directories to find the config file
    # Check if it exists and create it if it doesn't exist
    def find_config_file(start_dir, target_file):
        for root, _, files in os.walk(start_dir):
            if target_file in files:
                return os.path.join(root, target_file)
        return None

    start_dir = os.path.abspath(os.path.dirname(config.logging.file_path))
    config_file_path = find_config_file(start_dir, os.path.basename(config.logging.file_path))

    if config_file_path is None and not os.path.exists(config.logging.file_path):
        os.makedirs(os.path.dirname(config.logging.file_path), exist_ok=True)
        with open(config.logging.file_path, 'w') as f:
            pass

    logging.basicConfig(
        level=config.logging.level, 
        format=config.logging.format, 
        handlers=[
            logging.FileHandler(config.logging.file_path),
            logging.StreamHandler()
        ])
    logger.info('Logger is setup')
    