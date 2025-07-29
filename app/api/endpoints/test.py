import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.constants import API_TOKEN

router = APIRouter(
    tags=["test"],
    prefix="/test",
)


def get_file_or_404(file_path):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=os.path.basename(file_path))


@router.get("/excel")
async def download_excel():
    return get_file_or_404("app/data/export_test_data.xlsx")


@router.get("/image")
async def download_image():
    return get_file_or_404("app/data/export_test_image.png")


@router.get("/token")
async def get_token():
    if API_TOKEN:
        return {"token": API_TOKEN}
    else:
        raise HTTPException(status_code=404, detail="Token not found")
