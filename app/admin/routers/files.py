# app/admin/routers/files.py
import os
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import uuid
import secrets

from ...database.database import get_db
from ...database.models import AdminUser, Project, ProjectFile
from ...config.logging import get_logger
from ...config.settings import settings
from ...services.auth_service import AuthService
from ...services.projects_service import ProjectsService

logger = get_logger(__name__)

router = APIRouter(tags=["files"])

# Базовая аутентификация
security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Проверка аутентификации - такая же как в основной админ-панели"""
    # Проверяем основного владельца
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    if correct_username and correct_password:
        return credentials.username
    
    # Проверяем исполнителей в базе данных
    try:
        admin_user = AuthService.authenticate_user(credentials.username, credentials.password)
        if admin_user:
            return credentials.username
    except Exception as e:
        logger.error(f"Ошибка при проверке исполнителя: {e}")
    
    # Если ни один способ не сработал
    raise HTTPException(
        status_code=401,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )

def get_current_user(username: str = Depends(authenticate_user)) -> AdminUser:
    """Получение текущего пользователя"""
    # Если это основной владелец
    if username == settings.ADMIN_USERNAME:
        # Создаем виртуального пользователя для владельца
        class VirtualOwner:
            def __init__(self):
                self.id = 1
                self.username = settings.ADMIN_USERNAME
                self.role = "owner"
                self.is_active = True
            
            def is_owner(self):
                return True
            
            def is_executor(self):
                return False
        
        return VirtualOwner()
    
    # Ищем в базе данных
    db = next(get_db())
    try:
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return user
    finally:
        db.close()

# Разрешенные типы файлов и максимальный размер
ALLOWED_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def get_upload_path():
    """Получить путь для загрузки файлов"""
    upload_dir = os.path.join(os.getcwd(), "uploads", "projects")
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

@router.post("/")
async def upload_file_with_query_param(
    project_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: AdminUser = Depends(get_current_user)
):
    """Загрузить файл для проекта (endpoint с query параметром для совместимости с frontend)"""
    return await upload_project_file(project_id, file, description, current_user)

@router.post("/upload/{project_id}")
async def upload_project_file(
    project_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: AdminUser = Depends(get_current_user)
):
    """Загрузить файл для проекта (с учетом прав доступа)"""
    try:
        # Проверяем доступ к проекту
        project = ProjectsService.get_project_by_id(project_id, current_user)
        if not project:
            return {
                "success": False,
                "message": "Проект не найден или у вас нет доступа к нему"
            }
        
        # Проверяем размер файла
        if file.size > MAX_FILE_SIZE:
            return {
                "success": False,
                "message": f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB"
            }
        
        # Проверяем расширение файла
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            return {
                "success": False,
                "message": f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
            }
        
        # Генерируем уникальное имя файла
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = get_upload_path()
        file_path = os.path.join(upload_path, unique_filename)
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Определяем тип файла
        if file_extension in {'.zip', '.rar', '.7z', '.tar', '.gz'}:
            file_type = 'archive'
        elif file_extension in {'.jpg', '.jpeg', '.png', '.gif'}:
            file_type = 'image'
        elif file_extension in {'.pdf', '.doc', '.docx', '.txt'}:
            file_type = 'document'
        else:
            file_type = 'other'
        
        # Сохраняем информацию о файле в БД
        db = next(get_db())
        try:
            project_file = ProjectFile(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file.size,
                file_type=file_type,
                description=description,
                project_id=project_id,
                uploaded_by_id=current_user.id
            )
            
            db.add(project_file)
            db.commit()
            db.refresh(project_file)
            
            return {
                "success": True,
                "message": "Файл успешно загружен",
                "file": project_file.to_dict()
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка загрузки файла для проекта {project_id}: {e}")
        # Удаляем файл если произошла ошибка
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return {
            "success": False,
            "message": f"Ошибка загрузки файла: {str(e)}"
        }

@router.get("/project/{project_id}")
async def get_project_files(
    project_id: int,
    current_user: AdminUser = Depends(get_current_user)
):
    """Получить список файлов проекта (с учетом прав доступа)"""
    try:
        files = ProjectsService.get_project_files(project_id, current_user)
        return {
            "success": True,
            "files": files
        }
    except Exception as e:
        logger.error(f"Ошибка получения файлов проекта {project_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка получения файлов: {str(e)}",
            "files": []
        }

@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    current_user: AdminUser = Depends(get_current_user)
):
    """Скачать файл проекта (с проверкой доступа)"""
    try:
        db = next(get_db())
        try:
            # Получаем файл
            project_file = db.query(ProjectFile).join(Project).filter(
                ProjectFile.id == file_id
            ).first()
            
            if not project_file:
                raise HTTPException(status_code=404, detail="Файл не найден")
            
            # Проверяем доступ к проекту
            project = ProjectsService.get_project_by_id(project_file.project_id, current_user)
            if not project:
                raise HTTPException(status_code=403, detail="У вас нет доступа к этому файлу")
            
            # Проверяем существование файла на диске
            if not os.path.exists(project_file.file_path):
                raise HTTPException(status_code=404, detail="Файл не найден на диске")
            
            return FileResponse(
                path=project_file.file_path,
                filename=project_file.original_filename,
                media_type='application/octet-stream'
            )
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка скачивания файла {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка скачивания файла")

@router.delete("/delete/{file_id}")
async def delete_file(
    file_id: int,
    current_user: AdminUser = Depends(get_current_user)
):
    """Удалить файл проекта (с проверкой доступа)"""
    try:
        db = next(get_db())
        try:
            # Получаем файл
            project_file = db.query(ProjectFile).join(Project).filter(
                ProjectFile.id == file_id
            ).first()
            
            if not project_file:
                return {
                    "success": False,
                    "message": "Файл не найден"
                }
            
            # Проверяем доступ к проекту
            project = ProjectsService.get_project_by_id(project_file.project_id, current_user)
            if not project:
                return {
                    "success": False,
                    "message": "У вас нет доступа к этому файлу"
                }
            
            # Удаляем файл с диска
            if os.path.exists(project_file.file_path):
                os.remove(project_file.file_path)
            
            # Удаляем запись из БД
            db.delete(project_file)
            db.commit()
            
            return {
                "success": True,
                "message": "Файл успешно удален"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка удаления файла {file_id}: {e}")
        return {
            "success": False,
            "message": f"Ошибка удаления файла: {str(e)}"
        }

@router.get("/all")
async def get_all_files(
    current_user: AdminUser = Depends(get_current_user)
):
    """Получить все файлы (база проектов - только для владельца)"""
    try:
        if not current_user.is_owner():
            return {
                "success": False,
                "message": "Только владелец может просматривать все файлы"
            }
        
        db = next(get_db())
        try:
            files = db.query(ProjectFile).join(Project).all()
            return {
                "success": True,
                "files": [file.to_dict() for file in files]
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка получения всех файлов: {e}")
        return {
            "success": False,
            "message": f"Ошибка получения файлов: {str(e)}",
            "files": []
        }
