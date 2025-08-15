# app/services/reports_service.py
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
import pandas as pd
from io import BytesIO
import xlsxwriter

from ..database.models import Project, User, Transaction, AdminUser, Task
from ..config.logging import get_logger

logger = get_logger(__name__)


class ReportsService:
    """Сервис для генерации отчетов и аналитики"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_projects_report(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        executor_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Получить отчет по проектам"""
        try:
            query = self.db.query(Project)
            
            # Фильтры
            if start_date:
                query = query.filter(Project.created_at >= start_date)
            if end_date:
                query = query.filter(Project.created_at <= end_date)
            if status:
                query = query.filter(Project.status == status)
            if executor_id:
                query = query.filter(Project.assigned_executor_id == executor_id)
            
            projects = query.all()
            
            # Считаем статистику
            total_projects = len(projects)
            total_revenue = sum(p.estimated_cost or 0 for p in projects)
            
            # Получаем доходы по проектам
            project_ids = [p.id for p in projects]
            total_received = self.db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.project_id.in_(project_ids),
                    Transaction.transaction_type == 'income',
                    Transaction.status == 'completed'
                )
            ).scalar() or 0
            
            # Получаем расходы по проектам
            total_expenses = self.db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.project_id.in_(project_ids),
                    Transaction.transaction_type == 'expense',
                    Transaction.status == 'completed'
                )
            ).scalar() or 0
            
            # Статистика по статусам
            status_distribution = {}
            for project in projects:
                status_distribution[project.status] = status_distribution.get(project.status, 0) + 1
            
            # Средние показатели
            avg_project_cost = total_revenue / total_projects if total_projects > 0 else 0
            avg_completion_time = self._calculate_avg_completion_time(projects)
            
            # Топ клиентов
            top_clients = self._get_top_clients(projects)
            
            # Топ исполнителей
            top_executors = self._get_top_executors(projects)
            
            return {
                'period': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                },
                'summary': {
                    'total_projects': total_projects,
                    'total_revenue': total_revenue,
                    'total_received': total_received,
                    'total_expenses': total_expenses,
                    'profit': total_received - total_expenses,
                    'profitability': ((total_received - total_expenses) / total_received * 100) if total_received > 0 else 0,
                    'avg_project_cost': avg_project_cost,
                    'avg_completion_time': avg_completion_time,
                    'completion_rate': self._calculate_completion_rate(projects)
                },
                'status_distribution': status_distribution,
                'top_clients': top_clients,
                'top_executors': top_executors,
                'projects': [self._project_to_dict(p) for p in projects]
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчета по проектам: {str(e)}")
            raise
    
    def get_financial_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Получить финансовый отчет"""
        try:
            # Базовые запросы
            income_query = self.db.query(Transaction).filter(
                Transaction.transaction_type == 'income',
                Transaction.status == 'completed'
            )
            expense_query = self.db.query(Transaction).filter(
                Transaction.transaction_type == 'expense',
                Transaction.status == 'completed'
            )
            
            # Применяем фильтры дат
            if start_date:
                income_query = income_query.filter(Transaction.transaction_date >= start_date)
                expense_query = expense_query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                income_query = income_query.filter(Transaction.transaction_date <= end_date)
                expense_query = expense_query.filter(Transaction.transaction_date <= end_date)
            
            incomes = income_query.all()
            expenses = expense_query.all()
            
            # Считаем суммы
            total_income = sum(t.amount for t in incomes)
            total_expense = sum(t.amount for t in expenses)
            profit = total_income - total_expense
            
            # Группировка по месяцам
            monthly_data = self._group_transactions_by_month(incomes, expenses)
            
            # Топ категорий расходов
            expense_categories = {}
            for expense in expenses:
                category = expense.category or 'Другое'
                expense_categories[category] = expense_categories.get(category, 0) + expense.amount
            
            # Топ проектов по доходам
            project_income = {}
            for income in incomes:
                if income.project_id:
                    project = self.db.query(Project).filter(Project.id == income.project_id).first()
                    if project:
                        project_income[project.title] = project_income.get(project.title, 0) + income.amount
            
            top_projects = sorted(project_income.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Прогноз на следующий месяц
            forecast = self._calculate_forecast(monthly_data)
            
            return {
                'period': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                },
                'summary': {
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'profit': profit,
                    'profit_margin': (profit / total_income * 100) if total_income > 0 else 0,
                    'transactions_count': len(incomes) + len(expenses)
                },
                'monthly_data': monthly_data,
                'expense_categories': expense_categories,
                'top_projects_by_income': top_projects,
                'forecast': forecast,
                'cash_flow': self._calculate_cash_flow(incomes, expenses)
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации финансового отчета: {str(e)}")
            raise
    
    def get_executor_report(self, executor_id: int) -> Dict[str, Any]:
        """Получить отчет по исполнителю"""
        try:
            executor = self.db.query(AdminUser).filter(AdminUser.id == executor_id).first()
            if not executor:
                raise ValueError(f"Исполнитель с ID {executor_id} не найден")
            
            # Проекты исполнителя
            projects = self.db.query(Project).filter(
                Project.assigned_executor_id == executor_id
            ).all()
            
            # Задачи исполнителя
            tasks = self.db.query(Task).filter(
                Task.assigned_to_id == executor_id
            ).all() if Task else []
            
            # Финансовые показатели
            total_earned = sum(p.executor_cost or 0 for p in projects if p.status == 'completed')
            total_paid = self.db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.contractor_id == executor_id,
                    Transaction.transaction_type == 'expense',
                    Transaction.status == 'completed'
                )
            ).scalar() or 0
            
            # Статистика по проектам
            project_stats = {
                'total': len(projects),
                'completed': len([p for p in projects if p.status == 'completed']),
                'in_progress': len([p for p in projects if p.status == 'in_progress']),
                'overdue': len([p for p in projects if p.status == 'overdue'])
            }
            
            # Эффективность
            completion_rate = (project_stats['completed'] / project_stats['total'] * 100) if project_stats['total'] > 0 else 0
            
            # Средние показатели
            avg_project_time = self._calculate_avg_completion_time(
                [p for p in projects if p.status == 'completed']
            )
            
            return {
                'executor': {
                    'id': executor.id,
                    'username': executor.username,
                    'full_name': f"{executor.first_name or ''} {executor.last_name or ''}".strip(),
                    'email': executor.email,
                    'role': executor.role
                },
                'financial': {
                    'total_earned': total_earned,
                    'total_paid': total_paid,
                    'balance': total_earned - total_paid
                },
                'projects': project_stats,
                'tasks': {
                    'total': len(tasks),
                    'completed': len([t for t in tasks if t.status == 'completed']),
                    'in_progress': len([t for t in tasks if t.status == 'in_progress'])
                },
                'performance': {
                    'completion_rate': completion_rate,
                    'avg_project_time': avg_project_time,
                    'projects_this_month': len([
                        p for p in projects 
                        if p.created_at >= datetime.now() - timedelta(days=30)
                    ])
                },
                'recent_projects': [
                    self._project_to_dict(p) for p in 
                    sorted(projects, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
                ]
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчета по исполнителю: {str(e)}")
            raise
    
    def export_to_excel(self, report_data: Dict[str, Any], report_type: str) -> BytesIO:
        """Экспорт отчета в Excel"""
        try:
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Форматы
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4472C4',
                    'font_color': 'white',
                    'align': 'center',
                    'valign': 'vcenter'
                })
                
                money_format = workbook.add_format({'num_format': '#,##0 ₽'})
                percent_format = workbook.add_format({'num_format': '0.00%'})
                
                if report_type == 'projects':
                    # Сводка
                    summary_df = pd.DataFrame([report_data['summary']])
                    summary_df.to_excel(writer, sheet_name='Сводка', index=False)
                    
                    # Проекты
                    if report_data.get('projects'):
                        projects_df = pd.DataFrame(report_data['projects'])
                        projects_df.to_excel(writer, sheet_name='Проекты', index=False)
                    
                    # Распределение по статусам
                    if report_data.get('status_distribution'):
                        status_df = pd.DataFrame(
                            list(report_data['status_distribution'].items()),
                            columns=['Статус', 'Количество']
                        )
                        status_df.to_excel(writer, sheet_name='Статусы', index=False)
                
                elif report_type == 'financial':
                    # Финансовая сводка
                    summary_df = pd.DataFrame([report_data['summary']])
                    summary_df.to_excel(writer, sheet_name='Сводка', index=False)
                    
                    # Месячные данные
                    if report_data.get('monthly_data'):
                        monthly_df = pd.DataFrame(report_data['monthly_data'])
                        monthly_df.to_excel(writer, sheet_name='По месяцам', index=False)
                    
                    # Категории расходов
                    if report_data.get('expense_categories'):
                        categories_df = pd.DataFrame(
                            list(report_data['expense_categories'].items()),
                            columns=['Категория', 'Сумма']
                        )
                        categories_df.to_excel(writer, sheet_name='Категории расходов', index=False)
                
                elif report_type == 'executor':
                    # Информация об исполнителе
                    executor_df = pd.DataFrame([report_data['executor']])
                    executor_df.to_excel(writer, sheet_name='Исполнитель', index=False)
                    
                    # Финансы
                    financial_df = pd.DataFrame([report_data['financial']])
                    financial_df.to_excel(writer, sheet_name='Финансы', index=False)
                    
                    # Показатели
                    performance_df = pd.DataFrame([report_data['performance']])
                    performance_df.to_excel(writer, sheet_name='Показатели', index=False)
            
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Ошибка экспорта в Excel: {str(e)}")
            raise
    
    def _calculate_avg_completion_time(self, projects: List[Project]) -> float:
        """Рассчитать среднее время выполнения проектов"""
        completion_times = []
        for project in projects:
            if project.status == 'completed' and project.created_at:
                end_date = project.actual_end_date or project.updated_at
                if end_date:
                    days = (end_date - project.created_at).days
                    completion_times.append(days)
        
        return sum(completion_times) / len(completion_times) if completion_times else 0
    
    def _calculate_completion_rate(self, projects: List[Project]) -> float:
        """Рассчитать процент завершенных проектов"""
        if not projects:
            return 0
        completed = len([p for p in projects if p.status == 'completed'])
        return (completed / len(projects)) * 100
    
    def _get_top_clients(self, projects: List[Project], limit: int = 5) -> List[Dict[str, Any]]:
        """Получить топ клиентов по проектам"""
        client_stats = {}
        
        for project in projects:
            if project.user_id:
                user = self.db.query(User).filter(User.id == project.user_id).first()
                if user:
                    key = user.id
                    if key not in client_stats:
                        client_stats[key] = {
                            'id': user.id,
                            'name': user.first_name or user.username or 'Неизвестный',
                            'projects_count': 0,
                            'total_revenue': 0
                        }
                    client_stats[key]['projects_count'] += 1
                    client_stats[key]['total_revenue'] += project.estimated_cost or 0
        
        # Сортируем по выручке
        sorted_clients = sorted(
            client_stats.values(), 
            key=lambda x: x['total_revenue'], 
            reverse=True
        )
        
        return sorted_clients[:limit]
    
    def _get_top_executors(self, projects: List[Project], limit: int = 5) -> List[Dict[str, Any]]:
        """Получить топ исполнителей по проектам"""
        executor_stats = {}
        
        for project in projects:
            if project.assigned_executor_id:
                executor = self.db.query(AdminUser).filter(
                    AdminUser.id == project.assigned_executor_id
                ).first()
                if executor:
                    key = executor.id
                    if key not in executor_stats:
                        executor_stats[key] = {
                            'id': executor.id,
                            'name': executor.username,
                            'projects_count': 0,
                            'completed_count': 0,
                            'total_earned': 0
                        }
                    executor_stats[key]['projects_count'] += 1
                    if project.status == 'completed':
                        executor_stats[key]['completed_count'] += 1
                        executor_stats[key]['total_earned'] += project.executor_cost or 0
        
        # Сортируем по количеству завершенных проектов
        sorted_executors = sorted(
            executor_stats.values(),
            key=lambda x: x['completed_count'],
            reverse=True
        )
        
        return sorted_executors[:limit]
    
    def _group_transactions_by_month(
        self, 
        incomes: List[Transaction], 
        expenses: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Группировать транзакции по месяцам"""
        monthly_data = {}
        
        # Обрабатываем доходы
        for income in incomes:
            if income.transaction_date:
                month_key = income.transaction_date.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': month_key,
                        'income': 0,
                        'expense': 0,
                        'profit': 0
                    }
                monthly_data[month_key]['income'] += income.amount
        
        # Обрабатываем расходы
        for expense in expenses:
            if expense.transaction_date:
                month_key = expense.transaction_date.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': month_key,
                        'income': 0,
                        'expense': 0,
                        'profit': 0
                    }
                monthly_data[month_key]['expense'] += expense.amount
        
        # Рассчитываем прибыль
        for month_data in monthly_data.values():
            month_data['profit'] = month_data['income'] - month_data['expense']
        
        # Сортируем по месяцам
        return sorted(monthly_data.values(), key=lambda x: x['month'])
    
    def _calculate_forecast(self, monthly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Рассчитать прогноз на следующий месяц"""
        if len(monthly_data) < 3:
            return {
                'income': 0,
                'expense': 0,
                'profit': 0,
                'confidence': 'low'
            }
        
        # Простое скользящее среднее за последние 3 месяца
        recent_months = monthly_data[-3:]
        avg_income = sum(m['income'] for m in recent_months) / 3
        avg_expense = sum(m['expense'] for m in recent_months) / 3
        
        return {
            'income': avg_income,
            'expense': avg_expense,
            'profit': avg_income - avg_expense,
            'confidence': 'medium' if len(monthly_data) >= 6 else 'low'
        }
    
    def _calculate_cash_flow(
        self, 
        incomes: List[Transaction], 
        expenses: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """Рассчитать денежный поток"""
        all_transactions = sorted(
            incomes + expenses,
            key=lambda x: x.transaction_date or datetime.min
        )
        
        cash_flow = []
        balance = 0
        
        for transaction in all_transactions:
            if transaction.transaction_type == 'income':
                balance += transaction.amount
                flow_type = 'in'
            else:
                balance -= transaction.amount
                flow_type = 'out'
            
            cash_flow.append({
                'date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                'type': flow_type,
                'amount': transaction.amount,
                'balance': balance,
                'description': transaction.description
            })
        
        return cash_flow[-50:]  # Последние 50 транзакций
    
    def _project_to_dict(self, project: Project) -> Dict[str, Any]:
        """Преобразовать проект в словарь для отчета"""
        return {
            'id': project.id,
            'title': project.title,
            'status': project.status,
            'priority': project.priority,
            'estimated_cost': project.estimated_cost,
            'client': project.user.first_name if project.user else 'Неизвестный',
            'executor': project.assigned_executor.username if project.assigned_executor else None,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'deadline': project.planned_end_date.isoformat() if project.planned_end_date else None,
            'completion_percentage': project.completion_percentage or 0
        }