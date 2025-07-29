from fastapi import FastAPI, HTTPException, Depends, Request, Form, APIRouter, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from datetime import datetime
import secrets
from typing import Optional, Dict, Any, List
import json
import os

from ..config.settings import settings
from ..config.logging import get_logger
from ..database.database import get_db_context
from ..database.models import User, Project, ConsultantSession, Portfolio, Settings as DBSettings, AdminUser, ProjectFile
from ..services.analytics_service import analytics_service, get_dashboard_data
from ..services.auth_service import AuthService
from .middleware.roles import RoleMiddleware

# Импорт роутера портфолио
try:
    from .routers.portfolio import router as portfolio_router
except ImportError:
    portfolio_router = None

# Импорт роутера проектов
try:
    from .routers.projects import router as projects_router
    print("Используется основной роутер проектов")
except ImportError as e:
    print(f"Ошибка импорта роутера проектов: {e}")
    projects_router = None

# Импорт роутера пользователей
try:
    from .routers.users import router as users_router
    print("Роутер пользователей подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера пользователей: {e}")
    users_router = None

# Импорт роутера файлов
try:
    from .routers.files import router as files_router
    print("Роутер файлов подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера файлов: {e}")
    files_router = None

# Импорт роутера задач
try:
    from .routers.tasks import router as tasks_router
    print("Роутер задач подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера задач: {e}")
    tasks_router = None

# Импорт роутера статусов проектов
try:
    from .routers.project_statuses import router as project_statuses_router
    print("Роутер статусов проектов подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера статусов проектов: {e}")
    project_statuses_router = None

# Импорт роутера финансов
try:
    from .routers.finance import router as finance_router
    print("Роутер финансов подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера финансов: {e}")
    finance_router = None

# Импорт роутера настроек
try:
    from .routers.settings_simple import router as settings_router
    print("Роутер настроек подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера настроек: {e}")
    settings_router = None

# Импорт роутера исполнителей
try:
    from .routers.contractors import router as contractors_router
    print("Роутер исполнителей подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера исполнителей: {e}")
    contractors_router = None

# Импорт роутера сервисов
try:
    from .routers.services import router as services_router
    print("Роутер сервисов подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера сервисов: {e}")
    services_router = None

# Импорт роутера правок
try:
    from .routers.revisions import router as revisions_router
    print("Роутер правок подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера правок: {e}")
    revisions_router = None

logger = get_logger(__name__)

# Создаем роутер для админки
admin_router = APIRouter()

# Подключаем роутер портфолио
if portfolio_router:
    admin_router.include_router(portfolio_router)

# Подключаем роутер проектов
if projects_router:
    admin_router.include_router(projects_router, prefix="/api/projects")

# Подключаем роутер пользователей
if users_router:
    admin_router.include_router(users_router, prefix="/api/users")

# Подключаем роутер файлов
if files_router:
    admin_router.include_router(files_router, prefix="/api/files")

# Подключаем роутер задач
if tasks_router:
    admin_router.include_router(tasks_router, prefix="/tasks")

# Подключаем роутер статусов проектов
if project_statuses_router:
    admin_router.include_router(project_statuses_router, prefix="/api/project-statuses")

# Подключаем роутер финансов
if finance_router:
    admin_router.include_router(finance_router, prefix="/api/finance")

# Подключаем роутер настроек
if settings_router:
    admin_router.include_router(settings_router)

# Подключаем роутер исполнителей
if contractors_router:
    admin_router.include_router(contractors_router, prefix="/api/contractors")

# Подключаем роутер сервисов
if services_router:
    admin_router.include_router(services_router)

# Подключаем роутер правок
if revisions_router:
    admin_router.include_router(revisions_router)

# Настройка шаблонов
templates = Jinja2Templates(directory="app/admin/templates")

# Базовая аутентификация
security = HTTPBasic()

def get_user_role(username: str) -> str:
    """Определение роли пользователя"""
    if username == settings.ADMIN_USERNAME:
        return "owner"
    else:
        # Проверяем в базе данных
        with get_db_context() as db:
            admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
            if admin_user:
                return admin_user.role
        return "executor"

def get_current_user(username: str):
    """Получение текущего пользователя"""
    if username == settings.ADMIN_USERNAME:
        return {"username": username, "role": "owner", "id": 1}
    else:
        with get_db_context() as db:
            admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
            if admin_user:
                return {
                    "username": admin_user.username,
                    "role": admin_user.role,
                    "id": admin_user.id,
                    "first_name": admin_user.first_name,
                    "last_name": admin_user.last_name,
                    "email": admin_user.email
                }
        return None

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """Проверка аутентификации с поддержкой обеих систем"""
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


@admin_router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(authenticate)):
    """Главная страница админ-панели"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        if user_role == "executor":
            # Перенаправляем исполнителя на специальную страницу
            return templates.TemplateResponse("executor_dashboard.html", {
                "request": request,
                "username": username,
                "user_role": user_role,
                "navigation_items": navigation_items
            })
        
        # Получаем статистику используя правильную функцию
        from ..services.analytics_service import get_dashboard_data
        stats = get_dashboard_data(7)
        
        # Получаем последние проекты и пользователей в отдельных сессиях
        with get_db_context() as db:
            recent_projects_raw = db.query(Project).order_by(
                Project.created_at.desc()
            ).limit(5).all()
            
            # Конвертируем в словари сразу в сессии
            recent_projects = []
            for p in recent_projects_raw:
                # Получаем пользователя для каждого проекта
                user = db.query(User).filter(User.id == p.user_id).first()
                project_dict = {
                    'id': p.id,
                    'title': p.title,
                    'status': p.status,
                    'estimated_cost': p.estimated_cost or 0,
                    'created_at': p.created_at.isoformat() if p.created_at else None,
                    'complexity': p.complexity,
                    'user': {
                        'first_name': user.first_name if user else 'Неизвестно',
                        'username': user.username if user else None
                    }
                }
                recent_projects.append(project_dict)
        
        with get_db_context() as db:
            recent_users_raw = db.query(User).order_by(
                User.registration_date.desc()
            ).limit(5).all()
            
            # Конвертируем в словари сразу в сессии
            recent_users = []
            for u in recent_users_raw:
                # Считаем проекты пользователя
                projects_count = db.query(Project).filter(Project.user_id == u.id).count()
                user_dict = {
                    'id': u.id,
                    'telegram_id': u.telegram_id,
                    'username': u.username,
                    'first_name': u.first_name,
                    'registration_date': u.registration_date.isoformat() if u.registration_date else None,
                    'last_activity': u.last_activity.isoformat() if u.last_activity else None,
                    'projects_count': projects_count
                }
                recent_users.append(user_dict)
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "stats": stats,
            "recent_projects": recent_projects,
            "recent_users": recent_users
        })
        
    except Exception as e:
        logger.error(f"Ошибка в dashboard: {e}")
        
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        # Возвращаем пустую статистику при ошибке
        empty_stats = {
            'user_stats': {
                'total_users': 0,
                'new_users': 0,
                'active_users': 0,
                'conversion_rate': 0
            },
            'project_stats': {
                'total_projects': 0,
                'new_projects': 0,
                'completed_projects': 0,
                'completion_rate': 0,
                'status_distribution': {
                    'new': 0,
                    'in_progress': 0,
                    'completed': 0,
                    'cancelled': 0
                }
            },
            'consultant_stats': {
                'total_sessions': 0,
                'new_sessions': 0,
                'total_queries': 0,
                'avg_rating': 0
            },
            'financial_stats': {
                'total_revenue': 0,
                'potential_revenue': 0,
                'avg_check': 0
            }
        }
        
        template_name = "executor_dashboard.html" if user_role == "executor" else "dashboard.html"
        
        return templates.TemplateResponse(template_name, {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "stats": empty_stats,
            "recent_projects": [],
            "recent_users": [],
            "error": "Ошибка загрузки данных"
        })

@admin_router.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request, username: str = Depends(authenticate)):
    """Страница управления проектами"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        projects = []
        with get_db_context() as db:
            # Базовый запрос с присоединением пользователя для избежания N+1
            query = db.query(Project).join(User, Project.user_id == User.id, isouter=True)

            # Получаем проекты в зависимости от роли
            if user_role == "owner":
                # Владелец видит все проекты
                projects_raw = query.order_by(Project.created_at.desc()).all()
            else:
                # Исполнитель видит только назначенные ему проекты
                admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
                if admin_user:
                    projects_raw = query.filter(
                        Project.assigned_executor_id == admin_user.id
                    ).order_by(Project.created_at.desc()).all()
                else:
                    projects_raw = []

            # Конвертируем в словари, добавляя информацию о пользователе
            for p in projects_raw:
                project_dict = p.to_dict()
                # Добавляем связанный объект пользователя
                project_dict['user'] = p.user.to_dict() if p.user else None
                
                # Для исполнителя скрываем полную стоимость
                if user_role == "executor":
                    project_dict["estimated_cost"] = p.executor_cost or 0
                
                projects.append(project_dict)
        
        # Добавляем функцию для расчета прогресса в контекст шаблона
        def calculate_progress(status):
            progress_map = {
                'new': 0,
                'review': 10,
                'accepted': 20,
                'in_progress': 50,
                'testing': 80,
                'completed': 100,
                'cancelled': 0,
                'on_hold': 30
            }
            return progress_map.get(status, 0)
        
        return templates.TemplateResponse("projects.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "projects": projects,
            "calculate_progress": calculate_progress
        })
        
    except Exception as e:
        logger.error(f"Ошибка в projects_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/projects/{project_id}/detail", response_class=HTMLResponse)
async def project_detail_page(request: Request, project_id: int, username: str = Depends(authenticate)):
    """Детальная страница проекта"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        with get_db_context() as db:
            # Получаем проект с присоединением пользователя и исполнителя
            project = db.query(Project)\
                .join(User, Project.user_id == User.id, isouter=True)\
                .outerjoin(AdminUser, Project.assigned_executor_id == AdminUser.id)\
                .filter(Project.id == project_id)\
                .first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Проект не найден")
            
            # Проверяем права доступа
            if user_role == "executor":
                admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
                if not admin_user or project.assigned_executor_id != admin_user.id:
                    raise HTTPException(status_code=403, detail="У вас нет доступа к этому проекту")
            
            # Рассчитываем прогресс выполнения
            progress_map = {
                'new': 0,
                'review': 10,
                'accepted': 20,
                'in_progress': 50,
                'testing': 80,
                'completed': 100,
                'cancelled': 0,
                'on_hold': 30
            }
            progress_percentage = progress_map.get(project.status, 0)
            
            # Рассчитываем финансовый прогресс
            financial_progress = 0
            if project.estimated_cost and project.estimated_cost > 0:
                financial_progress = min(100, (project.client_paid_total or 0) / project.estimated_cost * 100)
            
            return templates.TemplateResponse("project_detail.html", {
                "request": request,
                "username": username,
                "user_role": user_role,
                "navigation_items": navigation_items,
                "project": project,
                "progress_percentage": int(progress_percentage),
                "financial_progress": int(financial_progress)
            })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в project_detail_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/users", response_class=HTMLResponse)
@RoleMiddleware.require_role("owner")
async def users_page(request: Request, username: str = Depends(authenticate), current_user: dict = None):
    """Страница управления пользователями (только для владельца)"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        with get_db_context() as db:
            users_raw = db.query(User).order_by(
                User.registration_date.desc()
            ).all()
            
            # Конвертируем в словари В РАМКАХ СЕССИИ
            users = []
            for u in users_raw:
                try:
                    # Считаем проекты и консультации в сессии
                    projects_count = db.query(Project).filter(Project.user_id == u.id).count()
                    sessions_count = 0  # Временно убираем подсчет сессий
                    # sessions_count = db.query(ConsultantSession).filter(ConsultantSession.user_id == u.id).count()
                    
                    user_dict = {
                        'id': u.id,
                        'telegram_id': u.telegram_id,
                        'username': u.username,
                        'first_name': u.first_name,
                        'last_name': u.last_name,
                        'phone': u.phone,
                        'email': u.email,
                        'registration_date': u.registration_date.isoformat() if u.registration_date else None,
                        'last_activity': u.last_activity.isoformat() if u.last_activity else None,
                        'state': u.state,
                        'is_active': u.is_active,
                        'preferences': u.preferences or {},
                        'notes': u.notes,
                        'projects_count': projects_count,
                        'sessions_count': sessions_count
                    }
                    users.append(user_dict)
                except Exception as e:
                    logger.error(f"Ошибка обработки пользователя {u.id}: {e}")
                    continue
        
        return templates.TemplateResponse("users.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "users": users
        })
        
    except Exception as e:
        logger.error(f"Ошибка в users_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/contractors", response_class=HTMLResponse)
async def contractors_page(request: Request, username: str = Depends(authenticate)):
    """Страница управления исполнителями (только для владельца)"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        return templates.TemplateResponse("contractors.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items
        })
        
    except Exception as e:
        logger.error(f"Ошибка в contractors_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/analytics", response_class=HTMLResponse)
@RoleMiddleware.require_role("owner")
async def analytics_page(request: Request, username: str = Depends(authenticate), current_user: dict = None):
    """Страница аналитики (только для владельца)"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        # Получаем полный отчет
        full_report = analytics_service.generate_full_report(30)
        
        return templates.TemplateResponse("analytics.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "report": full_report
        })
        
    except Exception as e:
        logger.error(f"Ошибка в analytics_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/settings", response_class=HTMLResponse)
@RoleMiddleware.require_role("owner")
async def settings_page(request: Request, username: str = Depends(authenticate), current_user: dict = None):
    """Страница настроек (только для владельца)"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        with get_db_context() as db:
            settings_items_raw = db.query(DBSettings).order_by(
                DBSettings.key.asc()
            ).all()
            
            # Конвертируем в словари В РАМКАХ СЕССИИ
            settings_items = []
            for s in settings_items_raw:
                settings_items.append(s.to_dict())
        
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "settings": settings_items
        })
        
    except Exception as e:
        logger.error(f"Ошибка в settings_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/finance", response_class=HTMLResponse)
async def finance_page(request: Request, username: str = Depends(authenticate)):
    """Страница управления финансами"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        return templates.TemplateResponse("finance.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items
        })
        
    except Exception as e:
        logger.error(f"Ошибка в finance_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(request: Request, username: str = Depends(authenticate)):
    """Страница управления портфолио"""
    try:
        with get_db_context() as db:
            portfolio_items_raw = db.query(Portfolio).order_by(
                Portfolio.sort_order.asc(),
                Portfolio.created_at.desc()
            ).all()
            
            # Конвертируем в словари В РАМКАХ СЕССИИ
            portfolio_items = []
            for p in portfolio_items_raw:
                portfolio_items.append(p.to_dict())
        
        # Статистика по категориям
        category_stats = {}
        for item in portfolio_items:
            category = item.get('category', 'other')
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'visible': 0,
                    'featured': 0,
                    'total_views': 0,
                    'total_likes': 0
                }
            
            category_stats[category]['count'] += 1
            if item.get('is_visible'):
                category_stats[category]['visible'] += 1
            if item.get('is_featured'):
                category_stats[category]['featured'] += 1
            category_stats[category]['total_views'] += item.get('views_count', 0)
            category_stats[category]['total_likes'] += item.get('likes_count', 0)
        
        portfolio_stats = {
            'total': len(portfolio_items),
            'visible': len([p for p in portfolio_items if p.get('is_visible')]),
            'featured': len([p for p in portfolio_items if p.get('is_featured')]),
            'total_views': sum(p.get('views_count', 0) for p in portfolio_items),
            'total_likes': sum(p.get('likes_count', 0) for p in portfolio_items),
            'categories': category_stats
        }
        
        # Словарь для красивых названий категорий
        category_names = {
            "telegram_bots": "🤖 Telegram боты",
            "web_development": "🌐 Веб-разработка", 
            "mobile_apps": "📱 Мобильные приложения",
            "ai_integration": "🧠 AI интеграции",
            "automation": "⚙️ Автоматизация",
            "ecommerce": "🛒 E-commerce",
            "other": "🔧 Другое"
        }
        
        return templates.TemplateResponse("portfolio.html", {
            "request": request,
            "username": username,
            "user_role": get_user_role(username),
            "navigation_items": get_navigation_items(get_user_role(username)),
            "portfolio_items": portfolio_items,
            "portfolio_stats": portfolio_stats,
            "category_names": category_names
        })
        
    except Exception as e:
        logger.error(f"Ошибка в portfolio_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/project-files", response_class=HTMLResponse)
async def project_files_page(request: Request, username: str = Depends(authenticate)):
    """Страница управления файлами проектов"""
    try:
        user_role = get_user_role(username)
        
        with get_db_context() as db:
            # Получаем проекты в зависимости от роли
            if user_role == 'owner':
                # Владелец видит все проекты
                projects_raw = db.query(Project).join(User).order_by(Project.created_at.desc()).all()
            else:
                # Исполнитель видит только назначенные ему проекты
                admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
                if admin_user:
                    projects_raw = db.query(Project).filter(Project.assigned_executor_id == admin_user.id).order_by(Project.created_at.desc()).all()
                else:
                    projects_raw = []
            
            # Конвертируем проекты в словари
            projects = []
            total_files = 0
            total_size = 0
            
            for project in projects_raw:
                project_dict = project.to_dict()
                
                # Получаем файлы проекта
                project_files = db.query(ProjectFile).filter(ProjectFile.project_id == project.id).all()
                project_dict['files'] = [f.to_dict() for f in project_files]
                project_dict['files_count'] = len(project_files)
                
                # Подсчитываем общую статистику
                total_files += len(project_files)
                for f in project_files:
                    total_size += f.file_size if f.file_size else 0
                
                projects.append(project_dict)
        
        # Статистика
        files_stats = {
            'total_projects': len(projects),
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size > 0 else 0
        }
        
        return templates.TemplateResponse("project_files.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": get_navigation_items(user_role),
            "projects": projects,
            "files_stats": files_stats
        })
        
    except Exception as e:
        logger.error(f"Ошибка в project_files_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# API endpoints для портфолио
@admin_router.get("/api/portfolio")
async def api_portfolio(username: str = Depends(authenticate)):
    """API для получения портфолио"""
    try:
        with get_db_context() as db:
            portfolio_items_raw = db.query(Portfolio).order_by(
                Portfolio.sort_order.asc(),
                Portfolio.created_at.desc()
            ).all()
            
            # Конвертируем в словари В РАМКАХ СЕССИИ
            portfolio_items = []
            for p in portfolio_items_raw:
                item_dict = p.to_dict()
                # Добавляем дополнительные поля для JavaScript
                item_dict.update({
                    'main_image': item_dict.get('image_paths', [None])[0] if item_dict.get('image_paths') else None,
                    'additional_images': item_dict.get('image_paths', [])[1:] if item_dict.get('image_paths') else [],
                    'active': True,  # Пока все активные
                    'cost': 0,  # Добавим поле стоимости
                    'duration': item_dict.get('development_time'),
                    'technologies': ', '.join(item_dict.get('technologies', [])) if item_dict.get('technologies') else '',
                    'category': item_dict.get('category', 'other'),
                    'complexity': 'medium',  # По умолчанию
                    'featured': item_dict.get('is_featured', False),
                    'show_cost': False,
                    'order': item_dict.get('sort_order', 0)
                })
                portfolio_items.append(item_dict)
        
        portfolio_stats = {
            'total': len(portfolio_items),
            'featured': len([p for p in portfolio_items if p.get('featured')]),
            'total_views': sum(p.get('views_count', 0) for p in portfolio_items),
            'total_likes': 0
        }
        
        return {
            "success": True,
            "items": portfolio_items,
            "stats": portfolio_stats
        }
        
    except Exception as e:
        logger.error(f"Ошибка в api_portfolio: {e}")
        return {"success": False, "error": str(e)}

@admin_router.post("/api/portfolio")
async def create_portfolio_item(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    complexity: str = Form("medium"),
    technologies: str = Form(""),
    cost: int = Form(0),
    duration: int = Form(0),
    featured: bool = Form(False),
    active: bool = Form(True),
    show_cost: bool = Form(False),
    order: int = Form(0),
    main_image: UploadFile = File(None),
    username: str = Depends(authenticate)
):
    """API для создания элемента портфолио"""
    try:
        with get_db_context() as db:
            # Создаем новый элемент портфолио
            new_portfolio = Portfolio(
                title=title,
                description=description,
                category=category,
                complexity_level=1,  # Базовая сложность
                development_time=duration if duration > 0 else None,
                cost_range=f"{cost}-{cost}" if cost > 0 else None,
                is_featured=featured,
                sort_order=order,
                views_count=0,
                created_at=datetime.utcnow()
            )
            
            # Обрабатываем технологии
            if technologies:
                tech_list = [tech.strip() for tech in technologies.split(',')]
                new_portfolio.technologies = tech_list
            
            # Сохраняем изображение если есть
            image_paths = []
            if main_image and main_image.filename:
                # Создаем директорию если не существует
                upload_dir = "uploads/portfolio"
                os.makedirs(upload_dir, exist_ok=True)
                
                # Сохраняем файл
                file_path = f"{upload_dir}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{main_image.filename}"
                with open(file_path, "wb") as buffer:
                    content = await main_image.read()
                    buffer.write(content)
                
                image_paths.append(file_path)
            
            new_portfolio.image_paths = image_paths
            
            db.add(new_portfolio)
            db.commit()
            
            logger.info(f"Создан новый элемент портфолио: {title}")
            
            return {"success": True, "message": "Проект добавлен в портфолио", "id": new_portfolio.id}
        
    except Exception as e:
        logger.error(f"Ошибка в create_portfolio_item: {e}")
        return {"success": False, "error": str(e)}

@admin_router.delete("/api/portfolio/{item_id}")
async def delete_portfolio_item(item_id: int, username: str = Depends(authenticate)):
    """API для удаления элемента портфолио"""
    try:
        with get_db_context() as db:
            portfolio_item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not portfolio_item:
                return {"success": False, "error": "Элемент портфолио не найден"}
            
            # Удаляем файлы изображений
            if portfolio_item.image_paths:
                for image_path in portfolio_item.image_paths:
                    try:
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить файл {image_path}: {e}")
            
            # Удаляем элемент из базы
            db.delete(portfolio_item)
            db.commit()
            
            logger.info(f"Удален элемент портфолио: {portfolio_item.title}")
            
            return {"success": True, "message": "Элемент портфолио удален"}
        
    except Exception as e:
        logger.error(f"Ошибка в delete_portfolio_item: {e}")
        return {"success": False, "error": str(e)}

@admin_router.put("/api/portfolio/{item_id}")
async def update_portfolio_item(
    item_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    complexity: str = Form("medium"),
    technologies: str = Form(""),
    cost: int = Form(0),
    duration: int = Form(0),
    featured: bool = Form(False),
    active: bool = Form(True),
    show_cost: bool = Form(False),
    order: int = Form(0),
    main_image: UploadFile = File(None),
    username: str = Depends(authenticate)
):
    """API для обновления элемента портфолио"""
    try:
        with get_db_context() as db:
            portfolio_item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not portfolio_item:
                return {"success": False, "error": "Элемент портфолио не найден"}
            
            # Обновляем поля
            portfolio_item.title = title
            portfolio_item.description = description
            portfolio_item.category = category
            portfolio_item.development_time = duration if duration > 0 else None
            portfolio_item.cost_range = f"{cost}-{cost}" if cost > 0 else None
            portfolio_item.is_featured = featured
            portfolio_item.sort_order = order
            
            # Обрабатываем технологии
            if technologies:
                tech_list = [tech.strip() for tech in technologies.split(',')]
                portfolio_item.technologies = tech_list
            
            # Обрабатываем новое изображение
            if main_image and main_image.filename:
                # Удаляем старые изображения
                if portfolio_item.image_paths:
                    for old_path in portfolio_item.image_paths:
                        try:
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        except Exception as e:
                            logger.warning(f"Не удалось удалить старый файл {old_path}: {e}")
                
                # Сохраняем новое изображение
                upload_dir = "uploads/portfolio"
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = f"{upload_dir}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{main_image.filename}"
                with open(file_path, "wb") as buffer:
                    content = await main_image.read()
                    buffer.write(content)
                
                portfolio_item.image_paths = [file_path]
            
            db.commit()
            
            logger.info(f"Обновлен элемент портфолио: {title}")
            
            return {"success": True, "message": "Элемент портфолио обновлен"}
        
    except Exception as e:
        logger.error(f"Ошибка в update_portfolio_item: {e}")
        return {"success": False, "error": str(e)}

# API endpoints для управления проектами
@admin_router.get("/api/stats")
async def api_stats(username: str = Depends(authenticate)):
    """API для получения статистики"""
    try:
        stats = get_dashboard_data(7)
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Ошибка в api_stats: {e}")
        return {"success": False, "error": str(e)}

@admin_router.post("/api/project/{project_id}/status")
async def update_project_status(
    project_id: int,
    status: str = Form(...),
    comment: str = Form(""),
    username: str = Depends(authenticate)
):
    """API для обновления статуса проекта с уведомлением клиента"""
    try:
        with get_db_context() as db:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Проект не найден")
            
            old_status = project.status
            project.status = status
            project.updated_at = datetime.utcnow()
            db.commit()
            
            # Получаем пользователя для отправки уведомления
            user = db.query(User).filter(User.id == project.user_id).first()
            
            if user and user.telegram_id:
                try:
                    # Отправляем уведомление через notification_service
                    from ..services.notification_service import notification_service
                    
                    # Устанавливаем бот для notification_service если не установлен
                    if not notification_service.bot:
                        from telegram import Bot
                        notification_service.set_bot(Bot(settings.BOT_TOKEN))
                    
                    # Формируем сообщение об изменении статуса
                    status_names = {
                        'new': '🆕 Новый',
                        'review': '👀 На рассмотрении', 
                        'accepted': '✅ Принят в работу',
                        'in_progress': '🔄 В работе',
                        'testing': '🧪 Тестирование',
                        'completed': '🎉 Завершен',
                        'cancelled': '❌ Отменен'
                    }
                    
                    new_status_name = status_names.get(status, status)
                    
                    notification_text = f"""
{new_status_name} <b>Обновление по вашему проекту</b>

📋 <b>Проект:</b> {project.title}

🔄 <b>Статус изменен:</b> {status_names.get(old_status, old_status)} → {new_status_name}

{comment if comment else _get_status_description(status)}

<i>Дата обновления: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>
                    """
                    
                    await notification_service.send_user_notification(
                        user.telegram_id, 
                        notification_text
                    )
                    
                    logger.info(f"Уведомление о смене статуса отправлено пользователю {user.telegram_id}")
                    
                except Exception as notify_error:
                    logger.error(f"Ошибка отправки уведомления: {notify_error}")
                    # Не прерываем выполнение если уведомление не отправилось
            
            return {
                "success": True, 
                "message": f"Статус проекта изменен на '{new_status_name}'" + 
                          (" и клиент уведомлен" if user and user.telegram_id else "")
            }
        
    except Exception as e:
        logger.error(f"Ошибка в update_project_status: {e}")
        return {"success": False, "error": str(e)}

def _get_status_description(status: str) -> str:
    """Получение описания статуса для клиента"""
    descriptions = {
        'new': 'Ваш проект зарегистрирован в системе. Мы скоро свяжемся с вами для уточнения деталей.',
        'review': 'Мы изучаем ваш проект и готовим предложение. Ожидайте звонка в ближайшее время.',
        'accepted': 'Отлично! Ваш проект принят в работу. Мы свяжемся с вами для подписания договора.',
        'in_progress': 'Разработка началась! Мы будем регулярно информировать вас о прогрессе.',
        'testing': 'Проект находится на стадии тестирования. Скоро пришлем вам демо для ознакомления.',
        'completed': '🎉 Поздравляем! Ваш проект готов. Спасибо за доверие!',
        'cancelled': 'К сожалению, проект был отменен. Если у вас есть вопросы, свяжитесь с нами.'
    }
    
    return descriptions.get(status, 'Статус проекта обновлен.')

@admin_router.post("/api/settings/update")
async def update_settings(
    key: str = Form(...),
    value: str = Form(...),
    username: str = Depends(authenticate)
):
    """API для обновления настроек"""
    try:
        with get_db_context() as db:
            setting = db.query(DBSettings).filter(DBSettings.key == key).first()
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = DBSettings(
                    key=key, 
                    value=value,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(setting)
            
            db.commit()
        
        return {"success": True, "message": "Настройка обновлена"}
        
    except Exception as e:
        logger.error(f"Ошибка в update_settings: {e}")
        return {"success": False, "error": str(e)}

@admin_router.get("/api/export/projects")
async def export_projects(username: str = Depends(authenticate)):
    """Экспорт проектов в JSON"""
    try:
        with get_db_context() as db:
            projects_raw = db.query(Project).all()
            
            # Конвертируем в словари В РАМКАХ СЕССИИ
            projects_data = []
            for p in projects_raw:
                projects_data.append(p.to_dict())
        
        return {"success": True, "data": projects_data}
        
    except Exception as e:
        logger.error(f"Ошибка в export_projects: {e}")
        return {"success": False, "error": str(e)}

@admin_router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        # Проверяем подключение к базе данных
        with get_db_context() as db:
            db.query(User).count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@admin_router.get("/notifications")
async def notifications_page(request: Request):
    """Страница тестирования уведомлений"""
    return templates.TemplateResponse("notifications.html", {"request": request})




@admin_router.get("/api/notifications/bot-status")
async def check_bot_status(request: Request):
    """Проверка статуса бота"""
    try:
        from telegram import Bot
        
        bot = Bot(settings.BOT_TOKEN)
        bot_info = await bot.get_me()
        
        return JSONResponse({
            "success": True,
            "bot_info": {
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "id": bot_info.id
            }
        })
        
    except Exception as e:
        logger.error(f"Ошибка проверки статуса бота: {e}")
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=500)


@admin_router.put("/api/projects/{project_id}/status")
async def update_project_status_direct(
    project_id: int,
    request: Request,
    username: str = Depends(authenticate)
):
    """Прямое обновление статуса проекта с уведомлением"""
    try:
        data = await request.json()
        new_status = data.get("status")
        comment = data.get("comment", "")
        
        logger.info(f"[DIRECT] Смена статуса проекта {project_id} на '{new_status}'")
        
        # Статусы проектов
        PROJECT_STATUSES = {
            "new": "Новый",
            "review": "На рассмотрении", 
            "accepted": "Принят",
            "in_progress": "В работе",
            "testing": "Тестирование",
            "completed": "Завершен",
            "cancelled": "Отменен",
            "on_hold": "Приостановлен"
        }
        
        if not new_status or new_status not in PROJECT_STATUSES:
            raise HTTPException(status_code=400, detail="Неверный статус")
        
        with get_db_context() as db:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Проект не найден")
            
            old_status = project.status
            project.status = new_status
            project.updated_at = datetime.utcnow()
            
            # Обновляем историю
            if not project.project_metadata:
                project.project_metadata = {}
            
            if "status_history" not in project.project_metadata:
                project.project_metadata["status_history"] = []
            
            project.project_metadata["status_history"].append({
                "from_status": old_status,
                "to_status": new_status,
                "changed_at": datetime.utcnow().isoformat(),
                "comment": comment
            })
            
            db.commit()
            db.refresh(project)
            
            # Отправляем уведомление
            user = db.query(User).filter(User.id == project.user_id).first()
            notification_sent = False
            
            if user and user.telegram_id:
                try:
                    from ..services.notification_service import NotificationService
                    from telegram import Bot
                    
                    notification_service = NotificationService()
                    notification_service.set_bot(Bot(settings.BOT_TOKEN))
                    
                    notification_sent = await notification_service.notify_project_status_changed(
                        project, old_status, user
                    )
                    
                    logger.info(f"[DIRECT] Уведомление клиенту {user.telegram_id}: {'отправлено' if notification_sent else 'ошибка'}")
                    
                except Exception as e:
                    logger.error(f"[DIRECT] Ошибка уведомления: {e}")
            
            logger.info(f"[DIRECT] Статус проекта {project_id} изменен: {old_status} -> {new_status}")
            
            return {
                "success": True,
                "message": f"Статус изменен на '{PROJECT_STATUSES[new_status]}'" + 
                          (" (уведомление отправлено)" if notification_sent else " (уведомление не отправлено)"),
                "project": {
                    "id": project.id,
                    "status": project.status,
                    "status_name": PROJECT_STATUSES[project.status],
                    "updated_at": project.updated_at.isoformat()
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DIRECT] Ошибка смены статуса проекта {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_navigation_items(user_role: str) -> List[Dict[str, Any]]:
    """Получение элементов навигации в зависимости от роли"""
    base_items = [
        {"name": "Главная", "url": "/", "icon": "fas fa-tachometer-alt"}
    ]
    
    if user_role == "owner":
        # Владелец видит все разделы
        return base_items + [
            {"name": "Проекты", "url": "/projects", "icon": "fas fa-project-diagram"},
            {"name": "Планировщик задач", "url": "/tasks", "icon": "fas fa-tasks"},
            {"name": "Пользователи", "url": "/users", "icon": "fas fa-users"},
            {"name": "Исполнители", "url": "/contractors", "icon": "fas fa-users-cog"},
            {"name": "Портфолио", "url": "/portfolio", "icon": "fas fa-briefcase"},
            {"name": "База проектов", "url": "/project-files", "icon": "fas fa-database"},
            {"name": "Финансы", "url": "/finance", "icon": "fas fa-money-bill-wave"},
            {"name": "Аналитика", "url": "/analytics", "icon": "fas fa-chart-bar"},
            {"name": "Настройки", "url": "/settings", "icon": "fas fa-cogs"}
        ]
    else:
        # Исполнитель видит ограниченный набор
        return base_items + [
            {"name": "Мои проекты", "url": "/projects", "icon": "fas fa-project-diagram"},
            {"name": "Мои задачи", "url": "/tasks", "icon": "fas fa-tasks"},
            {"name": "База проектов", "url": "/project-files", "icon": "fas fa-database"},
            {"name": "Правки", "url": "/revisions", "icon": "fas fa-edit"},
            {"name": "Финансы", "url": "/finance", "icon": "fas fa-money-bill-wave"},
            {"name": "Настройки", "url": "/settings", "icon": "fas fa-cogs"}
        ]
@admin_router.post("/api/projects/{project_id}/assign-executor")
async def assign_executor_to_project(
    project_id: int,
    executor_id: int = Form(...),
    username: str = Depends(authenticate)
):
    """Назначить исполнителя на проект (только владелец)"""
    try:
        user_role = get_user_role(username)
        if user_role != "owner":
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        with get_db_context() as db:
            # Проверяем существование проекта
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Проект не найден")
            
            # Проверяем существование исполнителя
            executor = db.query(AdminUser).filter(
                AdminUser.id == executor_id,
                AdminUser.role == "executor"
            ).first()
            if not executor:
                raise HTTPException(status_code=404, detail="Исполнитель не найден")
            
            # Назначаем исполнителя
            project.assigned_executor_id = executor_id
            project.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "message": f"Исполнитель {executor.username} назначен на проект {project.title}"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка назначения исполнителя: {str(e)}")
        return {"success": False, "error": str(e)}

