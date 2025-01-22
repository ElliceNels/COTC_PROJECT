
import logging
from app import launch_app
from logger import setup_logger

setup_logger()

logger = logging.getLogger(__name__)

def main():
    """Entry function."""

    logger.info('Starting the application')
    launch_app()

if __name__ == '__main__':
    main()