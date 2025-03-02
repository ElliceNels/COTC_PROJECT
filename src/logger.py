"""This module contains the logger setup function."""

import logging
from config import config
import os

logger = logging.getLogger(__name__)

def setup_logger():
    """Setup the logger."""
    # Walk through directories to find the config file
    # Check if it exists and create it if it doesn't exist
    current_dir = os.path.abspath(os.path.dirname(config.logging.file_path))
    while not os.path.isfile(config.logging.file_path):
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            log_dir = os.path.dirname(config.logging.file_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            break
        current_dir = parent_dir
        filepath = os.path.join(current_dir, os.path.basename(filepath))

    logging.basicConfig(
        level=config.logging.level, 
        format=config.logging.format, 
        handlers=[
            logging.FileHandler(config.logging.file_path),
            logging.StreamHandler()
        ])
    logger.info('Logger is setup')
    