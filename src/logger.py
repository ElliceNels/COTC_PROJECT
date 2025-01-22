"""This module contains the logger setup function."""

import logging
from config import config

logger = logging.getLogger(__name__)

def setup_logger():
    """Setup the logger."""

    logging.basicConfig(
        level=config.logging.level, 
        format=config.logging.format, 
        handlers=[
            logging.FileHandler(config.logging.file_path),
            logging.StreamHandler()
        ])
    logger.info('Logger is setup')
    