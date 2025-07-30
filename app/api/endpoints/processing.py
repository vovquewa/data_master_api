import asyncio
import tempfile
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from app.core.logging import logger
from app.core.security import verify_token
from app.core.settings import settings
from app.services import get_file_or_404, match_products_post, remove_folder

router = APIRouter(tags=["processing"], prefix="/processing")

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
DATA_DIR = settings.DATA_DIR
MAX_FILE_SIZE = settings.MAX_FILE_SIZE


def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(400, "Filename is required")

    if Path(file.filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Only {ALLOWED_EXTENSIONS} files allowed")


def validate_file_size(contents: bytes, filename: str):
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, f"File {filename} too large")


@router.post("/match-orders-tmc", dependencies=[Depends(verify_token)])
async def match_orders_tmc(
    background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(400, "No files provided")

    session_id = uuid.uuid4()
    logger.info("Processing session started: %s", session_id)

    try:
        with tempfile.TemporaryDirectory(prefix=f"match_{session_id}_") as temp_dir:
            temp_path = Path(temp_dir)
            # Validate and save files
            for file in files:
                validate_file(file)

                contents = await file.read()
                validate_file_size(contents, file.filename)

                file_path = temp_path / file.filename
                file_path.write_bytes(contents)
                logger.info("File saved: %s", file.filename)

            # Process files
            result_path = await asyncio.to_thread(match_products_post, str(temp_path))

            # Prepare result
            result_dir = Path(DATA_DIR) / f"results_{session_id}"
            result_dir.mkdir(exist_ok=True)

            final_path = result_dir / "matched_results.xlsx"
            Path(result_path).rename(final_path)

            background_tasks.add_task(remove_folder, result_dir)
            logger.info("Processing completed: %s", session_id)

            return get_file_or_404(final_path)

    except ValueError as e:
        logger.error("Processing failed for session %s: %s", session_id, str(e))
        raise HTTPException(400, str(e))
    except HTTPException as e:
        logger.error("Processing failed for session %s: %s", session_id, str(e))
        raise e
    except Exception as e:
        logger.error("Processing failed for session %s: %s", session_id, str(e))
        raise HTTPException(500, "Processing failed")
