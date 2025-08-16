from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database.database import get_db
from app.database.models import (
    ServiceProvider, ServiceExpense, Project, AdminUser,
    FinanceTransaction, FinanceCategory
)
from app.admin.middleware.auth import require_admin_auth
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json
import calendar

router = APIRouter(tags=["admin_services"])
templates = Jinja2Templates(directory="app/admin/templates")

@router.get("/services", response_class=HTMLResponse)
async def services_page(request: Request, user: AdminUser = Depends(require_admin_auth)):
    """Страница управления сервисами"""
    # Получаем элементы навигации
    from app.admin.app import get_navigation_items
    navigation_items = get_navigation_items(user.get("role", "admin") if isinstance(user, dict) else user.role)
    
    return templates.TemplateResponse("services.html", {
        "request": request,
        "user": user,
        "username": user.get("username") if isinstance(user, dict) else user.username,
        "user_role": user.role,
        "navigation_items": navigation_items
    })

@router.get("/api/services", response_class=JSONResponse)
async def get_services(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth),
    service_type: Optional[str] = None,
    status: Optional[str] = None
):
    """Получить список сервисов"""
    try:
        query = db.query(ServiceProvider)
        
        # Фильтры
        if service_type:
            query = query.filter(ServiceProvider.provider_type == service_type)
            
        if status:
            query = query.filter(ServiceProvider.status == status)
        
        services = query.order_by(ServiceProvider.name).all()
        
        # Добавляем статистику расходов для каждого сервиса
        services_data = []
        for service in services:
            service_dict = service.to_dict()
            
            # Статистика за текущий месяц
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            monthly_cost = db.query(func.sum(ServiceExpense.amount)).filter(
                ServiceExpense.service_provider_id == service.id,
                ServiceExpense.expense_date >= current_month_start
            ).scalar() or 0
            
            # Расходы за всё время
            total_cost = db.query(func.sum(ServiceExpense.amount)).filter(
                ServiceExpense.service_provider_id == service.id
            ).scalar() or 0
            
            # Количество расходов
            expense_count = db.query(func.count(ServiceExpense.id)).filter(
                ServiceExpense.service_provider_id == service.id
            ).scalar() or 0
            
            service_dict["statistics"] = {
                "monthly_cost": monthly_cost,
                "total_cost": total_cost,
                "expense_count": expense_count
            }
            
            services_data.append(service_dict)
        
        return {
            "success": True,
            "services": services_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при получении сервисов: {str(e)}"
        }

@router.post("/api/services", response_class=JSONResponse)
async def create_service(
    request: Request,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Создать новый сервис"""
    try:
        data = await request.json()
        
        service = ServiceProvider(
            name=data["name"],
            description=data.get("description"),
            provider_type=data["provider_type"],
            website=data.get("website"),
            contact_info=data.get("contact_info", {}),
            pricing_model=data.get("pricing_model"),
            status=data.get("status", "active"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(service)
        db.commit()
        db.refresh(service)
        
        return {
            "success": True,
            "message": "Сервис успешно создан",
            "service": service.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка при создании сервиса: {str(e)}"
        }

@router.get("/api/services/{service_id}", response_class=JSONResponse)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Получить данные сервиса"""
    try:
        service = db.query(ServiceProvider).filter(ServiceProvider.id == service_id).first()
        if not service:
            return {
                "success": False,
                "message": "Сервис не найден"
            }
        
        # Получаем расходы за последние 30 дней
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        expenses = db.query(ServiceExpense).filter(
            ServiceExpense.service_provider_id == service_id,
            ServiceExpense.expense_date >= thirty_days_ago
        ).order_by(ServiceExpense.expense_date.desc()).all()
        
        return {
            "success": True,
            "service": service.to_dict(),
            "recent_expenses": [expense.to_dict() for expense in expenses]
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при получении данных сервиса: {str(e)}"
        }

@router.put("/api/services/{service_id}", response_class=JSONResponse)
async def update_service(
    service_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Обновить данные сервиса"""
    try:
        service = db.query(ServiceProvider).filter(ServiceProvider.id == service_id).first()
        if not service:
            return {
                "success": False,
                "message": "Сервис не найден"
            }
        
        data = await request.json()
        
        # Обновляем поля
        for field, value in data.items():
            if hasattr(service, field):
                setattr(service, field, value)
        
        service.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Данные сервиса обновлены",
            "service": service.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка при обновлении сервиса: {str(e)}"
        }

@router.post("/api/services/{service_id}/expense", response_class=JSONResponse)
async def create_service_expense(
    service_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Создать расход для сервиса"""
    try:
        data = await request.json()
        
        service = db.query(ServiceProvider).filter(ServiceProvider.id == service_id).first()
        if not service:
            return {
                "success": False,
                "message": "Сервис не найден"
            }
        
        # Создаем расход
        expense = ServiceExpense(
            service_provider_id=service_id,
            project_id=data.get("project_id"),
            amount=float(data["amount"]),
            expense_type=data.get("expense_type", "usage"),
            description=data.get("description", ""),
            expense_date=datetime.fromisoformat(data.get("expense_date", datetime.utcnow().isoformat())),
            usage_details=data.get("usage_details", {}),
            created_by_id=user.id
        )
        
        db.add(expense)
        
        # Создаем финансовую транзакцию
        expense_category = db.query(FinanceCategory).filter(
            FinanceCategory.type == "expense",
            FinanceCategory.name.contains("сервис")
        ).first()
        
        if expense_category:
            transaction = FinanceTransaction(
                amount=expense.amount,
                type="expense",
                description=f"Расход на сервис {service.name}: {expense.description}",
                date=expense.expense_date,
                category_id=expense_category.id,
                notes=f"Автоматическая запись расхода на сервис",
                created_by_id=user.id
            )
            db.add(transaction)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Расход записан",
            "expense": expense.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка при записи расхода: {str(e)}"
        }

@router.get("/api/services/stats", response_class=JSONResponse)
async def get_services_statistics(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth),
    period: str = "month"  # week, month, quarter, year
):
    """Получить статистику по сервисам"""
    try:
        # Определяем период
        now = datetime.utcnow()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        # Общая статистика
        total_services = db.query(ServiceProvider).count()
        active_services = db.query(ServiceProvider).filter(ServiceProvider.status == "active").count()
        
        # Статистика расходов за период
        total_cost = db.query(func.sum(ServiceExpense.amount)).filter(
            ServiceExpense.expense_date >= start_date
        ).scalar() or 0
        
        # Статистика по типам сервисов
        service_types_stats = db.query(
            ServiceProvider.provider_type,
            func.count(ServiceProvider.id).label("count"),
            func.sum(ServiceExpense.amount).label("total_cost")
        ).outerjoin(
            ServiceExpense, ServiceProvider.id == ServiceExpense.service_provider_id
        ).filter(
            ServiceExpense.expense_date >= start_date
        ).group_by(
            ServiceProvider.provider_type
        ).all()
        
        # Топ сервисы по расходам
        top_services = db.query(
            ServiceProvider.name,
            ServiceProvider.provider_type,
            func.sum(ServiceExpense.amount).label("total_cost"),
            func.count(ServiceExpense.id).label("expense_count")
        ).join(
            ServiceExpense, ServiceProvider.id == ServiceExpense.service_provider_id
        ).filter(
            ServiceExpense.expense_date >= start_date
        ).group_by(
            ServiceProvider.id, ServiceProvider.name, ServiceProvider.provider_type
        ).order_by(
            func.sum(ServiceExpense.amount).desc()
        ).limit(10).all()
        
        # Прогноз расходов на месяц
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        days_passed = (now - current_month_start).days + 1
        
        month_cost_so_far = db.query(func.sum(ServiceExpense.amount)).filter(
            ServiceExpense.expense_date >= current_month_start
        ).scalar() or 0
        
        projected_month_cost = 0
        if days_passed > 0:
            daily_average = month_cost_so_far / days_passed
            projected_month_cost = daily_average * days_in_month
        
        return {
            "success": True,
            "statistics": {
                "period": period,
                "total_services": total_services,
                "active_services": active_services,
                "total_cost": total_cost,
                "projected_month_cost": projected_month_cost,
                "month_cost_so_far": month_cost_so_far,
                "service_types": [
                    {
                        "type": service_type,
                        "count": count,
                        "total_cost": float(total_cost) if total_cost else 0
                    }
                    for service_type, count, total_cost in service_types_stats
                ],
                "top_services": [
                    {
                        "name": name,
                        "type": service_type,
                        "total_cost": float(total_cost) if total_cost else 0,
                        "expense_count": int(expense_count) if expense_count else 0
                    }
                    for name, service_type, total_cost, expense_count in top_services
                ]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при получении статистики: {str(e)}"
        }

@router.get("/api/services/billing/upcoming", response_class=JSONResponse)
async def get_upcoming_billing(
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth),
    days_ahead: int = 30
):
    """Получить предстоящие платежи за сервисы"""
    try:
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        # Получаем recurring расходы (подписки)
        recurring_expenses = db.query(ServiceExpense).filter(
            ServiceExpense.status == "active",
            ServiceExpense.is_recurring == True,
            ServiceExpense.period_end <= end_date,
            ServiceExpense.period_end.isnot(None)
        ).order_by(ServiceExpense.period_end).all()
        
        billing_data = []
        total_upcoming_cost = 0
        
        for expense in recurring_expenses:
            # Берем сумму текущего расхода как оценку
            estimated_cost = expense.amount
            
            billing_info = expense.to_dict()
            billing_info["estimated_cost"] = estimated_cost
            billing_info["days_until_billing"] = (expense.period_end - datetime.utcnow()).days if expense.period_end else 0
            
            billing_data.append(billing_info)
            total_upcoming_cost += estimated_cost
        
        return {
            "success": True,
            "upcoming_billing": billing_data,
            "total_upcoming_cost": total_upcoming_cost,
            "days_ahead": days_ahead
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при получении предстоящих платежей: {str(e)}"
        }

@router.post("/api/services/{service_id}/reset-usage", response_class=JSONResponse)
async def reset_service_usage(
    service_id: int,
    db: Session = Depends(get_db),
    user: AdminUser = Depends(require_admin_auth)
):
    """Сбросить текущее использование сервиса (обновить период подписки)"""
    try:
        service = db.query(ServiceProvider).filter(ServiceProvider.id == service_id).first()
        if not service:
            return {
                "success": False,
                "message": "Сервис не найден"
            }
        
        # Обновляем timestamp
        service.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Данные сервиса обновлены",
            "service": service.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Ошибка при обновлении сервиса: {str(e)}"
        }
