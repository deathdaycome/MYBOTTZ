# app/admin/routers/contractors.py
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from pydantic import BaseModel

from ...database.database import get_db
from ...database.models import User, AdminUser
from ...config.logging import get_logger
from ..middleware.auth import get_current_admin_user

logger = get_logger(__name__)

router = APIRouter(tags=["contractors"])

# Модель для подрядчика
class ContractorModel(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    admin_login: Optional[str] = None
    admin_password: Optional[str] = None
    force_password_change: Optional[bool] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=dict)
async def get_contractors(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить список всех подрядчиков."""
    try:
        
        # Получаем всех пользователей-исполнителей
        contractors = db.query(AdminUser).filter(AdminUser.role == 'executor').all()
        
        contractors_data = []
        for contractor in contractors:
            contractors_data.append({
                "id": contractor.id,
                "username": contractor.username,
                "first_name": contractor.first_name,
                "last_name": contractor.last_name,
                "email": contractor.email,
                "role": contractor.role,
                "is_active": contractor.is_active,
                "created_at": contractor.created_at.isoformat() if contractor.created_at else None,
                "last_login": contractor.last_login.isoformat() if contractor.last_login else None
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

@router.get("/{contractor_id}", response_model=dict)
async def get_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить информацию о конкретном подрядчике."""
    try:
        
        contractor = db.query(AdminUser).filter(
            AdminUser.id == contractor_id,
            AdminUser.role == 'executor'
        ).first()
        
        if not contractor:
            raise HTTPException(status_code=404, detail="Подрядчик не найден")
        
        contractor_data = {
            "id": contractor.id,
            "username": contractor.username,
            "first_name": contractor.first_name,
            "last_name": contractor.last_name,
            "email": contractor.email,
            "role": contractor.role,
            "is_active": contractor.is_active,
            "created_at": contractor.created_at.isoformat() if contractor.created_at else None,
            "last_login": contractor.last_login.isoformat() if contractor.last_login else None
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

@router.put("/{contractor_id}", response_model=dict)
async def update_contractor(
    contractor_id: int,
    contractor_data: ContractorModel,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Обновить информацию о подрядчике."""
    try:
        
        contractor = db.query(AdminUser).filter(
            AdminUser.id == contractor_id,
            AdminUser.role == 'executor'
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
                "email": contractor.email,
                "role": contractor.role,
                "is_active": contractor.is_active
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

@router.post("/", response_model=dict)
async def create_contractor(
    contractor_data: ContractorModel,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Создать нового исполнителя."""
    try:
        logger.info(f"Получен запрос на создание исполнителя: {contractor_data.dict()}")
        
        # Проверяем, не существует ли уже пользователь с таким email
        existing_contractor = db.query(AdminUser).filter(AdminUser.email == contractor_data.email).first()
        if existing_contractor:
            logger.warning(f"Попытка создать исполнителя с существующим email: {contractor_data.email}")
            return {"success": False, "message": "Пользователь с таким email уже существует"}
        
        # Создаем нового исполнителя
        admin_login = contractor_data.admin_login or contractor_data.username
        logger.info(f"Создаем исполнителя с логином: {admin_login}")
        
        new_contractor = AdminUser(
            username=admin_login,
            email=contractor_data.email,
            first_name=contractor_data.first_name,
            last_name=contractor_data.last_name,
            role='executor',
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Устанавливаем пароль для доступа к админке
        if contractor_data.admin_password:
            logger.info(f"Устанавливаем пароль для исполнителя {admin_login}")
            new_contractor.set_password(contractor_data.admin_password)
        else:
            logger.info(f"Устанавливаем временный пароль для исполнителя {admin_login}")
            new_contractor.set_password("temp123")
        
        db.add(new_contractor)
        db.commit()
        db.refresh(new_contractor)
        
        logger.info(f"Исполнитель успешно создан: ID={new_contractor.id}, username={new_contractor.username}")
        
        return {
            "success": True,
            "message": f"Исполнитель успешно создан. Доступ к админке: логин '{admin_login}', пароль установлен.",
            "data": {
                "id": new_contractor.id,
                "username": new_contractor.username,
                "admin_login": admin_login,
                "email": new_contractor.email,
                "first_name": new_contractor.first_name,
                "last_name": new_contractor.last_name,
                "role": new_contractor.role,
                "is_active": new_contractor.is_active
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка при создании исполнителя: {str(e)}", exc_info=True)
        db.rollback()
        return {"success": False, "message": str(e)}
