"""This module contains the logger setup function."""

import logging
from config import Config 

logger = logging.getLogger(__name__)

def setup_logger():
    """Setup the logger."""

    config: Config = Config()
    logging.basicConfig(
        level=config.logging.level, 
        format=config.logging.format, 
        handlers=[
            logging.FileHandler(config.logging.file_path),
            logging.StreamHandler()
        ])
    logger.info('Logger is setup')
    