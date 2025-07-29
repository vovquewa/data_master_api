import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import FileResponse

from app.core.constants import DATA_DIR
from app.core.logging import logger
from app.core.security import verify_token
from app.services import match_products

router = APIRouter(tags=["processing"], prefix="/processing")


@router.post("/match-orders-tmc", dependencies=[Depends(verify_token)])
async def match_orders_tmc(
    background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)
):
    session_id = uuid.uuid4()
    logger.info("Старт функции сопоставления файлов. Сессия: %s", session_id)
    with tempfile.TemporaryDirectory(prefix=f"match_{session_id}_") as temp_dir:

        # Создаем список для хранения информации о файлах
        file_info = []

        for file in files:
            # Читаем содержимое файла
            contents = await file.read()

            # Получаем метаданные файла
            file_metadata = {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(contents),
                # Здесь можно добавить дополнительную обработку
            }
            # Сохраняем файл в папку temp_dir
            temp_dir_path = Path(temp_dir)
            if file_metadata["filename"]:
                file_path = temp_dir_path / file_metadata["filename"]
                with open(file_path, "wb") as f:
                    f.write(contents)

            # Добавляем информацию в список
            file_info.append(file_metadata)
            logger.info("Файл %s загружен", file.filename)
        logger.info("Старт обработки файлов. Сессия: %s", session_id)
        result = match_products(temp_dir)
        logger.info("Завершение обработки файлов. Сессия: %s", session_id)
        result_dir_tmp = Path(os.path.join(DATA_DIR, f"results_{session_id}"))
        logger.info("Создание папки %s", result_dir_tmp)
        if not os.path.exists(result_dir_tmp):
            os.mkdir(result_dir_tmp)
        shutil.copy(Path(result), Path(result_dir_tmp) / "matched_results.xlsx")
        if os.path.exists(Path(result)):
            logger.info("Результат сохранен в %s", result_dir_tmp)
        background_tasks.add_task(shutil.rmtree, result_dir_tmp)
        return FileResponse(Path(result_dir_tmp) / "matched_results.xlsx")
