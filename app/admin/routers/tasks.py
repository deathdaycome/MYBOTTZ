"""
Router для управления задачами
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Form, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from typing import Optional, List
import json
from sqlalchemy import desc, or_, cast, String
from sqlalchemy.orm import joinedload
import os
import uuid
from pathlib import Path

from ...config.logging import get_logger
from ...database.database import get_db_context
from ...database.models import Task, TaskComment, AdminUser, Project
from ..middleware.auth import get_current_admin_user
from ...services.task_notification_service import task_notification_service
from fastapi import Cookie
from ..middleware.roles import RoleMiddleware

logger = get_logger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/admin/templates")

def translate_status(status: str) -> str:
    """Перевод статуса задачи на русский"""
    translations = {
        "pending": "Ожидает",
        "in_progress": "В работе",
        "completed": "Выполнено"
    }
    return translations.get(status, status)

def get_current_user_from_request(request: Request):
    """Получить текущего пользователя из запроса"""
    try:
        # Попробуем получить из заголовка авторизации
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Basic "):
            import base64
            from ..middleware.auth import security, require_admin_auth
            from fastapi.security import HTTPBasicCredentials
            
            # Декодируем Basic auth
            try:
                credentials_str = auth_header[6:]  # Убираем "Basic "
                decoded = base64.b64decode(credentials_str).decode('utf-8')
                username, password = decoded.split(':', 1)
                credentials = HTTPBasicCredentials(username=username, password=password)
                return require_admin_auth(credentials)
            except Exception as e:
                logger.error(f"Ошибка декодирования Basic auth: {e}")
        
        # Если не удалось получить из заголовка, возвращаем дефолтного пользователя для тестирования
        # В продакшене здесь должна быть обработка сессий или cookies
        return {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com", 
            "first_name": "Администратор",
            "last_name": "",
            "role": "owner",
            "is_active": True
        }
    except Exception as e:
        logger.error(f"Ошибка получения пользователя: {e}")
        raise HTTPException(status_code=401, detail="Не авторизован")

@router.get("/archive", response_class=HTMLResponse)
async def tasks_archive_page(request: Request, current_user: dict = Depends(get_current_admin_user)):
    """Страница архива задач"""
    try:
        with get_db_context() as db:
            # Получаем элементы навигации
            from app.admin.app import get_navigation_items
            navigation_items = get_navigation_items(current_user['role'])

            # Получаем список сотрудников для фильтра
            employees = db.query(AdminUser).filter(
                AdminUser.is_active == True,
                AdminUser.role.in_(['executor', 'manager'])
            ).all()

            return templates.TemplateResponse("tasks_archive.html", {
                "request": request,
                "current_user": current_user,
                "current_user_id": current_user['id'],
                "username": current_user['username'],
                "user_role": current_user['role'],
                "navigation_items": navigation_items,
                "employees": employees
            })

    except Exception as e:
        logger.error(f"Ошибка при загрузке архива задач: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при загрузке архива задач")

@router.get("/kanban", response_class=HTMLResponse)
async def kanban_board_page(request: Request, current_user: dict = Depends(get_current_admin_user)):
    """Страница канбан-доски с исполнителями (только для владельца)"""
    try:
        # Проверяем, что пользователь - владелец
        if current_user["role"] != "owner":
            raise HTTPException(status_code=403, detail="Доступ запрещен")

        with get_db_context() as db:
            # Получаем элементы навигации
            from app.admin.app import get_navigation_items
            navigation_items = get_navigation_items(current_user['role'])

            return templates.TemplateResponse("tasks_kanban.html", {
                "request": request,
                "current_user": current_user,
                "current_user_id": current_user['id'],
                "username": current_user['username'],
                "user_role": current_user['role'],
                "navigation_items": navigation_items
            })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при загрузке канбан-доски: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при загрузке канбан-доски")

@router.get("/user/my-tasks", response_class=HTMLResponse)
async def my_tasks_page(request: Request, current_user: dict = Depends(get_current_admin_user)):
    """Страница 'Мои задачи' для всех пользователей с канбан-доской"""
    try:
        with get_db_context() as db:
            # По умолчанию все пользователи (включая владельца) видят только свои задачи
            query = db.query(Task).filter(Task.assigned_to_id == current_user["id"])
            tasks = query.order_by(Task.created_at.desc()).all()
            
            # Получаем список всех исполнителей для владельца
            executors = []
            if current_user["role"] == "owner":
                executors = db.query(AdminUser).filter(
                    AdminUser.role.in_(["executor", "owner"]),
                    AdminUser.is_active == True
                ).all()
            
            # Преобразуем задачи в словари
            tasks_data = []
            for task in tasks:
                # Загружаем связанные объекты
                if task.created_by_id:
                    task.created_by = db.query(AdminUser).filter(AdminUser.id == task.created_by_id).first()
                if task.assigned_to_id:
                    task.assigned_to = db.query(AdminUser).filter(AdminUser.id == task.assigned_to_id).first()
                
                # Преобразуем в словарь с дополнительными полями
                task_dict = task.to_dict()
                task_dict["is_overdue"] = task.is_overdue
                task_dict["days_until_deadline"] = task.days_until_deadline
                # Определяем, может ли пользователь удалять задачу
                # Исполнители могут удалять только свои задачи (не от админа)
                # Владелец может удалять любые задачи
                task_dict["can_delete"] = (
                    current_user["role"] == "owner" or 
                    (task.created_by_id == current_user["id"] and not task_dict.get("created_by_admin", False))
                )
                # Добавляем флаг, что задача создана админом
                task_dict["created_by_admin"] = (
                    task.created_by and 
                    task.created_by.role == "owner" and 
                    task.created_by_id != task.assigned_to_id
                )
                tasks_data.append(task_dict)
            
            # Статистика
            stats = {
                "total": len(tasks_data),
                "pending": len([t for t in tasks_data if t["status"] == "pending"]),
                "in_progress": len([t for t in tasks_data if t["status"] == "in_progress"]),
                "completed": len([t for t in tasks_data if t["status"] == "completed"]),
                "overdue": len([t for t in tasks_data if t["is_overdue"]])
            }
            
            # Получаем элементы навигации
            from app.admin.app import get_navigation_items
            navigation_items = get_navigation_items(current_user['role'])
            
            return templates.TemplateResponse("my_tasks.html", {
                "request": request,
                "tasks": tasks_data,
                "stats": stats,
                "current_user": current_user,
                "current_user_id": current_user['id'],
                "username": current_user['username'],
                "user_role": current_user['role'],
                "navigation_items": navigation_items,
                "executors": executors  # Добавляем список исполнителей
            })
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке страницы 'Мои задачи': {e}")
        raise HTTPException(status_code=500, detail="Ошибка при загрузке задач")

# Старый HTML endpoint удалён - теперь используется JSON API для React

@router.get("/{task_id}", response_class=HTMLResponse)
async def task_detail_page(request: Request, task_id: int, current_user: dict = Depends(get_current_admin_user)):
    """Страница детального просмотра задачи"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise HTTPException(status_code=404, detail="Задача не найдена")
            
            # Проверяем права доступа
            if current_user["role"] == "executor" and task.assigned_to_id != current_user["id"]:
                raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
            
            # Получаем элементы навигации
            from app.admin.app import get_navigation_items
            navigation_items = get_navigation_items(current_user['role'])
            
            return templates.TemplateResponse("task_detail.html", {
                "request": request,
                "task": task,
                "current_user": current_user,
                "username": current_user['username'],
                "user_role": current_user['role'],
                "navigation_items": navigation_items
            })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при загрузке задачи {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при загрузке задачи")

def _get_tasks_logic(
    request: Request,
    status: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    created_by_id: Optional[int] = None,
    priority: Optional[str] = None,
    per_page: Optional[int] = 100
):
    """Общая логика получения задач"""
    try:
        # Получаем текущего пользователя из запроса
        current_user = get_current_user_from_request(request)

        with get_db_context() as db:
            # Строим базовый запрос
            query = db.query(Task).options(
                joinedload(Task.created_by),
                joinedload(Task.assigned_to)
            )

            # Владелец видит все задачи, исполнители только свои
            if current_user["role"] != "owner":
                query = query.filter(Task.assigned_to_id == current_user["id"])

            # Применяем фильтры
            if status:
                query = query.filter(Task.status == status)
            if assigned_to_id:
                query = query.filter(Task.assigned_to_id == assigned_to_id)
            if created_by_id:
                query = query.filter(Task.created_by_id == created_by_id)
            if priority:
                query = query.filter(Task.priority == priority)

            # Сортировка и лимит
            query = query.order_by(Task.created_at.desc()).limit(per_page)

            # Выполняем запрос
            all_tasks = query.all()

            # Фильтруем архивные задачи
            tasks = [
                task for task in all_tasks
                if not task.task_metadata.get('archived', False)
            ]

            # Преобразуем задачи в словари
            tasks_data = []
            for task in tasks:
                task_dict = task.to_dict()
                task_dict["is_overdue"] = task.is_overdue
                task_dict["days_until_deadline"] = task.days_until_deadline

                # Имена создателя и исполнителя
                task_dict["created_by_name"] = f"{task.created_by.first_name} {task.created_by.last_name}" if task.created_by else "Неизвестно"
                task_dict["assigned_to_name"] = f"{task.assigned_to.first_name} {task.assigned_to.last_name}" if task.assigned_to else "Не назначен"

                # Может ли пользователь удалить задачу
                task_dict["can_delete"] = (
                    current_user["role"] == "owner" or
                    (task.created_by_id == current_user["id"])
                )

                tasks_data.append(task_dict)

            logger.info(f"Возвращено {len(tasks_data)} задач для пользователя {current_user['username']}")

            return {"success": True, "tasks": tasks_data}

    except Exception as e:
        logger.error(f"Ошибка получения задач: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e), "tasks": []}


# Wrapper routes для поддержки обоих вариантов путей (с и без trailing slash)
@router.get("/", response_class=JSONResponse)
def get_tasks_with_slash(
    request: Request,
    status: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    created_by_id: Optional[int] = None,
    priority: Optional[str] = None,
    per_page: Optional[int] = 100
):
    """Получить список задач с фильтрацией - вариант с trailing slash"""
    return _get_tasks_logic(request, status, assigned_to_id, created_by_id, priority, per_page)


@router.get("", response_class=JSONResponse)
def get_tasks_no_slash(
    request: Request,
    status: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    created_by_id: Optional[int] = None,
    priority: Optional[str] = None,
    per_page: Optional[int] = 100
):
    """Получить список задач с фильтрацией - вариант без trailing slash"""
    return _get_tasks_logic(request, status, assigned_to_id, created_by_id, priority, per_page)


# Общая логика создания задачи
async def _create_task_logic(
    request: Request,
    current_user: dict
):
    """Общая логика создания задачи"""
    try:

        # Определяем тип контента
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            # JSON запрос (от канбан-доски)
            body = await request.json()
            title = body.get("title")
            description = body.get("description", "")
            assigned_to_id = body.get("assigned_to_id")
            priority = body.get("priority", "normal")
            deadline = body.get("deadline")
            estimated_hours = body.get("estimated_hours")
            color = body.get("color", "normal")
            tags = body.get("tags", [])
            created_by_admin = body.get("created_by_admin", False)
        else:
            # Form данные
            form = await request.form()
            title = form.get("title")
            description = form.get("description", "")
            assigned_to_id = int(form.get("assigned_to_id")) if form.get("assigned_to_id") else None
            priority = form.get("priority", "normal")
            deadline = form.get("deadline")
            estimated_hours = int(form.get("estimated_hours")) if form.get("estimated_hours") else None
            color = form.get("color", "normal")
            tags = []
            created_by_admin = False

        if not title:
            return {"success": False, "error": "Название задачи обязательно"}

        # Парсим дату дедлайна
        deadline_dt = None
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline.replace('T', ' '))
            except ValueError:
                return {"success": False, "error": "Неверный формат даты"}

        with get_db_context() as db:
            # Если исполнитель не указан, назначаем на создателя
            if not assigned_to_id:
                assigned_to_id = current_user["id"]

            # Проверяем существование исполнителя
            executor = db.query(AdminUser).filter(
                AdminUser.id == assigned_to_id,
                AdminUser.is_active == True
            ).first()

            if not executor:
                return {"success": False, "error": "Исполнитель не найден"}

            # Создаем задачу
            creator_id = current_user["id"] if current_user["id"] > 0 else 1

            new_task = Task(
                title=title,
                description=description,
                assigned_to_id=assigned_to_id,
                created_by_id=creator_id,
                priority=priority,
                deadline=deadline_dt,
                estimated_hours=estimated_hours,
                status="pending",
                color=color
            )

            db.add(new_task)
            db.commit()
            db.refresh(new_task)

            # Отправляем уведомление о назначенной задаче
            try:
                await task_notification_service.notify_task_assigned(db, new_task)
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления о назначенной задаче {new_task.id}: {e}")

            # Загружаем связанные данные для возврата
            if new_task.created_by_id:
                new_task.created_by = db.query(AdminUser).filter(AdminUser.id == new_task.created_by_id).first()
            if new_task.assigned_to_id:
                new_task.assigned_to = db.query(AdminUser).filter(AdminUser.id == new_task.assigned_to_id).first()

            task_dict = new_task.to_dict()
            task_dict["created_by_name"] = f"{new_task.created_by.first_name} {new_task.created_by.last_name}" if new_task.created_by else "Неизвестно"
            task_dict["assigned_to_name"] = f"{new_task.assigned_to.first_name} {new_task.assigned_to.last_name}" if new_task.assigned_to else "Не назначен"
            task_dict["created_by_admin"] = created_by_admin
            task_dict["can_delete"] = (
                current_user["role"] == "owner" or
                (new_task.created_by_id == current_user["id"] and not created_by_admin)
            )

            logger.info(f"Создана задача {new_task.id}: {title} пользователем {current_user['username']} (роль: {current_user['role']})")

            return {
                "success": True,
                "message": "Задача создана",
                "task": task_dict
            }

    except Exception as e:
        logger.error(f"Ошибка создания задачи: {e}")
        return {"success": False, "error": str(e)}


@router.post("/")
async def create_task_with_slash(
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Создать новую задачу - вариант с trailing slash"""
    return await _create_task_logic(request, current_user)


@router.post("")
async def create_task_no_slash(
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Создать новую задачу - вариант без trailing slash"""
    return await _create_task_logic(request, current_user)

@router.get("/my-tasks")
async def get_my_tasks(
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить задачи для канбан-доски"""
    try:
        with get_db_context() as db:
            # По умолчанию все пользователи (включая владельца) видят только свои задачи
            query = db.query(Task).filter(Task.assigned_to_id == current_user["id"])
            tasks = query.order_by(Task.created_at.desc()).all()
            
            tasks_data = []
            for task in tasks:
                # Загружаем связанные данные
                if task.created_by_id:
                    task.created_by = db.query(AdminUser).filter(AdminUser.id == task.created_by_id).first()
                if task.assigned_to_id:
                    task.assigned_to = db.query(AdminUser).filter(AdminUser.id == task.assigned_to_id).first()
                
                task_dict = task.to_dict()
                task_dict["is_overdue"] = task.is_overdue
                task_dict["days_until_deadline"] = task.days_until_deadline
                
                # Имена создателя и исполнителя
                task_dict["created_by_name"] = f"{task.created_by.first_name} {task.created_by.last_name}" if task.created_by else "Неизвестно"
                task_dict["assigned_to_name"] = f"{task.assigned_to.first_name} {task.assigned_to.last_name}" if task.assigned_to else "Не назначен"
                
                # Флаг, что задача создана админом
                task_dict["created_by_admin"] = (
                    task.created_by and 
                    task.created_by.role == "owner" and 
                    task.created_by_id != task.assigned_to_id
                )
                
                # Может ли пользователь удалить задачу
                task_dict["can_delete"] = (
                    current_user["role"] == "owner" or 
                    (task.created_by_id == current_user["id"] and not task_dict["created_by_admin"])
                )
                
                tasks_data.append(task_dict)
        
        return {"success": True, "tasks": tasks_data}
        
    except Exception as e:
        logger.error(f"Ошибка получения задач для канбан-доски: {e}")
        return {"success": False, "error": str(e)}

@router.get("/employee/{employee_id}")
async def get_employee_tasks(
    employee_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить задачи конкретного сотрудника (только для владельца)"""
    try:
        # Проверяем, что пользователь - владелец
        if current_user["role"] != "owner":
            return {"success": False, "error": "Доступ запрещен"}
        
        with get_db_context() as db:
            # Если employee_id == 'my', возвращаем задачи владельца
            if employee_id == 'my':
                query = db.query(Task).filter(Task.assigned_to_id == current_user["id"])
            else:
                # Иначе возвращаем задачи указанного сотрудника
                query = db.query(Task).filter(Task.assigned_to_id == int(employee_id))
            
            tasks = query.order_by(Task.created_at.desc()).all()
            
            tasks_data = []
            for task in tasks:
                # Загружаем связанные данные
                if task.created_by_id:
                    task.created_by = db.query(AdminUser).filter(AdminUser.id == task.created_by_id).first()
                if task.assigned_to_id:
                    task.assigned_to = db.query(AdminUser).filter(AdminUser.id == task.assigned_to_id).first()
                
                task_dict = task.to_dict()
                task_dict["is_overdue"] = task.is_overdue
                task_dict["days_until_deadline"] = task.days_until_deadline
                
                # Имена создателя и исполнителя
                task_dict["created_by_name"] = f"{task.created_by.first_name} {task.created_by.last_name}" if task.created_by else "Неизвестно"
                task_dict["assigned_to_name"] = f"{task.assigned_to.first_name} {task.assigned_to.last_name}" if task.assigned_to else "Не назначен"
                
                # Флаг, что задача создана админом
                task_dict["created_by_admin"] = (
                    task.created_by and 
                    task.created_by.role == "owner" and 
                    task.created_by_id != task.assigned_to_id
                )
                
                # Может ли пользователь удалить задачу (владелец может удалять все)
                task_dict["can_delete"] = True
                
                tasks_data.append(task_dict)
        
        return {"success": True, "tasks": tasks_data}
        
    except Exception as e:
        logger.error(f"Ошибка получения задач сотрудника {employee_id}: {e}")
        return {"success": False, "error": str(e)}

@router.get("/{task_id}")
async def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить детали задачи"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {"success": False, "error": "Задача не найдена"}
            
            # Проверяем права доступа
            if (current_user["role"] == "executor" and 
                task.assigned_to_id != current_user["id"]):
                return {"success": False, "error": "Недостаточно прав"}
            
            # Получаем комментарии
            comments = db.query(TaskComment).filter(
                TaskComment.task_id == task_id
            ).order_by(TaskComment.created_at.desc()).all()
            
            task_dict = task.to_dict()
            task_dict["comments"] = [comment.to_dict() for comment in comments]
            task_dict["is_overdue"] = task.is_overdue
            task_dict["days_until_deadline"] = task.days_until_deadline
        
        return {"success": True, "task": task_dict}
        
    except Exception as e:
        logger.error(f"Ошибка получения задачи {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.put("/{task_id}")
async def update_task(
    task_id: int,
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Обновить задачу"""
    try:
        # Определяем тип контента и извлекаем данные
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            # JSON запрос
            body = await request.json()
            title = body.get("title")
            description = body.get("description")
            status = body.get("status")
            priority = body.get("priority")
            deadline = body.get("deadline")
            estimated_hours = body.get("estimated_hours")
            actual_hours = body.get("actual_hours")
            assigned_to_id = body.get("assigned_to_id")
            color = body.get("color")
            tags = body.get("tags")
            deploy_url = body.get("deploy_url")
        else:
            # Form данные
            form = await request.form()
            title = form.get("title")
            description = form.get("description")
            status = form.get("status")
            priority = form.get("priority")
            deadline = form.get("deadline")
            estimated_hours = int(form.get("estimated_hours")) if form.get("estimated_hours") else None
            actual_hours = int(form.get("actual_hours")) if form.get("actual_hours") else None
            assigned_to_id = int(form.get("assigned_to_id")) if form.get("assigned_to_id") else None
            color = form.get("color")
            tags = None
            deploy_url = form.get("deploy_url")
        
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {"success": False, "error": "Задача не найдена"}
            
            # Проверяем права
            can_edit = (
                current_user["role"] == "owner" or  # Владелец может редактировать все
                task.assigned_to_id == current_user["id"]  # Исполнитель может редактировать свои
            )
            
            if not can_edit:
                return {"success": False, "error": "Недостаточно прав"}
            
            # Сохраняем старые значения для логирования
            old_status = task.status
            changes = []
            
            # Обновляем поля
            if title is not None:
                task.title = title
                changes.append(f"заголовок изменен")
            
            if description is not None:
                task.description = description
                changes.append(f"описание обновлено")
            
            if priority is not None and current_user["role"] == "owner":
                old_priority = task.priority
                task.priority = priority
                changes.append(f"приоритет: {old_priority} → {priority}")
            
            if deadline is not None:
                if deadline:
                    try:
                        task.deadline = datetime.fromisoformat(deadline.replace('T', ' '))
                        changes.append(f"дедлайн обновлен")
                    except ValueError:
                        return {"success": False, "error": "Неверный формат даты"}
                else:
                    task.deadline = None
                    changes.append(f"дедлайн удален")
            
            if estimated_hours is not None:
                task.estimated_hours = estimated_hours
                changes.append(f"оценка времени: {estimated_hours}ч")
            
            if actual_hours is not None:
                task.actual_hours = actual_hours
                changes.append(f"фактическое время: {actual_hours}ч")
            
            if assigned_to_id is not None and current_user["role"] == "owner":
                old_assignee = task.assigned_to_id
                task.assigned_to_id = assigned_to_id
                changes.append(f"исполнитель изменен")
            
            if color is not None and current_user["role"] == "owner":
                old_color = task.color
                task.color = color
                changes.append(f"цвет: {old_color} → {color}")

            if tags is not None:
                task.tags = tags if isinstance(tags, list) else []
                changes.append(f"теги обновлены")

            if deploy_url is not None:
                old_deploy_url = task.deploy_url
                task.deploy_url = deploy_url if deploy_url.strip() else None
                if old_deploy_url != task.deploy_url:
                    if task.deploy_url:
                        changes.append(f"ссылка на деплой обновлена")
                    else:
                        changes.append(f"ссылка на деплой удалена")

            if status is not None and status != old_status:
                task.status = status
                if status == "completed":
                    task.completed_at = datetime.utcnow()
                changes.append(f"статус: {translate_status(old_status)} → {translate_status(status)}")
                
                # Отправляем уведомление об изменении статуса
                try:
                    await task_notification_service.notify_task_status_changed(db, task, old_status)
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления об изменении статуса задачи {task.id}: {e}")
            
            task.updated_at = datetime.utcnow()
            db.commit()
            
            # Добавляем комментарий об изменениях
            if changes and current_user["role"] == "owner":
                change_comment = TaskComment(
                    task_id=task_id,
                    author_id=current_user["id"],
                    comment=f"Изменения: {', '.join(changes)}",
                    comment_type="status_change"
                )
                db.add(change_comment)
                db.commit()
            
            logger.info(f"Обновлена задача {task_id}: {', '.join(changes)}")
            
            return {
                "success": True,
                "message": "Задача обновлена",
                "task": task.to_dict()
            }
        
    except Exception as e:
        logger.error(f"Ошибка обновления задачи {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Удалить задачу"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {"success": False, "error": "Задача не найдена"}
            
            # Загружаем создателя задачи
            if task.created_by_id:
                task.created_by = db.query(AdminUser).filter(AdminUser.id == task.created_by_id).first()
            
            # Проверяем права на удаление
            # Владелец может удалять любые задачи
            # Исполнители могут удалять только свои задачи (созданные ими, а не админом)
            is_admin_task = (
                task.created_by and 
                task.created_by.role == "owner" and 
                task.created_by_id != task.assigned_to_id
            )
            
            can_delete = (
                current_user["role"] == "owner" or 
                (task.created_by_id == current_user["id"] and not is_admin_task)
            )
            
            if not can_delete:
                return {"success": False, "error": "Недостаточно прав для удаления этой задачи"}
            
            # Удаляем комментарии
            db.query(TaskComment).filter(TaskComment.task_id == task_id).delete()
            
            # Удаляем задачу
            task_title = task.title
            db.delete(task)
            db.commit()
            
            logger.info(f"Удалена задача {task_id}: {task_title} пользователем {current_user['username']}")
            
            return {"success": True, "message": "Задача удалена"}
        
    except Exception as e:
        logger.error(f"Ошибка удаления задачи {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/{task_id}/comments")
async def add_task_comment(
    task_id: int,
    comment: str = Form(...),
    is_internal: bool = Form(False),
    files: List[UploadFile] = File(None),
    current_user: dict = Depends(get_current_admin_user)
):
    """Добавить комментарий к задаче с возможностью прикрепления фотографий"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()

            if not task:
                return {"success": False, "error": "Задача не найдена"}

            # Проверяем права доступа
            can_comment = (
                current_user["role"] == "owner" or
                task.assigned_to_id == current_user["id"]
            )

            if not can_comment:
                return {"success": False, "error": "Недостаточно прав"}

            # Обработка загруженных файлов
            attachments = []
            if files:
                upload_dir = Path("uploads/task_comments")
                upload_dir.mkdir(parents=True, exist_ok=True)

                for file in files:
                    if file and file.filename:
                        # Генерируем уникальное имя файла
                        file_ext = os.path.splitext(file.filename)[1]
                        unique_filename = f"{uuid.uuid4()}{file_ext}"
                        file_path = upload_dir / unique_filename

                        # Сохраняем файл
                        with open(file_path, "wb") as f:
                            content = await file.read()
                            f.write(content)

                        # Определяем тип файла
                        file_type = "image" if file.content_type and file.content_type.startswith("image/") else "file"

                        attachments.append({
                            "filename": unique_filename,
                            "original_filename": file.filename,
                            "path": str(file_path),
                            "type": file_type,
                            "size": len(content)
                        })

                        logger.info(f"Файл {file.filename} сохранен как {unique_filename}")

            # Создаем комментарий
            new_comment = TaskComment(
                task_id=task_id,
                author_id=current_user["id"],
                comment=comment,
                is_internal=is_internal and current_user["role"] == "owner",  # Только владелец может создавать внутренние комментарии
                attachments=attachments,
                is_read=False,
                read_by=[]
            )

            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)

            # Отправляем уведомление о новом комментарии
            try:
                await task_notification_service.notify_new_task_comment(db, task, new_comment, current_user)
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления о комментарии к задаче {task.id}: {e}")

            logger.info(f"Добавлен комментарий к задаче {task_id} с {len(attachments)} вложениями")

            return {
                "success": True,
                "message": "Комментарий добавлен",
                "comment": new_comment.to_dict()
            }

    except Exception as e:
        logger.error(f"Ошибка добавления комментария к задаче {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/{task_id}/comments/{comment_id}/mark_read")
async def mark_comment_as_read(
    task_id: int,
    comment_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Отметить комментарий как прочитанный"""
    try:
        with get_db_context() as db:
            comment = db.query(TaskComment).filter(
                TaskComment.id == comment_id,
                TaskComment.task_id == task_id
            ).first()

            if not comment:
                return {"success": False, "error": "Комментарий не найден"}

            # Добавляем пользователя в список прочитавших
            read_by = comment.read_by or []
            if current_user["id"] not in read_by:
                read_by.append(current_user["id"])
                comment.read_by = read_by
                comment.is_read = True  # Помечаем как прочитанный
                db.commit()

            return {"success": True, "message": "Комментарий отмечен как прочитанный"}

    except Exception as e:
        logger.error(f"Ошибка отметки комментария {comment_id} как прочитанного: {e}")
        return {"success": False, "error": str(e)}

@router.post("/{task_id}/mark_all_comments_read")
async def mark_all_comments_as_read(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Отметить все комментарии задачи как прочитанные"""
    try:
        with get_db_context() as db:
            # Получаем все комментарии задачи
            comments = db.query(TaskComment).filter(
                TaskComment.task_id == task_id
            ).all()

            marked_count = 0
            for comment in comments:
                # Проверяем, не прочитан ли уже комментарий этим пользователем
                read_by = comment.read_by or []
                if current_user["id"] not in read_by:
                    read_by.append(current_user["id"])
                    comment.read_by = read_by
                    comment.is_read = True
                    marked_count += 1

            db.commit()
            logger.info(f"Отмечено {marked_count} комментариев как прочитанные для задачи {task_id}")

            return {"success": True, "marked_count": marked_count}

    except Exception as e:
        logger.error(f"Ошибка отметки всех комментариев задачи {task_id} как прочитанных: {e}")
        return {"success": False, "error": str(e)}

@router.get("/{task_id}/unread_comments_count")
async def get_unread_comments_count(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить количество непрочитанных комментариев для задачи"""
    try:
        with get_db_context() as db:
            # Получаем все комментарии задачи, которые не прочитаны текущим пользователем
            comments = db.query(TaskComment).filter(
                TaskComment.task_id == task_id,
                TaskComment.author_id != current_user["id"]  # Исключаем свои комментарии
            ).all()

            unread_count = 0
            for comment in comments:
                read_by = comment.read_by or []
                if current_user["id"] not in read_by:
                    unread_count += 1

            return {
                "success": True,
                "task_id": task_id,
                "unread_count": unread_count
            }

    except Exception as e:
        logger.error(f"Ошибка получения количества непрочитанных комментариев для задачи {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.get("/{task_id}/comments")
async def get_task_comments(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить все комментарии задачи"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()

            if not task:
                return {"success": False, "error": "Задача не найдена"}

            # Проверяем права доступа (owner, исполнитель или создатель)
            can_view = (
                current_user["role"] == "owner" or
                task.assigned_to_id == current_user["id"] or
                task.created_by_id == current_user["id"]
            )

            if not can_view:
                return {"success": False, "error": "Недостаточно прав"}

            comments = db.query(TaskComment).filter(
                TaskComment.task_id == task_id
            ).order_by(TaskComment.created_at.asc()).all()

            # Подсчитываем непрочитанные комментарии
            unread_count = 0
            comments_data = []
            for comment in comments:
                comment_dict = comment.to_dict()
                # Проверяем, прочитан ли комментарий текущим пользователем
                read_by = comment.read_by or []
                comment_dict["is_read_by_me"] = current_user["id"] in read_by or comment.author_id == current_user["id"]

                if not comment_dict["is_read_by_me"]:
                    unread_count += 1

                comments_data.append(comment_dict)

            return {
                "success": True,
                "comments": comments_data,
                "total_count": len(comments_data),
                "unread_count": unread_count
            }

    except Exception as e:
        logger.error(f"Ошибка получения комментариев задачи {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.get("/stats/dashboard")
def get_task_dashboard_stats():
    """Получить статистику для дашборда задач"""
    try:
        with get_db_context() as db:
            # Получаем все задачи, ИСКЛЮЧАЯ архивные
            all_tasks = db.query(Task).options(
                joinedload(Task.assigned_to),
                joinedload(Task.created_by)
            ).all()

            # Фильтруем архивные задачи
            active_tasks = [
                task for task in all_tasks
                if not task.task_metadata.get('archived', False)
            ]

            # Подсчитываем статистику только по активным задачам
            total_tasks = len(active_tasks)
            pending_tasks = sum(1 for t in active_tasks if t.status == "pending")
            in_progress_tasks = sum(1 for t in active_tasks if t.status == "in_progress")
            completed_tasks = sum(1 for t in active_tasks if t.status == "completed")
            overdue_tasks = sum(1 for t in active_tasks if t.is_overdue)

            # Задачи на сегодня
            today = datetime.utcnow().date()
            today_tasks = sum(
                1 for t in active_tasks
                if t.deadline and t.deadline.date() == today
            )

            # Статистика по приоритетам
            priority_stats = {
                "urgent": sum(1 for t in active_tasks if t.priority == "urgent"),
                "high": sum(1 for t in active_tasks if t.priority == "high"),
                "normal": sum(1 for t in active_tasks if t.priority == "normal"),
                "low": sum(1 for t in active_tasks if t.priority == "low")
            }

            # Последние задачи (только активные)
            recent_tasks = sorted(active_tasks, key=lambda x: x.created_at, reverse=True)[:5]
            recent_tasks_data = []
            for task in recent_tasks:
                task_dict = task.to_dict()
                task_dict["assigned_to_name"] = f"{task.assigned_to.first_name} {task.assigned_to.last_name}" if task.assigned_to else "Не назначен"
                recent_tasks_data.append(task_dict)

            # Статистика по сотрудникам (только активные задачи)
            employees = db.query(AdminUser).filter(
                AdminUser.role.in_(["executor", "owner"]),
                AdminUser.is_active == True
            ).all()

            employee_stats = []
            for emp in employees:
                emp_active_tasks = [t for t in active_tasks if t.assigned_to_id == emp.id]
                employee_stats.append({
                    "id": emp.id,
                    "name": f"{emp.first_name} {emp.last_name}",
                    "total": len(emp_active_tasks),
                    "pending": sum(1 for t in emp_active_tasks if t.status == "pending"),
                    "in_progress": sum(1 for t in emp_active_tasks if t.status == "in_progress"),
                    "completed": sum(1 for t in emp_active_tasks if t.status == "completed")
                })

            stats = {
                "total_tasks": total_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "today_tasks": today_tasks,
                "priority_stats": priority_stats,
                "recent_tasks": recent_tasks_data,
                "employee_stats": employee_stats
            }

            logger.info(f"Статистика дашборда: всего активных задач {total_tasks}, архивных исключено {len(all_tasks) - total_tasks}")

            return {"success": True, "stats": stats}

    except Exception as e:
        logger.error(f"Ошибка получения статистики дашборда: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

@router.get("/api/employees")
async def get_employees(
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить список сотрудников для назначения задач"""
    try:
        # Только владелец может получать список всех сотрудников
        if current_user["role"] != "owner":
            return {"success": False, "error": "Недостаточно прав"}
        
        with get_db_context() as db:
            employees = db.query(AdminUser).filter(
                AdminUser.role == "executor",
                AdminUser.is_active == True
            ).all()
            
            employees_data = []
            for employee in employees:
                # Получаем статистику по задачам
                tasks_count = db.query(Task).filter(Task.assigned_to_id == employee.id).count()
                active_tasks = db.query(Task).filter(
                    Task.assigned_to_id == employee.id,
                    Task.status.in_(["pending", "in_progress"])
                ).count()
                
                employee_dict = employee.to_dict()
                employee_dict["tasks_count"] = tasks_count
                employee_dict["active_tasks"] = active_tasks
                
                employees_data.append(employee_dict)
        
        return {"success": True, "employees": employees_data}
        
    except Exception as e:
        logger.error(f"Ошибка получения списка сотрудников: {e}")
        return {"success": False, "error": str(e)}

@router.put("/{task_id}/status")
async def update_task_status(
    task_id: int,
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Обновить статус задачи (для drag-and-drop в канбан-доске)"""
    try:
        
        body = await request.json()
        new_status = body.get("status")
        
        if not new_status:
            return {"success": False, "error": "Статус не указан"}
        
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {"success": False, "error": "Задача не найдена"}
            
            # Проверяем права
            can_update = (
                current_user["role"] == "owner" or
                task.assigned_to_id == current_user["id"]
            )
            
            if not can_update:
                return {"success": False, "error": "Недостаточно прав"}
            
            old_status = task.status
            task.status = new_status
            
            if new_status == "completed":
                task.completed_at = datetime.utcnow()
            
            task.updated_at = datetime.utcnow()
            db.commit()
            
            # Отправляем уведомление об изменении статуса
            if old_status != new_status:
                try:
                    await task_notification_service.notify_task_status_changed(db, task, old_status)
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления об изменении статуса задачи {task.id}: {e}")
            
            # Добавляем комментарий об изменении статуса
            if old_status != new_status:
                status_comment = TaskComment(
                    task_id=task_id,
                    author_id=current_user["id"],
                    comment=f"Статус изменен: {translate_status(old_status)} → {translate_status(new_status)}",
                    comment_type="status_change"
                )
                db.add(status_comment)
                db.commit()
            
            logger.info(f"Обновлен статус задачи {task_id}: {old_status} → {new_status}")
            
            return {"success": True, "message": "Статус обновлен"}
        
    except Exception as e:
        logger.error(f"Ошибка обновления статуса задачи {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/users/executors")
async def get_executors(
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить список исполнителей для назначения задач"""
    try:
        with get_db_context() as db:
            # Получаем всех активных пользователей (и владельца, и исполнителей)
            users = db.query(AdminUser).filter(
                AdminUser.is_active == True
            ).all()
            
            executors = []
            for user in users:
                executors.append({
                    "id": user.id,
                    "name": f"{user.first_name} {user.last_name}",
                    "role": user.role,
                    "username": user.username
                })
        
        return executors
        
    except Exception as e:
        logger.error(f"Ошибка получения списка исполнителей: {e}")
        return []

@router.put("/{task_id}/reassign")
async def reassign_task(
    task_id: int,
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Переназначить задачу другому исполнителю (для drag-and-drop)"""
    try:
        # Только владелец может переназначать задачи
        if current_user["role"] != "owner":
            return {"success": False, "error": "Только администратор может переназначать задачи"}
        
        body = await request.json()
        new_assignee_id = body.get("assigned_to_id")
        
        if not new_assignee_id:
            return {"success": False, "error": "Не указан новый исполнитель"}
        
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {"success": False, "error": "Задача не найдена"}
            
            # Проверяем существование нового исполнителя
            new_assignee = db.query(AdminUser).filter(
                AdminUser.id == new_assignee_id,
                AdminUser.is_active == True
            ).first()
            
            if not new_assignee:
                return {"success": False, "error": "Исполнитель не найден"}
            
            # Получаем старого исполнителя для логирования
            old_assignee = db.query(AdminUser).filter(AdminUser.id == task.assigned_to_id).first()
            old_name = f"{old_assignee.first_name} {old_assignee.last_name}" if old_assignee else "Не назначен"
            new_name = f"{new_assignee.first_name} {new_assignee.last_name}"
            
            # Обновляем исполнителя
            task.assigned_to_id = new_assignee_id
            task.updated_at = datetime.utcnow()
            
            # Отправляем уведомление новому исполнителю
            try:
                await task_notification_service.notify_task_assigned(db, task)
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления о переназначении задачи {task.id}: {e}")
            
            # Добавляем комментарий об изменении
            reassign_comment = TaskComment(
                task_id=task_id,
                author_id=current_user["id"],
                comment=f"Задача переназначена: {old_name} → {new_name}",
                comment_type="reassignment"
            )
            db.add(reassign_comment)
            
            db.commit()
            
            logger.info(f"Задача {task_id} переназначена с {old_name} на {new_name}")
            
            return {
                "success": True,
                "message": f"Задача переназначена на {new_name}"
            }
        
    except Exception as e:
        logger.error(f"Ошибка переназначения задачи {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.delete("/api/users/executor/{executor_id}")
async def delete_executor(
    executor_id: int,
    reassign_to_id: Optional[int] = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """Удалить исполнителя и переназначить его задачи"""
    try:
        # Только владелец может удалять исполнителей
        if current_user["role"] != "owner":
            return {"success": False, "error": "Недостаточно прав"}
        
        with get_db_context() as db:
            # Проверяем существование исполнителя
            executor = db.query(AdminUser).filter(
                AdminUser.id == executor_id,
                AdminUser.role == "executor"
            ).first()
            
            if not executor:
                return {"success": False, "error": "Исполнитель не найден"}
            
            # Если указан новый исполнитель для переназначения
            if reassign_to_id:
                new_executor = db.query(AdminUser).filter(
                    AdminUser.id == reassign_to_id,
                    AdminUser.is_active == True
                ).first()
                
                if not new_executor:
                    return {"success": False, "error": "Новый исполнитель не найден"}
                
                # Переназначаем все задачи
                tasks_to_reassign = db.query(Task).filter(
                    Task.assigned_to_id == executor_id
                ).all()
                
                for task in tasks_to_reassign:
                    task.assigned_to_id = reassign_to_id
                    task.updated_at = datetime.utcnow()
                
                logger.info(f"Переназначено {len(tasks_to_reassign)} задач с исполнителя {executor_id} на {reassign_to_id}")
            else:
                # Удаляем все задачи исполнителя
                tasks_to_delete = db.query(Task).filter(
                    Task.assigned_to_id == executor_id
                ).all()
                
                for task in tasks_to_delete:
                    # Удаляем комментарии к задаче
                    db.query(TaskComment).filter(TaskComment.task_id == task.id).delete()
                    db.delete(task)
                
                logger.info(f"Удалено {len(tasks_to_delete)} задач исполнителя {executor_id}")
            
            # Деактивируем исполнителя (не удаляем полностью для сохранения истории)
            executor.is_active = False
            executor.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Исполнитель {executor.first_name} {executor.last_name} удален"
            }
        
    except Exception as e:
        logger.error(f"Ошибка удаления исполнителя {executor_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/import-projects")
async def import_projects_as_tasks(
    current_user: dict = Depends(get_current_admin_user)
):
    """Импортировать все проекты как задачи"""
    try:
        if current_user["role"] != "owner":
            return {"success": False, "error": "Недостаточно прав"}
        
        with get_db_context() as db:
            # Получаем все проекты, которые еще не имеют соответствующих задач
            projects = db.query(Project).filter(
                Project.status.in_(["new", "review", "accepted", "in_progress", "testing"])
            ).all()
            
            imported_count = 0
            
            for project in projects:
                # Проверяем, нет ли уже задачи для этого проекта
                existing_task = db.query(Task).filter(
                    Task.title.contains(project.title),
                    Task.description.contains(str(project.id))
                ).first()
                
                if not existing_task:
                    # Определяем приоритет на основе приоритета проекта
                    priority_map = {
                        "low": "low",
                        "normal": "normal", 
                        "high": "high",
                        "urgent": "urgent"
                    }
                    
                    # Определяем статус задачи на основе статуса проекта
                    status_map = {
                        "new": "pending",
                        "review": "pending",
                        "accepted": "pending",
                        "in_progress": "in_progress",
                        "testing": "in_progress",
                        "completed": "completed",
                        "cancelled": "cancelled"
                    }
                    
                    # Создаем задачу
                    new_task = Task(
                        title=f"Проект: {project.title}",
                        description=f"Проект ID: {project.id}\n\n{project.description or 'Нет описания'}",
                        assigned_to_id=project.assigned_executor_id or 1,  # Назначаем владельцу если нет исполнителя
                        created_by_id=current_user["id"] if current_user["id"] > 0 else 1,
                        priority=priority_map.get(project.priority, "normal"),
                        status=status_map.get(project.status, "pending"),
                        deadline=project.deadline,
                        estimated_hours=project.estimated_hours
                    )
                    
                    db.add(new_task)
                    imported_count += 1
            
            db.commit()
            
            logger.info(f"Импортировано {imported_count} проектов как задачи")
            
            return {
                "success": True,
                "message": f"Импортировано {imported_count} проектов как задачи",
                "imported_count": imported_count
            }
        
    except Exception as e:
        logger.error(f"Ошибка импорта проектов: {e}")
        return {"success": False, "error": str(e)}

@router.post("/{task_id}/progress")
async def update_task_progress(
    task_id: int,
    progress_data: dict,
    current_user: dict = Depends(get_current_admin_user)
):
    """Обновить прогресс выполнения задачи"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"success": False, "message": "Задача не найдена"}

            progress = progress_data.get("progress", 0)
            if not isinstance(progress, int) or progress < 0 or progress > 100:
                return {"success": False, "message": "Прогресс должен быть числом от 0 до 100"}

            task.progress = progress
            task.updated_at = datetime.utcnow()

            # Если прогресс 100%, автоматически завершаем задачу
            if progress == 100 and task.status != "completed":
                task.status = "completed"
                task.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "message": f"Прогресс обновлен до {progress}%",
                "data": task.to_dict()
            }
    except Exception as e:
        logger.error(f"Ошибка обновления прогресса задачи {task_id}: {e}")
        return {"success": False, "message": str(e)}

@router.post("/{task_id}/timer/start")
async def start_task_timer(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Запустить таймер работы над задачей"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"success": False, "message": "Задача не найдена"}

            if task.timer_started_at:
                return {"success": False, "message": "Таймер уже запущен"}

            task.timer_started_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()

            # Автоматически переводим в статус "в работе"
            if task.status == "pending":
                task.status = "in_progress"

            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "message": "Таймер запущен",
                "data": task.to_dict()
            }
    except Exception as e:
        logger.error(f"Ошибка запуска таймера задачи {task_id}: {e}")
        return {"success": False, "message": str(e)}

@router.post("/{task_id}/timer/stop")
async def stop_task_timer(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Остановить таймер работы над задачей"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"success": False, "message": "Задача не найдена"}

            if not task.timer_started_at:
                return {"success": False, "message": "Таймер не был запущен"}

            # Вычисляем затраченное время
            time_elapsed = (datetime.utcnow() - task.timer_started_at).total_seconds()
            task.time_spent_seconds = (task.time_spent_seconds or 0) + int(time_elapsed)
            task.timer_started_at = None
            task.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(task)

            hours = int(task.time_spent_seconds // 3600)
            minutes = int((task.time_spent_seconds % 3600) // 60)

            return {
                "success": True,
                "message": f"Таймер остановлен. Всего времени: {hours}ч {minutes}м",
                "data": task.to_dict(),
                "time_formatted": f"{hours}:{minutes:02d}"
            }
    except Exception as e:
        logger.error(f"Ошибка остановки таймера задачи {task_id}: {e}")
        return {"success": False, "message": str(e)}
@router.post("/{task_id}/upload-image")
async def upload_task_image(
    task_id: int,
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Загрузить изображение к задаче"""
    try:
        from fastapi import UploadFile, File
        import os
        import uuid
        
        # Получаем multipart form data
        form = await request.form()
        files = form.getlist("files")
        
        if not files:
            return {"success": False, "error": "Файлы не найдены"}
        
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {"success": False, "error": "Задача не найдена"}
            
            # Проверяем права доступа
            can_upload = (
                current_user["role"] == "owner" or
                task.assigned_to_id == current_user["id"] or
                task.created_by_id == current_user["id"]
            )
            
            if not can_upload:
                return {"success": False, "error": "Недостаточно прав"}
            
            # Создаём директорию для сохранения
            upload_dir = f"uploads/tasks/{task_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            uploaded_files = []
            
            for file in files:
                if hasattr(file, 'filename') and file.filename:
                    # Генерируем уникальное имя файла
                    file_ext = os.path.splitext(file.filename)[1]
                    unique_filename = f"{uuid.uuid4()}{file_ext}"
                    file_path = os.path.join(upload_dir, unique_filename)
                    
                    # Сохраняем файл
                    content = await file.read()
                    with open(file_path, "wb") as f:
                        f.write(content)
                    
                    uploaded_files.append({
                        "filename": file.filename,
                        "path": file_path,
                        "uploaded_at": datetime.utcnow().isoformat(),
                        "uploaded_by": current_user["id"]
                    })
            
            # Обновляем metadata задачи, добавляя информацию о файлах
            if not task.task_metadata:
                task.task_metadata = {}
            
            if "attachments" not in task.task_metadata:
                task.task_metadata["attachments"] = []
            
            task.task_metadata["attachments"].extend(uploaded_files)
            task.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(task)
            
            return {
                "success": True,
                "message": f"Загружено файлов: {len(uploaded_files)}",
                "files": uploaded_files
            }
            
    except Exception as e:
        logger.error(f"Ошибка загрузки файлов к задаче {task_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

@router.post("/{task_id}/comments/upload")
async def upload_comment_attachment(
    task_id: int,
    comment_id: int = Form(...),
    request: Request = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """Загрузить изображение к комментарию"""
    try:
        from fastapi import UploadFile, File
        import os
        import uuid
        
        # Получаем multipart form data
        form = await request.form()
        files = form.getlist("files")
        
        if not files:
            return {"success": False, "error": "Файлы не найдены"}
        
        with get_db_context() as db:
            comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
            
            if not comment or comment.task_id != task_id:
                return {"success": False, "error": "Комментарий не найден"}
            
            # Проверяем права доступа
            can_upload = (
                current_user["role"] == "owner" or
                comment.author_id == current_user["id"]
            )
            
            if not can_upload:
                return {"success": False, "error": "Недостаточно прав"}
            
            # Создаём директорию для сохранения
            upload_dir = f"uploads/tasks/{task_id}/comments"
            os.makedirs(upload_dir, exist_ok=True)
            
            uploaded_files = []
            
            for file in files:
                if hasattr(file, 'filename') and file.filename:
                    # Генерируем уникальное имя файла
                    file_ext = os.path.splitext(file.filename)[1]
                    unique_filename = f"{uuid.uuid4()}{file_ext}"
                    file_path = os.path.join(upload_dir, unique_filename)
                    
                    # Сохраняем файл
                    content = await file.read()
                    with open(file_path, "wb") as f:
                        f.write(content)
                    
                    uploaded_files.append({
                        "filename": file.filename,
                        "path": file_path,
                        "uploaded_at": datetime.utcnow().isoformat(),
                        "uploaded_by": current_user["id"]
                    })
            
            # Обновляем attachments комментария
            if not comment.attachments:
                comment.attachments = []
            
            comment.attachments.extend(uploaded_files)
            
            db.commit()
            db.refresh(comment)
            
            return {
                "success": True,
                "message": f"Загружено файлов: {len(uploaded_files)}",
                "files": uploaded_files
            }
            
    except Exception as e:
        logger.error(f"Ошибка загрузки файлов к комментарию {comment_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

@router.post("/{task_id}/progress")
async def update_task_progress(
    task_id: int,
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Обновление прогресса выполнения задачи"""
    try:
        data = await request.json()
        progress = data.get('progress', 0)

        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"success": False, "error": "Задача не найдена"}

            # Проверка прав: создатель или исполнитель
            if task.created_by_id != current_user['id'] and task.assigned_to_id != current_user['id']:
                return {"success": False, "error": "Нет прав для изменения прогресса"}

            task.progress = progress
            db.commit()

            logger.info(f"Прогресс задачи {task_id} обновлён на {progress}% пользователем {current_user['username']}")

            return {
                "success": True,
                "progress": progress,
                "message": "Прогресс обновлён"
            }

    except Exception as e:
        logger.error(f"Ошибка обновления прогресса задачи {task_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

@router.post("/{task_id}/mark-completed")
async def mark_task_completed(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Отметить задачу как выполненную (для сотрудника)"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"success": False, "error": "Задача не найдена"}

            # Проверка прав: только исполнитель может отметить как выполненную
            if task.assigned_to_id != current_user['id']:
                return {"success": False, "error": "Только исполнитель может отметить задачу как выполненную"}

            # Сохраняем в метаданные информацию о том, что сотрудник отметил задачу
            if not task.task_metadata:
                task.task_metadata = {}

            task.task_metadata['marked_completed_by_employee'] = {
                'employee_id': current_user['id'],
                'employee_name': current_user['username'],
                'marked_at': datetime.utcnow().isoformat()
            }

            # Меняем статус на "completed"
            task.status = "completed"
            task.progress = 100

            # Останавливаем таймер если он запущен
            if task.timer_started_at:
                elapsed = int((datetime.utcnow() - task.timer_started_at).total_seconds())
                task.time_spent_seconds = (task.time_spent_seconds or 0) + elapsed
                task.timer_started_at = None

            db.commit()
            db.refresh(task)

            logger.info(f"Задача {task_id} отмечена как выполненная сотрудником {current_user['username']}")

            return {
                "success": True,
                "message": "Задача отмечена как выполненная и ожидает подтверждения администратора",
                "task": task.to_dict()
            }

    except Exception as e:
        logger.error(f"Ошибка отметки задачи {task_id} как выполненной: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

@router.post("/{task_id}/archive")
async def archive_task(
    task_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    """Архивировать задачу (только для владельца)"""
    try:
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return {"success": False, "error": "Задача не найдена"}

            # Проверка прав: только создатель (владелец) может архивировать
            if task.created_by_id != current_user['id']:
                admin_user = db.query(AdminUser).filter(AdminUser.id == current_user['id']).first()
                if not admin_user or admin_user.role != 'owner':
                    return {"success": False, "error": "Только владелец может архивировать задачи"}

            # Сохраняем в метаданные информацию об архивации
            if not task.task_metadata:
                task.task_metadata = {}

            task.task_metadata['archived'] = True
            task.task_metadata['archived_by'] = {
                'admin_id': current_user['id'],
                'admin_name': current_user['username'],
                'archived_at': datetime.utcnow().isoformat()
            }

            # Устанавливаем время завершения если не установлено
            if not task.completed_at:
                task.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(task)

            logger.info(f"Задача {task_id} ({task.title}) архивирована администратором {current_user['username']}")

            return {
                "success": True,
                "message": "Задача успешно архивирована",
                "task": task.to_dict()
            }

    except Exception as e:
        logger.error(f"Ошибка архивации задачи {task_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

@router.get("/archive/list")
async def get_archived_tasks(
    current_user: dict = Depends(get_current_admin_user),
    employee_id: int = None,
    date_from: str = None,
    date_to: str = None
):
    """Получить список архивных задач с фильтрацией по сотруднику и датам"""
    try:
        with get_db_context() as db:
            # Базовый запрос - только архивные задачи
            query = db.query(Task).filter(
                cast(Task.task_metadata['archived'], String) == 'true'
            )

            # Фильтр по сотруднику
            if employee_id:
                query = query.filter(Task.assigned_to_id == employee_id)

            # Фильтр по датам
            if date_from:
                date_from_dt = datetime.fromisoformat(date_from)
                query = query.filter(Task.completed_at >= date_from_dt)

            if date_to:
                date_to_dt = datetime.fromisoformat(date_to)
                query = query.filter(Task.completed_at <= date_to_dt)

            # Сортировка по дате завершения
            tasks = query.order_by(desc(Task.completed_at)).all()

            # Группируем задачи по дням и сотрудникам
            tasks_by_date = {}
            for task in tasks:
                if task.completed_at:
                    date_key = task.completed_at.strftime('%Y-%m-%d')
                    if date_key not in tasks_by_date:
                        tasks_by_date[date_key] = {}

                    employee_key = str(task.assigned_to_id)
                    if employee_key not in tasks_by_date[date_key]:
                        tasks_by_date[date_key][employee_key] = {
                            'employee': task.assigned_to.to_dict() if task.assigned_to else None,
                            'tasks': []
                        }

                    tasks_by_date[date_key][employee_key]['tasks'].append(task.to_dict())

            return {
                "success": True,
                "tasks_by_date": tasks_by_date,
                "total_tasks": len(tasks)
            }

    except Exception as e:
        logger.error(f"Ошибка получения архивных задач: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}
