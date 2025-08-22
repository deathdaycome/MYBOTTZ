"""
Router для управления задачами
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from typing import Optional, List
import json

from ...config.logging import get_logger
from ...database.database import get_db_context
from ...database.models import Task, TaskComment, AdminUser, Project
from ..middleware.auth import get_current_admin_user
from fastapi import Cookie
from ..middleware.roles import RoleMiddleware

logger = get_logger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/admin/templates")

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

@router.get("/", response_class=HTMLResponse)
async def tasks_page(request: Request, current_user: dict = Depends(get_current_admin_user)):
    """Страница планировщика задач"""
    try:
        with get_db_context() as db:
            # Получаем все задачи
            query = db.query(Task).outerjoin(AdminUser, Task.assigned_to_id == AdminUser.id)
            
            # Владелец видит все задачи, исполнители только свои
            if current_user["role"] != "owner":
                query = query.filter(Task.assigned_to_id == current_user["id"])
            
            tasks = query.order_by(Task.created_at.desc()).all()
            
            # Отладка
            logger.info(f"=== Планировщик задач ===")
            logger.info(f"Текущий пользователь: {current_user['username']} (ID: {current_user['id']}, Role: {current_user['role']})")
            logger.info(f"Найдено задач для пользователя: {len(tasks)}")
            for task in tasks[:3]:  # Показываем первые 3 задачи для отладки
                logger.info(f"  - Task: {task.title[:30]}... (assigned_to_id={task.assigned_to_id})")
            
            # Преобразуем задачи в словари для передачи в шаблон
            tasks_data = []
            for task in tasks:
                # Загружаем связанные объекты
                if task.assigned_to_id:
                    task.assigned_to = db.query(AdminUser).filter(AdminUser.id == task.assigned_to_id).first()
                if task.created_by_id:
                    task.created_by = db.query(AdminUser).filter(AdminUser.id == task.created_by_id).first()
                
                # Преобразуем в словарь с дополнительными полями
                task_dict = task.to_dict()
                task_dict["is_overdue"] = task.is_overdue
                task_dict["days_until_deadline"] = task.days_until_deadline
                task_dict["can_delete"] = current_user["role"] == "owner"
                tasks_data.append(task_dict)
            
            # Получаем сотрудников для канбан-доски
            employees = []
            executors = []
            if current_user["role"] == "owner":
                # Владелец видит всех активных сотрудников (исполнителей + себя)
                employees_raw = db.query(AdminUser).filter(
                    AdminUser.is_active == True,
                    AdminUser.role.in_(["owner", "executor"])
                ).all()
                employees = [emp.to_dict() for emp in employees_raw]
                # Также получаем список исполнителей для селектора
                executors = employees_raw
            elif current_user["role"] == "executor":
                # Исполнители видят только себя
                employees = [current_user]
            
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
            
            return templates.TemplateResponse("tasks_new.html", {
                "request": request,
                "tasks": tasks_data,
                "employees": employees,
                "executors": executors,  # Добавляем список исполнителей
                "stats": stats,
                "current_user": current_user,
                "current_user_id": current_user['id'],
                "username": current_user['username'],
                "user_role": current_user['role'],
                "navigation_items": navigation_items
            })
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке страницы задач: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при загрузке задач")

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

@router.get("/api/tasks")
async def get_tasks(
    status: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    created_by_id: Optional[int] = None,
    priority: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить список задач с фильтрацией"""
    try:
        with get_db_context() as db:
            query = db.query(Task).join(AdminUser, Task.assigned_to_id == AdminUser.id)
            
            # Если пользователь исполнитель, показываем только его задачи
            if current_user["role"] == "executor":
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
            
            tasks_raw = query.order_by(
                Task.priority.desc(),
                Task.deadline.asc(),
                Task.created_at.desc()
            ).all()
            
            tasks = []
            for task in tasks_raw:
                task_dict = task.to_dict()
                # Добавляем дополнительные поля для UI
                task_dict["is_overdue"] = task.is_overdue
                task_dict["days_until_deadline"] = task.days_until_deadline
                tasks.append(task_dict)
        
        return {"success": True, "tasks": tasks}
        
    except Exception as e:
        logger.error(f"Ошибка получения задач: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/tasks")
async def create_task(
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Создать новую задачу"""
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

@router.get("/api/tasks/my-tasks")
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

@router.get("/api/tasks/employee/{employee_id}")
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

@router.get("/api/tasks/{task_id}")
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

@router.put("/api/tasks/{task_id}")
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
            
            if status is not None and status != old_status:
                task.status = status
                if status == "completed":
                    task.completed_at = datetime.utcnow()
                changes.append(f"статус: {old_status} → {status}")
            
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

@router.delete("/api/tasks/{task_id}")
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

@router.post("/api/tasks/{task_id}/comments")
async def add_task_comment(
    task_id: int,
    comment: str = Form(...),
    is_internal: bool = Form(False),
    current_user: dict = Depends(get_current_admin_user)
):
    """Добавить комментарий к задаче"""
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
            
            # Создаем комментарий
            new_comment = TaskComment(
                task_id=task_id,
                author_id=current_user["id"],
                comment=comment,
                is_internal=is_internal and current_user["role"] == "owner"  # Только владелец может создавать внутренние комментарии
            )
            
            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)
            
            logger.info(f"Добавлен комментарий к задаче {task_id}")
            
            return {
                "success": True,
                "message": "Комментарий добавлен",
                "comment": new_comment.to_dict()
            }
        
    except Exception as e:
        logger.error(f"Ошибка добавления комментария к задаче {task_id}: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/tasks/stats/dashboard")
async def get_task_dashboard_stats(
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить статистику для дашборда задач"""
    try:
        with get_db_context() as db:
            stats = {}
            
            # Базовый запрос в зависимости от роли
            if current_user["role"] == "owner":
                base_query = db.query(Task)
            else:
                base_query = db.query(Task).filter(Task.assigned_to_id == current_user["id"])
            
            # Общая статистика
            stats["total_tasks"] = base_query.count()
            stats["pending_tasks"] = base_query.filter(Task.status == "pending").count()
            stats["in_progress_tasks"] = base_query.filter(Task.status == "in_progress").count()
            stats["completed_tasks"] = base_query.filter(Task.status == "completed").count()
            
            # Просроченные задачи
            overdue_tasks = base_query.filter(
                Task.deadline < datetime.utcnow(),
                Task.status.in_(["pending", "in_progress"])
            ).count()
            stats["overdue_tasks"] = overdue_tasks
            
            # Задачи на сегодня
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            stats["today_tasks"] = base_query.filter(
                Task.deadline >= today_start,
                Task.deadline < today_end
            ).count()
            
            # Статистика по приоритетам
            stats["priority_stats"] = {
                "urgent": base_query.filter(Task.priority == "urgent").count(),
                "high": base_query.filter(Task.priority == "high").count(),
                "normal": base_query.filter(Task.priority == "normal").count(),
                "low": base_query.filter(Task.priority == "low").count()
            }
            
            # Последние задачи
            recent_tasks = base_query.order_by(
                Task.created_at.desc()
            ).limit(5).all()
            
            stats["recent_tasks"] = [task.to_dict() for task in recent_tasks]
            
            # Если владелец, добавляем статистику по сотрудникам
            if current_user["role"] == "owner":
                employee_stats = db.query(AdminUser).filter(
                    AdminUser.role == "executor",
                    AdminUser.is_active == True
                ).all()
                
                stats["employee_stats"] = []
                for employee in employee_stats:
                    emp_tasks = db.query(Task).filter(Task.assigned_to_id == employee.id)
                    
                    stats["employee_stats"].append({
                        "employee": employee.to_dict(),
                        "total_tasks": emp_tasks.count(),
                        "pending_tasks": emp_tasks.filter(Task.status == "pending").count(),
                        "completed_tasks": emp_tasks.filter(Task.status == "completed").count(),
                        "overdue_tasks": emp_tasks.filter(
                            Task.deadline < datetime.utcnow(),
                            Task.status.in_(["pending", "in_progress"])
                        ).count()
                    })
        
        return {"success": True, "stats": stats}
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики дашборда: {e}")
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

@router.put("/api/tasks/{task_id}/status")
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
            
            # Добавляем комментарий об изменении статуса
            if old_status != new_status:
                status_comment = TaskComment(
                    task_id=task_id,
                    author_id=current_user["id"],
                    comment=f"Статус изменен: {old_status} → {new_status}",
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

@router.put("/api/tasks/{task_id}/reassign")
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