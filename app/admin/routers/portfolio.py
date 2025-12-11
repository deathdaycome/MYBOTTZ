# app/admin/routers/portfolio.py

import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from PIL import Image
import shutil
import secrets

from ...core.database import get_db_context, get_db
from ...database.models import Portfolio
from ...config.settings import settings
from ...config.logging import get_logger
from ..middleware.auth import get_current_admin_user

logger = get_logger(__name__)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

def check_portfolio_access(current_user: dict = Depends(get_current_admin_user)):
    """Проверка доступа к портфолио (только для владельцев)"""
    if current_user["role"] != "owner":
        raise HTTPException(
            status_code=403,
            detail="У исполнителей нет доступа к портфолио"
        )
    return current_user

# Константы
UPLOAD_DIR = "uploads/portfolio"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
IMAGE_SIZES = {
    "main": (800, 600),      # Основное изображение
    "thumb": (300, 200),     # Миниатюра
    "gallery": (600, 400)    # Галерея
}

# Создаем директории если их нет
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/main", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/additional", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/thumbs", exist_ok=True)

def save_uploaded_image(file: UploadFile, subfolder: str = "main") -> dict:
    """Сохранение загруженного изображения с ресайзом"""
    try:
        # Проверяем размер файла
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Проверяем расширение
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Генерируем уникальное имя файла
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_ext}"
        
        # Сохраняем оригинал
        file_path = os.path.join(UPLOAD_DIR, subfolder, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Создаем миниатюру
        thumb_path = os.path.join(UPLOAD_DIR, "thumbs", f"thumb_{filename}")
        try:
            with Image.open(file_path) as img:
                img.thumbnail(IMAGE_SIZES["thumb"], Image.Resampling.LANCZOS)
                img.save(thumb_path, optimize=True, quality=85)
        except Exception as e:
            logger.error(f"Ошибка создания миниатюры: {e}")
        
        return {
            "filename": filename,
            "original_path": f"{subfolder}/{filename}",
            "thumb_path": f"thumbs/thumb_{filename}",
            "size": file.size,
            "content_type": file.content_type
        }
        
    except Exception as e:
        logger.error(f"Ошибка сохранения изображения: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {str(e)}")

# =================== ADMIN API ENDPOINTS ===================

@router.get("/", dependencies=[Depends(check_portfolio_access)])
async def get_portfolio_list(
    page: int = 1,
    per_page: int = 10,
    category: Optional[str] = None,
    search: Optional[str] = None,
    featured_only: bool = False,
    visible_only: bool = True,
    sort_by: str = "created_desc",
    db: Session = Depends(get_db)
):
    """Получить список проектов портфолио с пагинацией и фильтрами"""
    try:
        query = db.query(Portfolio)
        
        # Применяем фильтры
        if visible_only:
            query = query.filter(Portfolio.is_visible == True)
        
        if featured_only:
            query = query.filter(Portfolio.is_featured == True)
            
        if category:
            query = query.filter(Portfolio.category == category)
            
        if search:
            search_filter = or_(
                Portfolio.title.ilike(f"%{search}%"),
                Portfolio.description.ilike(f"%{search}%"),
                Portfolio.technologies.ilike(f"%{search}%"),
                Portfolio.tags.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Применяем сортировку
        if sort_by == "created_desc":
            query = query.order_by(desc(Portfolio.created_at))
        elif sort_by == "created_asc":
            query = query.order_by(asc(Portfolio.created_at))
        elif sort_by == "title_asc":
            query = query.order_by(asc(Portfolio.title))
        elif sort_by == "title_desc":
            query = query.order_by(desc(Portfolio.title))
        elif sort_by == "order_asc":
            query = query.order_by(asc(Portfolio.sort_order), asc(Portfolio.id))
        else:
            query = query.order_by(desc(Portfolio.created_at))
        
        # Подсчитываем общее количество
        total = query.count()
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        projects = query.offset(offset).limit(per_page).all()
        
        return {
            "success": True,
            "data": [project.to_dict() for project in projects],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения списка портфолио: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")

@router.get("/categories", dependencies=[Depends(check_portfolio_access)])
async def get_categories(db: Session = Depends(get_db)):
    """Получить список всех категорий"""
    try:
        categories = db.query(Portfolio.category).filter(
            Portfolio.category.isnot(None),
            Portfolio.is_visible == True
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        # Добавляем описания для категорий
        category_map = {
            "telegram_bots": "Telegram боты",
            "web_development": "Веб-разработка", 
            "mobile_apps": "Мобильные приложения",
            "ai_integration": "AI интеграции",
            "automation": "Автоматизация",
            "ecommerce": "E-commerce",
            "other": "Другое"
        }
        
        result = [
            {
                "id": cat,
                "name": category_map.get(cat, cat.replace("_", " ").title()),
                "count": db.query(Portfolio).filter(
                    Portfolio.category == cat,
                    Portfolio.is_visible == True
                ).count()
            }
            for cat in category_list
        ]
        
        return {
            "success": True,
            "categories": result
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения категорий: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения категорий: {str(e)}")

@router.get("/{project_id}", dependencies=[Depends(check_portfolio_access)])
async def get_portfolio_item(project_id: int, db: Session = Depends(get_db)):
    """Получить конкретный проект портфолио"""
    try:
        project = db.query(Portfolio).filter(Portfolio.id == project_id).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        return {
            "success": True,
            "data": project.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения проекта {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения проекта: {str(e)}")

@router.post("/", dependencies=[Depends(check_portfolio_access)])
async def create_portfolio_item(
    request: Request,
    db: Session = Depends(get_db)
):
    """Создать новый проект в портфолио"""
    try:
        # Получаем данные формы
        form_data = await request.form()
        
        # Логируем входящие данные
        logger.info(f"Создание нового проекта:")
        logger.info(f"Данные формы: {dict(form_data)}")
        
        # Извлекаем и конвертируем данные
        title = form_data.get("title", "").strip()
        subtitle = form_data.get("subtitle", "").strip()
        description = form_data.get("description", "").strip()
        category = form_data.get("category", "").strip()
        technologies = form_data.get("technologies", "").strip()
        complexity = form_data.get("complexity", "medium").strip()
        
        # Конвертируем числовые поля
        try:
            complexity_level = int(form_data.get("complexity_level", "5"))
        except (ValueError, TypeError):
            complexity_level = 5
            
        try:
            development_time = int(form_data.get("development_time")) if form_data.get("development_time") else None
        except (ValueError, TypeError):
            development_time = None
            
        try:
            cost = float(form_data.get("cost")) if form_data.get("cost") else None
        except (ValueError, TypeError):
            cost = None
            
        try:
            sort_order = int(form_data.get("sort_order", "0"))
        except (ValueError, TypeError):
            sort_order = 0
        
        # Конвертируем булевы поля
        is_featured = form_data.get("is_featured") in ["true", "1", "on", True]
        is_visible = form_data.get("is_visible") in ["true", "1", "on", True]
        show_cost = form_data.get("show_cost") in ["true", "1", "on", True]
        
        # Остальные поля
        cost_range = form_data.get("cost_range", "").strip()
        demo_link = form_data.get("demo_link", "").strip()
        repository_link = form_data.get("repository_link", "").strip()
        external_links_str = form_data.get("external_links", "[]").strip()
        tags = form_data.get("tags", "").strip()
        client_name = form_data.get("client_name", "").strip()
        project_status = form_data.get("project_status", "completed").strip()
        
        # Валидация обязательных полей
        if not title:
            raise HTTPException(status_code=422, detail="Название проекта обязательно")
        if not description:
            raise HTTPException(status_code=422, detail="Описание проекта обязательно")
        if not category:
            raise HTTPException(status_code=422, detail="Категория проекта обязательна")
        
        # Обрабатываем main_image
        main_image = form_data.get("main_image")
        main_image_path = None
        if main_image and hasattr(main_image, 'filename') and main_image.filename:
            image_info = save_uploaded_image(main_image, "main")
            main_image_path = image_info["original_path"]
        
        # Обрабатываем дополнительные изображения (пока пропускаем)
        image_paths = []
        
        # Парсим external_links
        try:
            external_links_json = json.loads(external_links_str) if external_links_str else []
        except:
            external_links_json = []
        
        # Создаем новый проект
        new_project = Portfolio(
            title=title,
            subtitle=subtitle,
            description=description,
            category=category,
            main_image=main_image_path,
            image_paths=image_paths,
            technologies=technologies,
            complexity=complexity,
            complexity_level=complexity_level,
            development_time=development_time,
            cost=cost,
            cost_range=cost_range,
            show_cost=show_cost,
            demo_link=demo_link,
            repository_link=repository_link,
            external_links=external_links_json,
            is_featured=is_featured,
            is_visible=is_visible,
            sort_order=sort_order,
            tags=tags,
            client_name=client_name,
            project_status=project_status,
            created_by=1  # TODO: получать ID админа из сессии
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        logger.info(f"Создан новый проект портфолио: {new_project.id}")
        
        return {
            "success": True,
            "message": "Проект успешно создан",
            "item": new_project.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка создания проекта: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания проекта: {str(e)}")

@router.put("/{project_id}", dependencies=[Depends(check_portfolio_access)])
async def update_portfolio_item(
    project_id: int,
    title: str = Form(...),
    subtitle: str = Form(""),
    description: str = Form(...),
    category: str = Form(...),
    technologies: str = Form(""),
    complexity: str = Form("medium"),
    complexity_level: int = Form(5),
    development_time: Optional[int] = Form(None),
    cost: Optional[float] = Form(None),
    cost_range: str = Form(""),
    show_cost: bool = Form(False),
    demo_link: str = Form(""),
    repository_link: str = Form(""),
    external_links: str = Form("[]"),
    is_featured: bool = Form(False),
    is_visible: bool = Form(True),
    sort_order: int = Form(0),
    tags: str = Form(""),
    client_name: str = Form(""),
    project_status: str = Form("completed"),
    main_image: Optional[UploadFile] = File(None),
    additional_images: List[UploadFile] = File([]),
    remove_main_image: bool = Form(False),
    remove_additional_images: str = Form("[]"),
    db: Session = Depends(get_db)
):
    """Обновить проект в портфолио"""
    try:
        project = db.query(Portfolio).filter(Portfolio.id == project_id).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        # Обновляем основные поля
        project.title = title
        project.subtitle = subtitle
        project.description = description
        project.category = category
        project.technologies = technologies
        project.complexity = complexity
        project.complexity_level = complexity_level
        project.development_time = development_time
        project.cost = cost
        project.cost_range = cost_range
        project.show_cost = show_cost
        project.demo_link = demo_link
        project.repository_link = repository_link
        project.is_featured = is_featured
        project.is_visible = is_visible
        project.sort_order = sort_order
        project.tags = tags
        project.client_name = client_name
        project.project_status = project_status
        project.updated_at = datetime.utcnow()
        
        # Парсим external_links
        try:
            project.external_links = json.loads(external_links) if external_links else []
        except:
            project.external_links = []
        
        # Обрабатываем главное изображение
        if remove_main_image:
            if project.main_image:
                # Удаляем старое изображение
                old_path = os.path.join(UPLOAD_DIR, project.main_image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            project.main_image = None
        elif main_image and main_image.filename:
            # Удаляем старое изображение
            if project.main_image:
                old_path = os.path.join(UPLOAD_DIR, project.main_image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            # Сохраняем новое
            image_info = save_uploaded_image(main_image, "main")
            project.main_image = image_info["original_path"]
        
        # Обрабатываем дополнительные изображения
        try:
            remove_images = json.loads(remove_additional_images) if remove_additional_images else []
        except:
            remove_images = []
        
        current_images = project.image_paths if project.image_paths else []
        
        # Удаляем помеченные изображения
        for img_path in remove_images:
            if img_path in current_images:
                current_images.remove(img_path)
                # Удаляем файл
                full_path = os.path.join(UPLOAD_DIR, img_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
        
        # Добавляем новые изображения
        for img in additional_images:
            if img.filename:
                image_info = save_uploaded_image(img, "additional")
                current_images.append(image_info["original_path"])
        
        project.image_paths = current_images
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"Обновлен проект портфолио: {project.id}")
        
        return {
            "success": True,
            "message": "Проект успешно обновлен",
            "data": project.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка обновления проекта {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления проекта: {str(e)}")

@router.delete("/{project_id}", dependencies=[Depends(check_portfolio_access)])
async def delete_portfolio_item(project_id: int, db: Session = Depends(get_db)):
    """Удалить проект из портфолио"""
    try:
        project = db.query(Portfolio).filter(Portfolio.id == project_id).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        # Удаляем связанные файлы
        if project.main_image:
            main_image_path = os.path.join(UPLOAD_DIR, project.main_image)
            if os.path.exists(main_image_path):
                os.remove(main_image_path)
        
        if project.image_paths:
            for img_path in project.image_paths:
                full_path = os.path.join(UPLOAD_DIR, img_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
        
        # Удаляем проект из базы
        db.delete(project)
        db.commit()
        
        logger.info(f"Удален проект портфолио: {project_id}")
        
        return {
            "success": True,
            "message": "Проект успешно удален"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка удаления проекта {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления проекта: {str(e)}")

@router.post("/upload-image", dependencies=[Depends(check_portfolio_access)])
async def upload_image(
    file: UploadFile = File(...),
    subfolder: str = Form("main")
):
    """Загрузить изображение"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Файл не выбран")
        
        result = save_uploaded_image(file, subfolder)
        
        return {
            "success": True,
            "message": "Изображение успешно загружено",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки изображения: {str(e)}")

@router.post("/reorder", dependencies=[Depends(check_portfolio_access)])
async def reorder_portfolio(
    order_data: dict,
    db: Session = Depends(get_db)
):
    """Изменить порядок проектов в портфолио"""
    try:
        projects_order = order_data.get("projects", [])
        
        for item in projects_order:
            project_id = item.get("id")
            new_order = item.get("order", 0)
            
            project = db.query(Portfolio).filter(Portfolio.id == project_id).first()
            if project:
                project.sort_order = new_order
        
        db.commit()
        
        logger.info("Порядок проектов портфолио обновлен")
        
        return {
            "success": True,
            "message": "Порядок успешно обновлен"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка изменения порядка: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка изменения порядка: {str(e)}")

@router.get("/stats/overview", dependencies=[Depends(check_portfolio_access)])
async def get_portfolio_stats(db: Session = Depends(get_db)):
    """Получить статистику портфолио"""
    try:
        total_projects = db.query(Portfolio).count()
        visible_projects = db.query(Portfolio).filter(Portfolio.is_visible == True).count()
        featured_projects = db.query(Portfolio).filter(Portfolio.is_featured == True).count()
        total_views = db.query(Portfolio).with_entities(Portfolio.views_count).all()
        total_views_sum = sum([v[0] for v in total_views if v[0]]) if total_views else 0
        
        # Статистика по категориям
        categories_stats = db.query(
            Portfolio.category,
            Portfolio.id
        ).filter(Portfolio.is_visible == True).all()
        
        category_counts = {}
        for cat, _ in categories_stats:
            if cat:
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "success": True,
            "stats": {
                "total": total_projects,
                "visible": visible_projects,
                "featured": featured_projects,
                "total_views": total_views_sum,
                "categories": category_counts
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

# =================== PUBLIC API ДЛЯ БОТА ===================

@router.get("/public/categories")
async def get_public_categories(db: Session = Depends(get_db)):
    """Публичное API для получения категорий (для бота)"""
    try:
        categories = db.query(Portfolio.category).filter(
            Portfolio.category.isnot(None),
            Portfolio.is_visible == True
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        category_map = {
            "telegram_bots": "🤖 Telegram боты",
            "web_development": "🌐 Веб-разработка", 
            "mobile_apps": "📱 Мобильные приложения",
            "ai_integration": "🧠 AI интеграции",
            "automation": "⚡ Автоматизация",
            "ecommerce": "🛒 E-commerce",
            "other": "📦 Другое"
        }
        
        result = [
            {
                "id": cat,
                "name": category_map.get(cat, cat.replace("_", " ").title())
            }
            for cat in category_list
        ]
        
        return {
            "success": True,
            "categories": result
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения публичных категорий: {e}")
        return {
            "success": False,
            "categories": []
        }

@router.get("/public/list")
async def get_public_portfolio_list(
    category: Optional[str] = None,
    featured_only: bool = False,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """Публичное API для получения портфолио (для бота)"""
    try:
        query = db.query(Portfolio).filter(Portfolio.is_visible == True)
        
        if featured_only:
            query = query.filter(Portfolio.is_featured == True)
            
        if category:
            query = query.filter(Portfolio.category == category)
        
        # Сортировка: сначала рекомендуемые, затем по порядку, затем по дате
        query = query.order_by(
            desc(Portfolio.is_featured),
            asc(Portfolio.sort_order),
            desc(Portfolio.created_at)
        )
        
        # Подсчитываем общее количество
        total = query.count()
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        projects = query.offset(offset).limit(per_page).all()
        
        return {
            "success": True,
            "data": [project.to_bot_dict() for project in projects],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "has_next": offset + per_page < total
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения публичного списка портфолио: {e}")
        return {
            "success": False,
            "data": [],
            "pagination": {"page": 1, "per_page": per_page, "total": 0, "has_next": False}
        }

@router.get("/public/{project_id}")
async def get_public_portfolio_item(project_id: int, db: Session = Depends(get_db)):
    """Публичное API для получения конкретного проекта (для бота)"""
    try:
        project = db.query(Portfolio).filter(
            Portfolio.id == project_id,
            Portfolio.is_visible == True
        ).first()
        
        if not project:
            return {
                "success": False,
                "error": "Проект не найден"
            }
        
        # Увеличиваем счетчик просмотров
        project.views_count += 1
        db.commit()
        
        return {
            "success": True,
            "data": project.to_bot_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения публичного проекта {project_id}: {e}")
        return {
            "success": False,
            "error": "Ошибка получения проекта"
        }

@router.post("/public/{project_id}/like")
async def like_portfolio_item(project_id: int, db: Session = Depends(get_db)):
    """Публичное API для лайка проекта (для бота)"""
    try:
        project = db.query(Portfolio).filter(
            Portfolio.id == project_id,
            Portfolio.is_visible == True
        ).first()
        
        if not project:
            return {
                "success": False,
                "error": "Проект не найден"
            }
        
        project.likes_count += 1
        db.commit()
        
        return {
            "success": True,
            "likes_count": project.likes_count
        }
        
    except Exception as e:
        logger.error(f"Ошибка лайка проекта {project_id}: {e}")
        return {
            "success": False,
            "error": "Ошибка обработки лайка"
        }

@router.post("/{portfolio_id}/publish")
async def publish_to_telegram(
    portfolio_id: int,
    current_user: dict = Depends(check_portfolio_access),
    db: Session = Depends(get_db)
):
    """Опубликовать элемент портфолио в Telegram канал"""
    try:
        from ...services.portfolio_telegram_service import portfolio_telegram_service
        
        # Получаем элемент портфолио
        portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio_item:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Элемент портфолио не найден"}
            )
        
        # Проверяем, не опубликован ли уже
        if portfolio_item.is_published:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Элемент уже опубликован в канале"}
            )
        
        # Публикуем в Telegram канал
        result = await portfolio_telegram_service.publish_portfolio_item(portfolio_item, db)
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": "Элемент портфолио опубликован в Telegram канал",
                "message_id": result.get("message_id"),
                "channel_id": result.get("channel_id")
            })
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": result["error"]}
            )
        
    except Exception as e:
        logger.error(f"Ошибка публикации в Telegram: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Внутренняя ошибка сервера"}
        )

@router.put("/{portfolio_id}/update-published")
async def update_published_item(
    portfolio_id: int,
    current_user: dict = Depends(check_portfolio_access),
    db: Session = Depends(get_db)
):
    """Обновить уже опубликованный элемент портфолио в Telegram канале"""
    try:
        from ...services.portfolio_telegram_service import portfolio_telegram_service
        
        # Получаем элемент портфолио
        portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio_item:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Элемент портфолио не найден"}
            )
        
        # Обновляем в Telegram канале
        result = await portfolio_telegram_service.update_published_item(portfolio_item, db)
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": "Элемент портфолио обновлен в Telegram канале"
            })
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": result["error"]}
            )
        
    except Exception as e:
        logger.error(f"Ошибка обновления в Telegram: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Внутренняя ошибка сервера"}
        )

@router.delete("/{portfolio_id}/unpublish")
async def unpublish_from_telegram(
    portfolio_id: int,
    current_user: dict = Depends(check_portfolio_access),
    db: Session = Depends(get_db)
):
    """Удалить элемент портфолио из Telegram канала"""
    try:
        from ...services.portfolio_telegram_service import portfolio_telegram_service
        
        # Получаем элемент портфолио
        portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio_item:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Элемент портфолио не найден"}
            )
        
        # Удаляем из Telegram канала
        result = await portfolio_telegram_service.delete_published_item(portfolio_item, db)
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": "Элемент портфолио удален из Telegram канала"
            })
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": result["error"]}
            )
        
    except Exception as e:
        logger.error(f"Ошибка удаления из Telegram: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Внутренняя ошибка сервера"}
        )