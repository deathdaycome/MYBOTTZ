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

from ..dependencies import get_db, get_current_admin_user, templates
from ...database.models import AdminUser
from ...database.notification_models import (
    EmployeeNotificationSettings,
    NotificationQueue,
    NotificationLog
)
from ...services.employee_notification_service import employee_notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/settings", response_class=HTMLResponse)
async def notification_settings_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Страница настроек уведомлений"""
    
    # Получаем всех сотрудников
    employees = db.query(AdminUser).filter(
        AdminUser.role.in_(['executor', 'salesperson'])
    ).all()
    
    # Получаем настройки уведомлений для каждого сотрудника
    employee_settings = {}
    for employee in employees:
        settings = employee_notification_service.get_employee_settings(db, employee.id)
        employee_settings[employee.id] = settings
    
    return templates.TemplateResponse("admin/notifications/settings.html", {
        "request": request,
        "current_user": current_user,
        "employees": employees,
        "employee_settings": employee_settings,
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
    if current_user.role not in ['owner', 'admin']:
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
    if current_user.role not in ['owner', 'admin']:
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
    if current_user.role not in ['owner', 'admin']:
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
    if current_user.role not in ['owner', 'admin']:
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
    if current_user.role not in ['owner', 'admin']:
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
    if current_user.role not in ['owner', 'admin']:
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