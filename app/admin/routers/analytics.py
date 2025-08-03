# app/admin/routers/analytics.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from ...database.database import get_db, get_db_context
from ...database.models import User, Project, ConsultantSession, FinanceTransaction
from ...config.logging import get_logger
from ...services.analytics_service import analytics_service, get_dashboard_data
from ..middleware.auth import get_current_admin_user

logger = get_logger(__name__)
templates = Jinja2Templates(directory="app/admin/templates")

router = APIRouter(tags=["analytics"])

# Роут для страницы аналитики удален, так как он уже есть в основном приложении

@router.get("/api/analytics/dashboard")
async def get_dashboard_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """API для получения данных дашборда аналитики"""
    try:
        analytics_data = get_dashboard_data(days)
        
        return {
            "success": True,
            "data": analytics_data
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения аналитики: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/api/analytics/users")
async def get_user_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """API для получения аналитики пользователей"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Общая статистика пользователей
        total_users = db.query(User).count()
        new_users = db.query(User).filter(
            User.registration_date >= start_date
        ).count()
        
        # Активные пользователи (с проектами)
        active_users = db.query(User).join(Project).distinct().count()
        
        # Данные по дням для графика
        daily_registrations = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_registrations = db.query(User).filter(
                and_(
                    User.registration_date >= day_start,
                    User.registration_date < day_end
                )
            ).count()
            
            daily_registrations.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "registrations": day_registrations
            })
        
        return {
            "success": True,
            "data": {
                "total_users": total_users,
                "new_users": new_users,
                "active_users": active_users,
                "conversion_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 2),
                "daily_registrations": daily_registrations
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения аналитики пользователей: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/api/analytics/projects")
async def get_project_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """API для получения аналитики проектов"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Общая статистика проектов
        total_projects = db.query(Project).count()
        new_projects = db.query(Project).filter(
            Project.created_at >= start_date
        ).count()
        completed_projects = db.query(Project).filter(
            Project.status == "completed"
        ).count()
        
        # Распределение по статусам
        status_distribution = {}
        statuses = ["new", "review", "accepted", "in_progress", "testing", "completed", "cancelled"]
        
        for status in statuses:
            count = db.query(Project).filter(Project.status == status).count()
            status_distribution[status] = count
        
        # Данные по дням для графика
        daily_projects = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_projects = db.query(Project).filter(
                and_(
                    Project.created_at >= day_start,
                    Project.created_at < day_end
                )
            ).count()
            
            daily_projects.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "projects": day_projects
            })
        
        return {
            "success": True,
            "data": {
                "total_projects": total_projects,
                "new_projects": new_projects,
                "completed_projects": completed_projects,
                "completion_rate": round((completed_projects / total_projects * 100) if total_projects > 0 else 0, 2),
                "status_distribution": status_distribution,
                "daily_projects": daily_projects
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения аналитики проектов: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/api/analytics/finance")
async def get_finance_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """API для получения финансовой аналитики"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Общая финансовая статистика
        total_revenue = db.query(func.sum(Project.estimated_cost)).filter(
            Project.status == "completed"
        ).scalar() or 0
        
        potential_revenue = db.query(func.sum(Project.estimated_cost)).filter(
            Project.status.in_(["new", "review", "accepted", "in_progress", "testing"])
        ).scalar() or 0
        
        avg_check = db.query(func.avg(Project.estimated_cost)).filter(
            Project.estimated_cost.isnot(None)
        ).scalar() or 0
        
        # Платежи клиентов
        client_payments = db.query(func.sum(Project.client_paid_total)).scalar() or 0
        
        # Выплаты исполнителям
        executor_payments = db.query(func.sum(Project.executor_paid_total)).scalar() or 0
        
        return {
            "success": True,
            "data": {
                "total_revenue": float(total_revenue),
                "potential_revenue": float(potential_revenue),
                "avg_check": float(avg_check),
                "client_payments": float(client_payments),
                "executor_payments": float(executor_payments),
                "profit": float(client_payments - executor_payments)
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения финансовой аналитики: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/api/analytics/export")
async def export_analytics(
    format: str = "json",
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Экспорт данных аналитики"""
    try:
        analytics_data = get_dashboard_data(days)
        
        if format.lower() == "json":
            return {
                "success": True,
                "data": analytics_data,
                "exported_at": datetime.utcnow().isoformat(),
                "period_days": days
            }
        else:
            return {
                "success": False,
                "error": "Поддерживается только JSON формат"
            }
        
    except Exception as e:
        logger.error(f"Ошибка экспорта аналитики: {e}")
        return {
            "success": False,
            "error": str(e)
        }