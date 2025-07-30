from pathlib import Path
from typing import Union

from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.core.logging import logger


def get_file_or_404(file_path: Union[str, Path]) -> FileResponse:
    """Return file or 404 error."""
    path = Path(file_path)
    if not path.exists():
        logger.error("File not found: %s", file_path)
        raise HTTPException(404, "File not found")
    return FileResponse(path, filename=path.name)
