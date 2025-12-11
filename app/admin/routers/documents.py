"""
Роутер для управления документами
"""

from fastapi import APIRouter, Depends, Request, HTTPException, Response, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

from ...core.database import get_db
from sqlalchemy.orm import Session
from ..middleware.auth import get_current_admin_user
from ...services.document_service import DocumentService
from ...services.rbac_service import RBACService
from ...database.crm_models import Document, DocumentTemplate
from ...config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_class=HTMLResponse)
async def documents_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Страница управления документами"""
    rbac = RBACService(db)
    
    # Проверяем доступ к модулю
    if not rbac.has_module_access(user, 'documents'):
        raise HTTPException(status_code=403, detail="Доступ к документам запрещен")
    
    # Получаем навигацию
    from .admin_main import get_navigation_items
    navigation_items = get_navigation_items(user, db)
    
    # Статистика
    doc_service = DocumentService(db)
    
    total_docs = db.query(Document).count()
    draft_docs = db.query(Document).filter(Document.status == 'draft').count()
    sent_docs = db.query(Document).filter(Document.status == 'sent').count()
    signed_docs = db.query(Document).filter(Document.status == 'signed').count()
    
    templates_count = db.query(DocumentTemplate).filter(DocumentTemplate.is_active == True).count()
    
    # Получаем последние документы
    recent_docs = db.query(Document).order_by(Document.created_at.desc()).limit(10).all()
    
    return request.state.templates.TemplateResponse("documents.html", {
        "request": request,
        "user": user,
        "navigation_items": navigation_items,
        "stats": {
            "total": total_docs,
            "draft": draft_docs,
            "sent": sent_docs,
            "signed": signed_docs,
            "templates": templates_count
        },
        "recent_documents": recent_docs
    })


# === API для документов ===

@router.get("/api")
async def get_documents(
    request: Request,
    page: int = 1,
    limit: int = 20,
    type: Optional[str] = None,
    status: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Получить список документов"""
    rbac = RBACService(db)
    
    if not rbac.has_module_access(user, 'documents'):
        return JSONResponse(content={"success": False, "message": "Нет доступа"}, status_code=403)
    
    doc_service = DocumentService(db)
    
    # Формируем фильтры
    filters = {}
    if type:
        filters['type'] = type
    if status:
        filters['status'] = status
    if entity_type:
        filters['entity_type'] = entity_type
    if entity_id:
        filters['entity_id'] = entity_id
    if search:
        filters['search'] = search
    if date_from:
        filters['date_from'] = datetime.fromisoformat(date_from)
    if date_to:
        filters['date_to'] = datetime.fromisoformat(date_to)
    
    # Проверяем доступ к данным
    if not rbac.check_data_access(user, 'documents', None, 'read'):
        # Показываем только свои документы
        filters['created_by'] = user.id
    
    documents = doc_service.get_documents(filters)
    
    # Пагинация
    total = len(documents)
    start = (page - 1) * limit
    end = start + limit
    documents_page = documents[start:end]
    
    # Формируем ответ
    return JSONResponse(content={
        "success": True,
        "documents": [
            {
                "id": doc.id,
                "number": doc.number,
                "type": doc.type,
                "title": doc.title,
                "status": doc.status,
                "entity_type": doc.entity_type,
                "entity_id": doc.entity_id,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "sent_at": doc.sent_at.isoformat() if doc.sent_at else None,
                "signed_at": doc.signed_at.isoformat() if doc.signed_at else None,
                "created_by_name": doc.creator.username if doc.creator else None,
                "file_path": doc.file_path
            }
            for doc in documents_page
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    })


@router.post("/api/generate")
async def generate_document(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Генерация документа из шаблона"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.create'):
        return JSONResponse(content={"success": False, "message": "Нет прав на создание документов"}, status_code=403)
    
    data = await request.json()
    
    template_id = data.get('template_id')
    entity_type = data.get('entity_type')
    entity_id = data.get('entity_id')
    
    if not all([template_id, entity_type, entity_id]):
        return JSONResponse(content={"success": False, "message": "Не все параметры указаны"}, status_code=400)
    
    doc_service = DocumentService(db)
    
    # Генерируем документ
    document = doc_service.generate_document(
        template_id=template_id,
        entity_type=entity_type,
        entity_id=entity_id,
        created_by=user.id
    )
    
    if document:
        logger.info(f"Document generated: {document.id} by user {user.id}")
        return JSONResponse(content={
            "success": True,
            "message": "Документ успешно создан",
            "document_id": document.id
        })
    else:
        return JSONResponse(content={
            "success": False,
            "message": "Ошибка генерации документа"
        }, status_code=500)


@router.post("/api/batch-generate")
async def batch_generate_documents(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Массовая генерация документов"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.create'):
        return JSONResponse(content={"success": False, "message": "Нет прав на создание документов"}, status_code=403)
    
    data = await request.json()
    
    template_id = data.get('template_id')
    entity_type = data.get('entity_type')
    entity_ids = data.get('entity_ids', [])
    
    if not all([template_id, entity_type, entity_ids]):
        return JSONResponse(content={"success": False, "message": "Не все параметры указаны"}, status_code=400)
    
    doc_service = DocumentService(db)
    
    # Генерируем документы
    documents = doc_service.batch_generate_documents(
        template_id=template_id,
        entity_type=entity_type,
        entity_ids=entity_ids,
        created_by=user.id
    )
    
    logger.info(f"Batch generated {len(documents)} documents by user {user.id}")
    
    return JSONResponse(content={
        "success": True,
        "message": f"Создано документов: {len(documents)}",
        "document_ids": [doc.id for doc in documents]
    })


@router.get("/api/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Получить документ по ID"""
    rbac = RBACService(db)
    
    if not rbac.check_data_access(user, 'documents', document_id, 'read'):
        return JSONResponse(content={"success": False, "message": "Нет доступа к документу"}, status_code=403)
    
    doc_service = DocumentService(db)
    document = doc_service.get_document(document_id)
    
    if not document:
        return JSONResponse(content={"success": False, "message": "Документ не найден"}, status_code=404)
    
    return JSONResponse(content={
        "success": True,
        "document": {
            "id": document.id,
            "number": document.number,
            "type": document.type,
            "title": document.title,
            "content": document.content,
            "status": document.status,
            "entity_type": document.entity_type,
            "entity_id": document.entity_id,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "sent_at": document.sent_at.isoformat() if document.sent_at else None,
            "signed_at": document.signed_at.isoformat() if document.signed_at else None,
            "file_path": document.file_path,
            "settings": document.settings
        }
    })


@router.put("/api/{document_id}/status")
async def update_document_status(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Обновить статус документа"""
    rbac = RBACService(db)
    
    if not rbac.check_data_access(user, 'documents', document_id, 'update'):
        return JSONResponse(content={"success": False, "message": "Нет прав на изменение документа"}, status_code=403)
    
    data = await request.json()
    new_status = data.get('status')
    
    if new_status not in ['draft', 'sent', 'signed', 'cancelled']:
        return JSONResponse(content={"success": False, "message": "Недопустимый статус"}, status_code=400)
    
    doc_service = DocumentService(db)
    
    signed_at = None
    if new_status == 'signed':
        signed_at = datetime.utcnow()
    
    document = doc_service.update_document_status(document_id, new_status, signed_at)
    
    if document:
        logger.info(f"Document {document_id} status updated to {new_status} by user {user.id}")
        return JSONResponse(content={
            "success": True,
            "message": f"Статус документа обновлен на {new_status}"
        })
    else:
        return JSONResponse(content={
            "success": False,
            "message": "Ошибка обновления статуса"
        }, status_code=500)


@router.post("/api/{document_id}/send")
async def send_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Отправить документ"""
    rbac = RBACService(db)
    
    if not rbac.check_data_access(user, 'documents', document_id, 'update'):
        return JSONResponse(content={"success": False, "message": "Нет прав на отправку документа"}, status_code=403)
    
    data = await request.json()
    recipient_email = data.get('email')
    message = data.get('message', '')
    
    if not recipient_email:
        return JSONResponse(content={"success": False, "message": "Email получателя не указан"}, status_code=400)
    
    doc_service = DocumentService(db)
    result = doc_service.send_document(document_id, recipient_email, message)
    
    if result:
        logger.info(f"Document {document_id} sent to {recipient_email} by user {user.id}")
        return JSONResponse(content={
            "success": True,
            "message": f"Документ отправлен на {recipient_email}"
        })
    else:
        return JSONResponse(content={
            "success": False,
            "message": "Ошибка отправки документа"
        }, status_code=500)


@router.post("/api/{document_id}/duplicate")
async def duplicate_document(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Дублировать документ"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.create'):
        return JSONResponse(content={"success": False, "message": "Нет прав на создание документов"}, status_code=403)
    
    doc_service = DocumentService(db)
    new_document = doc_service.duplicate_document(document_id, user.id)
    
    if new_document:
        logger.info(f"Document {document_id} duplicated as {new_document.id} by user {user.id}")
        return JSONResponse(content={
            "success": True,
            "message": "Документ успешно продублирован",
            "document_id": new_document.id
        })
    else:
        return JSONResponse(content={
            "success": False,
            "message": "Ошибка дублирования документа"
        }, status_code=500)


@router.get("/api/{document_id}/download")
async def download_document(
    document_id: int,
    format: str = 'pdf',
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Скачать документ"""
    rbac = RBACService(db)
    
    if not rbac.check_data_access(user, 'documents', document_id, 'read'):
        raise HTTPException(status_code=403, detail="Нет доступа к документу")
    
    doc_service = DocumentService(db)
    document = doc_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    if not document.file_path:
        raise HTTPException(status_code=404, detail="Файл документа не найден")
    
    # Определяем путь к файлу в зависимости от формата
    file_paths = document.settings.get('file_paths', {}) if document.settings else {}
    
    if format == 'pdf' and file_paths.get('pdf'):
        file_path = file_paths['pdf']
        media_type = 'application/pdf'
        filename = f"{document.number}.pdf"
    elif format == 'html' and file_paths.get('html'):
        file_path = file_paths['html']
        media_type = 'text/html'
        filename = f"{document.number}.html"
    else:
        file_path = document.file_path
        media_type = 'application/octet-stream'
        filename = f"{document.number}.pdf"
    
    import os
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден на сервере")
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


# === API для шаблонов ===

@router.get("/templates")
async def templates_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Страница управления шаблонами"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.templates'):
        raise HTTPException(status_code=403, detail="Доступ к шаблонам запрещен")
    
    # Получаем навигацию
    from .admin_main import get_navigation_items
    navigation_items = get_navigation_items(user, db)
    
    return request.state.templates.TemplateResponse("document_templates.html", {
        "request": request,
        "user": user,
        "navigation_items": navigation_items
    })


@router.get("/templates/api")
async def get_templates(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Получить список шаблонов"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.templates'):
        return JSONResponse(content={"success": False, "message": "Нет доступа к шаблонам"}, status_code=403)
    
    query = db.query(DocumentTemplate).filter(DocumentTemplate.is_active == True)
    
    if type:
        query = query.filter(DocumentTemplate.type == type)
    
    templates = query.order_by(DocumentTemplate.name).all()
    
    return JSONResponse(content={
        "success": True,
        "templates": [
            {
                "id": tpl.id,
                "name": tpl.name,
                "type": tpl.type,
                "variables": tpl.variables,
                "created_at": tpl.created_at.isoformat() if tpl.created_at else None,
                "updated_at": tpl.updated_at.isoformat() if tpl.updated_at else None
            }
            for tpl in templates
        ]
    })


@router.post("/templates/api")
async def create_template(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Создать новый шаблон"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.templates'):
        return JSONResponse(content={"success": False, "message": "Нет прав на создание шаблонов"}, status_code=403)
    
    data = await request.json()
    
    doc_service = DocumentService(db)
    template = doc_service.create_template(data, user.id)
    
    logger.info(f"Template created: {template.id} by user {user.id}")
    
    return JSONResponse(content={
        "success": True,
        "message": "Шаблон успешно создан",
        "template_id": template.id
    })


@router.put("/templates/api/{template_id}")
async def update_template(
    template_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Обновить шаблон"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.templates'):
        return JSONResponse(content={"success": False, "message": "Нет прав на изменение шаблонов"}, status_code=403)
    
    data = await request.json()
    
    doc_service = DocumentService(db)
    template = doc_service.update_template(template_id, data)
    
    if template:
        logger.info(f"Template {template_id} updated by user {user.id}")
        return JSONResponse(content={
            "success": True,
            "message": "Шаблон успешно обновлен"
        })
    else:
        return JSONResponse(content={
            "success": False,
            "message": "Шаблон не найден"
        }, status_code=404)


@router.delete("/templates/api/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Удалить (деактивировать) шаблон"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.templates'):
        return JSONResponse(content={"success": False, "message": "Нет прав на удаление шаблонов"}, status_code=403)
    
    doc_service = DocumentService(db)
    result = doc_service.deactivate_template(template_id)
    
    if result:
        logger.info(f"Template {template_id} deactivated by user {user.id}")
        return JSONResponse(content={
            "success": True,
            "message": "Шаблон успешно удален"
        })
    else:
        return JSONResponse(content={
            "success": False,
            "message": "Шаблон не найден"
        }, status_code=404)


@router.post("/templates/api/create-defaults")
async def create_default_templates(
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Создать стандартные шаблоны"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.templates'):
        return JSONResponse(content={"success": False, "message": "Нет прав на создание шаблонов"}, status_code=403)
    
    doc_service = DocumentService(db)
    doc_service.create_default_templates(user.id)
    
    logger.info(f"Default templates created by user {user.id}")
    
    return JSONResponse(content={
        "success": True,
        "message": "Стандартные шаблоны успешно созданы"
    })


@router.post("/api/ai-fill")
async def ai_fill_template(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Заполнить шаблон с помощью AI"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.create'):
        return JSONResponse(content={"success": False, "message": "Нет прав на создание документов"}, status_code=403)
    
    try:
        data = await request.json()
        template_id = data.get('template_id')
        entity_type = data.get('entity_type')
        entity_id = data.get('entity_id')
        
        if not all([template_id, entity_type, entity_id]):
            return JSONResponse(content={"success": False, "message": "Не указаны все параметры"}, status_code=400)
        
        # Получаем шаблон
        template = db.query(DocumentTemplate).filter(
            DocumentTemplate.id == template_id, 
            DocumentTemplate.is_active == True
        ).first()
        
        if not template:
            return JSONResponse(content={"success": False, "message": "Шаблон не найден"}, status_code=404)
        
        # Получаем данные сущности для заполнения
        entity_data = await get_entity_data(db, entity_type, entity_id)
        if not entity_data:
            return JSONResponse(content={"success": False, "message": f"Не найдена {entity_type} с ID {entity_id}"}, status_code=404)
        
        # Используем простую AI логику (заглушка - можно подключить OpenAI/Claude API)
        filled_content = ai_fill_template_content(template.content, entity_data, template.doc_type)
        suggestions = generate_ai_suggestions(entity_data, template.doc_type)
        
        logger.info(f"Template {template_id} AI-filled for {entity_type} {entity_id} by user {user.id}")
        
        return JSONResponse(content={
            "success": True,
            "content": filled_content,
            "suggestions": suggestions,
            "message": "Шаблон заполнен с помощью ИИ"
        })
        
    except Exception as e:
        logger.error(f"Error AI-filling template: {e}")
        return JSONResponse(content={"success": False, "message": f"Ошибка заполнения: {str(e)}"}, status_code=500)


@router.post("/api/create-with-content")
async def create_document_with_content(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_admin_user)
):
    """Создать документ с готовым контентом"""
    rbac = RBACService(db)
    
    if not rbac.has_permission(user, 'documents.create'):
        return JSONResponse(content={"success": False, "message": "Нет прав на создание документов"}, status_code=403)
    
    try:
        data = await request.json()
        template_id = data.get('template_id')
        entity_type = data.get('entity_type') 
        entity_id = data.get('entity_id')
        content = data.get('content')
        filled_by = data.get('filled_by', 'manual')
        
        if not all([template_id, entity_type, entity_id, content]):
            return JSONResponse(content={"success": False, "message": "Не указаны все параметры"}, status_code=400)
        
        doc_service = DocumentService(db)
        document = doc_service.create_document_with_content(
            template_id=template_id,
            entity_type=entity_type,
            entity_id=entity_id,
            content=content,
            created_by=user.id,
            filled_by=filled_by
        )
        
        if document:
            logger.info(f"Document created with {filled_by} content by user {user.id}")
            return JSONResponse(content={
                "success": True,
                "document_id": document.id,
                "message": f"Документ создан (заполнен {filled_by})"
            })
        else:
            return JSONResponse(content={"success": False, "message": "Ошибка создания документа"}, status_code=500)
            
    except Exception as e:
        logger.error(f"Error creating document with content: {e}")
        return JSONResponse(content={"success": False, "message": f"Ошибка создания: {str(e)}"}, status_code=500)


async def get_entity_data(db: Session, entity_type: str, entity_id: int) -> dict:
    """Получить данные сущности для заполнения шаблона"""
    try:
        if entity_type == 'client':
            from ...database.crm_models import Client
            entity = db.query(Client).filter(Client.id == entity_id).first()
            if entity:
                return {
                    'name': entity.name,
                    'phone': entity.phone or '',
                    'email': entity.email or '',
                    'company_name': entity.company_name or '',
                    'address': entity.address or '',
                    'type': 'Клиент'
                }
        elif entity_type == 'deal':
            from ...database.crm_models import Deal
            entity = db.query(Deal).filter(Deal.id == entity_id).first()
            if entity:
                client_name = entity.client.name if entity.client else 'Не указан'
                return {
                    'title': entity.title,
                    'amount': entity.amount or 0,
                    'description': entity.description or '',
                    'client_name': client_name,
                    'status': entity.status.value if entity.status else 'новая',
                    'type': 'Сделка'
                }
        elif entity_type == 'lead':
            from ...database.crm_models import Lead
            entity = db.query(Lead).filter(Lead.id == entity_id).first()
            if entity:
                return {
                    'title': entity.title,
                    'contact_name': entity.contact_name or '',
                    'contact_phone': entity.contact_phone or '',
                    'contact_email': entity.contact_email or '',
                    'company_name': entity.company_name or '',
                    'description': entity.description or '',
                    'budget': entity.budget or 0,
                    'type': 'Лид'
                }
    except Exception as e:
        logger.error(f"Error getting entity data: {e}")
    
    return None


def ai_fill_template_content(template_content: str, entity_data: dict, doc_type: str) -> str:
    """Простая AI заглушка для заполнения шаблона"""
    # Это упрощенная версия - можно подключить OpenAI API или Claude API
    filled_content = template_content
    
    # Заменяем основные плейсхолдеры
    replacements = {
        '{client_name}': entity_data.get('name', entity_data.get('client_name', 'Клиент')),
        '{client_phone}': entity_data.get('phone', entity_data.get('contact_phone', '')),
        '{client_email}': entity_data.get('email', entity_data.get('contact_email', '')),
        '{company_name}': entity_data.get('company_name', ''),
        '{amount}': str(entity_data.get('amount', entity_data.get('budget', 0))),
        '{description}': entity_data.get('description', ''),
        '{title}': entity_data.get('title', ''),
        '{date}': datetime.now().strftime('%d.%m.%Y'),
        '{current_date}': datetime.now().strftime('%d.%m.%Y')
    }
    
    for placeholder, value in replacements.items():
        filled_content = filled_content.replace(placeholder, str(value))
    
    return filled_content


def generate_ai_suggestions(entity_data: dict, doc_type: str) -> List[str]:
    """Генерация AI рекомендаций"""
    suggestions = []
    
    if doc_type == 'contract':
        suggestions.extend([
            "Проверьте правильность указания реквизитов сторон",
            "Убедитесь в корректности суммы договора",
            "Проверьте сроки выполнения работ"
        ])
    elif doc_type == 'invoice':
        if entity_data.get('amount', 0) > 100000:
            suggestions.append("Крупная сумма - рекомендуется разбить на этапы")
        suggestions.extend([
            "Проверьте НДС если применимо",
            "Укажите корректные банковские реквизиты"
        ])
    elif doc_type == 'offer':
        suggestions.extend([
            "Добавьте детальное описание услуг",
            "Укажите условия оплаты",
            "Проверьте срок действия предложения"
        ])
    
    # Общие рекомендации
    if not entity_data.get('phone') and not entity_data.get('contact_phone'):
        suggestions.append("Отсутствует контактный телефон")
    if not entity_data.get('email') and not entity_data.get('contact_email'):
        suggestions.append("Отсутствует email для связи")
    
    return suggestions