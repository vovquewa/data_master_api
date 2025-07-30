import uvicorn
from fastapi import FastAPI

from app.api.routers import main_router
from app.core.constants import APP_DESCRIPTION, APP_TITLE

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version="1.0.0")

app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
