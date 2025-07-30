import shutil
from pathlib import Path

from app.core import logger


def remove_folder(folder_path: Path):
    if folder_path.exists():
        try:
            shutil.rmtree(folder_path)
            logger.debug(f"Папка '{folder_path}' удалена.")
        except Exception as e:
            logger.error(f"Failed to remove folder '{folder_path}': {e}")
