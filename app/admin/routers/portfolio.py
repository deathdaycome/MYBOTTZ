# app/admin/routes/portfolio.py

import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from PIL import Image
import shutil

from ...database.database import get_db_context, get_db
from ...database.models import Portfolio
from ...config.settings import settings
from ...config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# Константы
UPLOAD_DIR = "uploads/portfolio"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
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
from sqlalchemy import and_, or_, desc, asc
from PIL import Image
import shutil
import secrets

from ...database.database import get_db_context, get_db
from ...database.models import Portfolio
from ...config.settings import settings
from ...config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# Базовая аутентификация
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """Проверка аутентификации"""
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

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

# =================== API ENDPOINTS ===================

@router.get("/", dependencies=[Depends(authenticate)])
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

@router.get("/categories", dependencies=[Depends(authenticate)])
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

@router.get("/{project_id}", dependencies=[Depends(authenticate)])
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

@router.post("/", dependencies=[Depends(authenticate)])
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
        
        logger.info(f"  title: {title}")
        logger.info(f"  subtitle: {subtitle}")
        logger.info(f"  description: {description[:100] if description else 'None'}...")
        logger.info(f"  category: {category}")
        logger.info(f"  technologies: {technologies}")
        logger.info(f"  complexity: {complexity}")
        logger.info(f"  complexity_level: {complexity_level}")
        logger.info(f"  development_time: {development_time}")
        logger.info(f"  cost: {cost}")
        logger.info(f"  is_featured: {is_featured}")
        logger.info(f"  is_visible: {is_visible}")
        logger.info(f"  show_cost: {show_cost}")
        
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
        logger.info(f"  title: {title}")
        logger.info(f"  subtitle: {subtitle}")
        logger.info(f"  description: {description[:100] if description else 'None'}...")
        logger.info(f"  category: {category}")
        logger.info(f"  technologies: {technologies}")
        logger.info(f"  complexity: {complexity}")
        logger.info(f"  main_image: {main_image.filename if main_image else 'None'}")
        
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

@router.put("/{project_id}", dependencies=[Depends(authenticate)])
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

@router.delete("/{project_id}", dependencies=[Depends(authenticate)])
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

@router.post("/upload-image", dependencies=[Depends(authenticate)])
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

@router.post("/reorder", dependencies=[Depends(authenticate)])
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

@router.get("/stats/overview", dependencies=[Depends(authenticate)])
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
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(400, f"Файл слишком большой. Максимум {MAX_FILE_SIZE/1024/1024}MB")
        
        # Проверяем расширение файла
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Неподдерживаемый формат файла: {file_ext}")
        
        # Генерируем уникальное имя файла
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Путь для сохранения
        save_path = os.path.join(UPLOAD_DIR, subfolder, unique_filename)
        
        # Сохраняем оригинальный файл
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Создаем миниатюру
        try:
            with Image.open(save_path) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Создаем миниатюру
                thumb_size = IMAGE_SIZES["thumb"]
                img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
                
                thumb_path = os.path.join(UPLOAD_DIR, "thumbs", unique_filename)
                img.save(thumb_path, "JPEG", quality=85)
                
                return {
                    "filename": unique_filename,
                    "path": save_path,
                    "thumb_path": thumb_path,
                    "relative_path": f"uploads/portfolio/{subfolder}/{unique_filename}",
                    "thumb_relative_path": f"uploads/portfolio/thumbs/{unique_filename}",
                    "size": file.size
                }
        except Exception as e:
            logger.error(f"Ошибка создания миниатюры: {e}")
            return {
                "filename": unique_filename,
                "path": save_path,
                "relative_path": f"uploads/portfolio/{subfolder}/{unique_filename}",
                "size": file.size
            }
            
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения: {e}")
        raise HTTPException(500, f"Ошибка загрузки файла: {str(e)}")

# API endpoints

@router.get("/")
async def get_portfolio_items(
    page: int = 1,
    limit: int = 10,
    category: Optional[str] = None,
    search: Optional[str] = None,
    is_featured: Optional[bool] = None,
    is_visible: Optional[bool] = None,
    sort_by: str = "sort_order",
    sort_order: str = "asc",
    username: str = Depends(authenticate)
):
    """Получить список портфолио с фильтрацией и пагинацией"""
    try:
        with get_db_context() as db:
            query = db.query(Portfolio)
            
            # Фильтры
            if category:
                query = query.filter(Portfolio.category == category)
            if search:
                query = query.filter(
                    or_(
                        Portfolio.title.ilike(f"%{search}%"),
                        Portfolio.description.ilike(f"%{search}%"),
                        Portfolio.technologies.ilike(f"%{search}%"),
                        Portfolio.tags.ilike(f"%{search}%")
                    )
                )
            if is_featured is not None:
                query = query.filter(Portfolio.is_featured == is_featured)
            if is_visible is not None:
                query = query.filter(Portfolio.is_visible == is_visible)
            
            # Сортировка
            if sort_by == "sort_order":
                query = query.order_by(asc(Portfolio.sort_order) if sort_order == "asc" else desc(Portfolio.sort_order))
            elif sort_by == "created_at":
                query = query.order_by(desc(Portfolio.created_at) if sort_order == "desc" else asc(Portfolio.created_at))
            elif sort_by == "views_count":
                query = query.order_by(desc(Portfolio.views_count) if sort_order == "desc" else asc(Portfolio.views_count))
            elif sort_by == "likes_count":
                query = query.order_by(desc(Portfolio.likes_count) if sort_order == "desc" else asc(Portfolio.likes_count))
            
            # Пагинация
            total = query.count()
            offset = (page - 1) * limit
            items = query.offset(offset).limit(limit).all()
            
            # Преобразуем в словари В РАМКАХ СЕССИИ
            portfolio_items = []
            for item in items:
                portfolio_items.append(item.to_dict())
            
            return {
                "items": portfolio_items,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения портфолио: {e}")
        raise HTTPException(500, f"Ошибка получения портфолио: {str(e)}")

@router.get("/{item_id}")
async def get_portfolio_item(item_id: int, username: str = Depends(authenticate)):
    """Получить конкретный элемент портфолио"""
    try:
        with get_db_context() as db:
            item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not item:
                raise HTTPException(404, "Элемент портфолио не найден")
            
            return item.to_dict()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения элемента портфолио: {e}")
        raise HTTPException(500, f"Ошибка получения элемента: {str(e)}")

@router.post("/")
async def create_portfolio_item(
    title: str = Form(...),
    subtitle: str = Form(None),
    description: str = Form(...),
    category: str = Form(...),
    technologies: str = Form(None),
    complexity: str = Form("medium"),
    complexity_level: int = Form(5),
    development_time: int = Form(None),
    cost: float = Form(None),
    cost_range: str = Form(None),
    show_cost: bool = Form(False),
    demo_link: str = Form(None),
    repository_link: str = Form(None),
    external_links: str = Form("[]"),
    is_featured: bool = Form(False),
    is_visible: bool = Form(True),
    sort_order: int = Form(0),
    tags: str = Form(None),
    client_name: str = Form(None),
    project_status: str = Form("completed"),
    completed_at: str = Form(None),
    main_image: UploadFile = File(None),
    additional_images: List[UploadFile] = File(None),
    username: str = Depends(authenticate)
):
    """Создать новый элемент портфолио"""
    try:
        with get_db_context() as db:
            # Обрабатываем основное изображение
            main_image_path = None
            if main_image and main_image.size > 0:
                image_result = save_uploaded_image(main_image, "main")
                main_image_path = image_result["relative_path"]
            
            # Обрабатываем дополнительные изображения
            additional_image_paths = []
            if additional_images:
                for img in additional_images:
                    if img.size > 0:
                        image_result = save_uploaded_image(img, "additional")
                        additional_image_paths.append(image_result["relative_path"])
            
            # Парсим JSON поля
            try:
                external_links_list = json.loads(external_links) if external_links else []
            except:
                external_links_list = []
                
            # Парсим дату
            completed_at_date = None
            if completed_at:
                try:
                    completed_at_date = datetime.fromisoformat(completed_at)
                except:
                    pass
            
            # Создаем новый элемент
            new_item = Portfolio(
                title=title,
                subtitle=subtitle,
                description=description,
                category=category,
                main_image=main_image_path,
                image_paths=additional_image_paths,
                technologies=technologies,
                complexity=complexity,
                complexity_level=complexity_level,
                development_time=development_time,
                cost=cost,
                cost_range=cost_range,
                show_cost=show_cost,
                demo_link=demo_link,
                repository_link=repository_link,
                external_links=external_links_list,
                is_featured=is_featured,
                is_visible=is_visible,
                sort_order=sort_order,
                tags=tags,
                client_name=client_name,
                project_status=project_status,
                completed_at=completed_at_date,
                created_by=1  # TODO: получать ID администратора из сессии
            )
            
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            
            return new_item.to_dict()
            
    except Exception as e:
        logger.error(f"Ошибка создания элемента портфолио: {e}")
        raise HTTPException(500, f"Ошибка создания элемента: {str(e)}")

@router.put("/{item_id}")
async def update_portfolio_item(
    item_id: int,
    title: str = Form(...),
    subtitle: str = Form(None),
    description: str = Form(...),
    category: str = Form(...),
    technologies: str = Form(None),
    complexity: str = Form("medium"),
    complexity_level: int = Form(5),
    development_time: int = Form(None),
    cost: float = Form(None),
    cost_range: str = Form(None),
    show_cost: bool = Form(False),
    demo_link: str = Form(None),
    repository_link: str = Form(None),
    external_links: str = Form("[]"),
    is_featured: bool = Form(False),
    is_visible: bool = Form(True),
    sort_order: int = Form(0),
    tags: str = Form(None),
    client_name: str = Form(None),
    project_status: str = Form("completed"),
    completed_at: str = Form(None),
    main_image: UploadFile = File(None),
    additional_images: List[UploadFile] = File(None),
    remove_images: str = Form("[]"),
    username: str = Depends(authenticate)
):
    """Обновить элемент портфолио"""
    try:
        with get_db_context() as db:
            item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not item:
                raise HTTPException(404, "Элемент портфолио не найден")
            
            # Обрабатываем основное изображение
            if main_image and main_image.size > 0:
                # Удаляем старое изображение
                if item.main_image:
                    old_path = item.main_image.replace("uploads/", "")
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                image_result = save_uploaded_image(main_image, "main")
                item.main_image = image_result["relative_path"]
            
            # Обрабатываем дополнительные изображения
            if additional_images:
                for img in additional_images:
                    if img.size > 0:
                        image_result = save_uploaded_image(img, "additional")
                        if not item.image_paths:
                            item.image_paths = []
                        item.image_paths.append(image_result["relative_path"])
            
            # Удаляем изображения если нужно
            try:
                remove_images_list = json.loads(remove_images) if remove_images else []
                if remove_images_list and item.image_paths:
                    for img_path in remove_images_list:
                        if img_path in item.image_paths:
                            item.image_paths.remove(img_path)
                            # Удаляем файл
                            file_path = img_path.replace("uploads/", "")
                            if os.path.exists(file_path):
                                os.remove(file_path)
            except:
                pass
            
            # Обновляем остальные поля
            item.title = title
            item.subtitle = subtitle
            item.description = description
            item.category = category
            item.technologies = technologies
            item.complexity = complexity
            item.complexity_level = complexity_level
            item.development_time = development_time
            item.cost = cost
            item.cost_range = cost_range
            item.show_cost = show_cost
            item.demo_link = demo_link
            item.repository_link = repository_link
            item.is_featured = is_featured
            item.is_visible = is_visible
            item.sort_order = sort_order
            item.tags = tags
            item.client_name = client_name
            item.project_status = project_status
            
            # Парсим JSON поля
            try:
                item.external_links = json.loads(external_links) if external_links else []
            except:
                item.external_links = []
                
            # Парсим дату
            if completed_at:
                try:
                    item.completed_at = datetime.fromisoformat(completed_at)
                except:
                    pass
            
            db.commit()
            db.refresh(item)
            
            return item.to_dict()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления элемента портфолио: {e}")
        raise HTTPException(500, f"Ошибка обновления элемента: {str(e)}")

@router.delete("/{item_id}")
async def delete_portfolio_item(item_id: int, username: str = Depends(authenticate)):
    """Удалить элемент портфолио"""
    try:
        with get_db_context() as db:
            item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not item:
                raise HTTPException(404, "Элемент портфолио не найден")
            
            # Удаляем связанные файлы
            if item.main_image:
                file_path = item.main_image.replace("uploads/", "")
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            if item.image_paths:
                for img_path in item.image_paths:
                    file_path = img_path.replace("uploads/", "")
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            db.delete(item)
            db.commit()
            
            return {"message": "Элемент портфолио успешно удален"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления элемента портфолио: {e}")
        raise HTTPException(500, f"Ошибка удаления элемента: {str(e)}")

@router.post("/{item_id}/like")
async def like_portfolio_item(item_id: int):
    """Поставить лайк элементу портфолио (публичный эндпоинт)"""
    try:
        with get_db_context() as db:
            item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not item:
                raise HTTPException(404, "Элемент портфолио не найден")
            
            item.increment_likes()
            db.commit()
            
            return {"message": "Лайк добавлен", "likes_count": item.likes_count}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка добавления лайка: {e}")
        raise HTTPException(500, f"Ошибка добавления лайка: {str(e)}")

@router.post("/{item_id}/view")
async def view_portfolio_item(item_id: int):
    """Увеличить счетчик просмотров (публичный эндпоинт)"""
    try:
        with get_db_context() as db:
            item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not item:
                raise HTTPException(404, "Элемент портфолио не найден")
            
            item.increment_views()
            db.commit()
            
            return {"message": "Просмотр засчитан", "views_count": item.views_count}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка увеличения просмотров: {e}")
        raise HTTPException(500, f"Ошибка увеличения просмотров: {str(e)}")

@router.post("/reorder")
async def reorder_portfolio_items(
    items_order: List[dict],
    username: str = Depends(authenticate)
):
    """Изменить порядок элементов портфолио"""
    try:
        with get_db_context() as db:
            for item_data in items_order:
                item_id = item_data.get("id")
                sort_order = item_data.get("sort_order")
                
                if item_id and sort_order is not None:
                    item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
                    if item:
                        item.sort_order = sort_order
            
            db.commit()
            
            return {"message": "Порядок элементов обновлен"}
            
    except Exception as e:
        logger.error(f"Ошибка изменения порядка: {e}")
        raise HTTPException(500, f"Ошибка изменения порядка: {str(e)}")

@router.get("/categories/stats")
async def get_categories_stats(username: str = Depends(authenticate)):
    """Получить статистику по категориям"""
    try:
        with get_db_context() as db:
            items = db.query(Portfolio).all()
            
            stats = {}
            for item in items:
                category = item.category
                if category not in stats:
                    stats[category] = {
                        "count": 0,
                        "visible_count": 0,
                        "featured_count": 0,
                        "total_views": 0,
                        "total_likes": 0
                    }
                
                stats[category]["count"] += 1
                if item.is_visible:
                    stats[category]["visible_count"] += 1
                if item.is_featured:
                    stats[category]["featured_count"] += 1
                stats[category]["total_views"] += item.views_count
                stats[category]["total_likes"] += item.likes_count
            
            return stats
            
    except Exception as e:
        logger.error(f"Ошибка получения статистики категорий: {e}")
        raise HTTPException(500, f"Ошибка получения статистики: {str(e)}")

@router.post("/upload-image")
async def upload_single_image(
    image: UploadFile = File(...),
    subfolder: str = Form("additional"),
    username: str = Depends(authenticate)
):
    """Загрузить одно изображение"""
    try:
        if image.size == 0:
            raise HTTPException(400, "Пустой файл")
        
        result = save_uploaded_image(image, subfolder)
        
        return {
            "filename": result["filename"],
            "path": result["relative_path"],
            "thumb_path": result.get("thumb_relative_path"),
            "size": result["size"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения: {e}")
        raise HTTPException(500, f"Ошибка загрузки изображения: {str(e)}")

# Публичные эндпоинты для бота
@router.get("/public/categories")
async def get_public_categories():
    """Получить список категорий для бота"""
    try:
        with get_db_context() as db:
            categories = db.query(Portfolio.category).filter(
                Portfolio.is_visible == True
            ).distinct().all()
            
            category_list = [cat[0] for cat in categories]
            
            # Словарь для красивых названий
            category_names = {
                "telegram_bots": "🤖 Telegram боты",
                "web_development": "🌐 Веб-разработка", 
                "mobile_apps": "📱 Мобильные приложения",
                "ai_integration": "🧠 AI интеграции",
                "automation": "⚙️ Автоматизация",
                "ecommerce": "🛒 E-commerce",
                "other": "🔧 Другое"
            }
            
            return {
                "categories": [
                    {"id": cat, "name": category_names.get(cat, cat)}
                    for cat in category_list
                ]
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения категорий: {e}")
        raise HTTPException(500, f"Ошибка получения категорий: {str(e)}")

@router.get("/public/category/{category}")
async def get_public_portfolio_by_category(category: str, page: int = 1, limit: int = 5):
    """Получить портфолио для бота по категории"""
    try:
        with get_db_context() as db:
            query = db.query(Portfolio).filter(
                and_(
                    Portfolio.category == category,
                    Portfolio.is_visible == True
                )
            ).order_by(
                desc(Portfolio.is_featured),
                asc(Portfolio.sort_order),
                desc(Portfolio.created_at)
            )
            
            total = query.count()
            offset = (page - 1) * limit
            items = query.offset(offset).limit(limit).all()
            
            # Увеличиваем счетчики просмотров
            for item in items:
                item.increment_views()
            
            db.commit()
            
            # Преобразуем для бота
            portfolio_items = []
            for item in items:
                portfolio_items.append(item.to_bot_dict())
            
            return {
                "items": portfolio_items,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения портфолио по категории: {e}")
        raise HTTPException(500, f"Ошибка получения портфолио: {str(e)}")

@router.get("/public/featured")
async def get_public_featured_portfolio(limit: int = 3):
    """Получить рекомендуемые работы для бота"""
    try:
        with get_db_context() as db:
            items = db.query(Portfolio).filter(
                and_(
                    Portfolio.is_featured == True,
                    Portfolio.is_visible == True
                )
            ).order_by(
                asc(Portfolio.sort_order),
                desc(Portfolio.views_count)
            ).limit(limit).all()
            
            # Увеличиваем счетчики просмотров
            for item in items:
                item.increment_views()
            
            db.commit()
            
            # Преобразуем для бота
            portfolio_items = []
            for item in items:
                portfolio_items.append(item.to_bot_dict())
            
            return {
                "items": portfolio_items,
                "total": len(portfolio_items)
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения рекомендуемых работ: {e}")
        raise HTTPException(500, f"Ошибка получения рекомендуемых работ: {str(e)}")

@router.get("/public/{item_id}")
async def get_public_portfolio_item(item_id: int):
    """Получить конкретный элемент портфолио для бота"""
    try:
        with get_db_context() as db:
            item = db.query(Portfolio).filter(
                and_(
                    Portfolio.id == item_id,
                    Portfolio.is_visible == True
                )
            ).first()
            
            if not item:
                raise HTTPException(404, "Элемент портфолио не найден")
            
            # Увеличиваем счетчик просмотров
            item.increment_views()
            db.commit()
            
            return item.to_bot_dict()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения элемента портфолио: {e}")
        raise HTTPException(500, f"Ошибка получения элемента: {str(e)}")
        # Определяем пути
        file_path = os.path.join(UPLOAD_DIR, subfolder, unique_filename)
        thumb_path = os.path.join(UPLOAD_DIR, "thumbs", unique_filename)
        
        # Сохраняем оригинал
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Создаем миниатюру
        with Image.open(file_path) as img:
            # Основное изображение (ресайз)
            if subfolder == "main":
                img.thumbnail(IMAGE_SIZES["main"], Image.Resampling.LANCZOS)
                img.save(file_path, optimize=True, quality=85)
            
            # Миниатюра
            img.thumbnail(IMAGE_SIZES["thumb"], Image.Resampling.LANCZOS)
            img.save(thumb_path, optimize=True, quality=80)
        
        return {
            "filename": unique_filename,
            "path": f"/uploads/portfolio/{subfolder}/{unique_filename}",
            "thumb_path": f"/uploads/portfolio/thumbs/{unique_filename}",
            "size": os.path.getsize(file_path)
        }
    
    except Exception as e:
        logger.error(f"Ошибка сохранения изображения: {e}")
        raise HTTPException(500, f"Ошибка сохранения изображения: {str(e)}")

@router.get("")
async def get_portfolio_list(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    visible: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    """Получить список портфолио с фильтрами и пагинацией"""
    try:
        # Строим запрос
        query = db.query(Portfolio)
        
        # Применяем фильтры
        if search:
            search_filter = or_(
                Portfolio.title.ilike(f"%{search}%"),
                Portfolio.description.ilike(f"%{search}%"),
                Portfolio.technologies.ilike(f"%{search}%"),
                Portfolio.tags.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if category:
            query = query.filter(Portfolio.category == category)
        
        if featured is not None:
            query = query.filter(Portfolio.is_featured == featured)
            
        if visible is not None:
            query = query.filter(Portfolio.is_visible == visible)
        
        # Применяем сортировку
        sort_column = getattr(Portfolio, sort_by, Portfolio.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Добавляем сортировку по sort_order как вторичную
        query = query.order_by(asc(Portfolio.sort_order))
        
        # Получаем общее количество
        total = query.count()
        
        # Применяем пагинацию
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()
        
        # Статистика
        stats = {
            "total": db.query(Portfolio).count(),
            "featured": db.query(Portfolio).filter(Portfolio.is_featured == True).count(),
            "visible": db.query(Portfolio).filter(Portfolio.is_visible == True).count(),
            "total_views": db.query(Portfolio).with_entities(
                func.sum(Portfolio.views_count)
            ).scalar() or 0,
            "total_likes": db.query(Portfolio).with_entities(
                func.sum(Portfolio.likes_count)
            ).scalar() or 0
        }
        
        return {
            "success": True,
            "items": [item.to_dict() for item in items],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения списка портфолио: {e}")
        return {"success": False, "error": str(e)}

@router.get("/{portfolio_id}")
async def get_portfolio_item(portfolio_id: int, db: Session = Depends(get_db)):
    """Получить конкретный элемент портфолио"""
    try:
        item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not item:
            raise HTTPException(404, "Проект не найден")
        
        return {
            "success": True,
            "item": item.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения проекта {portfolio_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("")
async def create_portfolio_item(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    subtitle: Optional[str] = Form(None),
    technologies: Optional[str] = Form(None),
    complexity: str = Form("medium"),
    development_time: Optional[int] = Form(None),
    cost: Optional[float] = Form(None),
    cost_range: Optional[str] = Form(None),
    show_cost: bool = Form(False),
    demo_link: Optional[str] = Form(None),
    repository_link: Optional[str] = Form(None),
    is_featured: bool = Form(False),
    is_visible: bool = Form(True),
    sort_order: int = Form(0),
    tags: Optional[str] = Form(None),
    client_name: Optional[str] = Form(None),
    project_status: str = Form("completed"),
    completed_at: Optional[str] = Form(None),
    main_image: Optional[UploadFile] = File(None),
    additional_images: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    """Создать новый элемент портфолио"""
    try:
        # Обработка основного изображения
        main_image_data = None
        if main_image and main_image.filename:
            main_image_data = save_uploaded_image(main_image, "main")
        
        # Обработка дополнительных изображений
        additional_image_paths = []
        for img in additional_images:
            if img.filename:
                img_data = save_uploaded_image(img, "additional")
                additional_image_paths.append(img_data["path"])
        
        # Парсинг даты завершения
        completed_date = None
        if completed_at:
            try:
                completed_date = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            except:
                pass
        
        # Создание записи
        portfolio_item = Portfolio(
            title=title,
            subtitle=subtitle,
            description=description,
            category=category,
            main_image=main_image_data["path"] if main_image_data else None,
            image_paths=additional_image_paths,
            technologies=technologies,
            complexity=complexity,
            development_time=development_time,
            cost=cost,
            cost_range=cost_range,
            show_cost=show_cost,
            demo_link=demo_link,
            repository_link=repository_link,
            is_featured=is_featured,
            is_visible=is_visible,
            sort_order=sort_order,
            tags=tags,
            client_name=client_name,
            project_status=project_status,
            completed_at=completed_date
        )
        
        db.add(portfolio_item)
        db.commit()
        db.refresh(portfolio_item)
        
        logger.info(f"Создан новый проект портфолио: {portfolio_item.title} (ID: {portfolio_item.id})")
        
        return {
            "success": True,
            "message": "Проект успешно создан",
            "item": portfolio_item.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка создания проекта: {e}")
        return {"success": False, "error": str(e)}

@router.put("/{portfolio_id}")
async def update_portfolio_item(
    portfolio_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    subtitle: Optional[str] = Form(None),
    technologies: Optional[str] = Form(None),
    complexity: str = Form("medium"),
    development_time: Optional[int] = Form(None),
    cost: Optional[float] = Form(None),
    cost_range: Optional[str] = Form(None),
    show_cost: bool = Form(False),
    demo_link: Optional[str] = Form(None),
    repository_link: Optional[str] = Form(None),
    is_featured: bool = Form(False),
    is_visible: bool = Form(True),
    sort_order: int = Form(0),
    tags: Optional[str] = Form(None),
    client_name: Optional[str] = Form(None),
    project_status: str = Form("completed"),
    completed_at: Optional[str] = Form(None),
    main_image: Optional[UploadFile] = File(None),
    additional_images: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    """Обновить элемент портфолио"""
    try:
        # Получаем существующий элемент
        portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio_item:
            raise HTTPException(404, "Проект не найден")
        
        # Обработка основного изображения
        if main_image and main_image.filename:
            # Удаляем старое изображение если есть
            if portfolio_item.main_image:
                old_path = portfolio_item.main_image.replace('/uploads/', 'uploads/')
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            main_image_data = save_uploaded_image(main_image, "main")
            portfolio_item.main_image = main_image_data["path"]
        
        # Обработка дополнительных изображений
        if additional_images and any(img.filename for img in additional_images):
            # Удаляем старые дополнительные изображения
            for old_path in portfolio_item.image_paths or []:
                old_file_path = old_path.replace('/uploads/', 'uploads/')
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Добавляем новые
            additional_image_paths = []
            for img in additional_images:
                if img.filename:
                    img_data = save_uploaded_image(img, "additional")
                    additional_image_paths.append(img_data["path"])
            
            portfolio_item.image_paths = additional_image_paths
        
        # Парсинг даты завершения
        if completed_at:
            try:
                portfolio_item.completed_at = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            except:
                pass
        
        # Обновление остальных полей
        portfolio_item.title = title
        portfolio_item.subtitle = subtitle
        portfolio_item.description = description
        portfolio_item.category = category
        portfolio_item.technologies = technologies
        portfolio_item.complexity = complexity
        portfolio_item.development_time = development_time
        portfolio_item.cost = cost
        portfolio_item.cost_range = cost_range
        portfolio_item.show_cost = show_cost
        portfolio_item.demo_link = demo_link
        portfolio_item.repository_link = repository_link
        portfolio_item.is_featured = is_featured
        portfolio_item.is_visible = is_visible
        portfolio_item.sort_order = sort_order
        portfolio_item.tags = tags
        portfolio_item.client_name = client_name
        portfolio_item.project_status = project_status
        portfolio_item.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Обновлен проект портфолио: {portfolio_item.title} (ID: {portfolio_item.id})")
        
        return {
            "success": True,
            "message": "Проект успешно обновлен",
            "item": portfolio_item.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка обновления проекта {portfolio_id}: {e}")
        return {"success": False, "error": str(e)}

@router.delete("/{portfolio_id}")
async def delete_portfolio_item(portfolio_id: int, db: Session = Depends(get_db)):
    """Удалить элемент портфолио"""
    try:
        portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio_item:
            raise HTTPException(404, "Проект не найден")
        
        # Удаляем файлы изображений
        if portfolio_item.main_image:
            main_file_path = portfolio_item.main_image.replace('/uploads/', 'uploads/')
            if os.path.exists(main_file_path):
                os.remove(main_file_path)
            
            # Удаляем миниатюру
            thumb_path = main_file_path.replace('/main/', '/thumbs/')
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        
        # Удаляем дополнительные изображения
        for img_path in portfolio_item.image_paths or []:
            file_path = img_path.replace('/uploads/', 'uploads/')
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Удаляем миниатюру
            thumb_path = file_path.replace('/additional/', '/thumbs/')
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        
        # Удаляем запись из БД
        db.delete(portfolio_item)
        db.commit()
        
        logger.info(f"Удален проект портфолио: {portfolio_item.title} (ID: {portfolio_id})")
        
        return {
            "success": True,
            "message": "Проект успешно удален"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка удаления проекта {portfolio_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/reorder")
async def reorder_portfolio(
    request: Request,
    db: Session = Depends(get_db)
):
    """Изменить порядок элементов портфолио"""
    try:
        data = await request.json()
        order_data = data.get("order", [])
        
        for item_order in order_data:
            portfolio_id = item_order.get("id")
            new_order = item_order.get("order")
            
            portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if portfolio_item:
                portfolio_item.sort_order = new_order
        
        db.commit()
        
        return {
            "success": True,
            "message": "Порядок успешно обновлен"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка изменения порядка: {e}")
        return {"success": False, "error": str(e)}

@router.post("/import")
async def import_portfolio(
    request: Request,
    db: Session = Depends(get_db)
):
    """Импорт портфолио из JSON"""
    try:
        data = await request.json()
        items = data.get("items", [])
        
        imported_count = 0
        
        for item_data in items:
            try:
                portfolio_item = Portfolio(
                    title=item_data.get("title"),
                    subtitle=item_data.get("subtitle"),
                    description=item_data.get("description"),
                    category=item_data.get("category"),
                    technologies=item_data.get("technologies"),
                    complexity=item_data.get("complexity", "medium"),
                    development_time=item_data.get("development_time"),
                    cost=item_data.get("cost"),
                    cost_range=item_data.get("cost_range"),
                    show_cost=item_data.get("show_cost", False),
                    demo_link=item_data.get("demo_link"),
                    is_featured=item_data.get("featured", False),
                    is_visible=item_data.get("active", True),
                    sort_order=item_data.get("order", 0),
                    tags=item_data.get("tags")
                )
                
                db.add(portfolio_item)
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Ошибка импорта элемента: {e}")
                continue
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Импортировано {imported_count} проектов",
            "imported": imported_count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка импорта: {e}")
        return {"success": False, "error": str(e)}

@router.get("/categories/list")
async def get_categories():
    """Получить список доступных категорий"""
    categories = {
        "telegram_bots": "Telegram боты",
        "web_development": "Веб-разработка", 
        "mobile_apps": "Мобильные приложения",
        "ai_integration": "AI интеграции",
        "automation": "Автоматизация",
        "ecommerce": "E-commerce",
        "other": "Другое"
    }
    
    return {
        "success": True,
        "categories": categories
    }

@router.post("/{portfolio_id}/increment-views")
async def increment_portfolio_views(portfolio_id: int, db: Session = Depends(get_db)):
    """Увеличить счетчик просмотров"""
    try:
        portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if portfolio_item:
            portfolio_item.increment_views()
            db.commit()
            
            return {"success": True, "views": portfolio_item.views_count}
        
        return {"success": False, "error": "Проект не найден"}
        
    except Exception as e:
        logger.error(f"Ошибка увеличения просмотров: {e}")
        return {"success": False, "error": str(e)}

@router.post("/{portfolio_id}/increment-likes")
async def increment_portfolio_likes(portfolio_id: int, db: Session = Depends(get_db)):
    """Увеличить счетчик лайков"""
    try:
        portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if portfolio_item:
            portfolio_item.increment_likes()
            db.commit()
            
            return {"success": True, "likes": portfolio_item.likes_count}
        
        return {"success": False, "error": "Проект не найден"}
        
    except Exception as e:
        logger.error(f"Ошибка увеличения лайков: {e}")
        return {"success": False, "error": str(e)}