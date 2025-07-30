import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():  # важно, чтобы не дублировать обработчики
    # Обработчик для лог-файла
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Обработчик для консоли (stdout)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(levelname)s:     %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

logger.propagate = False  # отключает проброс сообщений к root-логгеру
