import logging
import time

logger = logging.getLogger(__name__)

class BlockTimer:
    """RAII Context manager for timing code blocks."""

    def __init__(self, block_name="Code block"):
        """Initialize the BlockTimer.

        Args:
            block_name (str): Name of the code block being timed.
        """
        self.block_name = block_name

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self.start = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context related to this object.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        self.end = time.perf_counter()
        elapsed_time = self.end - self.start
        logger.debug(f"{self.block_name} executed in: {elapsed_time:.4f} seconds")