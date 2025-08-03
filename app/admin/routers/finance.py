# app/admin/routers/finance.py
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, extract
from pydantic import BaseModel
from decimal import Decimal

from ...database.database import get_db
from ...database.models import (
    FinanceCategory, FinanceTransaction, FinanceBudget, 
    AdminUser, Project
)
from ...config.logging import get_logger
from ..middleware.auth import get_current_admin_user

logger = get_logger(__name__)

router = APIRouter(tags=["finance"])

# Модели для API
class FinanceCategoryCreateModel(BaseModel):
    name: str
    type: str  # income или expense
    description: Optional[str] = None
    color: str = "#6c757d"
    icon: str = "fas fa-circle"

class FinanceTransactionCreateModel(BaseModel):
    amount: float
    type: str  # income или expense
    description: str
    date: datetime
    category_id: int
    project_id: Optional[int] = None
    contractor_name: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: bool = False
    recurring_period: Optional[str] = None

class FinanceBudgetCreateModel(BaseModel):
    name: str
    category_id: int
    planned_amount: float
    period_start: datetime
    period_end: datetime

# Категории финансов
@router.get("/categories")
async def get_finance_categories(
    type: Optional[str] = Query(None, description="Тип категории: income или expense"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить все категории финансов"""
    try:
        query = db.query(FinanceCategory).filter(FinanceCategory.is_active == True)
        
        if type:
            query = query.filter(FinanceCategory.type == type)
        
        categories = query.order_by(FinanceCategory.name).all()
        
        return {
            "success": True,
            "data": [category.to_dict() for category in categories]
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения категорий финансов: {e}")
        return {"success": False, "error": str(e)}

@router.post("/categories")
async def create_finance_category(
    category_data: FinanceCategoryCreateModel,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Создать новую категорию финансов"""
    try:
        # Проверяем, что тип корректный
        if category_data.type not in ["income", "expense"]:
            raise HTTPException(status_code=400, detail="Тип должен быть 'income' или 'expense'")
        
        new_category = FinanceCategory(
            name=category_data.name,
            type=category_data.type,
            description=category_data.description,
            color=category_data.color,
            icon=category_data.icon,
            created_by_id=current_user["id"],
            created_at=datetime.utcnow()
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        logger.info(f"Создана новая категория финансов: {new_category.name}")
        
        return {
            "success": True,
            "data": new_category.to_dict(),
            "message": "Категория успешно создана"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка создания категории финансов: {e}")
        return {"success": False, "error": str(e)}

# Транзакции
@router.get("/transactions")
async def get_finance_transactions(
    type: Optional[str] = Query(None, description="Тип транзакции: income или expense"),
    category_id: Optional[int] = Query(None, description="ID категории"),
    project_id: Optional[int] = Query(None, description="ID проекта"),
    date_from: Optional[datetime] = Query(None, description="Дата от"),
    date_to: Optional[datetime] = Query(None, description="Дата до"),
    limit: int = Query(50, description="Количество записей"),
    offset: int = Query(0, description="Смещение"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить финансовые транзакции с фильтрами"""
    try:
        query = db.query(FinanceTransaction)
        
        # Фильтрация по пользователю: исполнители видят только свои транзакции
        if current_user["role"] == "executor":
            query = query.filter(FinanceTransaction.created_by_id == current_user["id"])
            print(f"[DEBUG FINANCE] Executor {current_user['username']} (ID: {current_user['id']}) requesting transactions")
        else:
            print(f"[DEBUG FINANCE] Owner {current_user['username']} requesting ALL transactions")
        # Владелец видит все транзакции (без дополнительного фильтра)
        
        if type:
            query = query.filter(FinanceTransaction.type == type)
        
        if category_id:
            query = query.filter(FinanceTransaction.category_id == category_id)
        
        if project_id:
            query = query.filter(FinanceTransaction.project_id == project_id)
        
        if date_from:
            query = query.filter(FinanceTransaction.date >= date_from)
        
        if date_to:
            query = query.filter(FinanceTransaction.date <= date_to)
        
        total = query.count()
        transactions = query.order_by(desc(FinanceTransaction.date)).offset(offset).limit(limit).all()
        
        print(f"[DEBUG FINANCE] Returning {len(transactions)} transactions (total: {total}) for user {current_user['username']} (role: {current_user['role']})")
        
        return {
            "success": True,
            "data": [transaction.to_dict() for transaction in transactions],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения транзакций: {e}")
        return {"success": False, "error": str(e)}

@router.post("/transactions")
async def create_finance_transaction(
    transaction_data: FinanceTransactionCreateModel,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Создать новую финансовую транзакцию"""
    try:
        # Проверяем, что тип корректный
        if transaction_data.type not in ["income", "expense"]:
            raise HTTPException(status_code=400, detail="Тип должен быть 'income' или 'expense'")
        
        # Проверяем существование категории
        category = db.query(FinanceCategory).filter(FinanceCategory.id == transaction_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        
        # Проверяем существование проекта (если указан)
        if transaction_data.project_id:
            project = db.query(Project).filter(Project.id == transaction_data.project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Проект не найден")
        
        new_transaction = FinanceTransaction(
            amount=transaction_data.amount,
            type=transaction_data.type,
            description=transaction_data.description,
            date=transaction_data.date,
            category_id=transaction_data.category_id,
            project_id=transaction_data.project_id,
            contractor_name=transaction_data.contractor_name,
            receipt_url=transaction_data.receipt_url,
            notes=transaction_data.notes,
            is_recurring=transaction_data.is_recurring,
            recurring_period=transaction_data.recurring_period,
            created_by_id=current_user["id"],
            created_at=datetime.utcnow()
        )
        
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        logger.info(f"Создана новая транзакция: {new_transaction.description} - {new_transaction.amount}₽")
        
        return {
            "success": True,
            "data": new_transaction.to_dict(),
            "message": "Транзакция успешно создана"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка создания транзакции: {e}")
        return {"success": False, "error": str(e)}

# Аналитика
@router.get("/analytics/summary")
async def get_finance_summary(
    date_from: Optional[datetime] = Query(None, description="Дата от"),
    date_to: Optional[datetime] = Query(None, description="Дата до"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить сводку по финансам"""
    try:
        # Если даты не указаны, берем текущий месяц
        if not date_from:
            date_from = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not date_to:
            date_to = datetime.now()
        
        query = db.query(FinanceTransaction).filter(
            FinanceTransaction.date >= date_from,
            FinanceTransaction.date <= date_to
        )
        
        # Фильтрация по пользователю: исполнители видят только свои транзакции
        if current_user["role"] == "executor":
            query = query.filter(FinanceTransaction.created_by_id == current_user["id"])
            print(f"[DEBUG FINANCE SUMMARY] Executor {current_user['username']} (ID: {current_user['id']}) requesting summary")
        else:
            print(f"[DEBUG FINANCE SUMMARY] Owner {current_user['username']} requesting summary")
        
        # Доходы
        income_query = query.filter(FinanceTransaction.type == "income")
        total_income = income_query.with_entities(func.sum(FinanceTransaction.amount)).scalar() or 0
        income_count = income_query.count()
        
        # Расходы
        expense_query = query.filter(FinanceTransaction.type == "expense")
        total_expenses = expense_query.with_entities(func.sum(FinanceTransaction.amount)).scalar() or 0
        expense_count = expense_query.count()
        
        # Прибыль
        profit = total_income - total_expenses
        
        # Топ категории доходов
        top_income_query = db.query(
            FinanceCategory.name,
            func.sum(FinanceTransaction.amount).label('total')
        ).join(FinanceTransaction).filter(
            FinanceTransaction.type == "income",
            FinanceTransaction.date >= date_from,
            FinanceTransaction.date <= date_to
        )
        if current_user["role"] == "executor":
            top_income_query = top_income_query.filter(FinanceTransaction.created_by_id == current_user["id"])
        top_income_categories = top_income_query.group_by(FinanceCategory.id).order_by(desc('total')).limit(5).all()
        
        # Топ категории расходов
        top_expense_query = db.query(
            FinanceCategory.name,
            func.sum(FinanceTransaction.amount).label('total')
        ).join(FinanceTransaction).filter(
            FinanceTransaction.type == "expense",
            FinanceTransaction.date >= date_from,
            FinanceTransaction.date <= date_to
        )
        if current_user["role"] == "executor":
            top_expense_query = top_expense_query.filter(FinanceTransaction.created_by_id == current_user["id"])
        top_expense_categories = top_expense_query.group_by(FinanceCategory.id).order_by(desc('total')).limit(5).all()
        
        return {
            "success": True,
            "data": {
                "period": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                },
                "income": {
                    "total": float(total_income),
                    "count": income_count
                },
                "expenses": {
                    "total": float(total_expenses),
                    "count": expense_count
                },
                "profit": float(profit),
                "top_income_categories": [
                    {"name": name, "total": float(total)} 
                    for name, total in top_income_categories
                ],
                "top_expense_categories": [
                    {"name": name, "total": float(total)} 
                    for name, total in top_expense_categories
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения аналитики финансов: {e}")
        return {"success": False, "error": str(e)}

@router.get("/analytics/monthly")
async def get_monthly_analytics(
    year: int = Query(datetime.now().year, description="Год"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Получить месячную аналитику по финансам"""
    try:
        monthly_data = []
        
        for month in range(1, 13):
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(year, month + 1, 1) - timedelta(days=1)
            
            query = db.query(FinanceTransaction).filter(
                FinanceTransaction.date >= month_start,
                FinanceTransaction.date <= month_end
            )
            
            # Фильтрация по пользователю: исполнители видят только свои транзакции
            if current_user["role"] == "executor":
                query = query.filter(FinanceTransaction.created_by_id == current_user["id"])
            
            income = query.filter(FinanceTransaction.type == "income").with_entities(
                func.sum(FinanceTransaction.amount)
            ).scalar() or 0
            
            expenses = query.filter(FinanceTransaction.type == "expense").with_entities(
                func.sum(FinanceTransaction.amount)
            ).scalar() or 0
            
            monthly_data.append({
                "month": month,
                "month_name": datetime(year, month, 1).strftime("%B"),
                "income": float(income),
                "expenses": float(expenses),
                "profit": float(income - expenses)
            })
        
        return {
            "success": True,
            "data": {
                "year": year,
                "monthly_data": monthly_data
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения месячной аналитики: {e}")
        return {"success": False, "error": str(e)}

@router.delete("/transactions/{transaction_id}")
async def delete_finance_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Удалить финансовую транзакцию"""
    try:
        # Проверяем права доступа - владелец может удалять все, исполнители только свои
        # (Разрешим исполнителям удалять свои транзакции)
        
        # Получаем транзакцию
        transaction = db.query(FinanceTransaction).filter(
            FinanceTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Транзакция не найдена")
        
        # Проверяем права доступа: исполнители могут удалять только свои транзакции
        if current_user["role"] == "executor" and transaction.created_by_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="У вас нет прав для удаления этой транзакции")
        
        # Сохраняем информацию для логирования
        transaction_description = transaction.description
        transaction_amount = transaction.amount
        transaction_type = transaction.type
        
        # Удаляем транзакцию
        db.delete(transaction)
        db.commit()
        
        logger.info(f"Удалена транзакция: {transaction_description} - {transaction_amount}₽ ({transaction_type})")
        
        return {
            "success": True,
            "message": f"Транзакция '{transaction_description}' успешно удалена"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка удаления транзакции {transaction_id}: {e}")
        return {"success": False, "error": str(e)}

@router.put("/transactions/{transaction_id}")
async def update_finance_transaction(
    transaction_id: int,
    transaction_data: FinanceTransactionCreateModel,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Обновить финансовую транзакцию"""
    try:
        # Проверяем права доступа - владелец может редактировать все, исполнители только свои
        # (Разрешим исполнителям редактировать свои транзакции)
        
        # Получаем транзакцию
        transaction = db.query(FinanceTransaction).filter(
            FinanceTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Транзакция не найдена")
        
        # Проверяем права доступа: исполнители могут редактировать только свои транзакции
        if current_user["role"] == "executor" and transaction.created_by_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="У вас нет прав для редактирования этой транзакции")
        
        # Проверяем, что тип корректный
        if transaction_data.type not in ["income", "expense"]:
            raise HTTPException(status_code=400, detail="Тип должен быть 'income' или 'expense'")
        
        # Проверяем существование категории
        category = db.query(FinanceCategory).filter(FinanceCategory.id == transaction_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        
        # Проверяем существование проекта (если указан)
        if transaction_data.project_id:
            project = db.query(Project).filter(Project.id == transaction_data.project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Проект не найден")
        
        # Обновляем поля транзакции
        transaction.amount = transaction_data.amount
        transaction.type = transaction_data.type
        transaction.description = transaction_data.description
        transaction.date = transaction_data.date
        transaction.category_id = transaction_data.category_id
        transaction.project_id = transaction_data.project_id
        transaction.contractor_name = transaction_data.contractor_name
        transaction.receipt_url = transaction_data.receipt_url
        transaction.notes = transaction_data.notes
        transaction.is_recurring = transaction_data.is_recurring
        transaction.recurring_period = transaction_data.recurring_period
        
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Обновлена транзакция: {transaction.description} - {transaction.amount}₽")
        
        return {
            "success": True,
            "data": transaction.to_dict(),
            "message": "Транзакция успешно обновлена"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка обновления транзакции {transaction_id}: {e}")
        return {"success": False, "error": str(e)}
