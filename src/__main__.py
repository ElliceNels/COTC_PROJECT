
import logging
from logger import setup_logger

logger = logging.getLogger(__name__)

def main():
    """Entry function."""

    # Setup the logger
    setup_logger()

if __name__ == '__main__':
    main()