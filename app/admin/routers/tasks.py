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
from ..middleware.roles import RoleMiddleware

logger = get_logger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/admin/templates")

@router.get("/user/my-tasks", response_class=HTMLResponse)
async def my_tasks_page(request: Request, current_user: dict = Depends(get_current_admin_user)):
    """Страница 'Мои задачи' для всех пользователей"""
    try:
        with get_db_context() as db:
            # Получаем только задачи текущего пользователя
            query = db.query(Task).filter(Task.assigned_to_id == current_user["id"])
            tasks = query.order_by(Task.created_at.desc()).all()
            
            # Преобразуем задачи в словари
            tasks_data = []
            for task in tasks:
                # Загружаем связанные объекты
                if task.created_by_id:
                    task.created_by = db.query(AdminUser).filter(AdminUser.id == task.created_by_id).first()
                
                # Преобразуем в словарь с дополнительными полями
                task_dict = task.to_dict()
                task_dict["is_overdue"] = task.is_overdue
                task_dict["days_until_deadline"] = task.days_until_deadline
                task_dict["can_delete"] = current_user["role"] == "owner"  # Только владелец может удалять задачи
                tasks_data.append(task_dict)
            
            # Статистика
            stats = {
                "total": len(tasks_data),
                "pending": len([t for t in tasks_data if t["status"] == "pending"]),
                "in_progress": len([t for t in tasks_data if t["status"] == "in_progress"]),
                "completed": len([t for t in tasks_data if t["status"] == "completed"]),
                "overdue": len([t for t in tasks_data if t["is_overdue"]])
            }
            
            # Для исполнителей показываем только его самого в "сотрудниках"
            employees = [current_user]
            
            return templates.TemplateResponse("my_tasks.html", {
                "request": request,
                "tasks": tasks_data,
                "employees": employees,
                "stats": stats,
                "current_user": current_user
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
            
            # Владелец видит все задачи, исполнители - только свои
            if current_user["role"] == "executor":
                query = query.filter(Task.assigned_to_id == current_user["id"])
            elif current_user["role"] == "owner":
                # Владелец видит все задачи
                pass
            
            tasks = query.order_by(Task.created_at.desc()).all()
            
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
            if current_user["role"] == "owner":
                # Владелец видит всех активных сотрудников (исполнителей + себя)
                employees_raw = db.query(AdminUser).filter(
                    AdminUser.is_active == True,
                    AdminUser.role.in_(["owner", "executor"])
                ).all()
                employees = [emp.to_dict() for emp in employees_raw]
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
            
            return templates.TemplateResponse("tasks_new.html", {
                "request": request,
                "tasks": tasks_data,
                "employees": employees,
                "stats": stats,
                "current_user": current_user
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
            
            return templates.TemplateResponse("task_detail.html", {
                "request": request,
                "task": task,
                "current_user": current_user
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
    title: str = Form(...),
    description: str = Form(""),
    assigned_to_id: int = Form(...),
    priority: str = Form("normal"),
    deadline: Optional[str] = Form(None),
    estimated_hours: Optional[int] = Form(None),
    color: str = Form("normal"),
    current_user: dict = Depends(get_current_admin_user)
):
    """Создать новую задачу"""
    try:
        # Проверяем права (только владелец может создавать задачи)
        if current_user["role"] != "owner":
            return {"success": False, "error": "Недостаточно прав"}
        
        # Парсим дату дедлайна
        deadline_dt = None
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline.replace('T', ' '))
            except ValueError:
                return {"success": False, "error": "Неверный формат даты"}
        
        with get_db_context() as db:
            # Проверяем существование исполнителя
            executor = db.query(AdminUser).filter(
                AdminUser.id == assigned_to_id,
                AdminUser.is_active == True
            ).first()
            
            if not executor:
                return {"success": False, "error": "Исполнитель не найден"}
            
            # Создаем задачу (исправляем проблему с ID=0)
            creator_id = current_user["id"] if current_user["id"] > 0 else 1
            
            new_task = Task(
                title=title,
                description=description,
                assigned_to_id=assigned_to_id,
                created_by_id=creator_id,  # Используем правильный ID
                priority=priority,
                deadline=deadline_dt,
                estimated_hours=estimated_hours,
                status="pending",
                color=color
            )
            
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            
            logger.info(f"Создана задача {new_task.id}: {title}")
            
            return {
                "success": True,
                "message": "Задача создана",
                "task": new_task.to_dict()
            }
        
    except Exception as e:
        logger.error(f"Ошибка создания задачи: {e}")
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
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    priority: Optional[str] = Form(None),
    deadline: Optional[str] = Form(None),
    estimated_hours: Optional[int] = Form(None),
    actual_hours: Optional[int] = Form(None),
    assigned_to_id: Optional[int] = Form(None),
    color: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_admin_user)
):
    """Обновить задачу"""
    try:
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
    """Удалить задачу (только владелец)"""
    try:
        # Проверяем права доступа
        if current_user["role"] != "owner":
            return {"success": False, "error": "Недостаточно прав для удаления задач"}
            
        with get_db_context() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {"success": False, "error": "Задача не найдена"}
            
            # Удаляем комментарии
            db.query(TaskComment).filter(TaskComment.task_id == task_id).delete()
            
            # Удаляем задачу
            db.delete(task)
            db.commit()
            
            logger.info(f"Удалена задача {task_id}: {task.title}")
            
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