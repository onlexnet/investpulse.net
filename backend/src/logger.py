import logging
from typing import Any

def setup_logger(name: str, log_file: str) -> logging.Logger:
    """
    Set up a logger with the specified name and log file.

    Args:
        name (str): Logger name.
        log_file (str): Path to log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
