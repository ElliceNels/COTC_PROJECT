import argparse
import logging
from app import launch_app
from data.metrics_collector import MetricsCollector
from logger import setup_logger
import threading

setup_logger()

logger = logging.getLogger(__name__)

def main():
    """Entry function."""

    parser = argparse.ArgumentParser(description='Run the collector server.')
    parser.add_argument('-c', action='store_true', help='Enable the collector server')
    parser.add_argument('-a', action='store_true', help='Enable the web app')
    args = parser.parse_args()

    if args.a:
        logger.info('Starting the application')
        launch_app()
    if args.c:
        logger.info('Starting the data collector')
        MetricsCollector.collect_data()
    else:
        logger.info('DEFAULT: Starting the application')
        launch_app()

if __name__ == '__main__':
    main()