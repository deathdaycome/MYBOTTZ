"""
Роутер для отслеживания транспорта (Wialon интеграция)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ..middleware.auth import get_current_admin_user
from ...database.models import AdminUser
from ...services.wialon_service import wialon_service
from ...config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.get("/api/units", response_class=JSONResponse)
async def get_all_units(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить все единицы транспорта с координатами (JSON API для React)"""

    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin', 'executor']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    try:
        units = await wialon_service.get_all_units_with_locations()

        return JSONResponse({
            "success": True,
            "units": units,
            "count": len(units),
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting units: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")


@router.get("/api/unit/{unit_id}", response_class=JSONResponse)
async def get_unit_details(
    unit_id: int,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить детальную информацию о единице транспорта"""

    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin', 'executor']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    try:
        location = await wialon_service.get_unit_location(unit_id)

        if not location:
            raise HTTPException(status_code=404, detail="Транспорт не найден")

        return JSONResponse({
            "success": True,
            "unit": location
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting unit {unit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")


@router.get("/api/unit/{unit_id}/track", response_class=JSONResponse)
async def get_unit_track(
    unit_id: int,
    hours: int = 24,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить трек (маршрут) транспорта за период

    Args:
        unit_id: ID транспорта
        hours: Количество часов назад (по умолчанию 24)
    """

    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin', 'executor']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    try:
        # Вычисляем временной интервал
        time_to = int(datetime.utcnow().timestamp())
        time_from = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())

        messages = await wialon_service.get_unit_messages(
            unit_id=unit_id,
            time_from=time_from,
            time_to=time_to
        )

        # Преобразуем сообщения в координаты трека
        track_points = []
        for msg in messages:
            if "pos" in msg:
                track_points.append({
                    "lat": msg["pos"].get("y"),
                    "lon": msg["pos"].get("x"),
                    "speed": msg["pos"].get("s", 0),
                    "time": msg.get("t", 0)
                })

        return JSONResponse({
            "success": True,
            "track": track_points,
            "count": len(track_points),
            "period": {
                "from": time_from,
                "to": time_to,
                "hours": hours
            }
        })

    except Exception as e:
        logger.error(f"Error getting track for unit {unit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения трека: {str(e)}")


@router.get("/api/drivers", response_class=JSONResponse)
async def get_drivers(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить список водителей"""

    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin', 'executor']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    try:
        drivers = await wialon_service.get_drivers()

        return JSONResponse({
            "success": True,
            "drivers": drivers,
            "count": len(drivers)
        })

    except Exception as e:
        logger.error(f"Error getting drivers: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения водителей: {str(e)}")


@router.get("/api/status", response_class=JSONResponse)
async def get_wialon_status(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Проверить статус подключения к Wialon API"""

    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    try:
        # Пробуем получить список units для проверки подключения
        units = await wialon_service.get_units()

        is_connected = len(units) >= 0  # Если не было ошибки, значит подключены

        return JSONResponse({
            "success": True,
            "connected": is_connected,
            "units_count": len(units),
            "api_url": wialon_service.base_url,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error checking Wialon status: {e}")
        return JSONResponse({
            "success": False,
            "connected": False,
            "error": str(e)
        })
