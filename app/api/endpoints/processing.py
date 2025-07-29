import os
import tempfile
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse

from app.core.security import verify_token
from app.services import match

WORK_DIR = Path(os.getcwd())
FILES_DIR = WORK_DIR / "Общее"

router = APIRouter(tags=["processing"], prefix="/processing")


@router.post("/match-orders-tmc", dependencies=[Depends(verify_token)])
async def match_orders_tmc(files: List[UploadFile] = File(...)):
    session_id = uuid.uuid4()
    with tempfile.TemporaryDirectory(prefix=f"match_{session_id}_") as temp_dir:
        # запись тестового файла
        with open(temp_dir + "/test.txt", "w") as f:
            f.write("test")
        print(temp_dir)
        # Проверяем существование папки FILES_DIR
        if not FILES_DIR.exists():
            # Если папки не существует, создаем ее
            FILES_DIR.mkdir(parents=True)
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
            if file_metadata["filename"]:
                with open(FILES_DIR / file_metadata["filename"], "wb") as f:
                    f.write(contents)

            # Добавляем информацию в список
            file_info.append(file_metadata)

            # Пример обработки содержимого файла
            # process_file(contents)

            # Обработка файлов
        match()
        result_path = WORK_DIR / "matched_results.xlsx"
        for file in FILES_DIR.iterdir():
            if file.is_file():
                file_path = FILES_DIR / file
                file_path.unlink()

        # return {"message": "Файлы успешно загружены", "files": file_info}
        return FileResponse(result_path)
