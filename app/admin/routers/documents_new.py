"""
Роутер для управления документами (упрощенная версия)
"""

from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os
import uuid
import shutil

from ...database.database import get_db
from ...database.models import AdminUser, Project
from ...database.crm_models import Document
from ..middleware.auth import get_current_admin_user
from ..navigation import get_navigation_items
from ...config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])
templates = Jinja2Templates(directory="app/admin/templates")

# Директория для хранения документов
DOCUMENTS_DIR = "uploads/documents"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)


def get_user_role(user):
    """Получить роль пользователя (работает с объектом и словарем)"""
    return user.role if hasattr(user, 'role') else user.get('role')


def get_user_id(user):
    """Получить ID пользователя (работает с объектом и словарем)"""
    return user.id if hasattr(user, 'id') else user.get('id')


@router.get("/", response_class=HTMLResponse)
async def documents_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Страница управления документами"""
    try:
        # Статистика
        query = db.query(Document)

        # Если не owner, показываем только доступные документы (не договоры)
        if get_user_role(current_user) != 'owner':
            query = query.filter(Document.type != 'contract')

        total_docs = query.count()

        # Статистика по типам
        contracts_count = db.query(Document).filter(Document.type == 'contract').count() if get_user_role(current_user) == 'owner' else 0
        invoices_count = db.query(Document).filter(Document.type == 'invoice').count()
        acts_count = db.query(Document).filter(Document.type == 'act').count()
        other_count = db.query(Document).filter(Document.type == 'other').count()

        return templates.TemplateResponse("documents.html", {
            "request": request,
            "user": current_user,
            "navigation_items": get_navigation_items("/admin/documents"),
            "stats": {
                "total": total_docs,
                "contracts": contracts_count,
                "invoices": invoices_count,
                "acts": acts_count,
                "other": other_count
            }
        })
    except Exception as e:
        logger.error(f"Ошибка загрузки страницы документов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/list")
async def get_documents(
    type: Optional[str] = None,
    search: Optional[str] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить список документов"""
    try:
        query = db.query(Document)

        # Фильтр по правам доступа
        user_role = get_user_role(current_user) if hasattr(current_user, 'role') else current_user.get('role')
        if user_role != 'owner':
            # Не owner не видят договоры
            query = query.filter(Document.type != 'contract')

        # Фильтры
        if type:
            query = query.filter(Document.type == type)

        if search:
            query = query.filter(
                or_(
                    Document.name.ilike(f"%{search}%"),
                    Document.description.ilike(f"%{search}%"),
                    Document.number.ilike(f"%{search}%")
                )
            )

        if project_id:
            query = query.filter(Document.project_id == project_id)

        documents = query.order_by(Document.created_at.desc()).all()

        return {
            "success": True,
            "documents": [
                {
                    "id": doc.id,
                    "name": doc.name,
                    "type": doc.type,
                    "number": doc.number,
                    "description": doc.description,
                    "file_path": doc.file_path,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "project_id": doc.project_id,
                    "project_name": doc.project.title if doc.project else None,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "created_by": doc.created_by.username if doc.created_by else None
                }
                for doc in documents
            ],
            "total": len(documents)
        }
    except Exception as e:
        logger.error(f"Ошибка получения списка документов: {e}")
        return {"success": False, "message": str(e)}


@router.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    type: str = Form(...),
    description: Optional[str] = Form(None),
    number: Optional[str] = Form(None),
    project_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Загрузить новый документ"""
    try:
        # Проверка прав на загрузку договоров
        if type == 'contract' and get_user_role(current_user) != 'owner':
            return {"success": False, "message": "Только владелец может загружать договоры"}

        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(DOCUMENTS_DIR, unique_filename)

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Получаем размер файла
        file_size = os.path.getsize(file_path)

        # Создаем запись в БД
        document = Document(
            name=name,
            type=type,
            description=description,
            number=number,
            file_path=file_path,
            file_type=file.content_type,
            file_size=file_size,
            project_id=project_id,
            created_by_id=get_user_id(current_user),
            created_at=datetime.utcnow()
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        logger.info(f"Загружен документ: {name} (ID: {document.id}) пользователем {current_user.username}")

        return {
            "success": True,
            "message": "Документ успешно загружен",
            "document": {
                "id": document.id,
                "name": document.name,
                "type": document.type,
                "file_path": document.file_path
            }
        }
    except Exception as e:
        logger.error(f"Ошибка загрузки документа: {e}")
        return {"success": False, "message": f"Ошибка загрузки: {str(e)}"}


@router.get("/api/download/{document_id}")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Скачать документ"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(status_code=404, detail="Документ не найден")

        # Проверка прав доступа
        if document.type == 'contract' and get_user_role(current_user) != 'owner':
            raise HTTPException(status_code=403, detail="Нет доступа к договорам")

        # Проверяем существование файла
        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail="Файл не найден на сервере")

        return FileResponse(
            path=document.file_path,
            filename=document.name,
            media_type=document.file_type
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка скачивания документа {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Удалить документ"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            return {"success": False, "message": "Документ не найден"}

        # Проверка прав
        if document.type == 'contract' and get_user_role(current_user) != 'owner':
            return {"success": False, "message": "Нет прав на удаление договоров"}

        # Только создатель или owner может удалять
        if document.created_by_id != get_user_id(current_user) and get_user_role(current_user) != 'owner':
            return {"success": False, "message": "Нет прав на удаление этого документа"}

        # Удаляем файл
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Удаляем запись из БД
        db.delete(document)
        db.commit()

        logger.info(f"Удален документ ID: {document_id} пользователем {current_user.username}")

        return {"success": True, "message": "Документ удален"}
    except Exception as e:
        logger.error(f"Ошибка удаления документа {document_id}: {e}")
        return {"success": False, "message": str(e)}


@router.get("/api/projects")
async def get_projects_for_documents(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить список проектов для привязки документов"""
    try:
        projects = db.query(Project).order_by(Project.created_at.desc()).all()

        return {
            "success": True,
            "projects": [
                {
                    "id": p.id,
                    "title": p.title,
                    "client_name": f"{p.user.first_name or ''} {p.user.last_name or ''}".strip() if p.user else None
                }
                for p in projects
            ]
        }
    except Exception as e:
        logger.error(f"Ошибка получения проектов: {e}")
        return {"success": False, "message": str(e)}
