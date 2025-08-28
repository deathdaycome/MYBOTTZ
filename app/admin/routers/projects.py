# app/admin/routers/projects.py
from datetime import datetime
from typing import List, Optional
import os
import uuid
import secrets
import traceback
from fastapi import APIRouter, HTTPException, Depends, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from pydantic import BaseModel

from ...database.database import get_db, get_db_context
from ...database.models import (
    Project, User, AdminUser, ProjectFile, ProjectStatus, ProjectRevision, 
    RevisionMessage, RevisionFile, ProjectStatusLog, ConsultantSession, 
    FinanceTransaction, ContractorPayment, ServiceExpense
)
from ...config.logging import get_logger
from ...config.settings import settings
from ...services.notification_service import NotificationService
from ...services.employee_notification_service import employee_notification_service

logger = get_logger(__name__)
notification_service = NotificationService()

router = APIRouter(tags=["projects"])

# Базовая аутентификация
security = HTTPBasic()

# Модель для создания проекта с обязательными полями
class ProjectCreateModel(BaseModel):
    title: str  # Обязательное
    user_id: int  # Клиент (обязательное)
    estimated_cost: float  # Стоимость (обязательное)
    start_date: datetime  # Дата начала (обязательное)
    planned_end_date: datetime  # Плановая дата завершения (обязательное)
    responsible_manager_id: Optional[int] = None  # Ответственный менеджер
    description: Optional[str] = None
    priority: str = "normal"
    project_type: Optional[str] = None
    complexity: str = "medium"
    executor_cost: Optional[float] = None
    prepayment_amount: Optional[float] = None
    estimated_hours: Optional[int] = 0
    assigned_executor_id: Optional[int] = None

# Модель для редактирования проекта
class ProjectUpdateModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    project_type: Optional[str] = None
    complexity: Optional[str] = None
    estimated_cost: Optional[float] = None
    executor_cost: Optional[float] = None
    final_cost: Optional[float] = None
    prepayment_amount: Optional[float] = None
    client_paid_total: Optional[float] = None
    executor_paid_total: Optional[float] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    deadline: Optional[str] = None  # ISO format date string
    planned_end_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    responsible_manager_id: Optional[int] = None
    assigned_executor_id: Optional[int] = None
    comment: Optional[str] = None  # Комментарий к изменению
    bot_token: Optional[str] = None  # API токен Telegram бота
    timeweb_login: Optional[str] = None  # Логин Timeweb
    timeweb_password: Optional[str] = None  # Пароль Timeweb
    color: Optional[str] = None  # Цветовая метка проекта (default, green, yellow, red)
    telegram_id: Optional[str] = None  # Telegram ID пользователя

    class Config:
        from_attributes = True

# Модель для создания проекта
class ProjectCreateModel(BaseModel):
    title: str
    description: str
    user_id: Optional[int] = None  # ID существующего клиента
    client_telegram_id: Optional[str] = None  # Telegram ID клиента (для создания нового)
    client_name: Optional[str] = None  # Имя клиента (для создания нового)
    client_phone: Optional[str] = None  # Телефон клиента (для создания нового)
    project_type: str = "website"
    complexity: str = "medium"
    priority: str = "medium"
    estimated_cost: Optional[float] = None
    executor_cost: Optional[float] = None
    prepayment_amount: Optional[float] = 0
    client_paid_total: Optional[float] = 0
    executor_paid_total: Optional[float] = 0
    estimated_hours: Optional[int] = None
    deadline: Optional[str] = None  # ISO format date string
    status: str = "new"
    assigned_executor_id: Optional[int] = None
    bot_token: Optional[str] = None  # API токен Telegram бота
    timeweb_login: Optional[str] = None  # Логин Timeweb
    timeweb_password: Optional[str] = None  # Пароль Timeweb
    
    class Config:
        from_attributes = True

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """Получение текущего пользователя с проверкой аутентификации"""
    # Сначала проверяем старую систему (владелец)
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    if correct_username and correct_password:
        # Возвращаем объект владельца
        return {
            "id": 1,
            "username": credentials.username,
            "role": "owner",
            "is_active": True
        }
    
    # Если не подошло, проверяем новую систему (исполнители)
    try:
        with get_db_context() as db:
            from ...services.auth_service import AuthService
            admin_user = db.query(AdminUser).filter(
                AdminUser.username == credentials.username,
                AdminUser.is_active == True
            ).first()
            
            if admin_user and AuthService.verify_password(credentials.password, admin_user.password_hash):
                return {
                    "id": admin_user.id,
                    "username": admin_user.username,
                    "role": admin_user.role,
                    "is_active": admin_user.is_active
                }
    except Exception as e:
        logger.error(f"Ошибка проверки в новой системе: {e}")
    
    # Если ничего не подошло
    raise HTTPException(
        status_code=401,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )

# Статусы проектов
PROJECT_STATUSES = {
    # Старые статусы (для совместимости)
    "new": "Новый",
    "review": "На рассмотрении", 
    "accepted": "Принят",
    "in_progress": "В работе",
    "testing": "Тестирование",
    "completed": "Завершен",
    "cancelled": "Отменен",
    "on_hold": "Приостановлен",
    
    # Новые статусы (из таблицы project_statuses)
    "новый": "Новый",
    "на_рассмотрении": "На рассмотрении", 
    "согласован": "Согласован",
    "в_работе": "В работе",
    "на_тестировании": "На тестировании",
    "завершен": "Завершен",
    "отменен": "Отменен",
    "приостановлен": "Приостановлен",
    "тестовый_статус": "Тестовый статус",
    "админ_консоль_готова": "админ консоль готова",
    
    # Дополнительные вариации для совместимости
    "active": "В работе",
    "в работе": "В работе"
}

@router.get("/")
async def get_projects(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_desc",
    show_archived: bool = False,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список проектов с фильтрами (с учетом ролей доступа)"""
    try:
        # Начинаем с базового запроса
        query = db.query(Project).join(User, Project.user_id == User.id)
        
        # Фильтр архивных проектов
        if show_archived:
            query = query.filter(Project.is_archived == True)
        else:
            query = query.filter(or_(Project.is_archived == False, Project.is_archived == None))
        
        # Фильтрация по роли пользователя
        if current_user["role"] == "executor":
            # Исполнитель видит только назначенные ему проекты
            query = query.filter(Project.assigned_executor_id == current_user["id"])
        # Владелец видит все проекты (без дополнительных фильтров)
        
        # Применяем остальные фильтры
        if status:
            query = query.filter(Project.status == status)
        
        if search:
            search_filter = or_(
                Project.title.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Применяем сортировку
        if sort_by == "created_desc":
            query = query.order_by(desc(Project.created_at))
        elif sort_by == "created_asc":
            query = query.order_by(asc(Project.created_at))
        else:
            query = query.order_by(desc(Project.updated_at))
        
        # Подсчитываем общее количество
        total = query.count()
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        projects = query.offset(offset).limit(per_page).all()
        
        # Конвертируем в словари с дополнительной информацией
        projects_data = []
        for project in projects:
            project_dict = project.to_dict()
            
            # Добавляем информацию о пользователе (клиенте)
            user = db.query(User).filter(User.id == project.user_id).first()
            if user:
                user_dict = user.to_dict()
                
                # Добавляем Telegram ID из preferences или metadata проекта
                telegram_id = ""
                if user.preferences and user.preferences.get('telegram_id'):
                    telegram_id = user.preferences.get('telegram_id', '')
                elif project.project_metadata and project.project_metadata.get('user_telegram_id'):
                    telegram_id = project.project_metadata.get('user_telegram_id', '')
                    
                user_dict["telegram_id"] = telegram_id
                project_dict["user"] = user_dict
            
            # Добавляем информацию об исполнителе
            if project.assigned_executor_id:
                executor = db.query(AdminUser).filter(AdminUser.id == project.assigned_executor_id).first()
                if executor:
                    project_dict["assigned_executor"] = {
                        "id": executor.id,
                        "username": executor.username,
                        "first_name": executor.first_name,
                        "last_name": executor.last_name,
                        "role": executor.role
                    }
                else:
                    project_dict["assigned_executor"] = None
            else:
                project_dict["assigned_executor"] = None
            
            # Добавляем читаемые названия статуса и приоритета
            project_dict["status_name"] = PROJECT_STATUSES.get(project.status, project.status)
            
            # Для исполнителей скрываем полную стоимость
            if current_user["role"] == "executor":
                project_dict["estimated_cost"] = project.executor_cost or 0
                project_dict.pop("executor_cost", None)  # Убираем дублирование
            
            # Добавляем информацию о новых полях из metadata
            if project.project_metadata:
                # Информация о боте
                project_dict["bot_token"] = project.project_metadata.get('bot_token', '')
                
                # Информация о Timeweb
                if 'timeweb_login' in project.project_metadata or 'timeweb_credentials' in project.project_metadata:
                    # Новый формат
                    if 'timeweb_login' in project.project_metadata:
                        project_dict["timeweb"] = {
                            "login": project.project_metadata.get('timeweb_login', ''),
                            "has_credentials": bool(project.project_metadata.get('timeweb_login', '')),
                            "created_at": project.project_metadata.get('created_at', '')
                        }
                    # Старый формат для совместимости
                    elif 'timeweb_credentials' in project.project_metadata:
                        timeweb_data = project.project_metadata['timeweb_credentials']
                        project_dict["timeweb"] = {
                            "login": timeweb_data.get('login', ''),
                            "has_credentials": True,
                            "created_at": timeweb_data.get('created_at', '')
                        }
                else:
                    project_dict["timeweb"] = {
                        "has_credentials": False
                    }
            else:
                project_dict["bot_token"] = ''
                project_dict["timeweb"] = {
                    "has_credentials": False
                }
            
            projects_data.append(project_dict)
        
        return {
            "success": True,
            "projects": projects_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            },
            "user_role": current_user["role"]
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения проектов: {e}")
        return {
            "success": False,
            "message": f"Ошибка получения проектов: {str(e)}",
            "projects": []
        }

@router.get("/{project_id}")
async def get_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить проект по ID (с учетом ролей доступа)"""
    try:
        # Базовый запрос
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return {
                "success": False,
                "message": "Проект не найден"
            }
        
        # Проверяем права доступа
        if current_user["role"] == "executor":
            if project.assigned_executor_id != current_user["id"]:
                return {
                    "success": False,
                    "message": "У вас нет доступа к этому проекту"
                }
        
        project_dict = project.to_dict()
        
        # Добавляем информацию о пользователе (клиенте)
        user = db.query(User).filter(User.id == project.user_id).first()
        if user:
            user_dict = user.to_dict()
            
            # Добавляем Telegram ID из preferences или metadata проекта
            telegram_id = ""
            if user.preferences and user.preferences.get('telegram_id'):
                telegram_id = user.preferences.get('telegram_id', '')
            elif project.project_metadata and project.project_metadata.get('user_telegram_id'):
                telegram_id = project.project_metadata.get('user_telegram_id', '')
                
            user_dict["telegram_id"] = telegram_id
            project_dict["user"] = user_dict
        
        # Добавляем информацию об исполнителе
        if project.assigned_executor_id:
            executor = db.query(AdminUser).filter(AdminUser.id == project.assigned_executor_id).first()
            if executor:
                project_dict["assigned_executor"] = {
                    "id": executor.id,
                    "username": executor.username,
                    "first_name": executor.first_name,
                    "last_name": executor.last_name,
                    "role": executor.role,
                    "email": executor.email
                }
            else:
                project_dict["assigned_executor"] = None
        else:
            project_dict["assigned_executor"] = None
        
        # Добавляем читаемые названия
        project_dict["status_name"] = PROJECT_STATUSES.get(project.status, project.status)
        
        # Для исполнителей скрываем полную стоимость
        if current_user["role"] == "executor":
            project_dict["estimated_cost"] = project.executor_cost or 0
            project_dict.pop("executor_cost", None)
        
        # Добавляем информацию из новых полей пользователя и metadata проекта
        bot_token = ""
        timeweb_login = ""
        timeweb_password = ""
        user_telegram_id = ""
        chat_id = ""
        
        # Приоритет: сначала данные пользователя, потом из metadata проекта
        if user:
            bot_token = user.bot_token or ""
            timeweb_login = user.timeweb_login or ""
            timeweb_password = user.timeweb_password or ""
            user_telegram_id = user.user_telegram_id or ""
            chat_id = user.chat_id or ""
            
        # Если нет данных в полях пользователя, пробуем metadata проекта
        if project.project_metadata:
            if not bot_token:
                bot_token = project.project_metadata.get('bot_token', '')
            
            if not timeweb_login and 'timeweb_credentials' in project.project_metadata:
                timeweb_data = project.project_metadata['timeweb_credentials']
                timeweb_login = timeweb_data.get('login', '')
                timeweb_password = timeweb_data.get('password', '')
            
            if not user_telegram_id:
                user_telegram_id = project.project_metadata.get('user_telegram_id', '')
        
        # Добавляем данные в ответ
        project_dict["bot_token"] = bot_token
        project_dict["user_telegram_id"] = user_telegram_id  
        project_dict["chat_id"] = chat_id
        
        # Информация о Timeweb
        project_dict["timeweb"] = {
            "login": timeweb_login,
            "password": timeweb_password,  # В детальном просмотре показываем пароль
            "has_credentials": bool(timeweb_login),
        }
        
        return {
            "success": True,
            "project": project_dict
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения проекта {project_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка получения проекта: {str(e)}"
        }

@router.put("/{project_id}/status")
async def update_project_status(
    project_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить статус проекта (с учетом ролей доступа)"""
    try:
        data = await request.json()
        new_status_id = data.get("status_id")
        new_status_name = data.get("status")  # Поддерживаем старый формат
        comment = data.get("comment", "")
        
        # Определяем статус по ID или по имени
        status_obj = None
        if new_status_id:
            status_obj = db.query(ProjectStatus).filter(
                ProjectStatus.id == new_status_id,
                ProjectStatus.is_active == True
            ).first()
        elif new_status_name:
            # Поддерживаем старый формат со строковыми константами
            if new_status_name in PROJECT_STATUSES:
                status_obj = db.query(ProjectStatus).filter(
                    ProjectStatus.name == PROJECT_STATUSES[new_status_name],
                    ProjectStatus.is_active == True
                ).first()
        
        if not status_obj:
            return {
                "success": False,
                "message": "Статус обязателен или не найден"
            }
        
        # Получаем проект
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {
                "success": False,
                "message": "Проект не найден"
            }
        
        # Проверяем права доступа
        if current_user["role"] == "executor":
            if project.assigned_executor_id != current_user["id"]:
                return {
                    "success": False,
                    "message": "У вас нет доступа к этому проекту"
                }
        
        # Получаем старый статус для логирования
        old_status = project.status
        old_status_obj = db.query(ProjectStatus).filter(
            ProjectStatus.name == PROJECT_STATUSES.get(old_status, old_status),
            ProjectStatus.is_active == True
        ).first()
        
        # Обновляем статус (используем имя статуса в нижнем регистре как ключ)
        project.status = status_obj.name.lower().replace(' ', '_')
        project.updated_at = datetime.utcnow()
        
        # Логируем изменение статуса
        if not project.project_metadata:
            project.project_metadata = {}
        
        if "status_history" not in project.project_metadata:
            project.project_metadata["status_history"] = []
        
        project.project_metadata["status_history"].append({
            "from_status": old_status,
            "to_status": project.status,
            "from_status_name": old_status_obj.name if old_status_obj else old_status,
            "to_status_name": status_obj.name,
            "changed_at": datetime.utcnow().isoformat(),
            "comment": comment,
            "changed_by": current_user["username"]
        })
        
        db.commit()
        db.refresh(project)
        
        # Отправляем уведомление клиенту
        user = db.query(User).filter(User.id == project.user_id).first()
        notification_sent = False
        
        if user and user.telegram_id:
            try:
                if not notification_service.bot:
                    from telegram import Bot
                    notification_service.set_bot(Bot(settings.BOT_TOKEN))
                
                # Уведомление клиенту
                message = f"📋 Статус вашего проекта '{project.title}' изменен на: {status_obj.name}"
                if comment:
                    message += f"\n\n💬 Комментарий: {comment}"
                
                await notification_service.send_telegram_notification(
                    user_id=user.telegram_id,
                    message=message
                )
                notification_sent = True
                logger.info(f"Уведомление отправлено пользователю {user.telegram_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления: {e}")
        
        return {
            "success": True,
            "message": f"Статус успешно обновлен на '{status_obj.name}'" + 
                      (" (уведомление отправлено)" if notification_sent else "")
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления статуса проекта {project_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка обновления статуса: {str(e)}"
        }

@router.get("/statuses/list")
async def get_project_statuses(current_user: dict = Depends(get_current_user)):
    """Получить список доступных статусов проектов"""
    return {
        "success": True,
        "statuses": PROJECT_STATUSES
    }

@router.put("/{project_id}")
async def update_project(
    project_id: int,
    project_data: ProjectUpdateModel,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Полное редактирование проекта (с учетом ролей доступа)"""
    try:
        # Получаем проект
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {
                "success": False,
                "message": "Проект не найден"
            }
        
        # Проверяем права доступа
        if current_user["role"] == "executor":
            if project.assigned_executor_id != current_user["id"]:
                return {
                    "success": False,
                    "message": "У вас нет доступа к этому проекту"
                }
            # Исполнители могут менять только определенные поля
            allowed_fields = {"status", "actual_hours", "comment", "color"}
            for field_name, field_value in project_data.dict(exclude_unset=True).items():
                if field_name not in allowed_fields and field_value is not None:
                    return {
                        "success": False,
                        "message": f"Исполнители не могут изменять поле '{field_name}'"
                    }
        
        # Сохраняем исходные значения для логирования изменений
        original_values = {}
        changes_log = []
        
        # Обновляем поля проекта
        update_data = project_data.dict(exclude_unset=True, exclude={"comment"})
        
        # Специальные поля для metadata
        metadata_fields = {"bot_token", "timeweb_login", "timeweb_password", "telegram_id"}
        
        for field_name, new_value in update_data.items():
            if new_value is not None:
                # Поля для metadata
                if field_name in metadata_fields:
                    if not project.project_metadata:
                        project.project_metadata = {}
                    
                    old_value = project.project_metadata.get(field_name, '')
                    if old_value != new_value:
                        original_values[field_name] = old_value
                        project.project_metadata[field_name] = new_value
                        changes_log.append(f"{field_name}: '{old_value}' → '{new_value}'")
                        
                # Обычные поля модели
                elif hasattr(project, field_name):
                    old_value = getattr(project, field_name)
                    
                    # Проверяем, изменилось ли значение
                    if field_name == "deadline" and new_value:
                        # Обрабатываем дату
                        try:
                            new_deadline = datetime.fromisoformat(new_value.replace('Z', '+00:00'))
                            if old_value != new_deadline:
                                original_values[field_name] = old_value.isoformat() if old_value else None
                                setattr(project, field_name, new_deadline)
                                changes_log.append(f"{field_name}: '{old_value}' → '{new_deadline}'")
                        except ValueError:
                            return {
                                "success": False,
                                "message": f"Неверный формат даты для поля '{field_name}'"
                            }
                    elif field_name == "status" and new_value not in PROJECT_STATUSES:
                        return {
                            "success": False,
                            "message": "Недопустимый статус"
                        }
                    elif field_name == "color" and new_value not in ["default", "green", "yellow", "red"]:
                        return {
                            "success": False,
                            "message": "Недопустимый цвет. Допустимые значения: default, green, yellow, red"
                        }
                    elif old_value != new_value:
                        original_values[field_name] = old_value
                        setattr(project, field_name, new_value)
                        changes_log.append(f"{field_name}: '{old_value}' → '{new_value}'")
        
        # Если изменений нет
        if not changes_log:
            return {
                "success": True,
                "message": "Нет изменений для сохранения"
            }
        
        # Обновляем время изменения
        project.updated_at = datetime.utcnow()
        
        # Логируем изменения в метаданных
        if not project.project_metadata:
            project.project_metadata = {}
        
        if "edit_history" not in project.project_metadata:
            project.project_metadata["edit_history"] = []
        
        edit_record = {
            "edited_at": datetime.utcnow().isoformat(),
            "edited_by": current_user["username"],
            "changes": changes_log,
            "comment": project_data.comment if project_data.comment else ""
        }
        
        project.project_metadata["edit_history"].append(edit_record)
        
        # Сохраняем изменения
        db.commit()
        db.refresh(project)
        
        # Отправляем уведомление исполнителю при изменениях в проекте
        if project.assigned_executor_id:
            try:
                # Уведомление об изменении статуса
                if "status" in original_values:
                    await employee_notification_service.notify_project_status_changed(
                        db=db,
                        project_id=project.id,
                        executor_id=project.assigned_executor_id,
                        project_title=project.title,
                        old_status=original_values["status"],
                        new_status=project.status,
                        comment=project_data.comment if project_data.comment else None
                    )
                    logger.info(f"Уведомление об изменении статуса отправлено исполнителю {project.assigned_executor_id}")
                
                # Уведомление о назначении исполнителя (если изменился assigned_executor_id)
                if "assigned_executor_id" in original_values and project.assigned_executor_id != original_values["assigned_executor_id"]:
                    await employee_notification_service.notify_project_assigned(
                        db=db,
                        project_id=project.id,
                        executor_id=project.assigned_executor_id,
                        project_title=project.title,
                        description=project.description,
                        deadline=project.deadline,
                        estimated_hours=project.estimated_hours
                    )
                    logger.info(f"Уведомление о назначении на проект отправлено исполнителю {project.assigned_executor_id}")
                    
            except Exception as e:
                logger.error(f"Ошибка отправки уведомлений исполнителю: {e}")
        
        # Отправляем уведомление клиенту (только если изменен статус)
        notification_sent = False
        if "status" in original_values:
            user = db.query(User).filter(User.id == project.user_id).first()
            
            if user and user.telegram_id:
                try:
                    if not notification_service.bot:
                        from telegram import Bot
                        notification_service.set_bot(Bot(settings.BOT_TOKEN))
                    
                    # Уведомление клиенту о смене статуса
                    old_status_name = PROJECT_STATUSES.get(original_values["status"], original_values["status"])
                    new_status_name = PROJECT_STATUSES.get(project.status, project.status)
                    message = f"📋 Статус вашего проекта '{project.title}' изменен:\n{old_status_name} → {new_status_name}"
                    
                    if project_data.comment:
                        message += f"\n\n💬 Комментарий: {project_data.comment}"
                    
                    await notification_service.send_telegram_notification(
                        user_id=user.telegram_id,
                        message=message
                    )
                    notification_sent = True
                    logger.info(f"Уведомление отправлено пользователю {user.telegram_id}")
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления: {e}")
        
        return {
            "success": True,
            "message": f"Проект успешно обновлен. Изменения: {', '.join(changes_log)}" + 
                      (" (уведомление отправлено)" if notification_sent else ""),
            "project": project.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления проекта {project_id}: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка обновления проекта: {str(e)}"
        }

@router.post("/")
async def create_project_root(
    request: Request,
    db: Session = Depends(get_db)
):
    """Создать новый проект через корневой POST endpoint - временно без аутентификации"""
    try:
        logger.info("Получен запрос на создание проекта")
        
        # Получаем данные из запроса
        data = await request.json()
        logger.info(f"Данные проекта: {data}")
        
        # Проверяем, передан ли user_id (существующий клиент) или нужно создать нового
        user = None
        user_id = data.get('user_id')
        
        if user_id:
            # Используем существующего пользователя
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "success": False,
                    "message": f"Клиент с ID {user_id} не найден"
                }
        else:
            # Создаем нового пользователя
            client_telegram_id = data.get('client_telegram_id')
            client_name = data.get('client_name', 'Клиент')
            
            if client_telegram_id:
                # Проверяем, нет ли уже пользователя с таким telegram_id
                user = db.query(User).filter(User.telegram_id == int(client_telegram_id)).first()
            
            if not user:
                # Создаем нового пользователя
                import time
                base_username = (client_name or "client").replace(' ', '_').lower()
                username = f"{base_username}_{int(time.time())}"
                
                user = User(
                    telegram_id=int(client_telegram_id) if client_telegram_id else int(time.time()),
                    username=username,
                    first_name=client_name,
                    phone=data.get('client_phone'),
                    registration_date=datetime.utcnow(),
                    is_active=True,
                    state='registered'
                )
                db.add(user)
                db.flush()  # Получаем ID пользователя
        
        # Создаем объект проекта
        new_project = Project(
            user_id=user.id,  # Указываем user_id
            title=data.get('title', ''),
            description=data.get('description', ''),
            project_type=data.get('project_type', 'web'),
            complexity=data.get('complexity', 'medium'),
            priority=data.get('priority', 'normal'),
            status=data.get('status', 'new'),
            estimated_cost=data.get('estimated_cost'),
            executor_cost=data.get('executor_cost'),
            estimated_hours=data.get('estimated_hours'),
            assigned_executor_id=data.get('assigned_executor_id'),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        logger.info(f"Проект успешно создан с ID: {new_project.id}")
        
        return {
            "success": True,
            "message": "Проект успешно создан!",
            "project_id": new_project.id
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания проекта: {e}")
        return {
            "success": False,
            "message": f"Ошибка создания проекта: {str(e)}"
        }

@router.post("/create-validated")
async def create_project_validated(
    project_data: ProjectCreateModel,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Создать новый проект с валидацией обязательных полей"""
    try:
        # Проверяем аутентификацию
        from ...config.settings import settings
        correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
        correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
        
        if not (correct_username and correct_password):
            # Проверяем в БД
            admin_user = db.query(AdminUser).filter(AdminUser.username == credentials.username).first()
            if not admin_user or not admin_user.check_password(credentials.password):
                raise HTTPException(status_code=401, detail="Неверные учетные данные")
        
        logger.info(f"Создание проекта с валидацией: {project_data.title}")
        
        # Валидация обязательных полей (уже выполнена Pydantic)
        # Проверяем существование клиента
        user = db.query(User).filter(User.id == project_data.user_id).first()
        if not user:
            return {"success": False, "message": f"Клиент с ID {project_data.user_id} не найден"}
        
        # Проверяем менеджера если указан
        if project_data.responsible_manager_id:
            manager = db.query(AdminUser).filter(AdminUser.id == project_data.responsible_manager_id).first()
            if not manager:
                return {"success": False, "message": f"Менеджер с ID {project_data.responsible_manager_id} не найден"}
        
        # Проверяем корректность дат
        if project_data.planned_end_date <= project_data.start_date:
            return {"success": False, "message": "Дата завершения должна быть позже даты начала"}
        
        # Создаем проект
        project = Project(
            user_id=project_data.user_id,
            title=project_data.title,
            description=project_data.description,
            estimated_cost=project_data.estimated_cost,
            start_date=project_data.start_date,
            planned_end_date=project_data.planned_end_date,
            responsible_manager_id=project_data.responsible_manager_id,
            priority=project_data.priority,
            project_type=project_data.project_type,
            complexity=project_data.complexity,
            executor_cost=project_data.executor_cost,
            prepayment_amount=project_data.prepayment_amount or 0,
            estimated_hours=project_data.estimated_hours or 0,
            assigned_executor_id=project_data.assigned_executor_id,
            status="new",  # Автоматически новый
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Логируем создание
        logger.info(f"Проект '{project.title}' создан с ID {project.id}")
        
        # Если назначен исполнитель, обновляем статус
        if project_data.assigned_executor_id:
            project.status = "in_progress"
            project.assigned_at = datetime.utcnow()
            db.commit()
        
        return {
            "success": True,
            "message": "Проект успешно создан",
            "project": project.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании проекта: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}

@router.post("/create")
async def create_project(
    project_data: ProjectCreateModel,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новый проект вручную через админку (старый метод для совместимости)"""
    try:
        logger.info(f"Попытка создания проекта пользователем {current_user.get('username')} с ролью {current_user.get('role')}")
        
        # Проверяем права доступа (только владелец может создавать проекты)
        if current_user["role"] != "owner":
            logger.warning(f"Отказ в создании проекта: недостаточно прав для пользователя {current_user.get('username')}")
            return {
                "success": False,
                "message": "У вас нет прав для создания проектов"
            }
        
        # Проверяем, передан ли user_id или нужно создать нового клиента
        user = None
        
        # Проверяем, есть ли user_id в данных (для существующего клиента)
        if hasattr(project_data, 'user_id') and project_data.user_id:
            user = db.query(User).filter(User.id == project_data.user_id).first()
            if not user:
                return {
                    "success": False,
                    "message": f"Клиент с ID {project_data.user_id} не найден"
                }
        else:
            # Создаем нового клиента
            if project_data.client_telegram_id:
                # Ищем существующего пользователя по Telegram ID
                user = db.query(User).filter(User.telegram_id == int(project_data.client_telegram_id)).first()
            
            if not user:
                # Генерируем уникальный username на основе имени клиента или используем временную метку
                import time
                base_username = (project_data.client_name or "client").replace(' ', '_').lower()
                username = f"{base_username}_{int(time.time())}"
                
                # Создаем нового пользователя
                user = User(
                    telegram_id=int(project_data.client_telegram_id) if project_data.client_telegram_id else int(time.time()),
                    first_name=project_data.client_name or "Клиент",
                    last_name="",
                    username=username,
                    phone=project_data.client_phone,
                    is_active=True
                )
                db.add(user)
                db.flush()  # Получаем ID пользователя
        
        # Создаем проект
        project = Project(
            user_id=user.id,
            title=project_data.title,
            description=project_data.description,
            project_type=project_data.project_type,
            complexity=project_data.complexity,
            priority=project_data.priority,
            status=project_data.status,
            estimated_cost=project_data.estimated_cost,
            executor_cost=project_data.executor_cost,
            prepayment_amount=project_data.prepayment_amount or 0,
            client_paid_total=project_data.client_paid_total or 0,
            executor_paid_total=project_data.executor_paid_total or 0,
            assigned_executor_id=project_data.assigned_executor_id,
            estimated_hours=project_data.estimated_hours,
            deadline=datetime.fromisoformat(project_data.deadline) if project_data.deadline else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Логируем создание в метаданных
        project.project_metadata = {
            "created_manually": True,
            "created_by": current_user["username"],
            "created_at": datetime.utcnow().isoformat(),
            "edit_history": [],
            "bot_token": project_data.bot_token,
            "timeweb_login": project_data.timeweb_login,
            "timeweb_password": project_data.timeweb_password
        }
        
        db.commit()
        db.refresh(project)
        
        # Отправляем уведомление исполнителю о назначении на проект
        if project.assigned_executor_id:
            try:
                await employee_notification_service.notify_project_assigned(
                    db=db,
                    project_id=project.id,
                    executor_id=project.assigned_executor_id,
                    project_title=project.title,
                    description=project.description,
                    deadline=project.deadline,
                    estimated_hours=project.estimated_hours
                )
                logger.info(f"Уведомление о назначении проекта отправлено исполнителю {project.assigned_executor_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления исполнителю: {e}")
        
        # Отправляем уведомление клиенту (если у него есть Telegram ID)
        notification_sent = False
        if user.telegram_id:
            try:
                if not notification_service.bot:
                    from telegram import Bot
                    notification_service.set_bot(Bot(settings.BOT_TOKEN))
                
                message = f"🎉 Для вас создан новый проект!\n\n📋 Название: {project.title}\n📝 Описание: {project.description}\n\n💬 Вы можете следить за прогрессом через бота."
                
                await notification_service.send_telegram_notification(
                    user_id=user.telegram_id,
                    message=message
                )
                notification_sent = True
                logger.info(f"Уведомление о создании проекта отправлено пользователю {user.telegram_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления: {e}")
        
        logger.info(f"Проект '{project.title}' успешно создан с ID {project.id}")
        return {
            "success": True,
            "message": f"Проект '{project.title}' успешно создан" + 
                      (" (уведомление отправлено)" if notification_sent else ""),
            "project": project.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания проекта: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка создания проекта: {str(e)}"
        }

@router.get("/{project_id}/files")
async def get_project_files(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить файлы проекта"""
    try:
        logger.info(f"Запрос файлов проекта {project_id} от пользователя {current_user.get('username')}")
        
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            logger.warning(f"Проект {project_id} не найден")
            return {
                "success": False,
                "message": "Проект не найден"
            }
        
        # Проверяем права доступа
        if current_user["role"] == "executor":
            if project.assigned_executor_id != current_user["id"]:
                logger.warning(f"Отказ в доступе к файлам проекта {project_id} для исполнителя {current_user.get('username')}")
                return {
                    "success": False,
                    "message": "У вас нет доступа к файлам этого проекта"
                }
        
        # Получаем файлы проекта из БД
        files = db.query(ProjectFile).filter(ProjectFile.project_id == project_id).all()
        
        logger.info(f"Найдено {len(files)} файлов для проекта {project_id}")
        
        # Безопасно преобразуем файлы в словари
        files_data = []
        for file in files:
            try:
                files_data.append(file.to_dict())
            except Exception as e:
                logger.error(f"Ошибка преобразования файла {file.id} в словарь: {e}")
                # Добавляем минимальную информацию о файле
                files_data.append({
                    "id": file.id,
                    "filename": file.filename,
                    "original_filename": file.original_filename,
                    "file_size": file.file_size,
                    "file_type": file.file_type,
                    "description": file.description,
                    "uploaded_at": file.uploaded_at.isoformat() if file.uploaded_at else None,
                    "project_id": file.project_id,
                    "uploaded_by_id": file.uploaded_by_id,
                    "uploaded_by": None
                })
        
        return {
            "success": True,
            "files": files_data
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения файлов проекта {project_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"Ошибка получения файлов проекта: {str(e)}"
        }

@router.post("/{project_id}/files")
async def upload_project_file(
    project_id: int,
    file: UploadFile = File(...),
    description: str = Form(""),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Загрузить файл проекта"""
    try:
        # Проверяем существование проекта
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return {
                "success": False,
                "message": "Проект не найден"
            }
        
        # Проверяем права доступа
        if current_user["role"] == "executor":
            if project.assigned_executor_id != current_user["id"]:
                return {
                    "success": False,
                    "message": "У вас нет доступа к этому проекту"
                }
        
        # Директория для сохранения файла
        upload_dir = f"uploads/projects/{project_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Сохраняем файл
        contents = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Определяем тип файла
        file_type = "document"  # По умолчанию
        if file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_type = "image"
        elif file_extension.lower() == '.pdf':
            file_type = "pdf"
        elif file_extension.lower() in ['.zip', '.rar', '.7z']:
            file_type = "archive"
        elif file_extension.lower() in ['.mp4', '.avi', '.mov', '.webm']:
            file_type = "video"
        elif file_extension.lower() in ['.mp3', '.wav', '.ogg']:
            file_type = "audio"
        
        # Создаем запись в БД
        admin_user = None
        if current_user["role"] != "client":
            admin_user = db.query(AdminUser).filter(AdminUser.id == current_user["id"]).first()
        
        project_file = ProjectFile(
            project_id=project_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(contents),
            file_type=file_type,
            description=description,
            uploaded_by_id=admin_user.id if admin_user else None,
            uploaded_at=datetime.utcnow()
        )
        
        db.add(project_file)
        db.commit()
        db.refresh(project_file)
        
        # Возвращаем успешный результат
        return {
            "success": True,
            "message": "Файл успешно загружен",
            "file": project_file.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка загрузки файла для проекта {project_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка загрузки файла: {str(e)}"
        }

@router.delete("/{project_id}/files/{file_id}")
async def delete_project_file(
    project_id: int,
    file_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить файл проекта"""
    try:
        # Проверяем существование проекта
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            return {
                "success": False,
                "message": "Проект не найден"
            }
        
        # Проверяем права доступа
        if current_user["role"] == "executor":
            if project.assigned_executor_id != current_user["id"]:
                return {
                    "success": False,
                    "message": "У вас нет доступа к этому проекту"
                }
        
        # Ищем файл в БД
        project_file = db.query(ProjectFile).filter(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id
        ).first()
        
        if not project_file:
            return {
                "success": False,
                "message": "Файл не найден"
            }
        
        # Удаляем файл с диска
        if os.path.exists(project_file.file_path):
            try:
                os.remove(project_file.file_path)
            except Exception as e:
                logger.error(f"Ошибка удаления файла с диска: {e}")
                # Продолжаем удаление записи даже если файл на диске не удалился
        
        # Удаляем запись из БД
        db.delete(project_file)
        db.commit()
        
        # Возвращаем успешный результат
        return {
            "success": True,
            "message": "Файл успешно удален"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка удаления файла проекта {project_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка удаления файла: {str(e)}"
        }

@router.post("/{project_id}/archive")
async def archive_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Переместить проект в архив (только для владельца)"""
    try:
        logger.info(f"Запрос на архивирование проекта {project_id} от пользователя {current_user.get('username')}")
        
        # Проверяем права доступа (только владелец может архивировать проекты)
        if current_user["role"] != "owner":
            return {
                "success": False,
                "message": "У вас нет прав для архивирования проектов"
            }
        
        # Получаем проект
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {
                "success": False,
                "message": "Проект не найден"
            }
        
        # Переключаем статус архивирования
        project.is_archived = not project.is_archived
        project.updated_at = datetime.utcnow()
        
        # Логируем изменение в метаданных
        if not project.project_metadata:
            project.project_metadata = {}
        
        if "archive_history" not in project.project_metadata:
            project.project_metadata["archive_history"] = []
        
        project.project_metadata["archive_history"].append({
            "action": "archived" if project.is_archived else "unarchived",
            "timestamp": datetime.utcnow().isoformat(),
            "user": current_user["username"]
        })
        
        db.commit()
        db.refresh(project)
        
        action_text = "добавлен в архив" if project.is_archived else "восстановлен из архива"
        logger.info(f"Проект '{project.title}' (ID: {project_id}) {action_text}")
        
        return {
            "success": True,
            "message": f"Проект '{project.title}' успешно {action_text}",
            "is_archived": project.is_archived
        }
        
    except Exception as e:
        logger.error(f"Ошибка архивирования проекта {project_id}: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка архивирования проекта: {str(e)}"
        }

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить проект (только для владельца)"""
    try:
        logger.info(f"=== НАЧАЛО УДАЛЕНИЯ ПРОЕКТА {project_id} ===")
        logger.info(f"Текущий пользователь: {current_user}")
        logger.info(f"Роль пользователя: {current_user.get('role')}")
        
        # Проверяем права доступа (только владелец может удалять проекты)
        if current_user["role"] != "owner":
            logger.warning(f"Отказ в удалении: пользователь {current_user.get('username')} не владелец, роль: {current_user.get('role')}")
            return {
                "success": False,
                "message": f"У вас нет прав для удаления проектов. Ваша роль: {current_user.get('role')}"
            }
        
        # Получаем проект
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {
                "success": False,
                "message": "Проект не найден"
            }
        
        # Сохраняем информацию о проекте для логирования
        project_title = project.title
        user_id = project.user_id
        
        # Удаляем связанные файлы с диска
        project_files = db.query(ProjectFile).filter(ProjectFile.project_id == project_id).all()
        for project_file in project_files:
            if os.path.exists(project_file.file_path):
                try:
                    os.remove(project_file.file_path)
                except Exception as e:
                    logger.error(f"Ошибка удаления файла {project_file.file_path}: {e}")
        
        # Удаляем связанные записи из БД, используя прямые SQL-запросы
        # Это предотвращает проблемы с relationships и cascade
        
        # 1. Сначала удаляем файлы правок с диска
        revision_files_query = db.execute(
            text("SELECT rf.file_path FROM revision_files rf "
                 "JOIN project_revisions pr ON rf.revision_id = pr.id "
                 "WHERE pr.project_id = :project_id"), 
            {"project_id": project_id}
        ).fetchall()
        
        for (file_path,) in revision_files_query:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Ошибка удаления файла правки {file_path}: {e}")
        
        # 2. Удаляем связанные записи прямыми SQL-запросами
        try:
            # Удаляем файлы правок
            db.execute(
                text("DELETE FROM revision_files WHERE revision_id IN "
                     "(SELECT id FROM project_revisions WHERE project_id = :project_id)"), 
                {"project_id": project_id}
            )
            
            # Удаляем сообщения правок
            db.execute(
                text("DELETE FROM revision_messages WHERE revision_id IN "
                     "(SELECT id FROM project_revisions WHERE project_id = :project_id)"), 
                {"project_id": project_id}
            )
            
            # Удаляем правки проекта
            db.execute(text("DELETE FROM project_revisions WHERE project_id = :project_id"), 
                      {"project_id": project_id})
            
            # Удаляем логи изменения статусов
            db.execute(text("DELETE FROM project_status_logs WHERE project_id = :project_id"), 
                      {"project_id": project_id})
            
            # Удаляем файлы проекта
            db.execute(text("DELETE FROM project_files WHERE project_id = :project_id"), 
                      {"project_id": project_id})
            
            # Обновляем записи с nullable project_id (устанавливаем в NULL)
            # consultant_sessions не имеет project_id, пропускаем
            db.execute(text("UPDATE finance_transactions SET project_id = NULL WHERE project_id = :project_id"), 
                      {"project_id": project_id})
            db.execute(text("UPDATE contractor_payments SET project_id = NULL WHERE project_id = :project_id"), 
                      {"project_id": project_id})
            db.execute(text("UPDATE service_expenses SET project_id = NULL WHERE project_id = :project_id"), 
                      {"project_id": project_id})
            
            # Наконец, удаляем сам проект
            db.execute(text("DELETE FROM projects WHERE id = :project_id"), 
                      {"project_id": project_id})
            
            db.commit()
            logger.info(f"Проект {project_id} и все связанные записи успешно удалены")
            
        except Exception as e:
            logger.error(f"Ошибка при удалении связанных записей: {e}")
            db.rollback()
            raise
        
        # Отправляем уведомление клиенту
        user = db.query(User).filter(User.id == user_id).first()
        notification_sent = False
        
        if user and user.telegram_id:
            try:
                if not notification_service.bot:
                    from telegram import Bot
                    notification_service.set_bot(Bot(settings.BOT_TOKEN))
                
                message = f"📋 Ваш проект '{project_title}' был удален из системы."
                
                await notification_service.send_telegram_notification(
                    user_id=user.telegram_id,
                    message=message
                )
                notification_sent = True
                logger.info(f"Уведомление об удалении проекта отправлено пользователю {user.telegram_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления об удалении: {e}")
        
        logger.info(f"Проект '{project_title}' (ID: {project_id}) удален пользователем {current_user['username']}")
        logger.info(f"=== УДАЛЕНИЕ ПРОЕКТА {project_id} ЗАВЕРШЕНО УСПЕШНО ===")
        
        return {
            "success": True,
            "message": f"Проект '{project_title}' успешно удален" + 
                      (" (уведомление отправлено)" if notification_sent else "")
        }
        
    except Exception as e:
        logger.error(f"=== КРИТИЧЕСКАЯ ОШИБКА ПРИ УДАЛЕНИИ ПРОЕКТА {project_id} ===")
        logger.error(f"Ошибка: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Ошибка удаления проекта {project_id}: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка удаления проекта: {str(e)}"
        }


@router.post("/api/{project_id}/create-income", response_class=JSONResponse)
async def create_project_income(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Создать финансовую транзакцию дохода от проекта через IntegrationService"""
    try:
        # Получаем данные из запроса
        data = await request.json()
        
        # Валидация
        amount = data.get("amount")
        if not amount or amount <= 0:
            return {
                "success": False,
                "message": "Сумма должна быть больше 0"
            }
        
        description = data.get("description")
        if not description:
            return {
                "success": False,
                "message": "Описание обязательно"
            }
        
        # Аутентификация (базовая)
        credentials = request.headers.get('authorization', '')
        if not credentials.startswith('Basic '):
            return {
                "success": False,
                "message": "Требуется аутентификация"
            }
        
        # Извлекаем учетные данные
        import base64
        encoded_credentials = credentials.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        
        # Проверяем пользователя
        current_user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not current_user or not current_user.check_password(password):
            return {
                "success": False,
                "message": "Неверные учетные данные"
            }
        
        # Используем IntegrationService для создания транзакции
        from ...services.integration_service import IntegrationService
        integration_service = IntegrationService(db)
        
        result = integration_service.create_project_income_transaction(
            project_id=project_id,
            amount=float(amount),
            description=description,
            current_user_id=current_user.id,
            account=data.get("account", "card"),
            payment_date=datetime.fromisoformat(data["payment_date"]) if data.get("payment_date") else None
        )
        
        if result["success"]:
            logger.info(f"Создана транзакция дохода {amount}₽ для проекта {project_id}")
        
        return {
            "success": result["success"],
            "message": "Транзакция дохода создана успешно" if result["success"] else result.get("error", "Ошибка создания транзакции"),
            "data": result.get("data")
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания транзакции дохода от проекта: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/api/{project_id}/integration-chain", response_class=JSONResponse)
async def get_project_integration_chain(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Получить цепочку интеграции для проекта (Лид → Сделка → Проект → Транзакции)"""
    try:
        # Аутентификация (базовая)
        credentials = request.headers.get('authorization', '')
        if not credentials.startswith('Basic '):
            return {
                "success": False,
                "message": "Требуется аутентификация"
            }
        
        # Извлекаем учетные данные
        import base64
        encoded_credentials = credentials.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        
        # Проверяем пользователя
        current_user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not current_user or not current_user.check_password(password):
            return {
                "success": False,
                "message": "Неверные учетные данные"
            }
        
        # Используем IntegrationService для получения цепочки
        from ...services.integration_service import IntegrationService
        integration_service = IntegrationService(db)
        
        result = integration_service.get_integration_chain(
            entity_type="project",
            entity_id=project_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка получения цепочки интеграции для проекта: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }