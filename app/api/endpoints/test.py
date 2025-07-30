from pathlib import Path

from fastapi import APIRouter

from app.core.settings import settings
from app.services import get_file_or_404

router = APIRouter(tags=["test"], prefix="/test")

DATA_DIR = settings.DATA_DIR


@router.get("/excel")
async def download_excel():
    """Download test Excel file."""
    return get_file_or_404(f"{DATA_DIR}/export_test_data.xlsx")


@router.get("/image")
async def download_image():
    """Download test image file."""
    return get_file_or_404(f"{DATA_DIR}/export_test_image.png")
