# app/admin/routers/revisions.py
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_, and_
from pydantic import BaseModel
import os
import uuid
import shutil
from pathlib import Path
from PIL import Image
import io

from ...database.database import get_db
from ...database.models import (
    ProjectRevision, RevisionMessage, RevisionFile, RevisionMessageFile,
    Project, User, AdminUser
)
from ...config.logging import get_logger
from ..middleware.auth import get_current_admin_user
from ...middleware.auth import authenticate

logger = get_logger(__name__)
templates = Jinja2Templates(directory="app/admin/templates")

router = APIRouter(tags=["revisions"])

# Директория для загрузки файлов правок
REVISIONS_UPLOAD_DIR = Path("uploads/revisions")
REVISIONS_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Модели для API
class RevisionCreateModel(BaseModel):
    project_id: int
    title: str
    description: str
    priority: str = "normal"

class RevisionUpdateModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[int] = None
    estimated_time: Optional[int] = None
    actual_time: Optional[int] = None

class RevisionMessageCreateModel(BaseModel):
    revision_id: int
    message: str
    is_internal: bool = False

@router.get("/revisions", response_class=HTMLResponse)
async def revisions_page(request: Request, username: str = Depends(authenticate)):
    """Страница управления правками"""
    # Получаем роль пользователя и элементы навигации
    from app.admin.app import get_user_role, get_navigation_items
    user_role = get_user_role(username)
    navigation_items = get_navigation_items(user_role)
    
    # Debug logging
    print(f"[DEBUG] Username: {username}")
    print(f"[DEBUG] User role: {user_role}")
    print(f"[DEBUG] Navigation items count: {len(navigation_items) if navigation_items else 0}")
    if navigation_items:
        print(f"[DEBUG] First 3 navigation items: {navigation_items[:3]}")
    
    return templates.TemplateResponse("revisions.html", {
        "request": request,
        "username": username,
        "user_role": user_role,
        "navigation_items": navigation_items
    })

@router.get("/api/revisions", response_class=JSONResponse)
async def get_revisions(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user),
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to_me: Optional[bool] = None
):
    """Получить список правок"""
    try:
        query = db.query(ProjectRevision).join(Project)
        
        # Если пользователь не владелец, показываем только правки по его проектам
        if user["role"] != "owner":
            query = query.filter(Project.assigned_executor_id == user['id'])
        
        if project_id:
            query = query.filter(ProjectRevision.project_id == project_id)
        
        if status:
            query = query.filter(ProjectRevision.status == status)
        
        if priority:
            query = query.filter(ProjectRevision.priority == priority)
        
        if assigned_to_me:
            query = query.filter(ProjectRevision.assigned_to_id == user['id'])
        
        revisions = query.order_by(desc(ProjectRevision.created_at)).all()
        
        # Добавляем информацию о проекте к каждой правке
        result = []
        for revision in revisions:
            revision_data = revision.to_dict()
            if revision.project:
                revision_data["project"] = {
                    "id": revision.project.id,
                    "title": revision.project.title,
                    "status": revision.project.status
                }
            result.append(revision_data)
        
        return JSONResponse({
            "success": True,
            "data": result,
            "total": len(result)
        })
    
    except Exception as e:
        logger.error(f"Error fetching revisions: {e}")
        return JSONResponse({
            "success": False,
            "error": "Не удалось получить список правок"
        }, status_code=500)

@router.get("/api/revisions/{revision_id}", response_class=JSONResponse)
async def get_revision(
    revision_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Получить детали правки"""
    try:
        logger.info(f"Getting revision {revision_id} for user {user['id']}")
        
        query = db.query(ProjectRevision).join(Project).filter(
            ProjectRevision.id == revision_id
        )
        
        # Если пользователь не владелец, проверяем назначение проекта
        if user["role"] != "owner":  # Не владелец системы
            logger.info(f"User {user['id']} is not owner, filtering by assigned_executor_id")
            query = query.filter(Project.assigned_executor_id == user['id'])
        
        revision = query.first()
        
        if not revision:
            logger.warning(f"Revision {revision_id} not found for user {user['id']}")
            return JSONResponse({
                "success": False,
                "error": "Правка не найдена"
            }, status_code=404)
        
        revision_data = revision.to_dict()
        
        # Добавляем сообщения
        messages = db.query(RevisionMessage).filter(
            RevisionMessage.revision_id == revision_id
        ).order_by(asc(RevisionMessage.created_at)).all()
        
        revision_data["messages"] = [msg.to_dict() for msg in messages]
        
        # Добавляем файлы
        files = db.query(RevisionFile).filter(
            RevisionFile.revision_id == revision_id
        ).order_by(desc(RevisionFile.created_at)).all()
        
        revision_data["files"] = [file.to_dict() for file in files]
        
        # Добавляем информацию о проекте
        if revision.project:
            revision_data["project"] = {
                "id": revision.project.id,
                "title": revision.project.title,
                "status": revision.project.status
            }
        
        return JSONResponse({
            "success": True,
            "data": revision_data
        })
    
    except Exception as e:
        logger.error(f"Error fetching revision {revision_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": "Не удалось получить данные правки"
        }, status_code=500)

@router.get("/api/revisions/stats", response_class=JSONResponse)
async def get_revisions_stats(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Получить статистику правок"""
    try:
        # Базовый запрос с учетом роли пользователя
        base_query = db.query(ProjectRevision).join(Project)
        
        # Если пользователь не владелец, фильтруем по назначенным проектам
        if user["role"] != "owner":
            base_query = base_query.filter(Project.assigned_executor_id == user['id'])
        
        # Общее количество правок
        total_revisions = base_query.count()
        
        # Правки в ожидании
        pending_revisions = base_query.filter(
            ProjectRevision.status == "pending"
        ).count()
        
        # Завершенные правки
        completed_revisions = base_query.filter(
            ProjectRevision.status == "completed"
        ).count()
        
        # Мои правки (назначенные на текущего пользователя)
        if user["role"] == "owner":
            # Для владельца считаем все правки как "мои"
            my_revisions = total_revisions
        else:
            # Для исполнителя считаем только назначенные на него
            my_revisions = base_query.filter(
                ProjectRevision.assigned_to_id == user['id']
            ).count()
        
        return JSONResponse({
            "success": True,
            "data": {
                "total_revisions": total_revisions,
                "pending_revisions": pending_revisions,
                "completed_revisions": completed_revisions,
                "my_revisions": my_revisions
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching revisions stats: {e}")
        return JSONResponse({
            "success": False,
            "error": "Не удалось получить статистику правок"
        }, status_code=500)

@router.post("/api/revisions", response_class=JSONResponse)
async def create_revision(
    revision_data: RevisionCreateModel,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Создать новую правку (админ создает от имени клиента)"""
    try:
        # Проверяем, что проект существует
        project = db.query(Project).filter(Project.id == revision_data.project_id).first()
        if not project:
            return JSONResponse({
                "success": False,
                "error": "Проект не найден"
            }, status_code=404)
        
        # Определяем номер правки
        last_revision = db.query(ProjectRevision).filter(
            ProjectRevision.project_id == revision_data.project_id
        ).order_by(desc(ProjectRevision.revision_number)).first()
        
        revision_number = (last_revision.revision_number + 1) if last_revision else 1
        
        # Создаем правку
        revision = ProjectRevision(
            project_id=revision_data.project_id,
            revision_number=revision_number,
            title=revision_data.title,
            description=revision_data.description,
            priority=revision_data.priority,
            created_by_id=project.user_id,  # От имени клиента
            assigned_to_id=project.assigned_executor_id or user['id']
        )
        
        db.add(revision)
        db.commit()
        db.refresh(revision)
        
        # Отправляем уведомление исполнителю
        await send_revision_notification(revision, "new")
        
        return JSONResponse({
            "success": True,
            "message": "Правка создана",
            "data": revision.to_dict()
        })
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating revision: {e}")
        return JSONResponse({
            "success": False,
            "error": "Не удалось создать правку"
        }, status_code=500)

@router.put("/api/revisions/{revision_id}", response_class=JSONResponse)
async def update_revision(
    revision_id: int,
    revision_data: RevisionUpdateModel,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Обновить правку"""
    try:
        revision = db.query(ProjectRevision).filter(
            ProjectRevision.id == revision_id
        ).first()
        
        if not revision:
            return JSONResponse({
                "success": False,
                "error": "Правка не найдена"
            }, status_code=404)
        
        old_status = revision.status
        
        # Обновляем только переданные поля
        for field, value in revision_data.dict(exclude_unset=True).items():
            if field == "status" and value == "completed" and old_status != "completed":
                revision.completed_at = datetime.utcnow()
            setattr(revision, field, value)
        
        revision.updated_at = datetime.utcnow()
        db.commit()
        
        # Если статус изменился, отправляем уведомление
        if revision_data.status and revision_data.status != old_status:
            await send_revision_notification(revision, revision_data.status)
        
        return JSONResponse({
            "success": True,
            "message": "Правка обновлена",
            "data": revision.to_dict()
        })
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating revision {revision_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": "Не удалось обновить правку"
        }, status_code=500)

@router.post("/api/revisions/{revision_id}/messages", response_class=JSONResponse)
async def add_revision_message(
    revision_id: int,
    message: str = Form(...),
    is_internal: bool = Form(False),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Добавить сообщение к правке"""
    try:
        revision = db.query(ProjectRevision).filter(
            ProjectRevision.id == revision_id
        ).first()
        
        if not revision:
            return JSONResponse({
                "success": False,
                "error": "Правка не найдена"
            }, status_code=404)
        
        # Создаем сообщение
        revision_message = RevisionMessage(
            revision_id=revision_id,
            sender_type="admin",  # Всегда от админа/исполнителя
            sender_admin_id=user['id'],
            message=message,
            is_internal=is_internal
        )
        
        db.add(revision_message)
        db.commit()
        db.refresh(revision_message)
        
        # Сохраняем файлы
        for file in files:
            if file.filename:
                file_path = await save_revision_message_file(file, revision_message.id)
                if file_path:
                    revision_file = RevisionMessageFile(
                        message_id=revision_message.id,
                        filename=file_path.name,
                        original_filename=file.filename,
                        file_type=get_file_type(file.filename),
                        file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                        file_path=str(file_path)
                    )
                    db.add(revision_file)
        
        db.commit()
        
        # Отправляем уведомление клиенту (если сообщение не внутреннее)
        if not is_internal:
            await send_revision_message_notification(revision, revision_message)
        
        return JSONResponse({
            "success": True,
            "message": "Сообщение добавлено",
            "data": revision_message.to_dict()
        })
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding message to revision {revision_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": "Не удалось добавить сообщение"
        }, status_code=500)

@router.post("/api/revisions/{revision_id}/complete", response_class=JSONResponse)
async def complete_revision(
    revision_id: int,
    actual_time: Optional[int] = Form(None),
    completion_message: str = Form("Правки внесены"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Отметить правку как выполненную"""
    try:
        revision = db.query(ProjectRevision).filter(
            ProjectRevision.id == revision_id
        ).first()
        
        if not revision:
            return JSONResponse({
                "success": False,
                "error": "Правка не найдена"
            }, status_code=404)
        
        # Обновляем статус правки
        revision.status = "completed"
        revision.completed_at = datetime.utcnow()
        revision.updated_at = datetime.utcnow()
        
        if actual_time:
            revision.actual_time = actual_time
        
        # Добавляем сообщение о завершении
        completion_msg = RevisionMessage(
            revision_id=revision_id,
            sender_type="admin",
            sender_admin_id=user['id'],
            message=completion_message,
            is_internal=False
        )
        
        db.add(completion_msg)
        db.commit()
        
        # Отправляем уведомление клиенту
        await send_revision_notification(revision, "completed")
        
        return JSONResponse({
            "success": True,
            "message": "Правка отмечена как выполненная",
            "data": revision.to_dict()
        })
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error completing revision {revision_id}: {e}")
        return JSONResponse({
            "success": False,
            "error": "Не удалось завершить правку"
        }, status_code=500)


@router.get("/api/revisions/files/{file_id}", response_class=FileResponse)
async def download_revision_file(
    file_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Скачать файл правки"""
    try:
        # Проверяем файлы правок
        revision_file = db.query(RevisionFile).filter(RevisionFile.id == file_id).first()
        if revision_file and os.path.exists(revision_file.file_path):
            return FileResponse(
                revision_file.file_path,
                filename=revision_file.original_filename
            )
        
        # Проверяем файлы сообщений
        message_file = db.query(RevisionMessageFile).filter(RevisionMessageFile.id == file_id).first()
        if message_file and os.path.exists(message_file.file_path):
            return FileResponse(
                message_file.file_path,
                filename=message_file.original_filename
            )
        
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при скачивании файла")

@router.get("/api/revisions/files/{file_id}/thumbnail")
async def get_file_thumbnail(
    file_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Получить миниатюру изображения"""
    try:
        # Проверяем файлы правок
        revision_file = db.query(RevisionFile).filter(RevisionFile.id == file_id).first()
        file_path = None
        file_type = None
        
        if revision_file and os.path.exists(revision_file.file_path):
            file_path = revision_file.file_path
            file_type = revision_file.file_type
        else:
            # Проверяем файлы сообщений
            message_file = db.query(RevisionMessageFile).filter(RevisionMessageFile.id == file_id).first()
            if message_file and os.path.exists(message_file.file_path):
                file_path = message_file.file_path
                file_type = message_file.file_type
        
        if not file_path or file_type != 'image':
            raise HTTPException(status_code=404, detail="Изображение не найдено")
        
        # Создаем миниатюру
        thumbnail_path = await create_thumbnail(file_path, file_id)
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            from fastapi.responses import Response
            with open(thumbnail_path, "rb") as f:
                content = f.read()
            return Response(content=content, media_type="image/jpeg")
        else:
            raise HTTPException(status_code=500, detail="Не удалось создать миниатюру")
    
    except Exception as e:
        logger.error(f"Error creating thumbnail for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании миниатюры")

@router.get("/api/revisions/{revision_id}/files", response_class=JSONResponse)
async def get_revision_files(
    revision_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Получить файлы правки"""
    try:
        # Проверяем существование правки
        revision = db.query(ProjectRevision).filter(ProjectRevision.id == revision_id).first()
        if not revision:
            raise HTTPException(status_code=404, detail="Правка не найдена")
        
        # Получаем файлы правки
        files = db.query(RevisionFile).filter(RevisionFile.revision_id == revision_id).all()
        
        files_data = []
        for file in files:
            file_data = {
                "id": file.id,
                "filename": file.original_filename,
                "upload_date": file.created_at.isoformat() if file.created_at else None,
                "file_size": os.path.getsize(file.file_path) if os.path.exists(file.file_path) else 0,
                "download_url": f"/admin/api/revisions/files/{file.id}",
                "file_type": getattr(file, 'file_type', get_file_type(file.original_filename or ''))
            }
            
            # Добавляем URL миниатюры для изображений
            if file_data["file_type"] == "image":
                file_data["thumbnail_url"] = f"/admin/api/revisions/files/{file.id}/thumbnail"
            
            files_data.append(file_data)
        
        return JSONResponse(content={"success": True, "data": files_data})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting revision files: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения файлов")

@router.get("/api/revisions/{revision_id}/messages", response_class=JSONResponse)
async def get_revision_messages(
    revision_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Получить сообщения правки"""
    try:
        # Проверяем существование правки
        revision = db.query(ProjectRevision).filter(ProjectRevision.id == revision_id).first()
        if not revision:
            raise HTTPException(status_code=404, detail="Правка не найдена")
        
        # Получаем сообщения правки
        messages = db.query(RevisionMessage).filter(
            RevisionMessage.revision_id == revision_id
        ).order_by(RevisionMessage.created_at.asc()).all()
        
        messages_data = []
        for message in messages:
            # Получаем информацию об отправителе
            sender_name = "Неизвестно"
            sender_type = message.sender_type
            
            if message.sender_type == "client" and message.sender_user:
                sender_name = message.sender_user.first_name or message.sender_user.username or "Клиент"
            elif message.sender_type in ["admin", "executor"] and message.sender_admin:
                sender_name = f"{message.sender_admin.first_name or ''} {message.sender_admin.last_name or ''}".strip() or message.sender_admin.username or "Команда"
            
            # Получаем файлы сообщения
            message_files = db.query(RevisionMessageFile).filter(
                RevisionMessageFile.message_id == message.id
            ).all()
            
            files_data = []
            for file in message_files:
                file_data = {
                    "id": file.id,
                    "filename": file.original_filename,
                    "download_url": f"/admin/api/revisions/files/{file.id}",
                    "file_type": getattr(file, 'file_type', get_file_type(file.original_filename or ''))
                }
                
                # Добавляем URL миниатюры для изображений
                if file_data["file_type"] == "image":
                    file_data["thumbnail_url"] = f"/admin/api/revisions/files/{file.id}/thumbnail"
                
                files_data.append(file_data)
            
            messages_data.append({
                "id": message.id,
                "content": message.message,  # Используем поле 'message'
                "message": message.message,  # Добавляем и это поле для совместимости
                "sender_name": sender_name,
                "sender_type": sender_type,
                "is_internal": message.is_internal,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "files": files_data
            })
        
        return JSONResponse(content={"success": True, "data": messages_data})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting revision messages: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения сообщений")

# Вспомогательные функции
async def create_thumbnail(image_path: str, file_id: int, size: tuple = (150, 150)) -> str:
    """Создать миниатюру изображения"""
    try:
        thumbnail_dir = Path("uploads/thumbnails")
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        
        thumbnail_path = thumbnail_dir / f"thumb_{file_id}.jpg"
        
        # Если миниатюра уже существует, возвращаем её
        if thumbnail_path.exists():
            return str(thumbnail_path)
        
        # Открываем изображение и создаем миниатюру
        with Image.open(image_path) as img:
            # Конвертируем в RGB если изображение в другом формате
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Создаем миниатюру с сохранением пропорций
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Сохраняем миниатюру
            img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
            
        return str(thumbnail_path)
    
    except Exception as e:
        logger.error(f"Error creating thumbnail for {image_path}: {e}")
        return None

async def save_revision_message_file(file: UploadFile, message_id: int) -> Path:
    """Сохранить файл сообщения правки"""
    try:
        # Создаем папку для файлов сообщения
        message_dir = REVISIONS_UPLOAD_DIR / f"message_{message_id}"
        message_dir.mkdir(parents=True, exist_ok=True)
        
        # Генерируем уникальное имя файла
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = message_dir / unique_filename
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_path
    
    except Exception as e:
        logger.error(f"Error saving revision message file: {e}")
        return None

def get_file_type(filename: str) -> str:
    """Определить тип файла"""
    extension = Path(filename).suffix.lower()
    
    if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        return 'image'
    elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv']:
        return 'video'
    elif extension in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
        return 'document'
    else:
        return 'other'

async def send_revision_notification(revision: ProjectRevision, action: str):
    """Отправить уведомление о правке"""
    try:
        from ...services.notification_service import notification_service
        from ...database.database import get_db_context
        
        with get_db_context() as db:
            # Получаем данные проекта и клиента
            project = db.get(Project, revision.project_id)
            client_user = db.get(User, project.user_id)
            
            if action == "new":
                await notification_service.notify_new_revision(revision, project, client_user)
            elif action == "completed":
                await notification_service.notify_revision_status_changed(
                    revision, project, client_user, "in_progress"
                )
            elif action in ["open", "in_progress", "rejected"]:
                await notification_service.notify_revision_status_changed(
                    revision, project, client_user, "open"
                )
                
        logger.info(f"Revision notification sent: revision_id={revision.id}, action={action}")
        
    except Exception as e:
        logger.error(f"Error sending revision notification: {e}")

async def send_revision_message_notification(revision: ProjectRevision, message: RevisionMessage):
    """Отправить уведомление о новом сообщении"""
    try:
        from ...services.notification_service import notification_service
        from ...database.database import get_db_context
        
        with get_db_context() as db:
            # Получаем данные проекта и пользователей
            project = db.get(Project, revision.project_id)
            client_user = db.get(User, project.user_id)
            
            # Получаем отправителя в зависимости от типа
            sender_user = None
            if message.sender_type == "client" and message.sender_user_id:
                sender_user = db.get(User, message.sender_user_id)
            elif message.sender_type in ["admin", "executor"] and message.sender_admin_id:
                sender_user = db.get(AdminUser, message.sender_admin_id)
            
            # Определяем получателя по типу отправителя
            if message.sender_type == "client":
                # Сообщение от клиента - уведомляем админа
                await notification_service.send_admin_notification(
                    f"💬 Новое сообщение от клиента по правке #{revision.revision_number}\n"
                    f"📋 Проект: {project.title}\n"
                    f"📝 Сообщение: {message.message[:200]}{'...' if len(message.message) > 200 else ''}"
                )
            else:
                # Сообщение от исполнителя/админа - уведомляем клиента
                sender_user = message.sender_admin if message.sender_admin else None
                await notification_service.notify_revision_message(
                    revision, project, message, sender_user, client_user
                )
                
        logger.info(f"Revision message notification sent: revision_id={revision.id}, message_id={message.id}")
        
    except Exception as e:
        logger.error(f"Error sending revision message notification: {e}")

@router.post("/api/revisions/messages", response_class=JSONResponse)
async def create_revision_message_simple(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_admin_user)
):
    """Создать сообщение правки (упрощенный роут)"""
    try:
        logger.info(f"Creating revision message for user {user['id']}")
        
        # Получаем данные из формы
        form_data = await request.form()
        
        revision_id = form_data.get("revision_id")
        content = form_data.get("message")  # Фронтенд отправляет 'message', а не 'content'
        is_internal = form_data.get("is_internal") == "true"
        
        logger.info(f"Form data: revision_id={revision_id}, content_length={len(content) if content else 0}, is_internal={is_internal}")
        
        if not revision_id or not content:
            raise HTTPException(status_code=400, detail="Необходимо указать revision_id и message")
        
        revision_id = int(revision_id)
        
        # Проверяем существование правки
        revision = db.query(ProjectRevision).filter(ProjectRevision.id == revision_id).first()
        if not revision:
            raise HTTPException(status_code=404, detail="Правка не найдена")
        
        # Создаем сообщение
        message = RevisionMessage(
            revision_id=revision_id,
            sender_type="admin",
            sender_admin_id=user['id'],  # ID админа
            message=content,  # Используем поле 'message' вместо 'content'
            is_internal=is_internal,
            created_at=datetime.utcnow()
        )
        
        db.add(message)
        db.flush()
        
        # Обработка файлов
        files = form_data.getlist("files")
        uploaded_files = []
        
        for file in files:
            if hasattr(file, 'filename') and file.filename:
                # Сохраняем файл
                upload_dir = Path("uploads/revisions/messages")
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                file_ext = Path(file.filename).suffix
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                file_path = upload_dir / unique_filename
                
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Создаем запись в БД
                message_file = RevisionMessageFile(
                    message_id=message.id,
                    filename=unique_filename,
                    original_filename=file.filename,
                    file_type=get_file_type(file.filename),
                    file_size=len(content),
                    file_path=str(file_path),
                    created_at=datetime.utcnow()
                )
                
                db.add(message_file)
                uploaded_files.append(message_file)
        
        db.commit()
        
        # Отправляем уведомление
        await send_revision_message_notification(revision, message)
        
        return JSONResponse(content={
            "success": True,
            "message": "Сообщение добавлено",
            "message_id": message.id,
            "files_count": len(uploaded_files)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating revision message: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания сообщения")
