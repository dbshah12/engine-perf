import logging
import os
from logging.handlers import RotatingFileHandler


class FlushRotatingFileHandler(RotatingFileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()  # Force flush after each log write


def setup_logger():
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(os.path.dirname(parent_dir))
    log_dir = os.path.join(root_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "engine_perf.log")

    handler = FlushRotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=10
    )
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger("engine_perf")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


logger = setup_logger()
