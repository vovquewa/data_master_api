import os
from pathlib import Path
from typing import List, Union

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

from app.api.routers import main_router
from app.core.constants import APP_DESCRIPTION, APP_TITLE
from app.services.matchproducts import match

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION)

app.include_router(main_router)

WORK_DIR = Path(os.getcwd())
FILES_DIR = WORK_DIR / "Общее"


@app.post("/upload-files/")
async def upload_files(files: List[UploadFile] = File(...)):
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
        # Сохраняем файл в папку FILES_DIR
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


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # Имя файла и экземпляра приложения (main.py -> app)
        host="0.0.0.0",
        port=8000,
        reload=True,  # Для автообновления (опционально для разработки)
    )
