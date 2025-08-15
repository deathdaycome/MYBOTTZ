# app/admin/routers/automation.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, Any
import asyncio

from ...database.database import get_db
from ...database.models import AdminUser
from ...services.project_automation import ProjectAutomationService
from ...services.scheduler import scheduler
from ...config.logging import get_logger
from ..auth import get_current_admin_user

logger = get_logger(__name__)
router = APIRouter(prefix="/automation", tags=["automation"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("/", response_class=HTMLResponse)
async def automation_page(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Страница управления автоматизацией"""
    return templates.TemplateResponse(
        "automation.html",
        {
            "request": request,
            "user": current_user,
            "scheduler_running": scheduler.is_running
        }
    )


@router.get("/summary")
async def get_automation_summary(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить сводку по автоматизации"""
    try:
        automation = ProjectAutomationService(db)
        summary = automation.get_automation_summary()
        
        return {
            "success": True,
            "summary": summary,
            "scheduler_running": scheduler.is_running
        }
    except Exception as e:
        logger.error(f"Ошибка получения сводки автоматизации: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-overdue")
async def check_overdue_projects(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Проверить и обновить просроченные проекты"""
    try:
        automation = ProjectAutomationService(db)
        overdue = automation.check_overdue_projects()
        
        return {
            "success": True,
            "message": f"Обновлено {len(overdue)} просроченных проектов",
            "projects": [
                {
                    "id": item["project"].id,
                    "title": item["project"].title,
                    "old_status": item["old_status"],
                    "message": item["message"]
                }
                for item in overdue
            ]
        }
    except Exception as e:
        logger.error(f"Ошибка проверки просроченных проектов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-unpaid")
async def check_unpaid_projects(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Проверить неоплаченные проекты"""
    try:
        automation = ProjectAutomationService(db)
        
        unpaid_projects = automation.check_unpaid_projects()
        unpaid_executors = automation.check_unpaid_executors()
        
        return {
            "success": True,
            "unpaid_projects": [
                {
                    "id": item["project"].id,
                    "title": item["project"].title,
                    "remaining": item["remaining"],
                    "days_passed": item["days_passed"],
                    "total_cost": item["total_cost"],
                    "paid": item["paid"]
                }
                for item in unpaid_projects
            ],
            "unpaid_executors": [
                {
                    "project_id": item["project"].id,
                    "project_title": item["project"].title,
                    "executor_id": item["executor_id"],
                    "executor_name": item["executor"].username if item["executor"] else "Unknown",
                    "remaining": item["remaining"],
                    "days_passed": item["days_passed"],
                    "total_cost": item["total_cost"],
                    "paid": item["paid"]
                }
                for item in unpaid_executors
            ]
        }
    except Exception as e:
        logger.error(f"Ошибка проверки неоплаченных проектов: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-daily")
async def run_daily_checks(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Запустить ежедневные проверки вручную"""
    try:
        automation = ProjectAutomationService(db)
        
        # Запускаем асинхронно
        await automation.run_daily_checks()
        
        return {
            "success": True,
            "message": "Ежедневные проверки выполнены успешно"
        }
    except Exception as e:
        logger.error(f"Ошибка выполнения ежедневных проверок: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-notification")
async def send_test_notification(
    message: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Отправить тестовое уведомление"""
    try:
        automation = ProjectAutomationService(db)
        
        success = await automation.send_notification(message)
        
        return {
            "success": success,
            "message": "Уведомление отправлено" if success else "Ошибка отправки уведомления"
        }
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/start")
async def start_scheduler(
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Запустить планировщик"""
    try:
        scheduler.start()
        return {
            "success": True,
            "message": "Планировщик запущен"
        }
    except Exception as e:
        logger.error(f"Ошибка запуска планировщика: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/stop")
async def stop_scheduler(
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Остановить планировщик"""
    try:
        scheduler.stop()
        return {
            "success": True,
            "message": "Планировщик остановлен"
        }
    except Exception as e:
        logger.error(f"Ошибка остановки планировщика: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/run-task")
async def run_scheduler_task(
    task_name: str,
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Запустить задачу планировщика немедленно"""
    try:
        success = scheduler.run_task_now(task_name)
        
        if success:
            return {
                "success": True,
                "message": f"Задача {task_name} запущена"
            }
        else:
            return {
                "success": False,
                "message": f"Неизвестная задача: {task_name}"
            }
    except Exception as e:
        logger.error(f"Ошибка запуска задачи {task_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/status")
async def get_scheduler_status(
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить статус планировщика"""
    return {
        "success": True,
        "is_running": scheduler.is_running,
        "available_tasks": [
            "daily_checks",
            "overdue_projects",
            "financial_status",
            "weekly_report"
        ]
    }