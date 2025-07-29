import os

from dotenv import load_dotenv

load_dotenv("env/.env")

API_TOKEN = os.getenv("API_TOKEN")
APP_TITLE = "Data Master API"
APP_DESCRIPTION = "Сервис для обработки фалов эксель"
WORK_DIR = os.getcwd()
DATA_DIR = os.path.join(WORK_DIR, "app/data")
