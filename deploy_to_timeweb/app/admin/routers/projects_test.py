# Минимальный тестовый роутер для отладки
from fastapi import APIRouter

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/test")
async def test_endpoint():
    """Тестовый эндпоинт"""
    return {"message": "Роутер проектов работает!"}
