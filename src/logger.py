"""This module contains the logger setup function."""

import logging
from config import config
import os

logger = logging.getLogger(__name__)

def setup_logger():
    """Setup the logger."""
    # Check if the logging file path exists and create it if it doesn't exist
    log_dir = os.path.dirname(config.logging.file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=config.logging.level, 
        format=config.logging.format, 
        handlers=[
            logging.FileHandler(config.logging.file_path),
            logging.StreamHandler()
        ])
    logger.info('Logger is setup')
    