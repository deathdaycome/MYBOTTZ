# app/admin/routers/contractors.py
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from pydantic import BaseModel

from ...database.database import get_db
from ...database.models import User, AdminUser
from ...config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["contractors"])

# Базовая аутентификация
security = HTTPBasic()

# Модель для подрядчика
class ContractorModel(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    telegram_id: Optional[int] = None
    is_executor: Optional[bool] = None
    skills: Optional[str] = None
    hourly_rate: Optional[float] = None
    
    class Config:
        from_attributes = True

@router.get("/contractors/", response_model=dict)
async def get_contractors(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получить список всех подрядчиков."""
    try:
        # Проверяем аутентификацию
        admin = db.query(AdminUser).filter(
            AdminUser.username == credentials.username
        ).first()
        
        if not admin or not admin.check_password(credentials.password):
            raise HTTPException(status_code=401, detail="Неверные учетные данные")
        
        # Получаем всех пользователей-исполнителей
        contractors = db.query(User).filter(User.is_executor == True).all()
        
        contractors_data = []
        for contractor in contractors:
            contractors_data.append({
                "id": contractor.id,
                "username": contractor.username,
                "first_name": contractor.first_name,
                "last_name": contractor.last_name,
                "phone_number": contractor.phone_number,
                "telegram_id": contractor.telegram_id,
                "skills": contractor.skills,
                "hourly_rate": contractor.hourly_rate,
                "created_at": contractor.created_at.isoformat() if contractor.created_at else None
            })
        
        return {
            "success": True,
            "data": contractors_data,
            "total": len(contractors_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении списка подрядчиков: {str(e)}")
        return {
            "success": False,
            "message": f"Ошибка при получении списка подрядчиков: {str(e)}"
        }

@router.get("/contractors/{contractor_id}", response_model=dict)
async def get_contractor(
    contractor_id: int,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получить информацию о конкретном подрядчике."""
    try:
        # Проверяем аутентификацию
        admin = db.query(AdminUser).filter(
            AdminUser.username == credentials.username
        ).first()
        
        if not admin or not admin.check_password(credentials.password):
            raise HTTPException(status_code=401, detail="Неверные учетные данные")
        
        contractor = db.query(User).filter(
            User.id == contractor_id,
            User.is_executor == True
        ).first()
        
        if not contractor:
            raise HTTPException(status_code=404, detail="Подрядчик не найден")
        
        contractor_data = {
            "id": contractor.id,
            "username": contractor.username,
            "first_name": contractor.first_name,
            "last_name": contractor.last_name,
            "phone_number": contractor.phone_number,
            "telegram_id": contractor.telegram_id,
            "skills": contractor.skills,
            "hourly_rate": contractor.hourly_rate,
            "created_at": contractor.created_at.isoformat() if contractor.created_at else None
        }
        
        return {
            "success": True,
            "data": contractor_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении подрядчика {contractor_id}: {str(e)}")
        return {
            "success": False,
            "message": f"Ошибка при получении подрядчика: {str(e)}"
        }

@router.put("/contractors/{contractor_id}", response_model=dict)
async def update_contractor(
    contractor_id: int,
    contractor_data: ContractorModel,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Обновить информацию о подрядчике."""
    try:
        # Проверяем аутентификацию
        admin = db.query(AdminUser).filter(
            AdminUser.username == credentials.username
        ).first()
        
        if not admin or not admin.check_password(credentials.password):
            raise HTTPException(status_code=401, detail="Неверные учетные данные")
        
        contractor = db.query(User).filter(
            User.id == contractor_id,
            User.is_executor == True
        ).first()
        
        if not contractor:
            raise HTTPException(status_code=404, detail="Подрядчик не найден")
        
        # Обновляем данные подрядчика
        update_data = contractor_data.dict(exclude_unset=True, exclude_none=True)
        
        for field, value in update_data.items():
            if hasattr(contractor, field):
                setattr(contractor, field, value)
        
        contractor.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(contractor)
        
        return {
            "success": True,
            "message": "Информация о подрядчике успешно обновлена",
            "data": {
                "id": contractor.id,
                "username": contractor.username,
                "first_name": contractor.first_name,
                "last_name": contractor.last_name,
                "phone_number": contractor.phone_number,
                "telegram_id": contractor.telegram_id,
                "skills": contractor.skills,
                "hourly_rate": contractor.hourly_rate
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении подрядчика {contractor_id}: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка при обновлении подрядчика: {str(e)}"
        }
