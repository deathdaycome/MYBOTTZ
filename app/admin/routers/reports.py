# app/admin/routers/reports.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from ...database.database import get_db
from ...database.models import AdminUser
from ...services.reports_service import ReportsService
from ...config.logging import get_logger
from ..auth import get_current_admin_user

logger = get_logger(__name__)
router = APIRouter(tags=["reports"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("/reports", response_class=HTMLResponse)
async def reports_page(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Страница отчетов"""
    # Импортируем функцию get_navigation_items
    from ..app import get_navigation_items
    
    user_role = current_user.get("role", "owner") if isinstance(current_user, dict) else current_user.role
    navigation_items = get_navigation_items(user_role)
    
    return templates.TemplateResponse(
        "reports.html",
        {
            "request": request,
            "user": current_user,
            "username": current_user.get("username") if isinstance(current_user, dict) else current_user.username,
            "user_role": user_role,
            "navigation_items": navigation_items
        }
    )


@router.get("/reports/projects")
async def get_projects_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    executor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить отчет по проектам"""
    try:
        # Парсим даты
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        reports_service = ReportsService(db)
        report = reports_service.get_projects_report(
            start_date=start_dt,
            end_date=end_dt,
            status=status,
            executor_id=executor_id
        )
        
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        logger.error(f"Ошибка получения отчета по проектам: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/financial")
async def get_financial_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить финансовый отчет"""
    try:
        # Парсим даты
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        reports_service = ReportsService(db)
        report = reports_service.get_financial_report(
            start_date=start_dt,
            end_date=end_dt
        )
        
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        logger.error(f"Ошибка получения финансового отчета: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/executor/{executor_id}")
async def get_executor_report(
    executor_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить отчет по исполнителю"""
    try:
        reports_service = ReportsService(db)
        report = reports_service.get_executor_report(executor_id)
        
        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        logger.error(f"Ошибка получения отчета по исполнителю: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/export/excel")
async def export_report_to_excel(
    report_type: str = Query(..., description="Тип отчета: projects, financial, executor"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    executor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Экспорт отчета в Excel"""
    try:
        reports_service = ReportsService(db)
        
        # Получаем данные отчета в зависимости от типа
        if report_type == 'projects':
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            
            report_data = reports_service.get_projects_report(
                start_date=start_dt,
                end_date=end_dt,
                status=status,
                executor_id=executor_id
            )
            filename = f"projects_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
        elif report_type == 'financial':
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            
            report_data = reports_service.get_financial_report(
                start_date=start_dt,
                end_date=end_dt
            )
            filename = f"financial_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
        elif report_type == 'executor' and executor_id:
            report_data = reports_service.get_executor_report(executor_id)
            filename = f"executor_report_{executor_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
        else:
            raise ValueError(f"Неподдерживаемый тип отчета: {report_type}")
        
        # Экспортируем в Excel
        excel_file = reports_service.export_to_excel(report_data, report_type)
        
        return StreamingResponse(
            excel_file,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        logger.error(f"Ошибка экспорта отчета: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/dashboard-metrics")
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить метрики для дашборда"""
    try:
        reports_service = ReportsService(db)
        
        # Отчет за текущий месяц
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Отчет за прошлый месяц для сравнения
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        # Текущий месяц
        current_month_report = reports_service.get_financial_report(
            start_date=current_month_start,
            end_date=datetime.now()
        )
        
        # Прошлый месяц
        last_month_report = reports_service.get_financial_report(
            start_date=last_month_start,
            end_date=last_month_end
        )
        
        # Считаем изменения
        income_change = 0
        if last_month_report['summary']['total_income'] > 0:
            income_change = (
                (current_month_report['summary']['total_income'] - 
                 last_month_report['summary']['total_income']) / 
                last_month_report['summary']['total_income'] * 100
            )
        
        expense_change = 0
        if last_month_report['summary']['total_expense'] > 0:
            expense_change = (
                (current_month_report['summary']['total_expense'] - 
                 last_month_report['summary']['total_expense']) / 
                last_month_report['summary']['total_expense'] * 100
            )
        
        return {
            "success": True,
            "metrics": {
                "current_month": {
                    "income": current_month_report['summary']['total_income'],
                    "expense": current_month_report['summary']['total_expense'],
                    "profit": current_month_report['summary']['profit'],
                    "profit_margin": current_month_report['summary']['profit_margin']
                },
                "last_month": {
                    "income": last_month_report['summary']['total_income'],
                    "expense": last_month_report['summary']['total_expense'],
                    "profit": last_month_report['summary']['profit'],
                    "profit_margin": last_month_report['summary']['profit_margin']
                },
                "changes": {
                    "income_change": income_change,
                    "expense_change": expense_change,
                    "profit_change": (
                        current_month_report['summary']['profit'] - 
                        last_month_report['summary']['profit']
                    )
                },
                "forecast": current_month_report.get('forecast', {}),
                "top_projects": current_month_report.get('top_projects_by_income', [])[:5],
                "expense_categories": current_month_report.get('expense_categories', {})
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения метрик дашборда: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/quick-stats")
async def get_quick_stats(
    period: str = Query("month", description="Период: today, week, month, year"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить быструю статистику"""
    try:
        # Определяем период
        now = datetime.now()
        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = None
        
        reports_service = ReportsService(db)
        
        # Получаем отчеты
        projects_report = reports_service.get_projects_report(
            start_date=start_date,
            end_date=now
        )
        
        financial_report = reports_service.get_financial_report(
            start_date=start_date,
            end_date=now
        )
        
        return {
            "success": True,
            "period": period,
            "stats": {
                "projects": {
                    "total": projects_report['summary']['total_projects'],
                    "completed": len([
                        p for p in projects_report['projects'] 
                        if p['status'] == 'completed'
                    ]),
                    "in_progress": len([
                        p for p in projects_report['projects'] 
                        if p['status'] == 'in_progress'
                    ]),
                    "completion_rate": projects_report['summary']['completion_rate']
                },
                "financial": {
                    "income": financial_report['summary']['total_income'],
                    "expense": financial_report['summary']['total_expense'],
                    "profit": financial_report['summary']['profit'],
                    "transactions": financial_report['summary']['transactions_count']
                },
                "top_clients": projects_report.get('top_clients', [])[:3],
                "top_executors": projects_report.get('top_executors', [])[:3]
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения быстрой статистики: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/pnl-page", response_class=HTMLResponse)
async def pnl_page(
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """Страница отчета P&L"""
    from ..navigation import get_navigation_items
    
    user_role = current_user.get("role", "owner")
    
    # Проверяем доступ
    if user_role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра финансовых отчетов")
    
    navigation_items = get_navigation_items("/reports", user_role=user_role)
    
    return templates.TemplateResponse(
        "reports_pnl.html",
        {
            "request": request,
            "user": current_user,
            "username": current_user.get("username"),
            "password": current_user.get("password", ""),
            "user_role": user_role,
            "navigation_items": navigation_items
        }
    )


@router.get("/reports/pnl")
async def get_pnl_report(
    period: Optional[str] = Query("month", description="Период: month, quarter, year"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Получить отчет P&L (прибыли и убытки)"""
    try:
        # Проверяем доступ
        user_role = current_user.get("role", "executor")
        if user_role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        
        # Определяем период
        now = datetime.now()
        
        if start_date and end_date:
            # Произвольный период
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "quarter":
            current_quarter = (now.month - 1) // 3
            start = now.replace(month=current_quarter*3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == "year":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        
        reports_service = ReportsService(db)
        
        # Получаем финансовый отчет
        financial_report = reports_service.get_financial_report(
            start_date=start,
            end_date=end
        )
        
        # Получаем данные за предыдущий период для сравнения
        period_days = (end - start).days
        previous_start = start - timedelta(days=period_days)
        previous_end = start - timedelta(days=1)
        
        previous_report = reports_service.get_financial_report(
            start_date=previous_start,
            end_date=previous_end
        )
        
        # Подготавливаем данные для P&L
        revenue_by_category = []
        expenses_by_category = []
        
        # Группируем транзакции по категориям
        for category, transactions in financial_report.get('by_category', {}).items():
            total_amount = sum(t['amount'] for t in transactions)
            if transactions and transactions[0].get('type') == 'income':
                revenue_by_category.append({
                    'name': category,
                    'amount': total_amount
                })
            else:
                expenses_by_category.append({
                    'name': category,
                    'amount': total_amount
                })
        
        # Подготавливаем данные для графика динамики
        trend_data = {
            'labels': [],
            'revenue': [],
            'expenses': []
        }
        
        # Генерируем данные по дням/месяцам в зависимости от периода
        if period_days <= 31:  # По дням для месяца
            for i in range(period_days + 1):
                date = start + timedelta(days=i)
                trend_data['labels'].append(date.strftime('%d.%m'))
                # Здесь должна быть логика подсчета по дням
                trend_data['revenue'].append(0)
                trend_data['expenses'].append(0)
        else:  # По месяцам для квартала/года
            current = start
            while current <= end:
                trend_data['labels'].append(current.strftime('%b'))
                # Здесь должна быть логика подсчета по месяцам
                trend_data['revenue'].append(0)
                trend_data['expenses'].append(0)
                # Переход к следующему месяцу
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
        
        return {
            "success": True,
            "data": {
                "period": {
                    "start": start.isoformat(),
                    "end": end.isoformat()
                },
                "total_revenue": financial_report['summary']['total_income'],
                "total_expenses": financial_report['summary']['total_expense'],
                "net_profit": financial_report['summary']['profit'],
                "profit_margin": financial_report['summary']['profit_margin'],
                "revenue_by_category": revenue_by_category,
                "expenses_by_category": expenses_by_category,
                "trend_data": trend_data,
                "comparison": {
                    "previous_revenue": previous_report['summary']['total_income'],
                    "previous_expenses": previous_report['summary']['total_expense'],
                    "previous_profit": previous_report['summary']['profit']
                },
                "transactions_count": financial_report['summary']['transactions_count']
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения P&L отчета: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))