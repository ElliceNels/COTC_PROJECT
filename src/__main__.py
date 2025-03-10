import argparse
import logging
from app import launch_app
from data.metrics_collector import MetricsCollector
from logger import setup_logger
import threading

setup_logger()

logger = logging.getLogger(__name__)
stop_event = threading.Event()

def main():
    """Entry function."""

    parser = argparse.ArgumentParser(description='Run the collector server.')
    parser.add_argument('-c', action='store_true', help='Enable the collector server')
    parser.add_argument('-a', action='store_true', help='Enable the web app')
    args = parser.parse_args()

    if args.a:
        logger.info('Starting the application')
        app_thread = threading.Thread(target=launch_app)
        app_thread.start()
    elif args.c:
        try:
            logger.info('Starting the data collector')
            mc = MetricsCollector()
            mc.start_scheduler()
            # Keep the main thread alive efficiently
            while not stop_event.is_set():
                stop_event.wait(1)
        except KeyboardInterrupt:
            logger.info('Shutting down the data collector')
            mc.stop_scheduler()
            stop_event.set()
    else:
        logger.info('DEFAULT: Starting the application')
        launch_app()

if __name__ == '__main__':
    main()