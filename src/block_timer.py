import time

class BlockTimer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        elapsed_time = self.end - self.start
        print(f"Code block executed in: {elapsed_time:.4f} seconds")