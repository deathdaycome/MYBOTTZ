"""
Роутер для управления уведомлениями сотрудников
"""

from fastapi import APIRouter, Depends, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, timedelta

from ..middleware.auth import get_current_admin_user
from ...database.database import get_db
from ...database.models import AdminUser
from ...database.notification_models import (
    EmployeeNotificationSettings,
    NotificationQueue,
    NotificationLog
)
from ...services.employee_notification_service import employee_notification_service

# Настройка шаблонов
templates = Jinja2Templates(directory="app/admin/templates")

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_class=HTMLResponse)
async def notifications_main(request: Request):
    """Главная страница уведомлений - редирект на настройки"""
    return RedirectResponse(url="/admin/notifications/settings", status_code=302)

@router.get("/settings", response_class=HTMLResponse)
async def notification_settings_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Страница настроек уведомлений"""
    
    # Получаем всех сотрудников (включая sales и executor)
    employees = db.query(AdminUser).filter(
        AdminUser.role.in_(['executor', 'salesperson', 'sales'])
    ).all()
    
    # Получаем настройки уведомлений для каждого сотрудника
    employee_settings = {}
    for employee in employees:
        settings = employee_notification_service.get_employee_settings(db, employee.id)
        employee_settings[employee.id] = settings
    
    # Получаем статистику очереди
    stats = {
        'pending': db.query(NotificationQueue).filter(NotificationQueue.status == 'pending').count(),
        'sent': db.query(NotificationQueue).filter(NotificationQueue.status == 'sent').count(),
        'failed': db.query(NotificationQueue).filter(NotificationQueue.status == 'failed').count(),
    }
    
    return templates.TemplateResponse("admin/notifications/settings.html", {
        "request": request,
        "current_user": current_user,
        "employees": employees,
        "employee_settings": employee_settings,
        "stats": stats,
        "page_title": "Настройки уведомлений"
    })

@router.post("/settings/{employee_id}")
async def update_employee_settings(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
    telegram_user_id: str = Form(...),
    notifications_enabled: bool = Form(default=False),
    
    # Настройки для исполнителей
    project_assigned: bool = Form(default=False),
    project_status_changed: bool = Form(default=False),
    project_deadline_reminder: bool = Form(default=False),
    project_overdue: bool = Form(default=False),
    
    # Настройки для продажников
    avito_new_message: bool = Form(default=False),
    avito_unread_reminder: bool = Form(default=False),
    avito_urgent_message: bool = Form(default=False),
    lead_assigned: bool = Form(default=False),
    lead_status_changed: bool = Form(default=False),
    deal_assigned: bool = Form(default=False),
    deal_status_changed: bool = Form(default=False),
    
    # Настройки времени
    work_hours_start: str = Form(default="09:00"),
    work_hours_end: str = Form(default="18:00"),
    weekend_notifications: bool = Form(default=False),
    urgent_notifications_always: bool = Form(default=True),
    
    # Интервалы напоминаний
    avito_reminder_interval: int = Form(default=30),
    project_reminder_interval: int = Form(default=120)
):
    """Обновить настройки уведомлений сотрудника"""
    
    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверяем, что сотрудник существует
    employee = db.query(AdminUser).filter(AdminUser.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    # Подготавливаем данные для обновления
    settings_data = {
        'telegram_user_id': telegram_user_id,
        'notifications_enabled': notifications_enabled,
        'project_assigned': project_assigned,
        'project_status_changed': project_status_changed,
        'project_deadline_reminder': project_deadline_reminder,
        'project_overdue': project_overdue,
        'avito_new_message': avito_new_message,
        'avito_unread_reminder': avito_unread_reminder,
        'avito_urgent_message': avito_urgent_message,
        'lead_assigned': lead_assigned,
        'lead_status_changed': lead_status_changed,
        'deal_assigned': deal_assigned,
        'deal_status_changed': deal_status_changed,
        'work_hours_start': work_hours_start,
        'work_hours_end': work_hours_end,
        'weekend_notifications': weekend_notifications,
        'urgent_notifications_always': urgent_notifications_always,
        'avito_reminder_interval': avito_reminder_interval,
        'project_reminder_interval': project_reminder_interval
    }
    
    try:
        # Создаем или обновляем настройки
        settings = employee_notification_service.get_employee_settings(db, employee_id)
        if settings:
            employee_notification_service.update_employee_settings(db, employee_id, **settings_data)
        else:
            employee_notification_service.create_employee_settings(db, employee_id, **settings_data)
        
        return RedirectResponse(
            url="/admin/notifications/settings?success=1", 
            status_code=303
        )
        
    except Exception as e:
        return RedirectResponse(
            url=f"/admin/notifications/settings?error={str(e)}", 
            status_code=303
        )

@router.get("/queue", response_class=HTMLResponse)
async def notification_queue_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
    status: Optional[str] = Query(None),
    notification_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Страница очереди уведомлений"""
    
    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Базовый запрос
    query = db.query(NotificationQueue)
    
    # Фильтры
    if status:
        query = query.filter(NotificationQueue.status == status)
    if notification_type:
        query = query.filter(NotificationQueue.notification_type == notification_type)
    
    # Подсчет общего количества
    total = query.count()
    
    # Пагинация
    offset = (page - 1) * limit
    notifications = query.order_by(
        NotificationQueue.priority.desc(),
        NotificationQueue.scheduled_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Получаем статистику
    stats = {
        'pending': db.query(NotificationQueue).filter(NotificationQueue.status == 'pending').count(),
        'sent': db.query(NotificationQueue).filter(NotificationQueue.status == 'sent').count(),
        'failed': db.query(NotificationQueue).filter(NotificationQueue.status == 'failed').count(),
        'cancelled': db.query(NotificationQueue).filter(NotificationQueue.status == 'cancelled').count(),
    }
    
    return templates.TemplateResponse("admin/notifications/queue.html", {
        "request": request,
        "current_user": current_user,
        "notifications": notifications,
        "stats": stats,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "status_filter": status,
        "type_filter": notification_type,
        "page_title": "Очередь уведомлений"
    })

@router.get("/log", response_class=HTMLResponse)
async def notification_log_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
    employee_id: Optional[int] = Query(None),
    notification_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Страница лога уведомлений"""
    
    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Базовый запрос
    query = db.query(NotificationLog)
    
    # Фильтры
    if employee_id:
        query = query.filter(NotificationLog.admin_user_id == employee_id)
    if notification_type:
        query = query.filter(NotificationLog.notification_type == notification_type)
    if status:
        query = query.filter(NotificationLog.status == status)
    
    # Подсчет общего количества
    total = query.count()
    
    # Пагинация
    offset = (page - 1) * limit
    logs = query.order_by(NotificationLog.sent_at.desc()).offset(offset).limit(limit).all()
    
    # Получаем список сотрудников для фильтра
    employees = db.query(AdminUser).filter(
        AdminUser.role.in_(['executor', 'salesperson'])
    ).all()
    
    return templates.TemplateResponse("admin/notifications/log.html", {
        "request": request,
        "current_user": current_user,
        "logs": logs,
        "employees": employees,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "employee_filter": employee_id,
        "type_filter": notification_type,
        "status_filter": status,
        "page_title": "Лог уведомлений"
    })

@router.post("/test/{employee_id}")
async def send_test_notification(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Отправить тестовое уведомление сотруднику"""
    
    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Получаем настройки сотрудника
    settings = employee_notification_service.get_employee_settings(db, employee_id)
    if not settings:
        return JSONResponse({"success": False, "error": "Настройки уведомлений не найдены"})
    
    # Получаем сотрудника
    employee = db.query(AdminUser).filter(AdminUser.id == employee_id).first()
    if not employee:
        return JSONResponse({"success": False, "error": "Сотрудник не найден"})
    
    try:
        # Отправляем тестовое уведомление
        await employee_notification_service.create_notification(
            db=db,
            telegram_user_id=settings.telegram_user_id,
            admin_user_id=employee_id,
            notification_type='test',
            title='🧪 Тестовое уведомление',
            message=f'Привет, {employee.full_name}!\n\nЭто тестовое уведомление для проверки настроек.\n\n✅ Уведомления работают корректно!',
            priority='normal'
        )
        
        return JSONResponse({"success": True, "message": "Тестовое уведомление отправлено"})
        
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@router.post("/process-queue")
async def process_notification_queue_manual(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Принудительная обработка очереди уведомлений"""
    
    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    try:
        await employee_notification_service.process_notification_queue(db)
        return JSONResponse({"success": True, "message": "Очередь уведомлений обработана"})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@router.get("/stats")
async def notification_stats(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
    days: int = Query(7, ge=1, le=365)
):
    """Статистика уведомлений"""

    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # Период для статистики
    date_from = datetime.utcnow() - timedelta(days=days)

    # Статистика отправленных уведомлений
    sent_stats = db.query(
        NotificationLog.notification_type,
        func.count(NotificationLog.id).label('count'),
        func.count(func.distinct(NotificationLog.admin_user_id)).label('unique_users')
    ).filter(
        NotificationLog.sent_at >= date_from,
        NotificationLog.status == 'sent'
    ).group_by(NotificationLog.notification_type).all()

    # Статистика по дням
    daily_stats = db.query(
        func.date(NotificationLog.sent_at).label('date'),
        func.count(NotificationLog.id).label('count')
    ).filter(
        NotificationLog.sent_at >= date_from,
        NotificationLog.status == 'sent'
    ).group_by(func.date(NotificationLog.sent_at)).all()

    return JSONResponse({
        "success": True,
        "data": {
            "by_type": [{"type": stat[0], "count": stat[1], "unique_users": stat[2]} for stat in sent_stats],
            "by_day": [{"date": stat[0], "count": stat[1]} for stat in daily_stats],
            "period_days": days
        }
    })


# ==================== JSON API для React ====================

@router.get("/api/employees", response_class=JSONResponse)
async def get_employees_with_settings(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить список всех сотрудников с настройками уведомлений (JSON API для React)"""

    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # Получаем всех сотрудников
    employees = db.query(AdminUser).filter(
        AdminUser.role.in_(['executor', 'salesperson', 'sales', 'owner', 'admin'])
    ).all()

    result = []
    for employee in employees:
        settings = employee_notification_service.get_employee_settings(db, employee.id)

        employee_data = {
            "id": employee.id,
            "username": employee.username,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "full_name": employee.full_name,
            "email": employee.email,
            "role": employee.role,
            "telegram_id": employee.telegram_id,
            "settings": settings.to_dict() if settings else None
        }
        result.append(employee_data)

    return JSONResponse({"success": True, "employees": result})


@router.get("/api/settings/{employee_id}", response_class=JSONResponse)
async def get_employee_settings_api(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить настройки уведомлений сотрудника (JSON API для React)"""

    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # Проверяем существование сотрудника
    employee = db.query(AdminUser).filter(AdminUser.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    settings = employee_notification_service.get_employee_settings(db, employee_id)

    return JSONResponse({
        "success": True,
        "settings": settings.to_dict() if settings else None
    })


@router.put("/api/settings/{employee_id}", response_class=JSONResponse)
async def update_employee_settings_api(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Обновить настройки уведомлений сотрудника (JSON API для React)"""

    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # Проверяем существование сотрудника
    employee = db.query(AdminUser).filter(AdminUser.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    # Получаем JSON данные из request body
    try:
        settings_data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат JSON: {str(e)}")

    try:
        # Создаем или обновляем настройки
        settings = employee_notification_service.get_employee_settings(db, employee_id)
        if settings:
            updated_settings = employee_notification_service.update_employee_settings(
                db, employee_id, **settings_data
            )
        else:
            updated_settings = employee_notification_service.create_employee_settings(
                db, employee_id, **settings_data
            )

        return JSONResponse({
            "success": True,
            "message": "Настройки успешно обновлены",
            "settings": updated_settings.to_dict() if updated_settings else None
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек: {str(e)}")


@router.get("/api/types", response_class=JSONResponse)
async def get_notification_types(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить список всех типов уведомлений с описаниями (JSON API для React)"""

    # Проверяем права доступа
    user_role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if user_role not in ['owner', 'admin']:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    notification_types = {
        "projects": {
            "label": "Проекты",
            "types": [
                {
                    "key": "project_assigned",
                    "label": "Назначение на проект",
                    "description": "Уведомление при назначении сотрудника исполнителем проекта"
                },
                {
                    "key": "project_status_changed",
                    "label": "Изменение статуса проекта",
                    "description": "Уведомление при изменении статуса проекта"
                },
                {
                    "key": "project_deadline_reminder",
                    "label": "Напоминание о дедлайне проекта",
                    "description": "Напоминание за 24 часа до дедлайна проекта"
                },
                {
                    "key": "project_overdue",
                    "label": "Просрочка проекта",
                    "description": "Уведомление о просроченном проекте"
                },
                {
                    "key": "project_new_task",
                    "label": "Новая задача в проекте",
                    "description": "Уведомление о создании новой задачи в проекте"
                }
            ]
        },
        "tasks": {
            "label": "Задачи",
            "types": [
                {
                    "key": "task_assigned",
                    "label": "Назначение задачи",
                    "description": "Уведомление при назначении задачи на сотрудника"
                },
                {
                    "key": "task_status_changed",
                    "label": "Изменение статуса задачи",
                    "description": "Уведомление при изменении статуса задачи"
                },
                {
                    "key": "task_deadline_reminder",
                    "label": "Напоминание о дедлайне задачи",
                    "description": "Напоминание за 24/4/1 час до дедлайна задачи"
                },
                {
                    "key": "task_comment_added",
                    "label": "Новый комментарий к задаче",
                    "description": "Уведомление о новом комментарии в задаче"
                }
            ]
        },
        "revisions": {
            "label": "Правки",
            "types": [
                {
                    "key": "revision_new",
                    "label": "Новая правка",
                    "description": "Уведомление о создании новой правки от клиента"
                },
                {
                    "key": "revision_status_changed",
                    "label": "Изменение статуса правки",
                    "description": "Уведомление при изменении статуса правки"
                },
                {
                    "key": "revision_message_new",
                    "label": "Новое сообщение в правке",
                    "description": "Уведомление о новом сообщении в чате правки"
                }
            ]
        },
        "chats": {
            "label": "Чаты",
            "types": [
                {
                    "key": "project_chat_new_message",
                    "label": "Новое сообщение в чате проекта",
                    "description": "Уведомление о новом сообщении от клиента в чате проекта"
                }
            ]
        },
        "avito": {
            "label": "Avito и CRM",
            "types": [
                {
                    "key": "avito_new_message",
                    "label": "Новое сообщение с Avito",
                    "description": "Уведомление о новом сообщении от клиента с Avito"
                },
                {
                    "key": "avito_unread_reminder",
                    "label": "Напоминание о непрочитанных Avito",
                    "description": "Напоминание о непрочитанных сообщениях с Avito"
                },
                {
                    "key": "avito_urgent_message",
                    "label": "Срочное сообщение Avito",
                    "description": "Уведомление о срочном сообщении с Avito"
                },
                {
                    "key": "lead_assigned",
                    "label": "Назначение лида",
                    "description": "Уведомление при назначении лида на сотрудника"
                },
                {
                    "key": "lead_status_changed",
                    "label": "Изменение статуса лида",
                    "description": "Уведомление при изменении статуса лида"
                },
                {
                    "key": "deal_assigned",
                    "label": "Назначение сделки",
                    "description": "Уведомление при назначении сделки на сотрудника"
                },
                {
                    "key": "deal_status_changed",
                    "label": "Изменение статуса сделки",
                    "description": "Уведомление при изменении статуса сделки"
                }
            ]
        }
    }

    return JSONResponse({
        "success": True,
        "types": notification_types
    })