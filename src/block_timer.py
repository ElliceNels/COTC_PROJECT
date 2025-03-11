import logging
import time

logger = logging.getLogger(__name__)
class BlockTimer:

    def __init__(self, block_name="Code block"):
        self.block_name = block_name

    def __enter__(self):
        self.start = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        elapsed_time = self.end - self.start
        logger.debug(f"{self.block_name} executed in: {elapsed_time:.4f} seconds")