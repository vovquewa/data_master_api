import shutil
from pathlib import Path
from typing import Union

from app.core.logging import logger


def remove_folder(folder_path: Union[Path, str]) -> None:
    """Remove folder and its contents safely."""
    path = Path(folder_path)
    if path.exists():
        try:
            shutil.rmtree(path)
            logger.debug("Folder removed: %s", path)
        except PermissionError:
            logger.error("Permission denied removing folder: %s", path)
        except OSError as e:
            logger.error("OS error removing folder %s: %s", path, e)
        except Exception as e:
            logger.error("Unexpected error removing folder %s: %s", path, e)
