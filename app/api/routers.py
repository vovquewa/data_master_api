from fastapi import APIRouter

from app.api.endpoints import processing_router, test_router

main_router = APIRouter(
    prefix="/api",
)

main_router.include_router(test_router)
main_router.include_router(processing_router)
