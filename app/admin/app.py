from fastapi import FastAPI, HTTPException, Depends, Request, Form, APIRouter, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from datetime import datetime, timedelta
from sqlalchemy import func
import secrets
from typing import Optional, Dict, Any, List
import json
import os
import calendar

from ..config.settings import settings
from ..config.logging import get_logger
from ..database.database import get_db_context
from ..database.models import User, Project, ConsultantSession, Portfolio, Settings as DBSettings, AdminUser, ProjectFile
from ..services.analytics_service import analytics_service, get_dashboard_data
from ..services.auth_service import AuthService
from .middleware.roles import RoleMiddleware
from .navigation import get_navigation_items

def get_image_url(image_path: str, request: Request = None) -> str:
    """Формирует правильный URL для изображения"""
    if not image_path:
        return None
    
    # Убираем префикс uploads/portfolio/ если он есть
    clean_path = image_path.replace("uploads/portfolio/", "").replace("uploads/", "")
    
    # Формируем полный URL
    if request:
        # Используем хост из запроса
        base_url = f"{request.url.scheme}://{request.url.netloc}"
    else:
        # Fallback для случаев без request (например API для бота)
        base_url = f"http://localhost:{settings.ADMIN_PORT}"
    
    return f"{base_url}/uploads/portfolio/{clean_path}"

# Импорт роутера портфолио
try:
    from .routers.portfolio import router as portfolio_router
    print("Роутер портфолио подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера портфолио: {e}")
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

# Импорт роутера финансов (простая версия)
try:
    from .routers.finance_simple import router as finance_router
    print("Роутер финансов (простая версия) подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера финансов: {e}")
    # Fallback на основной роутер
    try:
        from .routers.finance import router as finance_router
        print("Роутер финансов подключен")
    except ImportError as e2:
        print(f"Ошибка импорта роутера финансов: {e2}")
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

# Импорт роутера транзакций
try:
    from .routers.transactions import router as transactions_router
    print("Роутер транзакций подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера транзакций: {e}")
    transactions_router = None

# Импорт роутера автоматизации
try:
    from .routers.automation import router as automation_router
    print("Роутер автоматизации подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера автоматизации: {e}")
    automation_router = None

# Импорт роутера отчетов
try:
    from .routers.reports import router as reports_router
    print("Роутер отчетов подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера отчетов: {e}")
    reports_router = None

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
    admin_router.include_router(finance_router)

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
    admin_router.include_router(revisions_router, prefix="")

# Подключаем роутер транзакций
if transactions_router:
    admin_router.include_router(transactions_router, prefix="/api/transactions")

if automation_router:
    # Подключаем роутер для страниц автоматизации
    admin_router.include_router(automation_router)

if reports_router:
    # Подключаем роутер для страниц отчетов
    admin_router.include_router(reports_router)

# Импорт роутера аналитики
try:
    from .routers.analytics import router as analytics_router
    print("Роутер аналитики подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера аналитики: {e}")
    analytics_router = None

# Подключаем роутер аналитики (только API, страница уже есть в основном роутере)
if analytics_router:
    admin_router.include_router(analytics_router)

# Импорт роутера клиентов CRM
try:
    from .routers.clients import router as clients_router
    print("Роутер клиентов подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера клиентов: {e}")
    # Fallback на простую версию
    try:
        from .routers.clients_simple import router as clients_router
        print("Роутер клиентов (простая версия) подключен")
    except ImportError as e2:
        print(f"Ошибка импорта простого роутера клиентов: {e2}")
        clients_router = None

# Подключаем роутер клиентов
if clients_router:
    admin_router.include_router(clients_router, prefix="/api/clients")

# Импорт роутера лидов
try:
    from .routers.leads import router as leads_router
    print("Роутер лидов подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера лидов: {e}")
    # Fallback на простую версию
    try:
        from .routers.leads_simple import router as leads_router
        print("Роутер лидов (простая версия) подключен")
    except ImportError as e2:
        print(f"Ошибка импорта простого роутера лидов: {e2}")
        leads_router = None

# Подключаем роутер лидов
if leads_router:
    admin_router.include_router(leads_router)

# Импорт роутера сделок
try:
    from .routers.deals import router as deals_router
    print("Роутер сделок подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера сделок: {e}")
    # Fallback на простую версию
    try:
        from .routers.deals_simple import router as deals_router
        print("Роутер сделок (простая версия) подключен")
    except ImportError as e2:
        print(f"Ошибка импорта простого роутера сделок: {e2}")
        deals_router = None

# Подключаем роутер сделок
if deals_router:
    admin_router.include_router(deals_router)

# Импорт роутера документов
try:
    from .routers.documents import router as documents_router
    print("Роутер документов подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера документов: {e}")
    documents_router = None

# Подключаем роутер документов
if documents_router:
    admin_router.include_router(documents_router)

# Импорт роутера Авито
try:
    from .routers.avito import router as avito_router
    print("Роутер Авито подключен")
except ImportError as e:
    print(f"Ошибка импорта роутера Авито: {e}")
    avito_router = None

# Импорт OAuth роутера Авито
try:
    from .routers.avito_oauth import router as avito_oauth_router
    print("OAuth роутер Авито подключен")
except ImportError as e:
    print(f"Ошибка импорта OAuth роутера Авито: {e}")
    avito_oauth_router = None

# Подключаем роутер Авито
if avito_router:
    admin_router.include_router(avito_router, prefix="/avito")

# Подключаем OAuth роутер Авито
if avito_oauth_router:
    admin_router.include_router(avito_oauth_router)

# Подключаем роутер управления правами
try:
    from .routers.permissions_management import router as permissions_router
    admin_router.include_router(permissions_router, prefix="/permissions")
    print("Роутер управления правами подключен")
except ImportError as e:
    print(f"⚠️ Не удалось подключить роутер управления правами: {e}")
    permissions_router = None

# Подключаем роутер уведомлений
try:
    from .routers.notifications import router as notifications_router
    admin_router.include_router(notifications_router)
    print("Роутер уведомлений подключен")
except ImportError as e:
    print(f"⚠️ Не удалось подключить роутер уведомлений: {e}")
    notifications_router = None

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
    logger.info(f"Попытка входа пользователя: {credentials.username}")
    logger.info(f"Ожидаемый admin username: {settings.ADMIN_USERNAME}")
    
    # Дополнительная проверка с дефолтными значениями
    if credentials.username == "admin" and credentials.password == "qwerty123":
        logger.info(f"Вход по дефолтным учетным данным")
        return credentials.username
    
    # Проверяем основного владельца
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    logger.info(f"Username совпадает: {correct_username}, Password совпадает: {correct_password}")
    
    if correct_username and correct_password:
        logger.info(f"Успешный вход владельца: {credentials.username}")
        return credentials.username
    
    # Проверяем исполнителей в базе данных
    try:
        admin_user = AuthService.authenticate_user(credentials.username, credentials.password)
        if admin_user:
            logger.info(f"Успешный вход исполнителя: {credentials.username}")
            return credentials.username
    except Exception as e:
        logger.error(f"Ошибка при проверке исполнителя: {e}")
    
    logger.warning(f"Неудачная попытка входа: {credentials.username}")
    # Если ни один способ не сработал
    raise HTTPException(
        status_code=401,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )

@admin_router.get("/test-simple")
async def test_simple():
    """Простой тестовый эндпоинт без аутентификации"""
    try:
        return {"status": "ok", "message": "Admin router работает!", "python_version": "3.x"}
    except Exception as e:
        return {"status": "error", "error": str(e), "message": "Ошибка в test-simple"}

@admin_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа в админ-панель"""
    return templates.TemplateResponse("login.html", {
        "request": request
    })

@admin_router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Обработка входа"""
    try:
        # Проверяем простую аутентификацию
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            response = RedirectResponse(url="/admin/", status_code=302)
            # Можно добавить установку cookies для сессии
            return response
        
        # Проверяем исполнителей в базе данных
        admin_user = AuthService.authenticate_user(username, password)
        if admin_user:
            response = RedirectResponse(url="/admin/", status_code=302)
            return response
            
        # Если аутентификация не прошла
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверные учетные данные"
        })
        
    except Exception as e:
        logger.error(f"Ошибка при входе: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Ошибка сервера"
        })

@admin_router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(authenticate)):
    """Главная страница админ-панели"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        if user_role == "executor":
            # Получаем данные для исполнителя
            with get_db_context() as db:
                # Получаем исполнителя
                admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
                
                # Получаем проекты назначенные исполнителю
                executor_projects = []
                if admin_user:
                    projects_raw = db.query(Project).filter(
                        Project.assigned_executor_id == admin_user.id
                    ).order_by(Project.created_at.desc()).all()
                    
                    # Конвертируем в словари
                    for p in projects_raw:
                        project_dict = p.to_dict()
                        # Добавляем информацию о пользователе
                        user = db.query(User).filter(User.id == p.user_id).first()
                        project_dict['user'] = user.to_dict() if user else None
                        executor_projects.append(project_dict)
            
            return templates.TemplateResponse("executor_dashboard.html", {
                "request": request,
                "username": username,
                "user_role": user_role,
                "navigation_items": navigation_items,
                "projects": executor_projects
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
async def projects_page(request: Request, show_archived: bool = False, username: str = Depends(authenticate)):
    """Страница управления проектами"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        
        projects = []
        with get_db_context() as db:
            # Базовый запрос с присоединением пользователя для избежания N+1
            query = db.query(Project).join(User, Project.user_id == User.id, isouter=True)

            # Фильтр архивных проектов
            if show_archived:
                query = query.filter(Project.is_archived == True)
            else:
                query = query.filter((Project.is_archived == False) | (Project.is_archived == None))
            
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
            "calculate_progress": calculate_progress,
            "show_archived": show_archived
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Ошибка в projects_page: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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

# Удалено - дублирует другой обработчик /users ниже

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
async def analytics_page(request: Request, username: str = Depends(authenticate)):
    """Страница аналитики (только для владельца)"""
    try:
        user_role = get_user_role(username)
        
        # Проверяем роль пользователя
        if user_role != "owner":
            raise HTTPException(status_code=403, detail="Доступ запрещен")
        
        # Получаем реальные данные из базы
        analytics_data = _get_full_analytics_data()
        
        # Генерируем HTML с реальными данными
        analytics_html = _generate_analytics_html(analytics_data)
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=analytics_html)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в analytics_page: {e}")
        return HTMLResponse(content=f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>Ошибка загрузки аналитики</h1>
            <p>Произошла ошибка: {str(e)}</p>
            <a href="/admin/" style="color: #007bff;">Вернуться на главную</a>
        </body>
        </html>
        """, status_code=200)

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

@admin_router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, username: str = Depends(authenticate)):
    """Страница управления пользователями"""
    try:
        user_role = get_user_role(username)
        current_user = get_current_user(username)
        
        logger.info(f"users_page: username={username}, user_role={user_role}, current_user={current_user}")
        navigation_items = get_navigation_items(user_role)
        
        # Получаем список пользователей
        with get_db_context() as db:
            # Владелец видит всех, исполнитель только себя
            if user_role == 'executor':
                # Исполнитель видит только свою учетную запись
                if current_user and isinstance(current_user, dict) and 'id' in current_user:
                    user_id = current_user['id']
                    users_raw = db.query(AdminUser).filter(AdminUser.id == user_id).all()
                else:
                    users_raw = []
            else:
                # Владелец видит всех пользователей
                users_raw = db.query(AdminUser).order_by(AdminUser.created_at.desc()).all()
            
            users = []
            for user in users_raw:
                if user:  # Проверяем, что пользователь существует
                    user_dict = user.to_dict()
                    # Добавляем статистику по задачам
                    from app.database.models import Task
                    user_dict['tasks_count'] = db.query(Task).filter(Task.assigned_to_id == user.id).count()
                    user_dict['active_tasks'] = db.query(Task).filter(
                        Task.assigned_to_id == user.id,
                        Task.status.in_(['pending', 'in_progress'])
                    ).count()
                    users.append(user_dict)
        
        return templates.TemplateResponse("users.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "users": users,
            "current_user": current_user
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в users_page: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# TODO: Добавить миграцию для таблицы admin_activity_logs
# @admin_router.get("/activity", response_class=HTMLResponse)
# async def activity_page(request: Request, username: str = Depends(authenticate)):
#     """Страница активности пользователей"""
#     try:
#         user_role = get_user_role(username)
#         
#         # Только владелец может просматривать активность всех
#         if user_role != 'owner':
#             raise HTTPException(status_code=403, detail="Недостаточно прав")
#         
#         navigation_items = get_navigation_items(user_role)
#         
#         # Получаем список пользователей для фильтра
#         with get_db_context() as db:
#             users = db.query(AdminUser).all()
#             users_list = [u.to_dict() for u in users]
#         
#         return templates.TemplateResponse("activity.html", {
#             "request": request,
#             "username": username,
#             "user_role": user_role,
#             "navigation_items": navigation_items,
#             "users": users_list
#         })
#         
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Ошибка в activity_page: {e}")
#         raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@admin_router.get("/finance", response_class=HTMLResponse)
async def finance_page(request: Request, username: str = Depends(authenticate)):
    """Страница управления финансами"""
    try:
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        current_user = get_current_user(username)
        
        # Получаем статистику для текущего месяца
        from datetime import datetime, timedelta
        from sqlalchemy import func
        from ..database.models import FinanceTransaction
        from ..database.database import get_db_context
        
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        with get_db_context() as db:
            # Базовый запрос с фильтрацией по пользователю для исполнителей
            base_query = db.query(FinanceTransaction)
            if user_role == "executor":
                base_query = base_query.filter(FinanceTransaction.created_by_id == current_user["id"])
            
            # Доходы за месяц
            total_income = base_query.filter(
            FinanceTransaction.type == "income",
            FinanceTransaction.date >= month_start
        ).with_entities(func.sum(FinanceTransaction.amount)).scalar() or 0
        
            # Расходы за месяц
            total_expenses = base_query.filter(
            FinanceTransaction.type == "expense",
            FinanceTransaction.date >= month_start
        ).with_entities(func.sum(FinanceTransaction.amount)).scalar() or 0
        
            # Общий баланс - считаем отдельно для избежания проблем с SQLAlchemy case
            total_income_all = base_query.filter(
                FinanceTransaction.type == "income"
            ).with_entities(func.sum(FinanceTransaction.amount)).scalar() or 0
            
            total_expenses_all = base_query.filter(
                FinanceTransaction.type == "expense"
            ).with_entities(func.sum(FinanceTransaction.amount)).scalar() or 0
            
            balance = total_income_all - total_expenses_all
        
            # Прибыль
            profit = total_income - total_expenses
            
            # Расчет изменений (пример)
            income_change = 12.5
            expense_change = 8.2
            profit_change = 15.0 if profit > 0 else -5.0
            savings_rate = round((profit / total_income * 100) if total_income > 0 else 0, 1)
            
            # Последние транзакции
            recent_transactions_query = base_query.order_by(
            FinanceTransaction.date.desc()
        ).limit(10).all()
        
            recent_transactions = []
            for t in recent_transactions_query:
                icon = "shopping-cart" if t.type == "expense" else "dollar-sign"
                recent_transactions.append({
                    "id": t.id,
                    "type": t.type,
                    "icon": icon,
                    "description": t.description,
                    "category": t.category.name if t.category else "Без категории",
                    "date": t.date.strftime("%d.%m.%Y"),
                    "amount": t.amount
                })
        
        stats = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance,
            "profit": profit,
            "income_change": income_change,
            "expense_change": expense_change,
            "profit_change": profit_change,
            "savings_rate": savings_rate
        }
        
        return templates.TemplateResponse("finance_simple.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "stats": stats,
            "recent_transactions": recent_transactions,
            "today": now.strftime("%Y-%m-%d")
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
        
        return templates.TemplateResponse("portfolio_improved.html", {
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
        
        return templates.TemplateResponse("project_files_improved.html", {
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
                
                # Формируем правильный URL для главного изображения
                main_image_url = None
                if p.main_image:
                    # Если в main_image есть путь, формируем полный URL
                    main_image_url = f"/uploads/portfolio/{p.main_image}"
                elif item_dict.get('image_paths') and item_dict['image_paths'][0]:
                    # Fallback на первое изображение из image_paths
                    main_image_url = f"/uploads/portfolio/{item_dict['image_paths'][0]}"
                
                # Добавляем дополнительные поля для JavaScript
                item_dict.update({
                    'main_image': main_image_url,
                    'additional_images': [f"/uploads/portfolio/{img}" for img in item_dict.get('image_paths', [])[1:]] if item_dict.get('image_paths') else [],
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

@admin_router.get("/api/portfolio/{item_id}")
async def get_portfolio_item(item_id: int, username: str = Depends(authenticate)):
    """API для получения элемента портфолио для редактирования"""
    try:
        with get_db_context() as db:
            portfolio_item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not portfolio_item:
                return {"success": False, "error": "Элемент портфолио не найден"}
            
            project_dict = portfolio_item.to_dict()
            
            # Формируем правильные URL для изображений
            if portfolio_item.main_image:
                project_dict['main_image'] = f"/uploads/portfolio/{portfolio_item.main_image}"
            
            if project_dict.get('image_paths'):
                project_dict['image_paths'] = [f"/uploads/portfolio/{img}" for img in project_dict['image_paths']]
            
            return {
                "success": True,
                "project": project_dict
            }
        
    except Exception as e:
        logger.error(f"Ошибка в get_portfolio_item: {e}")
        return {"success": False, "error": str(e)}

@admin_router.get("/portfolio/preview/{item_id}", response_class=HTMLResponse)
async def preview_portfolio_item(item_id: int, username: str = Depends(authenticate)):
    """Предварительный просмотр элемента портфолио"""
    try:
        with get_db_context() as db:
            portfolio_item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
            
            if not portfolio_item:
                raise HTTPException(status_code=404, detail="Проект не найден")
            
            # Преобразуем в словарь для шаблона
            project = portfolio_item.to_dict()
            
            # Обрабатываем технологии
            if project.get('technologies'):
                if isinstance(project['technologies'], str):
                    project['technologies_list'] = [tech.strip() for tech in project['technologies'].split(',')]
                else:
                    project['technologies_list'] = project['technologies']
            else:
                project['technologies_list'] = []
            
            # Обрабатываем изображения
            if project.get('main_image'):
                project['main_image_url'] = f"/uploads/portfolio/{project['main_image'].replace('uploads/portfolio/', '')}"
            
            if project.get('image_paths'):
                project['gallery_images'] = [
                    f"/uploads/portfolio/{img.replace('uploads/portfolio/', '')}"
                    for img in project['image_paths']
                ]
            else:
                project['gallery_images'] = []
            
            # Определяем сложность
            complexity_names = {
                'simple': '🟢 Простая',
                'medium': '🟡 Средняя', 
                'complex': '🔴 Сложная',
                'premium': '🟣 Премиум'
            }
            complexity_display = complexity_names.get(project.get('complexity', 'medium'), '🟡 Средняя')
            
            # Формируем технологии
            tech_tags_html = ""
            if project.get('technologies_list'):
                tech_tags_html = ''.join(f'<span class="tech-tag">{tech}</span>' for tech in project['technologies_list'])
            
            # Формируем ссылки
            links_html = ""
            if project.get('demo_link'):
                links_html += f'<a href="{project.get("demo_link")}" class="project-link" target="_blank"><i class="fas fa-rocket me-2"></i>Демо-версия</a>'
            if project.get('repository_link'):
                links_html += f'<a href="{project.get("repository_link")}" class="project-link" target="_blank"><i class="fab fa-github me-2"></i>Репозиторий</a>'
            
            # Формируем галерею
            gallery_html = ""
            if project.get('gallery_images'):
                gallery_images_html = ''.join(f'<div class="col-md-6"><img src="{img}" class="gallery-image" alt="Изображение проекта"></div>' for img in project['gallery_images'])
                gallery_html = f'<div class="gallery"><h5><i class="fas fa-images me-2"></i>Галерея:</h5><div class="row">{gallery_images_html}</div></div>'
            
            # Создаем HTML для предварительного просмотра
            preview_html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Предварительный просмотр: {project.get('title', 'Проект')}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        .preview-container {{
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }}
        
        .project-card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .project-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .project-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .project-subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 0;
        }}
        
        .project-image {{
            width: 100%;
            height: 300px;
            object-fit: cover;
        }}
        
        .project-body {{
            padding: 30px;
        }}
        
        .project-description {{
            font-size: 1.1rem;
            line-height: 1.7;
            color: #444;
            margin-bottom: 30px;
        }}
        
        .project-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .meta-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .meta-label {{
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .meta-value {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #333;
        }}
        
        .tech-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }}
        
        .tech-tag {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        .project-links {{
            margin-top: 30px;
        }}
        
        .project-link {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            margin-right: 10px;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }}
        
        .project-link:hover {{
            transform: translateY(-2px);
            color: white;
        }}
        
        .gallery {{
            margin-top: 30px;
        }}
        
        .gallery-image {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 15px;
        }}
        
        .complexity-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.9rem;
            font-weight: 600;
        }}
        
        .complexity-simple {{ background: #d4edda; color: #155724; }}
        .complexity-medium {{ background: #fff3cd; color: #856404; }}
        .complexity-complex {{ background: #f8d7da; color: #721c24; }}
        .complexity-premium {{ background: #e2e3f1; color: #383d41; }}
    </style>
</head>
<body>
    <div class="preview-container">
        <div class="project-card">
            <div class="project-header">
                <h1 class="project-title">{project.get('title', 'Без названия')}</h1>
                {f'<p class="project-subtitle">{project.get("subtitle")}</p>' if project.get('subtitle') else ''}
            </div>
            
            {f'<img src="{project.get("main_image_url")}" alt="{project.get("title")}" class="project-image">' if project.get('main_image_url') else ''}
            
            <div class="project-body">
                {f'<div class="project-description">{project.get("description", "")}</div>' if project.get('description') else ''}
                
                <div class="project-meta">
                    <div class="meta-item">
                        <div class="meta-label">Сложность</div>
                        <div class="meta-value">
                            <span class="complexity-badge complexity-{project.get('complexity', 'medium')}">
                                {complexity_display}
                            </span>
                        </div>
                    </div>
                    
                    {f'<div class="meta-item"><div class="meta-label">Время разработки</div><div class="meta-value">{project.get("development_time")} дн.</div></div>' if project.get('development_time') else ''}
                    
                    <div class="meta-item">
                        <div class="meta-label">Стоимость</div>
                        <div class="meta-value">
                            {f"{project.get('cost'):,.0f}₽" if project.get('show_cost') and project.get('cost') else 'По запросу'}
                        </div>
                    </div>
                    
                    <div class="meta-item">
                        <div class="meta-label">Статус</div>
                        <div class="meta-value">
                            {'⭐ Рекомендуемый' if project.get('is_featured') else '👁 Обычный'}
                        </div>
                    </div>
                </div>
                
                {f'<div><h5><i class="fas fa-tools me-2"></i>Технологии:</h5><div class="tech-tags">{tech_tags_html}</div></div>' if project.get('technologies_list') else ''}
                
                {f'<div class="project-links"><h5><i class="fas fa-link me-2"></i>Ссылки:</h5>{links_html}</div>' if links_html else ''}
                
                {gallery_html}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
            """
            
            return preview_html
        
    except Exception as e:
        logger.error(f"Ошибка в preview_portfolio_item: {e}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки предварительного просмотра")

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

@admin_router.get("/api/dashboard/crm")
async def api_dashboard_crm(username: str = Depends(authenticate)):
    """API для получения данных CRM дашборда"""
    try:
        with get_db_context() as db:
            from ..services.reports_service import ReportsService
            from ..database.crm_models import Client, Lead, Deal, DealStatus, LeadStatus
            
            reports_service = ReportsService(db)
            
            # Получаем основные метрики
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            last_month_start = (month_start - timedelta(days=1)).replace(day=1)
            
            # Клиенты
            total_clients = db.query(func.count(Client.id)).scalar()
            new_clients_month = db.query(func.count(Client.id)).filter(
                Client.created_at >= month_start
            ).scalar()
            
            # Сделки
            active_deals = db.query(func.count(Deal.id)).filter(
                Deal.status.notin_([DealStatus.COMPLETED, DealStatus.CANCELLED])
            ).scalar()
            
            deals_amount = db.query(func.sum(Deal.amount)).filter(
                Deal.status.notin_([DealStatus.COMPLETED, DealStatus.CANCELLED])
            ).scalar() or 0
            
            # Выручка
            month_revenue = db.query(func.sum(Deal.amount)).filter(
                Deal.status == DealStatus.COMPLETED,
                Deal.closed_at >= month_start
            ).scalar() or 0
            
            last_month_revenue = db.query(func.sum(Deal.amount)).filter(
                Deal.status == DealStatus.COMPLETED,
                Deal.closed_at >= last_month_start,
                Deal.closed_at < month_start
            ).scalar() or 0
            
            revenue_change = 0
            if last_month_revenue > 0:
                revenue_change = ((month_revenue - last_month_revenue) / last_month_revenue) * 100
            
            # Проекты
            active_projects = db.query(func.count(Project.id)).filter(
                Project.status == 'in_progress'
            ).scalar()
            
            completed_projects = db.query(func.count(Project.id)).filter(
                Project.status == 'completed',
                Project.actual_end_date >= month_start
            ).scalar()
            
            total_projects = db.query(func.count(Project.id)).filter(
                Project.status.in_(['in_progress', 'completed'])
            ).scalar()
            
            projects_completion = (completed_projects / total_projects * 100) if total_projects > 0 else 0
            
            # Воронка продаж
            leads_total = db.query(func.count(Lead.id)).filter(
                Lead.created_at >= month_start
            ).scalar()
            
            leads_qualified = db.query(func.count(Lead.id)).filter(
                Lead.created_at >= month_start,
                Lead.status.in_([LeadStatus.QUALIFICATION, LeadStatus.PROPOSAL_SENT, LeadStatus.NEGOTIATION, LeadStatus.WON])
            ).scalar()
            
            leads_proposals = db.query(func.count(Lead.id)).filter(
                Lead.created_at >= month_start,
                Lead.status.in_([LeadStatus.PROPOSAL_SENT, LeadStatus.NEGOTIATION, LeadStatus.WON])
            ).scalar()
            
            leads_won = db.query(func.count(Lead.id)).filter(
                Lead.created_at >= month_start,
                Lead.status == LeadStatus.WON
            ).scalar()
            
            conversion_rate = (leads_won / leads_total * 100) if leads_total > 0 else 0
            
            # График доходов
            revenue_chart = []
            for i in range(5, -1, -1):
                month_date = now - timedelta(days=30 * i)
                m_start = month_date.replace(day=1)
                m_end = (m_start + timedelta(days=32)).replace(day=1)
                
                m_revenue = db.query(func.sum(Deal.amount)).filter(
                    Deal.status == DealStatus.COMPLETED,
                    Deal.closed_at >= m_start,
                    Deal.closed_at < m_end
                ).scalar() or 0
                
                revenue_chart.append({
                    "month": calendar.month_name[m_start.month][:3],
                    "revenue": float(m_revenue)
                })
            
            # Топ клиенты
            top_clients = db.query(
                Client.name,
                func.count(Deal.id).label('deals_count'),
                func.sum(Deal.amount).label('total_revenue')
            ).join(
                Deal, Deal.client_id == Client.id
            ).filter(
                Deal.status == DealStatus.COMPLETED
            ).group_by(Client.id, Client.name).order_by(
                func.sum(Deal.amount).desc()
            ).limit(5).all()
            
            # Активные сделки
            active_deals_list = db.query(Deal).filter(
                Deal.status.notin_([DealStatus.COMPLETED, DealStatus.CANCELLED])
            ).order_by(Deal.amount.desc()).limit(5).all()
            
            # Последняя активность
            recent_activities = []
            
            # Последние сделки
            recent_deals = db.query(Deal).order_by(Deal.created_at.desc()).limit(3).all()
            for deal in recent_deals:
                recent_activities.append({
                    "type": "deal",
                    "title": f"Новая сделка: {deal.title}",
                    "amount": float(deal.amount or 0),
                    "date": deal.created_at.isoformat()
                })
            
            # Последние проекты
            recent_projects = db.query(Project).order_by(Project.created_at.desc()).limit(3).all()
            for project in recent_projects:
                recent_activities.append({
                    "type": "project",
                    "title": f"Проект: {project.title}",
                    "status": project.status,
                    "date": project.created_at.isoformat()
                })
            
            recent_activities.sort(key=lambda x: x['date'], reverse=True)
            
            # KPI менеджеров (упрощенная версия)
            managers_kpi = db.query(
                AdminUser.username.label('name'),
                func.count(func.distinct(Lead.id)).label('leads_count'),
                func.count(func.distinct(Deal.id)).label('deals_count'),
                func.sum(Deal.amount).label('revenue')
            ).outerjoin(
                Lead, Lead.responsible_manager_id == AdminUser.id
            ).outerjoin(
                Deal, Deal.responsible_manager_id == AdminUser.id
            ).filter(
                AdminUser.role.in_(['owner', 'manager'])
            ).group_by(AdminUser.id, AdminUser.username).all()
            
            return {
                "success": True,
                "metrics": {
                    "total_clients": total_clients,
                    "new_clients_month": new_clients_month,
                    "active_deals": active_deals,
                    "deals_amount": float(deals_amount),
                    "month_revenue": float(month_revenue),
                    "revenue_change": round(revenue_change, 1),
                    "active_projects": active_projects,
                    "projects_completion": round(projects_completion, 1)
                },
                "funnel": {
                    "leads": leads_total,
                    "qualified": leads_qualified,
                    "proposals": leads_proposals,
                    "won": leads_won,
                    "conversion_rate": round(conversion_rate, 1)
                },
                "revenue_chart": revenue_chart,
                "top_clients": [
                    {
                        "name": client.name,
                        "deals_count": client.deals_count,
                        "total_revenue": float(client.total_revenue or 0)
                    }
                    for client in top_clients
                ],
                "active_deals_list": [
                    {
                        "title": deal.title,
                        "status": deal.status.value,
                        "status_label": deal.status.value,
                        "amount": float(deal.amount or 0)
                    }
                    for deal in active_deals_list
                ],
                "recent_activities": recent_activities[:6],
                "managers_kpi": [
                    {
                        "name": row.name,
                        "leads_count": row.leads_count or 0,
                        "deals_count": row.deals_count or 0,
                        "conversion_rate": round((row.deals_count / row.leads_count * 100) if row.leads_count > 0 else 0, 1),
                        "revenue": float(row.revenue or 0),
                        "avg_deal_size": float(row.revenue / row.deals_count) if row.deals_count > 0 else 0,
                        "efficiency": min(100, round((row.deals_count / max(row.leads_count, 1)) * 100, 1))
                    }
                    for row in managers_kpi
                ]
            }
            
    except Exception as e:
        logger.error(f"Ошибка в api_dashboard_crm: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
async def notifications_page(request: Request, username: str = Depends(authenticate)):
    """Страница тестирования уведомлений"""
    user_role = get_user_role(username)
    navigation_items = get_navigation_items(user_role)
    return templates.TemplateResponse("notifications.html", {
        "request": request,
        "username": username,
        "user_role": user_role,
        "navigation_items": navigation_items
    })

# Добавляем fallback страницы если роутеры не загрузились
if not automation_router:
    @admin_router.get("/automation", response_class=HTMLResponse)  
    async def automation_page_fallback(request: Request, username: str = Depends(authenticate)):
        """Страница автоматизации (резервная)"""
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        return templates.TemplateResponse("automation.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "user": {"username": username, "role": user_role},
            "scheduler_running": False
        })

if not reports_router:
    @admin_router.get("/reports", response_class=HTMLResponse)
    async def reports_page_fallback(request: Request, username: str = Depends(authenticate)):
        """Страница отчетов (резервная)"""
        user_role = get_user_role(username)
        navigation_items = get_navigation_items(user_role)
        return templates.TemplateResponse("reports.html", {
            "request": request,
            "username": username,
            "user_role": user_role,
            "navigation_items": navigation_items,
            "user": {"username": username, "role": user_role}
        })




# TODO: Добавить миграцию для таблицы admin_activity_logs
# @admin_router.get("/api/activity")
# async def get_activity_logs(username: str = Depends(authenticate)):
#     """Получить логи активности"""
#     try:
#         user_role = get_user_role(username)
#         current_user = get_current_user(username)
#         
#         with get_db_context() as db:
#             from app.database.models import AdminActivityLog
#             
#             # Если не владелец, показываем только его активность
#             if user_role == 'owner':
#                 logs = db.query(AdminActivityLog).order_by(
#                     AdminActivityLog.created_at.desc()
#                 ).limit(100).all()
#             else:
#                 logs = db.query(AdminActivityLog).filter(
#                     AdminActivityLog.user_id == current_user['id']
#                 ).order_by(
#                     AdminActivityLog.created_at.desc()
#                 ).limit(50).all()
#             
#             # Добавляем имена пользователей
#             activities = []
#             for log in logs:
#                 log_dict = log.to_dict()
#                 user = db.query(AdminUser).filter(AdminUser.id == log.user_id).first()
#                 if user:
#                     log_dict['user_name'] = f"{user.first_name or ''} {user.last_name or ''} (@{user.username})".strip()
#                 activities.append(log_dict)
#             
#             return {
#                 "success": True,
#                 "activities": activities
#             }
#     except Exception as e:
#         logger.error(f"Ошибка получения логов активности: {e}")
#         return {"success": False, "error": str(e)}

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


@admin_router.post("/api/notifications/test-admin")
async def test_admin_notification(request: Request):
    """Тестовое уведомление администратору"""
    try:
        data = await request.json()
        message = data.get("message", "🧪 Тестовое уведомление из админ-панели")
        
        # Отправляем уведомление в admin chat
        from telegram import Bot
        bot = Bot(settings.BOT_TOKEN)
        
        # Получаем admin chat ID из настроек
        admin_chat_id = settings.ADMIN_CHAT_ID or settings.ADMIN_USERNAME
        
        if admin_chat_id:
            await bot.send_message(chat_id=admin_chat_id, text=message)
            logger.info(f"Тестовое уведомление отправлено администратору: {message}")
            
            return JSONResponse({
                "success": True,
                "message": "Тестовое уведомление отправлено администратору"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "Не настроен admin chat ID"
            }, status_code=400)
        
    except Exception as e:
        logger.error(f"Ошибка отправки тестового уведомления: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Ошибка отправки уведомления: {str(e)}"
        }, status_code=500)


@admin_router.post("/api/notifications/test-error")
async def test_error_notification(request: Request):
    """Тестовое уведомление об ошибке"""
    try:
        data = await request.json()
        error = data.get("error", "Тестовая ошибка из админ-панели")
        context = data.get("context", {})
        
        # Формируем сообщение об ошибке
        message = f"🚨 Ошибка в системе:\n\n{error}\n\nКонтекст: {json.dumps(context, ensure_ascii=False, indent=2)}"
        
        # Отправляем уведомление в admin chat
        from telegram import Bot
        bot = Bot(settings.BOT_TOKEN)
        
        admin_chat_id = settings.ADMIN_CHAT_ID or settings.ADMIN_USERNAME
        
        if admin_chat_id:
            await bot.send_message(chat_id=admin_chat_id, text=message)
            logger.info(f"Тестовое уведомление об ошибке отправлено: {error}")
            
            return JSONResponse({
                "success": True,
                "message": "Уведомление об ошибке отправлено"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "Не настроен admin chat ID"
            }, status_code=400)
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления об ошибке: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Ошибка отправки уведомления: {str(e)}"
        }, status_code=500)


@admin_router.post("/api/notifications/daily-report")
async def test_daily_report(request: Request):
    """Тестовый ежедневный отчет"""
    try:
        # Генерируем тестовый ежедневный отчет
        with get_db_context() as db:
            # Статистика проектов
            total_projects = db.query(Project).count()
            new_projects = db.query(Project).filter(Project.status == 'new').count()
            in_progress_projects = db.query(Project).filter(Project.status == 'in_progress').count()
            completed_projects = db.query(Project).filter(Project.status == 'completed').count()
            
            # Статистика пользователей
            total_users = db.query(User).count()
            
            report = f"""📊 Ежедневный отчет системы

🗂 Проекты:
• Всего проектов: {total_projects}
• Новые: {new_projects}
• В работе: {in_progress_projects}
• Завершенные: {completed_projects}

👥 Пользователи:
• Всего пользователей: {total_users}

📅 Дата отчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}
🤖 Сгенерировано автоматически"""
        
        # Отправляем отчет в admin chat
        from telegram import Bot
        bot = Bot(settings.BOT_TOKEN)
        
        admin_chat_id = settings.ADMIN_CHAT_ID or settings.ADMIN_USERNAME
        
        if admin_chat_id:
            await bot.send_message(chat_id=admin_chat_id, text=report)
            logger.info("Ежедневный отчет отправлен администратору")
            
            return JSONResponse({
                "success": True,
                "message": "Ежедневный отчет отправлен"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "Не настроен admin chat ID"
            }, status_code=400)
        
    except Exception as e:
        logger.error(f"Ошибка отправки ежедневного отчета: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Ошибка отправки отчета: {str(e)}"
        }, status_code=500)


@admin_router.post("/api/notifications/avito-webhook")
async def avito_notification_webhook(request: Request):
    """Webhook для получения уведомлений от Avito"""
    try:
        data = await request.json()
        
        # Логируем все входящие данные от Авито
        logger.info(f"Получено уведомление от Авито: {data}")
        
        # Парсим данные от Авито
        message_type = data.get('type', 'message')  # новое сообщение, изменение статуса и т.д.
        chat_id = data.get('chat_id')
        message = data.get('message', {})
        
        if message_type == 'message' and chat_id and message:
            # Находим всех продажников, которые должны получить уведомления
            with get_db_context() as db:
                salespeople = db.query(AdminUser).filter(
                    AdminUser.role.in_(['salesperson', 'sales']),
                    AdminUser.is_active == True
                ).all()
                
                # Отправляем уведомления всем продажникам
                from telegram import Bot
                bot = Bot(settings.BOT_TOKEN)
                
                for salesperson in salespeople:
                    if salesperson.telegram_id:
                        try:
                            notification_text = f"""📩 Новое сообщение в Авито!
                            
🔗 Чат ID: {chat_id}
👤 От: {message.get('author_name', 'Неизвестно')}
📝 Сообщение: {message.get('content', message.get('text', 'Без текста'))}
⏰ Время: {datetime.now().strftime('%H:%M:%S')}

👈 Перейти в админ-панель для ответа"""

                            await bot.send_message(
                                chat_id=salesperson.telegram_id,
                                text=notification_text
                            )
                            
                            logger.info(f"Уведомление отправлено продажнику {salesperson.username}")
                            
                        except Exception as e:
                            logger.error(f"Не удалось отправить уведомление продажнику {salesperson.username}: {e}")
                
                return JSONResponse({
                    "success": True,
                    "message": "Уведомления отправлены продажникам"
                })
        
        return JSONResponse({
            "success": True,
            "message": "Webhook обработан"
        })
        
    except Exception as e:
        logger.error(f"Ошибка обработки Авито webhook: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Ошибка: {str(e)}"
        }, status_code=500)


@admin_router.post("/api/notifications/test-avito")
async def test_avito_notification(request: Request):
    """Тестовое уведомление для Авито"""
    try:
        # Симулируем получение сообщения с Авито
        test_data = {
            "type": "message",
            "chat_id": "test_chat_123",
            "message": {
                "author_name": "Тестовый клиент",
                "content": "Здравствуйте! Интересует ваша услуга. Можете рассказать подробнее?",
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Прямо отправляем уведомление всем продавцам
        from app.services.notification_service import notification_service
        
        message = f"""🔔 <b>Новое сообщение с Авито</b>
        
👤 <b>От:</b> {test_data['message']['author_name']}
💬 <b>Сообщение:</b> {test_data['message']['content']}
🕐 <b>Время:</b> {test_data['message']['created_at']}
        
<i>Это тестовое уведомление от админ-панели</i>"""
        
        # Отправляем всем продавцам
        with get_db_context() as db:
            salespersons = db.query(AdminUser).filter(
                AdminUser.role == 'salesperson',
                AdminUser.telegram_id.isnot(None),
                AdminUser.is_active == True
            ).all()
            
            sent_count = 0
            for person in salespersons:
                try:
                    await notification_service.send_notification(
                        chat_id=person.telegram_id,
                        message=message
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления {person.username}: {e}")
        
        return JSONResponse({
            "success": True,
            "message": f"Тестовое уведомление отправлено {sent_count} продавцам"
        })
        
    except Exception as e:
        logger.error(f"Ошибка тестирования Авито уведомлений: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Ошибка: {str(e)}"
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

def _get_full_analytics_data() -> Dict[str, Any]:
    """Получение полных данных аналитики из базы данных"""
    try:
        with get_db_context() as db:
            # Общая статистика проектов
            total_projects = db.query(Project).count()
            active_projects = db.query(Project).filter(
                Project.status.in_(['new', 'review', 'accepted', 'in_progress', 'testing'])
            ).count()
            completed_projects = db.query(Project).filter(Project.status == 'completed').count()
            cancelled_projects = db.query(Project).filter(Project.status == 'cancelled').count()
            
            # Финансовая статистика
            total_estimated_cost = db.query(func.sum(Project.estimated_cost)).scalar() or 0
            total_completed_cost = db.query(func.sum(Project.final_cost)).filter(
                Project.status == 'completed'
            ).scalar() or 0
            
            # Открытые заказы (не завершенные)
            open_orders_sum = db.query(func.sum(Project.estimated_cost)).filter(
                Project.status.in_(['new', 'review', 'accepted', 'in_progress', 'testing'])
            ).scalar() or 0
            
            # Платежи клиентов
            total_client_payments = db.query(func.sum(Project.client_paid_total)).scalar() or 0
            
            # Выплаты исполнителям
            total_executor_payments = db.query(func.sum(Project.executor_paid_total)).scalar() or 0
            
            # Средние показатели
            avg_project_cost = db.query(func.avg(Project.estimated_cost)).scalar() or 0
            avg_completion_time = db.query(func.avg(Project.estimated_hours)).scalar() or 0
            
            # Статистика по статусам
            status_stats = {}
            status_names = {
                'new': 'Новые',
                'review': 'На рассмотрении', 
                'accepted': 'Приняты',
                'in_progress': 'В работе',
                'testing': 'Тестирование',
                'completed': 'Завершены',
                'cancelled': 'Отменены'
            }
            
            for status_key, status_name in status_names.items():
                count = db.query(Project).filter(Project.status == status_key).count()
                sum_cost = db.query(func.sum(Project.estimated_cost)).filter(
                    Project.status == status_key
                ).scalar() or 0
                status_stats[status_key] = {
                    'name': status_name,
                    'count': count,
                    'sum': float(sum_cost)
                }
            
            # Статистика по типам проектов
            type_stats = {}
            project_types = db.query(Project.project_type, func.count(Project.id)).group_by(
                Project.project_type
            ).all()
            
            for project_type, count in project_types:
                if project_type:
                    type_stats[project_type] = count
            
            # Статистика пользователей
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.projects.any()).count()
            
            # Прибыль (разница между платежами клиентов и выплатами исполнителям)
            profit = total_client_payments - total_executor_payments
            
            # Конверсия завершенных проектов
            completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
            
            # Средняя стоимость завершенного проекта
            avg_completed_cost = db.query(func.avg(Project.final_cost)).filter(
                Project.status == 'completed'
            ).scalar() or 0
            
            return {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'cancelled_projects': cancelled_projects,
                'total_estimated_cost': float(total_estimated_cost),
                'total_completed_cost': float(total_completed_cost),
                'open_orders_sum': float(open_orders_sum),
                'total_client_payments': float(total_client_payments),
                'total_executor_payments': float(total_executor_payments),
                'profit': float(profit),
                'avg_project_cost': float(avg_project_cost),
                'avg_completed_cost': float(avg_completed_cost),
                'avg_completion_time': float(avg_completion_time),
                'completion_rate': float(completion_rate),
                'status_stats': status_stats,
                'type_stats': type_stats,
                'total_users': total_users,
                'active_users': active_users
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения данных аналитики: {e}")
        return {}

def _generate_analytics_html(data: Dict[str, Any]) -> str:
    """Генерация HTML страницы с полной аналитикой"""
    
    # Если данные пустые, показываем ошибку
    if not data:
        return """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Аналитика - Ошибка</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>Ошибка загрузки аналитики</h1>
                <p>Не удалось загрузить данные аналитики.</p>
                <a href="/admin/" class="btn btn-primary">Вернуться на главную</a>
            </div>
        </body>
        </html>
        """
    
    # Форматирование чисел
    def format_number(num):
        if num is None:
            return "0"
        return f"{int(num):,}".replace(",", " ")
    
    def format_currency(num):
        if num is None:
            return "0₽"
        return f"{int(num):,}₽".replace(",", " ")
    
    # Статистика по статусам для графика
    status_labels = []
    status_data = []
    status_colors = {
        'new': '#6366f1',
        'review': '#f59e0b', 
        'accepted': '#22c55e',
        'in_progress': '#3b82f6',
        'testing': '#8b5cf6',
        'completed': '#10b981',
        'cancelled': '#ef4444'
    }
    
    for status_key, status_info in data.get('status_stats', {}).items():
        if status_info['count'] > 0:
            status_labels.append(f"'{status_info['name']}'")
            status_data.append(status_info['count'])
    
    status_labels_str = "[" + ", ".join(status_labels) + "]"
    status_data_str = "[" + ", ".join(map(str, status_data)) + "]"
    status_colors_str = "[" + ", ".join([f"'{status_colors.get(k, '#64748b')}'" for k in data.get('status_stats', {}).keys() if data['status_stats'][k]['count'] > 0]) + "]"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Полная аналитика - Админ панель</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                font-family: 'Comfortaa', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .analytics-container {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                margin: 0 auto;
                max-width: 1400px;
            }}
            
            .stat-card {{
                background: linear-gradient(135deg, #f8fafc, #e2e8f0);
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                height: 100%;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: none;
                position: relative;
                overflow: hidden;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            }}
            
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #6366f1, #3b82f6);
            }}
            
            .stat-value {{
                font-size: 2.5rem;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 8px;
            }}
            
            .stat-label {{
                color: #64748b;
                font-weight: 500;
                font-size: 0.95rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stat-icon {{
                font-size: 2.5rem;
                margin-bottom: 15px;
                opacity: 0.8;
            }}
            
            .section-title {{
                font-size: 1.75rem;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 25px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .chart-container {{
                background: white;
                border-radius: 16px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                height: 400px;
                margin-bottom: 30px;
            }}
            
            .profit-positive {{
                color: #22c55e !important;
            }}
            
            .profit-negative {{
                color: #ef4444 !important;
            }}
            
            .status-table {{
                background: white;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}
            
            .status-table th {{
                background: linear-gradient(135deg, #64748b, #475569);
                color: white;
                font-weight: 600;
                padding: 15px;
                border: none;
            }}
            
            .status-table td {{
                padding: 15px;
                border-color: #e2e8f0;
                vertical-align: middle;
            }}
            
            .status-badge {{
                padding: 8px 12px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 0.85rem;
            }}
            
            .back-button {{
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 1000;
                background: rgba(255,255,255,0.9);
                backdrop-filter: blur(10px);
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 500;
                text-decoration: none;
                color: #1e293b;
                transition: all 0.3s ease;
            }}
            
            .back-button:hover {{
                background: white;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                color: #1e293b;
                text-decoration: none;
            }}
            
            @media (max-width: 768px) {{
                .analytics-container {{
                    padding: 20px;
                    margin: 10px;
                }}
                
                .stat-value {{
                    font-size: 2rem;
                }}
                
                .section-title {{
                    font-size: 1.5rem;
                }}
            }}
        </style>
    </head>
    <body>
        <a href="/admin/" class="back-button">
            <i class="fas fa-arrow-left me-2"></i>Назад в админ панель
        </a>
        
        <div class="analytics-container">
            <div class="text-center mb-5">
                <h1 class="display-4 fw-bold text-primary mb-2">
                    <i class="fas fa-chart-line me-3"></i>Полная аналитика
                </h1>
                <p class="text-muted fs-5">Комплексный анализ бизнес-показателей</p>
            </div>
            
            <!-- Основные показатели -->
            <div class="section-title">
                <i class="fas fa-tachometer-alt text-primary"></i>
                Основные показатели
            </div>
            
            <div class="row g-4 mb-5">
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-primary">
                            <i class="fas fa-project-diagram"></i>
                        </div>
                        <div class="stat-value">{format_number(data.get('total_projects', 0))}</div>
                        <div class="stat-label">Всего проектов</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-warning">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="stat-value">{format_number(data.get('active_projects', 0))}</div>
                        <div class="stat-label">Активных проектов</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-success">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="stat-value">{format_number(data.get('completed_projects', 0))}</div>
                        <div class="stat-label">Завершено</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-info">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div class="stat-value">{format_number(data.get('completion_rate', 0))}%</div>
                        <div class="stat-label">Конверсия</div>
                    </div>
                </div>
            </div>
            
            <!-- Финансовые показатели -->
            <div class="section-title">
                <i class="fas fa-money-bill-wave text-success"></i>
                Финансовые показатели
            </div>
            
            <div class="row g-4 mb-5">
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-primary">
                            <i class="fas fa-coins"></i>
                        </div>
                        <div class="stat-value">{format_currency(data.get('total_estimated_cost', 0))}</div>
                        <div class="stat-label">Общая стоимость</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-warning">
                            <i class="fas fa-hourglass-half"></i>
                        </div>
                        <div class="stat-value">{format_currency(data.get('open_orders_sum', 0))}</div>
                        <div class="stat-label">Открытые заказы</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-success">
                            <i class="fas fa-hand-holding-usd"></i>
                        </div>
                        <div class="stat-value">{format_currency(data.get('total_client_payments', 0))}</div>
                        <div class="stat-label">Платежи клиентов</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon {'text-success' if data.get('profit', 0) >= 0 else 'text-danger'}">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="stat-value {'profit-positive' if data.get('profit', 0) >= 0 else 'profit-negative'}">{format_currency(data.get('profit', 0))}</div>
                        <div class="stat-label">Прибыль</div>
                    </div>
                </div>
            </div>
            
            <!-- Дополнительные показатели -->
            <div class="section-title">
                <i class="fas fa-chart-bar text-info"></i>
                Дополнительные показатели
            </div>
            
            <div class="row g-4 mb-5">
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-secondary">
                            <i class="fas fa-calculator"></i>
                        </div>
                        <div class="stat-value">{format_currency(data.get('avg_project_cost', 0))}</div>
                        <div class="stat-label">Средняя стоимость</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-info">
                            <i class="fas fa-star"></i>
                        </div>
                        <div class="stat-value">{format_currency(data.get('avg_completed_cost', 0))}</div>
                        <div class="stat-label">Средняя завершенных</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-warning">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="stat-value">{format_number(data.get('total_users', 0))}</div>
                        <div class="stat-label">Всего пользователей</div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6">
                    <div class="stat-card">
                        <div class="stat-icon text-success">
                            <i class="fas fa-user-check"></i>
                        </div>
                        <div class="stat-value">{format_number(data.get('active_users', 0))}</div>
                        <div class="stat-label">Активных пользователей</div>
                    </div>
                </div>
            </div>
            
            <!-- График распределения по статусам -->
            <div class="section-title">
                <i class="fas fa-pie-chart text-primary"></i>
                Распределение проектов по статусам
            </div>
            
            <div class="row mb-5">
                <div class="col-lg-6">
                    <div class="chart-container">
                        <canvas id="statusChart"></canvas>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="status-table">
                        <table class="table table-hover mb-0">
                            <thead>
                                <tr>
                                    <th>Статус</th>
                                    <th>Количество</th>
                                    <th>Сумма</th>
                                </tr>
                            </thead>
                            <tbody>"""
    
    # Добавляем строки таблицы статусов
    for status_key, status_info in data.get('status_stats', {}).items():
        badge_color = {
            'new': 'bg-primary',
            'review': 'bg-warning', 
            'accepted': 'bg-success',
            'in_progress': 'bg-info',
            'testing': 'bg-secondary',
            'completed': 'bg-success',
            'cancelled': 'bg-danger'
        }.get(status_key, 'bg-secondary')
        
        html_content += f"""
                                <tr>
                                    <td>
                                        <span class="status-badge {badge_color} text-white">
                                            {status_info['name']}
                                        </span>
                                    </td>
                                    <td><strong>{format_number(status_info['count'])}</strong></td>
                                    <td><strong>{format_currency(status_info['sum'])}</strong></td>
                                </tr>"""
    
    html_content += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Выплаты исполнителям -->
            <div class="section-title">
                <i class="fas fa-hand-holding-usd text-warning"></i>
                Выплаты исполнителям
            </div>
            
            <div class="row g-4 mb-5">
                <div class="col-lg-6">
                    <div class="stat-card">
                        <div class="stat-icon text-warning">
                            <i class="fas fa-money-check-alt"></i>
                        </div>
                        <div class="stat-value">{format_currency(data.get('total_executor_payments', 0))}</div>
                        <div class="stat-label">Всего выплачено исполнителям</div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="stat-card">
                        <div class="stat-icon text-info">
                            <i class="fas fa-balance-scale"></i>
                        </div>
                        <div class="stat-value">{format_currency(data.get('total_client_payments', 0) - data.get('total_executor_payments', 0))}</div>
                        <div class="stat-label">Баланс (Клиенты - Исполнители)</div>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-5">
                <small class="text-muted">
                    <i class="fas fa-clock me-1"></i>
                    Данные обновлены: {datetime.now().strftime('%d.%m.%Y %H:%M')}
                </small>
            </div>
        </div>
        
        <script>
            // График распределения по статусам
            const ctx = document.getElementById('statusChart').getContext('2d');
            const statusChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: {status_labels_str},
                    datasets: [{{
                        data: {status_data_str},
                        backgroundColor: {status_colors_str},
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 20,
                                font: {{
                                    family: 'Comfortaa',
                                    size: 12
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.label + ': ' + context.parsed + ' проектов';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content


# =============================================================================
# ПУБЛИЧНЫЕ API ENDPOINTS ДЛЯ ПОРТФОЛИО (для бота)
# =============================================================================

@admin_router.get("/api/portfolio/public/categories")
async def get_public_portfolio_categories():
    """Получить список категорий портфолио для бота"""
    try:
        with get_db_context() as db:
            # Получаем уникальные категории из видимых проектов
            categories_raw = db.query(Portfolio.category).filter(
                Portfolio.is_visible == True
            ).distinct().all()
            
            # Преобразуем в список с названиями
            category_map = {
                "telegram_bots": "🤖 Telegram боты",
                "web_development": "🌐 Веб-разработка", 
                "mobile_apps": "📱 Мобильные приложения",
                "ai_integration": "🧠 AI интеграции",
                "automation": "⚙️ Автоматизация",
                "ecommerce": "🛒 E-commerce",
                "other": "🔧 Другое"
            }
            
            categories = []
            for (cat,) in categories_raw:
                if cat in category_map:
                    categories.append({
                        "key": cat,
                        "name": category_map[cat],
                        "emoji": category_map[cat].split()[0]
                    })
            
            return {
                "success": True,
                "categories": categories
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения категорий портфолио: {e}")
        return {
            "success": False,
            "error": str(e),
            "categories": []
        }

@admin_router.get("/api/portfolio/public/featured")
async def get_public_featured_portfolio():
    """Получить рекомендуемые проекты портфолио для бота"""
    try:
        with get_db_context() as db:
            projects = db.query(Portfolio).filter(
                Portfolio.is_visible == True,
                Portfolio.is_featured == True
            ).order_by(Portfolio.sort_order.asc(), Portfolio.created_at.desc()).limit(10).all()
            
            projects_data = []
            for project in projects:
                project_dict = project.to_dict()
                
                # Добавляем полные URL для изображений
                if project_dict.get('main_image'):
                    project_dict['main_image'] = get_image_url(project_dict['main_image'])
                
                if project_dict.get('image_paths'):
                    project_dict['image_paths'] = [
                        get_image_url(img) for img in project_dict['image_paths']
                    ]
                
                projects_data.append(project_dict)
            
            return {
                "success": True,
                "projects": projects_data,
                "count": len(projects_data)
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения рекомендуемых проектов: {e}")
        return {
            "success": False,
            "error": str(e),
            "projects": []
        }

@admin_router.get("/api/portfolio/public/category/{category}")
async def get_public_portfolio_by_category(category: str, page: int = 0, limit: int = 5):
    """Получить проекты портфолио по категории для бота"""
    try:
        with get_db_context() as db:
            offset = page * limit
            
            projects = db.query(Portfolio).filter(
                Portfolio.is_visible == True,
                Portfolio.category == category
            ).order_by(
                Portfolio.sort_order.asc(), 
                Portfolio.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            total_count = db.query(Portfolio).filter(
                Portfolio.is_visible == True,
                Portfolio.category == category
            ).count()
            
            projects_data = []
            for project in projects:
                project_dict = project.to_dict()
                
                # Добавляем полные URL для изображений
                if project_dict.get('main_image'):
                    project_dict['main_image'] = get_image_url(project_dict['main_image'])
                
                if project_dict.get('image_paths'):
                    project_dict['image_paths'] = [
                        get_image_url(img) for img in project_dict['image_paths']
                    ]
                
                projects_data.append(project_dict)
            
            return {
                "success": True,
                "projects": projects_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "has_more": (offset + limit) < total_count
                }
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения проектов категории {category}: {e}")
        return {
            "success": False,
            "error": str(e),
            "projects": []
        }

@admin_router.get("/api/portfolio/public/{project_id}")
async def get_public_portfolio_item(project_id: int):
    """Получить детальную информацию о проекте портфолио для бота"""
    try:
        with get_db_context() as db:
            project = db.query(Portfolio).filter(
                Portfolio.id == project_id,
                Portfolio.is_visible == True
            ).first()
            
            if not project:
                return {
                    "success": False,
                    "error": "Проект не найден или недоступен"
                }
            
            # Увеличиваем счетчик просмотров
            project.views_count = (project.views_count or 0) + 1
            db.commit()
            
            project_dict = project.to_dict()
            
            # Добавляем полные URL для изображений
            if project_dict.get('main_image'):
                project_dict['main_image'] = get_image_url(project_dict['main_image'])
            
            if project_dict.get('image_paths'):
                project_dict['image_paths'] = [
                    get_image_url(img) for img in project_dict['image_paths']
                ]
            
            return {
                "success": True,
                "project": project_dict
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения проекта {project_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@admin_router.get("/api/portfolio/public/list")
async def get_public_portfolio_list(
    category: str = None, 
    featured: bool = None,
    page: int = 0, 
    limit: int = 5
):
    """Получить список проектов портфолио с фильтрами для бота"""
    try:
        with get_db_context() as db:
            query = db.query(Portfolio).filter(Portfolio.is_visible == True)
            
            if category:
                query = query.filter(Portfolio.category == category)
            
            if featured is not None:
                query = query.filter(Portfolio.is_featured == featured)
            
            total_count = query.count()
            offset = page * limit
            
            projects = query.order_by(
                Portfolio.sort_order.asc(), 
                Portfolio.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            projects_data = []
            for project in projects:
                project_dict = project.to_dict()
                
                # Добавляем полные URL для изображений
                if project_dict.get('main_image'):
                    project_dict['main_image'] = get_image_url(project_dict['main_image'])
                
                if project_dict.get('image_paths'):
                    project_dict['image_paths'] = [
                        get_image_url(img) for img in project_dict['image_paths']
                    ]
                
                projects_data.append(project_dict)
            
            return {
                "success": True,
                "projects": projects_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "has_more": (offset + limit) < total_count
                }
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения списка портфолио: {e}")
        return {
            "success": False,
            "error": str(e),
            "projects": []
        }

@admin_router.post("/api/portfolio/public/{project_id}/like")
async def like_portfolio_project(project_id: int):
    """Лайкнуть проект портфолио"""
    try:
        with get_db_context() as db:
            project = db.query(Portfolio).filter(
                Portfolio.id == project_id,
                Portfolio.is_visible == True
            ).first()
            
            if not project:
                return {
                    "success": False,
                    "error": "Проект не найден"
                }
            
            # Увеличиваем счетчик лайков
            project.likes_count = (project.likes_count or 0) + 1
            db.commit()
            
            return {
                "success": True,
                "likes": project.likes_count,
                "message": "Спасибо за лайк!"
            }
            
    except Exception as e:
        logger.error(f"Ошибка лайка проекта {project_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# API для публикации портфолио в Telegram
@admin_router.post("/api/portfolio/{portfolio_id}/publish")
async def publish_to_telegram(portfolio_id: int, username: str = Depends(authenticate)):
    """Опубликовать элемент портфолио в Telegram канал"""
    try:
        with get_db_context() as db:
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
            
            # Импортируем сервис публикации
            try:
                from ...services.portfolio_telegram_service import portfolio_telegram_service
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
            except ImportError:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Telegram сервис недоступен"}
                )
        
    except Exception as e:
        logger.error(f"Ошибка публикации в Telegram: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Внутренняя ошибка сервера"}
        )

@admin_router.put("/api/portfolio/{portfolio_id}/update-published")
async def update_published_item(portfolio_id: int, username: str = Depends(authenticate)):
    """Обновить уже опубликованный элемент портфолио в Telegram канале"""
    try:
        with get_db_context() as db:
            # Получаем элемент портфолио
            portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio_item:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Элемент портфолио не найден"}
                )
            
            # Импортируем сервис публикации
            try:
                from ...services.portfolio_telegram_service import portfolio_telegram_service
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
            except ImportError:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Telegram сервис недоступен"}
                )
        
    except Exception as e:
        logger.error(f"Ошибка обновления в Telegram: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Внутренняя ошибка сервера"}
        )

@admin_router.delete("/api/portfolio/{portfolio_id}/unpublish")
async def unpublish_from_telegram(portfolio_id: int, username: str = Depends(authenticate)):
    """Удалить элемент портфолио из Telegram канала"""
    try:
        with get_db_context() as db:
            # Получаем элемент портфолио
            portfolio_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio_item:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Элемент портфолио не найден"}
                )
            
            # Импортируем сервис публикации
            try:
                from ...services.portfolio_telegram_service import portfolio_telegram_service
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
            except ImportError:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Telegram сервис недоступен"}
                )
        
    except Exception as e:
        logger.error(f"Ошибка удаления из Telegram: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Внутренняя ошибка сервера"}
        )

# Роуты для аутентификации
@admin_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа в админ-панель"""
    return templates.TemplateResponse("login.html", {
        "request": request
    })

@admin_router.post("/logout")
async def logout():
    """Выход из системы"""
    return RedirectResponse(url="/admin/login", status_code=302)

@admin_router.get("/logout-auth")
async def logout_auth(request: Request, switch: str = None):
    """Специальный роут для очистки HTTP Basic Auth"""
    from fastapi.responses import HTMLResponse
    
    # Определяем URL для перенаправления
    redirect_url = "/admin/login?switch=true" if switch else "/admin/login"
    
    # HTML страница которая очищает аутентификацию и перенаправляет
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Выход из системы</title>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: 'Arial', sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
            }}
            .logout-container {{ 
                background: white; 
                padding: 2rem; 
                border-radius: 10px; 
                text-align: center; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 1rem auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="logout-container">
            <h3>🚪 Выход из системы</h3>
            <div class="spinner"></div>
            <p>Очистка данных аутентификации...</p>
            <p><small>Если перенаправление не произошло автоматически, <a href="{redirect_url}">нажмите здесь</a></small></p>
        </div>
        
        <script>
            // Попытка очистить HTTP Basic Auth через подмену заголовков
            function clearAuth() {{
                // Создаем XMLHttpRequest с неверными учетными данными для сброса кэша
                fetch('/admin/', {{
                    method: 'GET',
                    headers: {{
                        'Authorization': 'Basic ' + btoa('logout:logout')
                    }}
                }}).catch(() => {{
                    // Игнорируем ошибку - это ожидаемо
                }}).finally(() => {{
                    // Перенаправляем на страницу логина через 2 секунды
                    setTimeout(() => {{
                        window.location.href = '{redirect_url}';
                    }}, 2000);
                }});
            }}
            
            // Запускаем очистку при загрузке страницы
            document.addEventListener('DOMContentLoaded', clearAuth);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content, status_code=200)


# Основные HTML роуты
@admin_router.get("/permissions", response_class=HTMLResponse)
async def permissions_page(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """Страница управления правами"""
    if not auth_service.verify_credentials(credentials):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    return templates.TemplateResponse("permissions_management.html", {"request": request})

@admin_router.get("/notifications", response_class=HTMLResponse) 
async def notifications_page(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """Страница уведомлений"""
    if not auth_service.verify_credentials(credentials):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    
    return templates.TemplateResponse("notifications.html", {"request": request})

# Создание FastAPI приложения
app = FastAPI(title="Admin Panel")

# Корневой редирект на админку
@app.get("/")
async def root():
    return RedirectResponse(url="/admin/", status_code=302)

# Подключение роутера к приложению с префиксом /admin
app.include_router(admin_router, prefix="/admin")

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/admin/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Подключение шаблонов
templates = Jinja2Templates(directory="app/admin/templates")

# Добавление middleware
auth_service = AuthService()
security = HTTPBasic()

# Role middleware is applied via decorators in individual routes
role_middleware = RoleMiddleware()

