from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.constants import API_TOKEN, DATA_DIR

router = APIRouter(tags=["test"], prefix="/test")


def get_file_or_404(file_path: str) -> FileResponse:
    """Return file or 404 error."""
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(path, filename=path.name)


@router.get("/excel")
async def download_excel():
    """Download test Excel file."""
    return get_file_or_404(f"{DATA_DIR}/export_test_data.xlsx")


@router.get("/image")
async def download_image():
    """Download test image file."""
    return get_file_or_404(f"{DATA_DIR}/export_test_image.png")
