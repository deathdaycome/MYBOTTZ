"""
Сервис для генерации отчетов и аналитики
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract, case
from decimal import Decimal
import calendar
import json

from ..database.models import Project, AdminUser, ProjectFile, FinanceTransaction, FinanceCategory
from ..database.crm_models import Client, Lead, Deal, DealStatus, LeadStatus
from ..database.audit_models import AuditLog
from ..config.logging import get_logger

logger = get_logger(__name__)


class ReportsService:
    """Сервис для работы с отчетами и аналитикой"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # === Отчеты по продажам ===
    
    def get_sales_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Отчет по продажам за период"""
        
        # Статистика по лидам
        total_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.created_at >= start_date,
            Lead.created_at <= end_date
        ).scalar()
        
        converted_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.created_at >= start_date,
            Lead.created_at <= end_date,
            Lead.status == LeadStatus.WON
        ).scalar()
        
        lead_conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Статистика по сделкам
        total_deals = self.db.query(func.count(Deal.id)).filter(
            Deal.created_at >= start_date,
            Deal.created_at <= end_date
        ).scalar()
        
        completed_deals = self.db.query(func.count(Deal.id)).filter(
            Deal.created_at >= start_date,
            Deal.created_at <= end_date,
            Deal.status == DealStatus.COMPLETED
        ).scalar()
        
        deal_success_rate = (completed_deals / total_deals * 100) if total_deals > 0 else 0
        
        # Финансовые показатели
        total_revenue = self.db.query(func.sum(Deal.amount)).filter(
            Deal.created_at >= start_date,
            Deal.created_at <= end_date,
            Deal.status == DealStatus.COMPLETED
        ).scalar() or 0
        
        avg_deal_size = self.db.query(func.avg(Deal.amount)).filter(
            Deal.created_at >= start_date,
            Deal.created_at <= end_date,
            Deal.status == DealStatus.COMPLETED
        ).scalar() or 0
        
        # Продажи по менеджерам
        sales_by_manager = self.db.query(
            AdminUser.username,
            func.count(Deal.id).label('deals_count'),
            func.sum(Deal.amount).label('total_amount')
        ).join(
            Deal, Deal.responsible_manager_id == AdminUser.id
        ).filter(
            Deal.created_at >= start_date,
            Deal.created_at <= end_date,
            Deal.status == DealStatus.COMPLETED
        ).group_by(AdminUser.username).all()
        
        # Продажи по источникам
        sales_by_source = self.db.query(
            Lead.source,
            func.count(Deal.id).label('deals_count'),
            func.sum(Deal.amount).label('total_amount')
        ).join(
            Deal, Deal.lead_id == Lead.id
        ).filter(
            Deal.created_at >= start_date,
            Deal.created_at <= end_date,
            Deal.status == DealStatus.COMPLETED
        ).group_by(Lead.source).all()
        
        # Динамика по месяцам
        monthly_dynamics = self.db.query(
            extract('year', Deal.created_at).label('year'),
            extract('month', Deal.created_at).label('month'),
            func.count(Deal.id).label('deals_count'),
            func.sum(Deal.amount).label('total_amount')
        ).filter(
            Deal.created_at >= start_date,
            Deal.created_at <= end_date,
            Deal.status == DealStatus.COMPLETED
        ).group_by(
            extract('year', Deal.created_at),
            extract('month', Deal.created_at)
        ).order_by(
            extract('year', Deal.created_at),
            extract('month', Deal.created_at)
        ).all()
        
        # Средний цикл сделки
        avg_deal_cycle = self.db.query(
            func.avg(func.julianday(Deal.closed_at) - func.julianday(Deal.created_at))
        ).filter(
            Deal.created_at >= start_date,
            Deal.created_at <= end_date,
            Deal.status == DealStatus.COMPLETED,
            Deal.closed_at.isnot(None)
        ).scalar() or 0
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "leads": {
                "total": total_leads,
                "converted": converted_leads,
                "conversion_rate": round(lead_conversion_rate, 1)
            },
            "deals": {
                "total": total_deals,
                "completed": completed_deals,
                "success_rate": round(deal_success_rate, 1),
                "avg_cycle_days": round(avg_deal_cycle, 1)
            },
            "revenue": {
                "total": float(total_revenue),
                "avg_deal_size": float(avg_deal_size)
            },
            "by_manager": [
                {
                    "manager": row.username,
                    "deals_count": row.deals_count,
                    "total_amount": float(row.total_amount or 0)
                }
                for row in sales_by_manager
            ],
            "by_source": [
                {
                    "source": row.source or "Не указан",
                    "deals_count": row.deals_count,
                    "total_amount": float(row.total_amount or 0)
                }
                for row in sales_by_source
            ],
            "monthly_dynamics": [
                {
                    "year": int(row.year),
                    "month": int(row.month),
                    "month_name": calendar.month_name[int(row.month)],
                    "deals_count": row.deals_count,
                    "total_amount": float(row.total_amount or 0)
                }
                for row in monthly_dynamics
            ]
        }
    
    # === Отчеты по клиентам ===
    
    def get_clients_report(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Отчет по клиентам"""
        
        # Общая статистика
        total_clients = self.db.query(func.count(Client.id)).scalar()
        active_clients = self.db.query(func.count(Client.id)).filter(
            Client.status == 'active'
        ).scalar()
        
        # Новые клиенты за последний месяц
        last_month = datetime.utcnow() - timedelta(days=30)
        new_clients = self.db.query(func.count(Client.id)).filter(
            Client.created_at >= last_month
        ).scalar()
        
        # Сегментация клиентов
        segments = self.db.query(
            Client.segment,
            func.count(Client.id).label('count')
        ).group_by(Client.segment).all()
        
        # Топ клиентов по выручке
        top_clients = self.db.query(
            Client.name,
            Client.segment,
            func.sum(Deal.amount).label('total_revenue'),
            func.count(Deal.id).label('deals_count')
        ).join(
            Deal, Deal.client_id == Client.id
        ).filter(
            Deal.status == DealStatus.COMPLETED
        ).group_by(
            Client.id, Client.name, Client.segment
        ).order_by(
            func.sum(Deal.amount).desc()
        ).limit(10).all()
        
        # LTV (Lifetime Value) по сегментам
        ltv_by_segment = self.db.query(
            Client.segment,
            func.avg(
                self.db.query(func.sum(Deal.amount)).filter(
                    Deal.client_id == Client.id,
                    Deal.status == DealStatus.COMPLETED
                ).correlate(Client).as_scalar()
            ).label('avg_ltv')
        ).group_by(Client.segment).all()
        
        # Активность клиентов
        client_activity = self.db.query(
            case(
                (Client.last_contact_date >= datetime.utcnow() - timedelta(days=30), 'active'),
                (Client.last_contact_date >= datetime.utcnow() - timedelta(days=90), 'moderate'),
                else_='inactive'
            ).label('activity_level'),
            func.count(Client.id).label('count')
        ).group_by('activity_level').all()
        
        # География клиентов (если есть поле city/region)
        geography = self.db.query(
            Client.city,
            func.count(Client.id).label('count')
        ).filter(
            Client.city.isnot(None)
        ).group_by(Client.city).all()
        
        return {
            "summary": {
                "total": total_clients,
                "active": active_clients,
                "new_last_month": new_clients,
                "churn_rate": round(((total_clients - active_clients) / total_clients * 100) if total_clients > 0 else 0, 1)
            },
            "segments": [
                {
                    "segment": row.segment or "Не указан",
                    "count": row.count
                }
                for row in segments
            ],
            "top_clients": [
                {
                    "name": row.name,
                    "segment": row.segment,
                    "total_revenue": float(row.total_revenue or 0),
                    "deals_count": row.deals_count
                }
                for row in top_clients
            ],
            "ltv_by_segment": [
                {
                    "segment": row.segment or "Не указан",
                    "avg_ltv": float(row.avg_ltv or 0)
                }
                for row in ltv_by_segment
            ],
            "activity": [
                {
                    "level": row.activity_level,
                    "count": row.count
                }
                for row in client_activity
            ],
            "geography": [
                {
                    "city": row.city,
                    "count": row.count
                }
                for row in geography[:10]  # Топ-10 городов
            ]
        }
    
    # === Отчеты по проектам ===
    
    def get_projects_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Отчет по проектам"""
        
        query = self.db.query(Project)
        if start_date:
            query = query.filter(Project.created_at >= start_date)
        if end_date:
            query = query.filter(Project.created_at <= end_date)
        
        # Статистика по статусам
        status_stats = self.db.query(
            Project.status,
            func.count(Project.id).label('count'),
            func.sum(Project.estimated_cost).label('total_cost')
        ).group_by(Project.status).all()
        
        # Статистика по исполнителям
        executor_stats = self.db.query(
            AdminUser.username,
            func.count(Project.id).label('projects_count'),
            func.sum(Project.estimated_cost).label('total_cost'),
            func.avg(
                case(
                    (Project.status == 'completed', 100),
                    (Project.status == 'in_progress', 50),
                    else_=0
                )
            ).label('avg_completion')
        ).join(
            Project, Project.assigned_executor_id == AdminUser.id
        ).group_by(AdminUser.username).all()
        
        # Просроченные проекты
        overdue_projects = self.db.query(Project).filter(
            Project.planned_end_date < datetime.utcnow(),
            Project.status.notin_(['completed', 'cancelled'])
        ).all()
        
        # Средняя длительность проектов
        avg_duration = self.db.query(
            func.avg(
                func.julianday(Project.actual_end_date) - func.julianday(Project.start_date)
            )
        ).filter(
            Project.status == 'completed',
            Project.actual_end_date.isnot(None),
            Project.start_date.isnot(None)
        ).scalar() or 0
        
        # Рентабельность проектов
        profitability_data = self.db.query(
            func.sum(Project.estimated_cost).label('revenue'),
            func.sum(Project.executor_cost).label('costs')
        ).filter(
            Project.status == 'completed'
        ).first()
        
        profit_margin = 0
        if profitability_data and profitability_data.revenue:
            profit = (profitability_data.revenue or 0) - (profitability_data.costs or 0)
            profit_margin = (profit / profitability_data.revenue) * 100
        
        # Проекты по типам
        project_types = self.db.query(
            Project.type,
            func.count(Project.id).label('count'),
            func.avg(Project.estimated_cost).label('avg_cost')
        ).group_by(Project.type).all()
        
        return {
            "summary": {
                "total": sum(row.count for row in status_stats),
                "in_progress": next((row.count for row in status_stats if row.status == 'in_progress'), 0),
                "completed": next((row.count for row in status_stats if row.status == 'completed'), 0),
                "overdue": len(overdue_projects),
                "avg_duration_days": round(avg_duration, 1),
                "profit_margin": round(profit_margin, 1)
            },
            "by_status": [
                {
                    "status": row.status,
                    "count": row.count,
                    "total_cost": float(row.total_cost or 0)
                }
                for row in status_stats
            ],
            "by_executor": [
                {
                    "executor": row.username,
                    "projects_count": row.projects_count,
                    "total_cost": float(row.total_cost or 0),
                    "avg_completion": round(row.avg_completion or 0, 1)
                }
                for row in executor_stats
            ],
            "by_type": [
                {
                    "type": row.type or "Не указан",
                    "count": row.count,
                    "avg_cost": float(row.avg_cost or 0)
                }
                for row in project_types
            ],
            "overdue_projects": [
                {
                    "id": p.id,
                    "title": p.title,
                    "status": p.status,
                    "planned_end_date": p.planned_end_date.isoformat() if p.planned_end_date else None,
                    "days_overdue": (datetime.utcnow() - p.planned_end_date).days if p.planned_end_date else 0
                }
                for p in overdue_projects[:10]  # Топ-10 просроченных
            ]
        }
    
    # === Сводный дашборд ===
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Данные для главного дашборда"""
        
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0)
        
        # Ключевые метрики
        total_clients = self.db.query(func.count(Client.id)).scalar()
        active_deals = self.db.query(func.count(Deal.id)).filter(
            Deal.status.notin_([DealStatus.COMPLETED, DealStatus.CANCELLED])
        ).scalar()
        
        month_revenue = self.db.query(func.sum(Deal.amount)).filter(
            Deal.status == DealStatus.COMPLETED,
            Deal.closed_at >= month_start
        ).scalar() or 0
        
        active_projects = self.db.query(func.count(Project.id)).filter(
            Project.status == 'in_progress'
        ).scalar()
        
        # Последние активности
        recent_activities = []
        
        # Последние сделки
        recent_deals = self.db.query(Deal).order_by(Deal.created_at.desc()).limit(5).all()
        for deal in recent_deals:
            recent_activities.append({
                "type": "deal",
                "title": f"Новая сделка: {deal.title}",
                "amount": float(deal.amount or 0),
                "date": deal.created_at.isoformat()
            })
        
        # Последние проекты
        recent_projects = self.db.query(Project).order_by(Project.created_at.desc()).limit(5).all()
        for project in recent_projects:
            recent_activities.append({
                "type": "project",
                "title": f"Новый проект: {project.title}",
                "status": project.status,
                "date": project.created_at.isoformat()
            })
        
        # Сортируем активности по дате
        recent_activities.sort(key=lambda x: x['date'], reverse=True)
        
        # График доходов за последние 6 месяцев
        revenue_chart = []
        for i in range(5, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            month_revenue = self.db.query(func.sum(Deal.amount)).filter(
                Deal.status == DealStatus.COMPLETED,
                Deal.closed_at >= month_start,
                Deal.closed_at < month_end
            ).scalar() or 0
            
            revenue_chart.append({
                "month": calendar.month_name[month_start.month][:3],
                "revenue": float(month_revenue)
            })
        
        return {
            "metrics": {
                "total_clients": total_clients,
                "active_deals": active_deals,
                "month_revenue": float(month_revenue),
                "active_projects": active_projects
            },
            "recent_activities": recent_activities[:10],
            "revenue_chart": revenue_chart
        }