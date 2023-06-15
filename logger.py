import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import settings


def create_logger(filename, log_name, log_level=logging.DEBUG):
    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)
    log_location = Path(".") / "logs"
    log_file = log_location / filename
    if not log_location.exists():
        log_location.mkdir()
    file_logger = RotatingFileHandler(log_file, maxBytes=10**4, backupCount=3)
    file_logger.setLevel(log_level)

    formatter = logging.Formatter(
        "[%(asctime)s] : %(levelname)s - file: %(filename)s - function: %(funcName)s() - line: %(lineno)d - message: %(message)s"
    )

    file_logger.setFormatter(formatter)

    logger.addHandler(file_logger)

    return logger

logger = create_logger(filename=settings.log_filename, log_name="truck_logger", log_level=settings.log_level)
