"""
Сервис для финансовых расчетов и отчетности
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from decimal import Decimal
import calendar

from ..database.models import Project, AdminUser
from ..database.crm_models import Client, Deal, DealStatus
from ..database.finance_models import (
    FinanceTransaction, FinanceCategory, Budget, 
    CashFlow, Invoice, PaymentSchedule
)
from ..config.logging import get_logger

logger = get_logger(__name__)


class FinanceService:
    """Сервис для работы с финансами"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # === Расчеты по проектам ===
    
    def calculate_project_profitability(self, project_id: int) -> Dict[str, Any]:
        """Рассчитать рентабельность проекта"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Доходы
        revenue = float(project.estimated_cost or 0)
        paid_by_client = float(project.client_paid_total or 0)
        
        # Расходы
        executor_cost = float(project.executor_cost or 0)
        paid_to_executor = float(project.executor_paid_total or 0)
        
        # Дополнительные расходы из транзакций
        additional_expenses = self.db.query(
            func.sum(FinanceTransaction.amount)
        ).filter(
            FinanceTransaction.project_id == project_id,
            FinanceTransaction.type == 'expense'
        ).scalar() or 0
        
        total_expenses = executor_cost + float(additional_expenses)
        
        # Маржа и рентабельность
        gross_margin = revenue - executor_cost
        net_margin = revenue - total_expenses
        
        profitability = 0
        if revenue > 0:
            profitability = (net_margin / revenue) * 100
        
        roi = 0  # Return on Investment
        if total_expenses > 0:
            roi = ((revenue - total_expenses) / total_expenses) * 100
        
        # Статус оплат
        client_payment_progress = 0
        if revenue > 0:
            client_payment_progress = (paid_by_client / revenue) * 100
        
        executor_payment_progress = 0
        if executor_cost > 0:
            executor_payment_progress = (paid_to_executor / executor_cost) * 100
        
        return {
            "project_id": project_id,
            "project_title": project.title,
            "revenue": revenue,
            "paid_by_client": paid_by_client,
            "client_debt": revenue - paid_by_client,
            "client_payment_progress": round(client_payment_progress, 1),
            "executor_cost": executor_cost,
            "paid_to_executor": paid_to_executor,
            "executor_debt": executor_cost - paid_to_executor,
            "executor_payment_progress": round(executor_payment_progress, 1),
            "additional_expenses": float(additional_expenses),
            "total_expenses": total_expenses,
            "gross_margin": gross_margin,
            "net_margin": net_margin,
            "profitability": round(profitability, 1),
            "roi": round(roi, 1),
            "status": project.status,
            "is_profitable": net_margin > 0
        }
    
    def calculate_deal_metrics(self, deal_id: int) -> Dict[str, Any]:
        """Рассчитать финансовые метрики сделки"""
        deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            return None
        
        amount = float(deal.amount or 0)
        cost = float(deal.cost or 0)
        discount = float(deal.discount or 0)
        paid = float(deal.paid_amount or 0)
        prepayment = float(deal.prepayment_amount or 0)
        
        # Расчет с учетом скидки
        final_amount = amount - discount
        margin = final_amount - cost
        margin_percent = 0
        if final_amount > 0:
            margin_percent = (margin / final_amount) * 100
        
        # Статус платежей
        payment_status = "pending"
        if paid >= final_amount:
            payment_status = "paid"
        elif paid >= prepayment:
            payment_status = "prepaid"
        
        payment_progress = 0
        if final_amount > 0:
            payment_progress = (paid / final_amount) * 100
        
        # Прогноз поступлений
        remaining = final_amount - paid
        days_since_start = 0
        if deal.start_date:
            days_since_start = (datetime.utcnow() - deal.start_date).days
        
        return {
            "deal_id": deal_id,
            "deal_title": deal.title,
            "amount": amount,
            "discount": discount,
            "final_amount": final_amount,
            "cost": cost,
            "margin": margin,
            "margin_percent": round(margin_percent, 1),
            "prepayment_amount": prepayment,
            "paid_amount": paid,
            "remaining_amount": remaining,
            "payment_status": payment_status,
            "payment_progress": round(payment_progress, 1),
            "days_since_start": days_since_start,
            "is_overdue": deal.end_date and datetime.utcnow() > deal.end_date and payment_status != "paid"
        }
    
    # === Бюджетирование ===
    
    def get_or_create_budget(self, year: int, month: int, category_id: int) -> Budget:
        """Получить или создать бюджет на месяц"""
        budget = self.db.query(Budget).filter(
            Budget.year == year,
            Budget.month == month,
            Budget.category_id == category_id
        ).first()
        
        if not budget:
            budget = Budget(
                year=year,
                month=month,
                category_id=category_id,
                planned_amount=0,
                actual_amount=0
            )
            self.db.add(budget)
            self.db.commit()
        
        return budget
    
    def update_budget_actual(self, year: int, month: int, category_id: int) -> None:
        """Обновить фактические расходы в бюджете"""
        budget = self.get_or_create_budget(year, month, category_id)
        
        # Считаем фактические транзакции
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
        
        actual = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.category_id == category_id,
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).scalar() or 0
        
        budget.actual_amount = float(actual)
        self.db.commit()
    
    def get_budget_analysis(self, year: int, month: int) -> Dict[str, Any]:
        """Анализ исполнения бюджета"""
        budgets = self.db.query(Budget).filter(
            Budget.year == year,
            Budget.month == month
        ).all()
        
        total_planned = sum(b.planned_amount for b in budgets)
        total_actual = sum(b.actual_amount for b in budgets)
        
        categories_analysis = []
        for budget in budgets:
            if budget.category:
                deviation = budget.actual_amount - budget.planned_amount
                deviation_percent = 0
                if budget.planned_amount > 0:
                    deviation_percent = (deviation / budget.planned_amount) * 100
                
                categories_analysis.append({
                    "category": budget.category.name,
                    "type": budget.category.type,
                    "planned": budget.planned_amount,
                    "actual": budget.actual_amount,
                    "deviation": deviation,
                    "deviation_percent": round(deviation_percent, 1),
                    "status": "over" if deviation > 0 else "under" if deviation < 0 else "on_track"
                })
        
        execution_rate = 0
        if total_planned > 0:
            execution_rate = (total_actual / total_planned) * 100
        
        return {
            "year": year,
            "month": month,
            "total_planned": total_planned,
            "total_actual": total_actual,
            "deviation": total_actual - total_planned,
            "execution_rate": round(execution_rate, 1),
            "categories": categories_analysis
        }
    
    # === Cash Flow ===
    
    def calculate_cash_flow(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Рассчитать денежный поток за период"""
        # Входящие платежи
        income = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'income',
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).scalar() or 0
        
        # Исходящие платежи
        expense = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'expense',
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).scalar() or 0
        
        # Чистый денежный поток
        net_cash_flow = float(income) - float(expense)
        
        # Детализация по категориям
        income_by_category = self.db.query(
            FinanceCategory.name,
            func.sum(FinanceTransaction.amount).label('total')
        ).join(
            FinanceTransaction, FinanceCategory.id == FinanceTransaction.category_id
        ).filter(
            FinanceTransaction.type == 'income',
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).group_by(FinanceCategory.name).all()
        
        expense_by_category = self.db.query(
            FinanceCategory.name,
            func.sum(FinanceTransaction.amount).label('total')
        ).join(
            FinanceTransaction, FinanceCategory.id == FinanceTransaction.category_id
        ).filter(
            FinanceTransaction.type == 'expense',
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).group_by(FinanceCategory.name).all()
        
        # Прогноз на основе средних значений
        days_in_period = (end_date - start_date).days + 1
        daily_income = float(income) / days_in_period if days_in_period > 0 else 0
        daily_expense = float(expense) / days_in_period if days_in_period > 0 else 0
        
        # Прогноз на следующий месяц
        forecast_income = daily_income * 30
        forecast_expense = daily_expense * 30
        forecast_net = forecast_income - forecast_expense
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days_in_period
            },
            "income": float(income),
            "expense": float(expense),
            "net_cash_flow": net_cash_flow,
            "income_by_category": [
                {"category": cat, "amount": float(amt)} 
                for cat, amt in income_by_category
            ],
            "expense_by_category": [
                {"category": cat, "amount": float(amt)} 
                for cat, amt in expense_by_category
            ],
            "daily_average": {
                "income": round(daily_income, 2),
                "expense": round(daily_expense, 2),
                "net": round(daily_income - daily_expense, 2)
            },
            "forecast_30_days": {
                "income": round(forecast_income, 2),
                "expense": round(forecast_expense, 2),
                "net": round(forecast_net, 2)
            }
        }
    
    def save_cash_flow_snapshot(self) -> CashFlow:
        """Сохранить снимок денежного потока"""
        today = date.today()
        
        # Проверяем, есть ли уже снимок за сегодня
        existing = self.db.query(CashFlow).filter(
            CashFlow.date == today
        ).first()
        
        if existing:
            return existing
        
        # Рассчитываем показатели
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        income = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'income',
            FinanceTransaction.date >= start_of_day,
            FinanceTransaction.date <= end_of_day
        ).scalar() or 0
        
        expense = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'expense',
            FinanceTransaction.date >= start_of_day,
            FinanceTransaction.date <= end_of_day
        ).scalar() or 0
        
        # Баланс на начало дня (берем вчерашний closing_balance)
        yesterday = today - timedelta(days=1)
        yesterday_snapshot = self.db.query(CashFlow).filter(
            CashFlow.date == yesterday
        ).first()
        
        opening_balance = yesterday_snapshot.closing_balance if yesterday_snapshot else 0
        closing_balance = opening_balance + float(income) - float(expense)
        
        # Сохраняем снимок
        snapshot = CashFlow(
            date=today,
            opening_balance=opening_balance,
            income=float(income),
            expense=float(expense),
            closing_balance=closing_balance
        )
        
        self.db.add(snapshot)
        self.db.commit()
        
        return snapshot
    
    # === Финансовые показатели ===
    
    def get_financial_kpis(self) -> Dict[str, Any]:
        """Получить ключевые финансовые показатели"""
        now = datetime.utcnow()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0)
        last_month_end = current_month_start - timedelta(seconds=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0)
        
        # Текущий месяц
        current_income = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'income',
            FinanceTransaction.date >= current_month_start
        ).scalar() or 0
        
        current_expense = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'expense',
            FinanceTransaction.date >= current_month_start
        ).scalar() or 0
        
        # Прошлый месяц
        last_income = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'income',
            FinanceTransaction.date >= last_month_start,
            FinanceTransaction.date <= last_month_end
        ).scalar() or 0
        
        last_expense = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'expense',
            FinanceTransaction.date >= last_month_start,
            FinanceTransaction.date <= last_month_end
        ).scalar() or 0
        
        # Рентабельность
        current_profit = float(current_income) - float(current_expense)
        last_profit = float(last_income) - float(last_expense)
        
        current_margin = 0
        if current_income > 0:
            current_margin = (current_profit / float(current_income)) * 100
        
        # Дебиторская задолженность
        receivables = self.db.query(func.sum(Project.estimated_cost - Project.client_paid_total)).filter(
            Project.status.in_(['in_progress', 'completed']),
            Project.client_paid_total < Project.estimated_cost
        ).scalar() or 0
        
        # Кредиторская задолженность
        payables = self.db.query(func.sum(Project.executor_cost - Project.executor_paid_total)).filter(
            Project.status.in_(['in_progress', 'completed']),
            Project.executor_paid_total < Project.executor_cost
        ).scalar() or 0
        
        # Средний чек
        avg_deal_amount = self.db.query(func.avg(Deal.amount)).filter(
            Deal.status == DealStatus.COMPLETED,
            Deal.closed_at >= last_month_start
        ).scalar() or 0
        
        # Конверсия сделок
        total_deals = self.db.query(func.count(Deal.id)).filter(
            Deal.created_at >= last_month_start
        ).scalar() or 0
        
        completed_deals = self.db.query(func.count(Deal.id)).filter(
            Deal.status == DealStatus.COMPLETED,
            Deal.closed_at >= last_month_start
        ).scalar() or 0
        
        conversion_rate = 0
        if total_deals > 0:
            conversion_rate = (completed_deals / total_deals) * 100
        
        # Рост доходов
        income_growth = 0
        if last_income > 0:
            income_growth = ((float(current_income) - float(last_income)) / float(last_income)) * 100
        
        return {
            "current_month": {
                "income": float(current_income),
                "expense": float(current_expense),
                "profit": current_profit,
                "margin": round(current_margin, 1)
            },
            "last_month": {
                "income": float(last_income),
                "expense": float(last_expense),
                "profit": last_profit
            },
            "growth": {
                "income": round(income_growth, 1),
                "profit": round(((current_profit - last_profit) / last_profit * 100) if last_profit != 0 else 0, 1)
            },
            "receivables": float(receivables),
            "payables": float(payables),
            "net_working_capital": float(receivables) - float(payables),
            "avg_deal_amount": float(avg_deal_amount),
            "deal_conversion_rate": round(conversion_rate, 1),
            "active_projects": self.db.query(func.count(Project.id)).filter(
                Project.status == 'in_progress'
            ).scalar(),
            "pending_payments": self.db.query(func.count(Deal.id)).filter(
                Deal.status.in_([DealStatus.PAYMENT, DealStatus.PREPAYMENT])
            ).scalar()
        }
    
    # === Отчеты ===
    
    def generate_pnl_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Генерация отчета о прибылях и убытках (P&L)"""
        # Доходы по категориям
        income_data = self.db.query(
            FinanceCategory.name,
            func.sum(FinanceTransaction.amount).label('amount')
        ).join(
            FinanceTransaction
        ).filter(
            FinanceTransaction.type == 'income',
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).group_by(FinanceCategory.name).all()
        
        # Расходы по категориям
        expense_data = self.db.query(
            FinanceCategory.name,
            func.sum(FinanceTransaction.amount).label('amount')
        ).join(
            FinanceTransaction
        ).filter(
            FinanceTransaction.type == 'expense',
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).group_by(FinanceCategory.name).all()
        
        total_income = sum(float(amt) for _, amt in income_data)
        total_expense = sum(float(amt) for _, amt in expense_data)
        
        # Валовая прибыль (доходы от проектов минус прямые расходы)
        project_income = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'income',
            FinanceTransaction.project_id.isnot(None),
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).scalar() or 0
        
        project_expense = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'expense',
            FinanceTransaction.project_id.isnot(None),
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).scalar() or 0
        
        gross_profit = float(project_income) - float(project_expense)
        gross_margin = 0
        if project_income > 0:
            gross_margin = (gross_profit / float(project_income)) * 100
        
        # Операционные расходы (не связанные с проектами)
        operating_expense = self.db.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.type == 'expense',
            FinanceTransaction.project_id.is_(None),
            FinanceTransaction.date >= start_date,
            FinanceTransaction.date <= end_date
        ).scalar() or 0
        
        # EBITDA (прибыль до налогов)
        ebitda = gross_profit - float(operating_expense)
        
        # Чистая прибыль
        net_profit = total_income - total_expense
        net_margin = 0
        if total_income > 0:
            net_margin = (net_profit / total_income) * 100
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "income": {
                "total": total_income,
                "by_category": [
                    {"category": cat, "amount": float(amt)}
                    for cat, amt in income_data
                ]
            },
            "expense": {
                "total": total_expense,
                "by_category": [
                    {"category": cat, "amount": float(amt)}
                    for cat, amt in expense_data
                ]
            },
            "gross_profit": gross_profit,
            "gross_margin": round(gross_margin, 1),
            "operating_expense": float(operating_expense),
            "ebitda": ebitda,
            "net_profit": net_profit,
            "net_margin": round(net_margin, 1)
        }
    
    def generate_balance_sheet(self, as_of_date: datetime = None) -> Dict[str, Any]:
        """Генерация баланса"""
        if not as_of_date:
            as_of_date = datetime.utcnow()
        
        # Активы
        # Дебиторская задолженность
        accounts_receivable = self.db.query(
            func.sum(Project.estimated_cost - Project.client_paid_total)
        ).filter(
            Project.status.in_(['in_progress', 'completed']),
            Project.client_paid_total < Project.estimated_cost,
            Project.created_at <= as_of_date
        ).scalar() or 0
        
        # Незавершенное производство (проекты в работе)
        work_in_progress = self.db.query(
            func.sum(Project.executor_paid_total)
        ).filter(
            Project.status == 'in_progress',
            Project.created_at <= as_of_date
        ).scalar() or 0
        
        # Денежные средства (последний известный баланс)
        cash_balance = self.db.query(CashFlow.closing_balance).filter(
            CashFlow.date <= as_of_date.date()
        ).order_by(CashFlow.date.desc()).first()
        
        cash = cash_balance[0] if cash_balance else 0
        
        total_assets = float(accounts_receivable) + float(work_in_progress) + float(cash)
        
        # Обязательства
        # Кредиторская задолженность
        accounts_payable = self.db.query(
            func.sum(Project.executor_cost - Project.executor_paid_total)
        ).filter(
            Project.status.in_(['in_progress', 'completed']),
            Project.executor_paid_total < Project.executor_cost,
            Project.created_at <= as_of_date
        ).scalar() or 0
        
        # Полученные авансы
        prepayments_received = self.db.query(
            func.sum(Deal.prepayment_amount)
        ).filter(
            Deal.status.in_([DealStatus.PREPAYMENT, DealStatus.IN_WORK]),
            Deal.created_at <= as_of_date
        ).scalar() or 0
        
        total_liabilities = float(accounts_payable) + float(prepayments_received)
        
        # Собственный капитал
        equity = total_assets - total_liabilities
        
        return {
            "as_of_date": as_of_date.isoformat(),
            "assets": {
                "current": {
                    "cash": float(cash),
                    "accounts_receivable": float(accounts_receivable),
                    "work_in_progress": float(work_in_progress),
                    "total": total_assets
                },
                "total": total_assets
            },
            "liabilities": {
                "current": {
                    "accounts_payable": float(accounts_payable),
                    "prepayments_received": float(prepayments_received),
                    "total": total_liabilities
                },
                "total": total_liabilities
            },
            "equity": {
                "retained_earnings": equity,
                "total": equity
            },
            "total_liabilities_and_equity": total_assets,
            "balance_check": abs(total_assets - (total_liabilities + equity)) < 0.01
        }
    
    # === Прогнозирование ===
    
    def forecast_revenue(self, months_ahead: int = 3) -> List[Dict[str, Any]]:
        """Прогноз доходов на несколько месяцев вперед"""
        forecasts = []
        now = datetime.utcnow()
        
        # Получаем исторические данные за последние 6 месяцев
        six_months_ago = now - timedelta(days=180)
        
        historical_data = self.db.query(
            extract('year', FinanceTransaction.date).label('year'),
            extract('month', FinanceTransaction.date).label('month'),
            func.sum(FinanceTransaction.amount).label('amount')
        ).filter(
            FinanceTransaction.type == 'income',
            FinanceTransaction.date >= six_months_ago
        ).group_by(
            extract('year', FinanceTransaction.date),
            extract('month', FinanceTransaction.date)
        ).all()
        
        # Считаем средний доход
        if historical_data:
            avg_monthly_income = sum(float(d.amount) for d in historical_data) / len(historical_data)
        else:
            avg_monthly_income = 0
        
        # Считаем тренд (простая линейная регрессия)
        if len(historical_data) >= 3:
            # Упрощенный расчет тренда
            first_half = historical_data[:len(historical_data)//2]
            second_half = historical_data[len(historical_data)//2:]
            
            avg_first = sum(float(d.amount) for d in first_half) / len(first_half) if first_half else 0
            avg_second = sum(float(d.amount) for d in second_half) / len(second_half) if second_half else 0
            
            monthly_growth = (avg_second - avg_first) / len(first_half) if first_half else 0
        else:
            monthly_growth = 0
        
        # Добавляем активные сделки в прогноз
        active_deals = self.db.query(Deal).filter(
            Deal.status.in_([
                DealStatus.CONTRACT_SIGNED,
                DealStatus.PREPAYMENT,
                DealStatus.IN_WORK,
                DealStatus.TESTING,
                DealStatus.ACCEPTANCE,
                DealStatus.PAYMENT
            ])
        ).all()
        
        for i in range(1, months_ahead + 1):
            forecast_date = now + timedelta(days=30 * i)
            month_name = calendar.month_name[forecast_date.month]
            
            # Базовый прогноз на основе истории и тренда
            base_forecast = avg_monthly_income + (monthly_growth * i)
            
            # Корректировка на основе активных сделок
            deals_revenue = 0
            for deal in active_deals:
                # Проверяем, попадает ли ожидаемая оплата в прогнозируемый месяц
                if deal.end_date and deal.end_date.month == forecast_date.month:
                    remaining = float(deal.amount or 0) - float(deal.paid_amount or 0)
                    deals_revenue += remaining * 0.7  # 70% вероятность оплаты
            
            optimistic = (base_forecast + deals_revenue) * 1.2
            pessimistic = base_forecast * 0.8
            realistic = base_forecast + (deals_revenue * 0.5)
            
            forecasts.append({
                "month": month_name,
                "year": forecast_date.year,
                "optimistic": round(optimistic, 2),
                "realistic": round(realistic, 2),
                "pessimistic": round(pessimistic, 2),
                "deals_in_pipeline": len([d for d in active_deals if d.end_date and d.end_date.month == forecast_date.month])
            })
        
        return forecasts