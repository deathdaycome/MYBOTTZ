# app/admin/routers/contractors.py
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from pydantic import BaseModel

from ...core.database import get_db
from ...database.models import User, AdminUser, ContractorPayment, Task
from ...config.logging import get_logger
from ..middleware.auth import require_admin_auth
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)) -> AdminUser:
    """Получение текущего администратора"""
    from ...config.settings import settings
    
    # Сначала проверяем старую систему (владелец)
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    if correct_username and correct_password:
        # Возвращаем реального администратора из БД
        admin_user = db.query(AdminUser).filter(AdminUser.username == credentials.username).first()
        if admin_user:
            return admin_user
        # Если в БД нет такого пользователя, создаем его
        admin = AdminUser(
            username=settings.ADMIN_USERNAME,
            first_name='System',
            last_name='Administrator',
            email='admin@system.local',
            role='owner',  # Главный администратор - владелец
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.set_password(settings.ADMIN_PASSWORD)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    
    # Проверяем в БД для исполнителей
    admin_user = db.query(AdminUser).filter(AdminUser.username == credentials.username).first()
    if admin_user and admin_user.check_password(credentials.password):
        return admin_user
    
    raise HTTPException(
        status_code=401,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )

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
    telegram_id: Optional[int] = None  # Добавляем поле для Telegram ID
    
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
            # Подсчитываем общую сумму выплат
            total_payments = db.query(func.sum(ContractorPayment.amount)).filter(
                ContractorPayment.contractor_id == contractor.id
            ).scalar() or 0
            
            contractors_data.append({
                "id": contractor.id,
                "username": contractor.username,
                "first_name": contractor.first_name,
                "last_name": contractor.last_name,
                "email": contractor.email,
                "role": contractor.role,
                "is_active": contractor.is_active,
                "telegram_id": contractor.telegram_id,  # Добавляем Telegram ID
                "created_at": contractor.created_at.isoformat() if contractor.created_at else None,
                "last_login": contractor.last_login.isoformat() if contractor.last_login else None,
                "total_payments": total_payments
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
            "telegram_id": contractor.telegram_id,  # Добавляем Telegram ID
            "created_at": contractor.created_at.isoformat() if contractor.created_at else None,
            "last_login": contractor.last_login.isoformat() if contractor.last_login else None
        }
        
        # Получаем выплаты исполнителя
        payments = db.query(ContractorPayment).filter(
            ContractorPayment.contractor_id == contractor_id
        ).order_by(desc(ContractorPayment.created_at)).all()
        
        payments_data = []
        for payment in payments:
            payments_data.append({
                "id": payment.id,
                "amount": payment.amount,
                "description": payment.description,
                "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "status": payment.status,
                "created_at": payment.created_at.isoformat() if payment.created_at else None
            })
        
        return {
            "success": True,
            "contractor": contractor_data,
            "assignments": [],  # TODO: добавить реальные назначения
            "payments": payments_data
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

        # Исключаем admin_password из обновления (для смены пароля есть отдельный endpoint)
        excluded_fields = ['admin_password', 'id']

        for field, value in update_data.items():
            if field not in excluded_fields and hasattr(contractor, field):
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
                "is_active": contractor.is_active,
                "telegram_id": contractor.telegram_id  # Добавляем Telegram ID
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

@router.delete("/{contractor_id}", response_model=dict)
async def delete_contractor(
    contractor_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Удалить исполнителя."""
    try:
        logger.info(f"Запрос на удаление исполнителя: {contractor_id}")

        # Находим исполнителя
        contractor = db.query(AdminUser).filter(
            AdminUser.id == contractor_id,
            AdminUser.role == 'executor'
        ).first()

        if not contractor:
            logger.warning(f"Исполнитель с ID {contractor_id} не найден")
            return {"success": False, "message": "Исполнитель не найден"}

        # Проверяем, что не удаляем самого себя
        if contractor.id == current_user.id:
            logger.warning(f"Попытка удалить самого себя: {contractor_id}")
            return {"success": False, "message": "Нельзя удалить самого себя"}

        # Проверяем наличие задач, назначенных на исполнителя
        assigned_tasks = db.query(Task).filter(Task.assigned_to_id == contractor_id).all()

        if assigned_tasks:
            # Подсчитываем активные и завершенные задачи
            active_tasks = [t for t in assigned_tasks if t.status not in ['completed', 'cancelled']]

            if active_tasks:
                logger.warning(f"Попытка удалить исполнителя {contractor_id} с активными задачами: {len(active_tasks)} шт.")
                return {
                    "success": False,
                    "message": f"Невозможно удалить исполнителя. У него есть {len(active_tasks)} активных задач. Сначала переназначьте или завершите эти задачи."
                }

            # Если есть только завершенные задачи, переназначаем их на текущего пользователя для истории
            logger.info(f"Переназначение {len(assigned_tasks)} завершенных задач с исполнителя {contractor_id} на {current_user.id}")
            for task in assigned_tasks:
                task.assigned_to_id = current_user.id
                task.updated_at = datetime.utcnow()

        # Также проверяем задачи, созданные исполнителем
        created_tasks = db.query(Task).filter(Task.created_by_id == contractor_id).all()
        if created_tasks:
            logger.info(f"Переназначение {len(created_tasks)} задач, созданных исполнителем {contractor_id}, на {current_user.id}")
            for task in created_tasks:
                task.created_by_id = current_user.id
                task.updated_at = datetime.utcnow()

        # Удаляем исполнителя
        db.delete(contractor)
        db.commit()

        logger.info(f"Исполнитель успешно удален: ID={contractor_id}, username={contractor.username}")

        return {
            "success": True,
            "message": f"Исполнитель {contractor.username} успешно удален"
        }

    except Exception as e:
        logger.error(f"Ошибка при удалении исполнителя {contractor_id}: {str(e)}", exc_info=True)
        db.rollback()
        return {"success": False, "message": str(e)}

@router.post("/{contractor_id}/change-password", response_model=dict)
async def change_contractor_password(
    contractor_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Изменить пароль исполнителя (только для администраторов)."""
    try:
        logger.info(f"Пользователь {current_user.username} (роль: {current_user.role}) меняет пароль для исполнителя {contractor_id}")
        
        # Проверяем, что текущий пользователь - администратор или владелец
        if current_user.role not in ['admin', 'owner']:
            logger.warning(f"Попытка смены пароля не администратором: {current_user.username}, роль: {current_user.role}")
            return {"success": False, "message": "Только администраторы могут менять пароли исполнителей"}
        
        # Находим исполнителя
        contractor = db.query(AdminUser).filter(
            AdminUser.id == contractor_id,
            AdminUser.role == 'executor'
        ).first()
        
        if not contractor:
            logger.warning(f"Исполнитель с ID {contractor_id} не найден")
            return {"success": False, "message": "Исполнитель не найден"}
        
        # Получаем новый пароль
        new_password = password_data.get('new_password')
        if not new_password:
            return {"success": False, "message": "Новый пароль не указан"}
        
        if len(new_password) < 6:
            return {"success": False, "message": "Пароль должен содержать минимум 6 символов"}
        
        # Устанавливаем новый пароль
        contractor.set_password(new_password)
        contractor.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Пароль для исполнителя {contractor_id} ({contractor.username}) успешно изменен пользователем {current_user.username} (роль: {current_user.role})")
        
        return {
            "success": True,
            "message": f"Пароль для исполнителя {contractor.username} успешно изменен"
        }
        
    except Exception as e:
        logger.error(f"Ошибка при изменении пароля исполнителя {contractor_id}: {str(e)}", exc_info=True)
        db.rollback()
        return {"success": False, "message": str(e)}

@router.post("/{contractor_id}/payments", response_model=dict)
async def create_payment(
    contractor_id: int,
    payment_data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Создать выплату для исполнителя."""
    try:
        logger.info(f"Создание выплаты для исполнителя {contractor_id}: {payment_data}")
        
        # Находим исполнителя
        contractor = db.query(AdminUser).filter(
            AdminUser.id == contractor_id,
            AdminUser.role == 'executor'
        ).first()
        
        if not contractor:
            logger.warning(f"Исполнитель с ID {contractor_id} не найден")
            return {"success": False, "message": "Исполнитель не найден"}
        
        # Создаем выплату в базе данных
        new_payment = ContractorPayment(
            contractor_id=contractor_id,
            amount=payment_data.get('amount'),
            description=payment_data.get('description', ''),
            payment_type='project',
            status='pending',
            created_at=datetime.utcnow(),
            created_by_id=current_user.id
        )
        
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        
        logger.info(f"Выплата для исполнителя {contractor_id} создана успешно: ID={new_payment.id}, сумма={new_payment.amount}")
        
        return {
            "success": True,
            "message": f"Выплата {new_payment.amount}₽ для {contractor.username} успешно создана",
            "payment": {
                "id": new_payment.id,
                "amount": new_payment.amount,
                "description": new_payment.description,
                "status": new_payment.status,
                "created_at": new_payment.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка при создании выплаты для исполнителя {contractor_id}: {str(e)}", exc_info=True)
        db.rollback()
        return {"success": False, "message": str(e)}
