# app/admin/routers/project_statuses.py
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from pydantic import BaseModel
import secrets
from telegram import Bot

from ...database.database import get_db
from ...database.models import ProjectStatus, ProjectStatusLog, Project, AdminUser, User
from ...config.logging import get_logger
from ...config.settings import get_settings
from ...services.notification_service import NotificationService

logger = get_logger(__name__)
settings = get_settings()

# Создаем экземпляр бота для уведомлений
bot_instance = Bot(token=settings.bot_token)
notification_service = NotificationService(bot=bot_instance)

router = APIRouter(tags=["project_statuses"])

# Базовая аутентификация
security = HTTPBasic()

# Модели для API
class ProjectStatusCreateModel(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#6c757d"
    icon: str = "fas fa-circle"
    is_default: bool = False
    sort_order: int = 0

class ProjectStatusUpdateModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class ProjectStatusChangeModel(BaseModel):
    project_id: int
    status_id: int
    comment: Optional[str] = None

def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)) -> AdminUser:
    """Получение текущего администратора"""
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
            role='owner',
            is_active=True
        )
        admin.set_password(settings.ADMIN_PASSWORD)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    
    # Проверяем в базе данных
    admin_user = db.query(AdminUser).filter(AdminUser.username == credentials.username).first()
    if not admin_user or not admin_user.check_password(credentials.password):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    return admin_user

@router.get("/")
async def get_project_statuses(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить все статусы проектов"""
    try:
        statuses = db.query(ProjectStatus).filter(
            ProjectStatus.is_active == True
        ).order_by(ProjectStatus.sort_order, ProjectStatus.name).all()
        
        return {
            "success": True,
            "data": [status.to_dict() for status in statuses]
        }
    except Exception as e:
        logger.error(f"Ошибка получения статусов: {e}")
        return {"success": False, "error": str(e)}

@router.post("/")
async def create_project_status(
    status_data: ProjectStatusCreateModel,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Создать новый статус проекта"""
    try:
        # Проверяем, нет ли уже такого статуса
        existing = db.query(ProjectStatus).filter(ProjectStatus.name == status_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Статус с таким названием уже существует")
        
        new_status = ProjectStatus(
            name=status_data.name,
            description=status_data.description,
            color=status_data.color,
            icon=status_data.icon,
            is_default=status_data.is_default,
            sort_order=status_data.sort_order,
            created_by_id=current_user.id if current_user.id > 0 else None,
            created_at=datetime.utcnow()
        )
        
        db.add(new_status)
        db.commit()
        db.refresh(new_status)
        
        logger.info(f"Создан новый статус: {new_status.name}")
        
        return {
            "success": True,
            "data": new_status.to_dict(),
            "message": "Статус успешно создан"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка создания статуса: {e}")
        return {"success": False, "error": str(e)}

@router.put("/{status_id}")
async def update_project_status(
    status_id: int,
    status_data: ProjectStatusUpdateModel,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Обновить статус проекта"""
    try:
        status = db.query(ProjectStatus).filter(ProjectStatus.id == status_id).first()
        if not status:
            raise HTTPException(status_code=404, detail="Статус не найден")
        
        # Обновляем поля
        if status_data.name is not None:
            status.name = status_data.name
        if status_data.description is not None:
            status.description = status_data.description
        if status_data.color is not None:
            status.color = status_data.color
        if status_data.icon is not None:
            status.icon = status_data.icon
        if status_data.is_default is not None:
            status.is_default = status_data.is_default
        if status_data.is_active is not None:
            status.is_active = status_data.is_active
        if status_data.sort_order is not None:
            status.sort_order = status_data.sort_order
        
        db.commit()
        db.refresh(status)
        
        logger.info(f"Обновлен статус: {status.name}")
        
        return {
            "success": True,
            "data": status.to_dict(),
            "message": "Статус успешно обновлен"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка обновления статуса: {e}")
        return {"success": False, "error": str(e)}

@router.delete("/{status_id}")
async def delete_project_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Удалить статус проекта (мягкое удаление)"""
    try:
        status = db.query(ProjectStatus).filter(ProjectStatus.id == status_id).first()
        if not status:
            raise HTTPException(status_code=404, detail="Статус не найден")
        
        # Проверяем, используется ли статус в проектах
        projects_count = db.query(ProjectStatusLog).filter(ProjectStatusLog.status_id == status_id).count()
        if projects_count > 0:
            # Мягкое удаление
            status.is_active = False
        else:
            # Полное удаление
            db.delete(status)
        
        db.commit()
        
        logger.info(f"Удален статус: {status.name}")
        
        return {
            "success": True,
            "message": "Статус успешно удален"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка удаления статуса: {e}")
        return {"success": False, "error": str(e)}

@router.post("/change-status")
async def change_project_status(
    change_data: ProjectStatusChangeModel,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Изменить статус проекта и отправить уведомление клиенту"""
    try:
        # Находим проект
        project = db.query(Project).filter(Project.id == change_data.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        # Находим новый статус
        new_status = db.query(ProjectStatus).filter(ProjectStatus.id == change_data.status_id).first()
        if not new_status:
            raise HTTPException(status_code=404, detail="Статус не найден")
        
        # Находим предыдущий статус (если есть)
        previous_status_log = db.query(ProjectStatusLog).filter(
            ProjectStatusLog.project_id == change_data.project_id
        ).order_by(desc(ProjectStatusLog.changed_at)).first()
        
        previous_status_id = previous_status_log.status_id if previous_status_log else None
        
        # Создаем запись в логе изменений
        logger.info(f"Creating status log for project {change_data.project_id}, user ID: {current_user.id}")
        status_log = ProjectStatusLog(
            project_id=change_data.project_id,
            status_id=change_data.status_id,
            previous_status_id=previous_status_id,
            comment=change_data.comment,
            changed_at=datetime.utcnow(),
            changed_by_id=current_user.id
        )
        
        db.add(status_log)
        
        # Обновляем старое поле статуса для совместимости
        project.status = new_status.name.lower()
        
        db.commit()
        db.refresh(status_log)
        
        # Отправляем уведомление клиенту
        try:
            user = db.query(User).filter(User.id == project.user_id).first()
            if user and user.telegram_id:
                message = f"📋 *Обновление по проекту: {project.title}*\n\n"
                message += f"🔄 Статус изменен на: *{new_status.name}*\n"
                
                if change_data.comment:
                    message += f"💬 Комментарий: {change_data.comment}\n"
                
                message += f"\n📅 Дата изменения: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                
                logger.info(f"Отправляем уведомление пользователю {user.telegram_id}")
                logger.info(f"Сообщение: {message}")
                
                result = await notification_service.send_user_notification(
                    user_id=user.telegram_id,
                    message=message,
                    parse_mode="Markdown"
                )
                
                if result:
                    logger.info(f"Уведомление пользователю {user.telegram_id} успешно отправлено")
                else:
                    logger.warning(f"Не удалось отправить уведомление пользователю {user.telegram_id}")
            else:
                if not user:
                    logger.warning(f"Пользователь с ID {project.user_id} не найден")
                elif not user.telegram_id:
                    logger.warning(f"У пользователя {user.first_name} (ID: {user.id}) нет telegram_id")
        
        except Exception as notification_error:
            logger.error(f"Ошибка отправки уведомления: {notification_error}")
            # Не прерываем выполнение из-за ошибки уведомления
        
        logger.info(f"Изменен статус проекта {project.id} на {new_status.name}")
        
        return {
            "success": True,
            "message": "Статус проекта успешно изменен, уведомление отправлено клиенту",
            "data": {
                "project_id": project.id,
                "new_status": new_status.to_dict(),
                "comment": change_data.comment
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка изменения статуса проекта: {e}")
        return {"success": False, "error": str(e)}

@router.get("/logs/{project_id}")
async def get_project_status_logs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить историю изменений статусов проекта"""
    try:
        logs = db.query(ProjectStatusLog).filter(
            ProjectStatusLog.project_id == project_id
        ).order_by(desc(ProjectStatusLog.changed_at)).all()
        
        return {
            "success": True,
            "data": [log.to_dict() for log in logs]
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения логов статусов: {e}")
        return {"success": False, "error": str(e)}
