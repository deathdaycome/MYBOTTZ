# app/admin/routers/transactions.py
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from pydantic import BaseModel, Field

from ...core.database import get_db
from ...database.models import Transaction, Project, User, AdminUser, ExpenseCategory
from ...config.logging import get_logger
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)) -> AdminUser:
    """Получение текущего администратора"""
    from ...config.settings import settings
    
    # Проверяем главного админа
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    if correct_username and correct_password:
        admin_user = db.query(AdminUser).filter(AdminUser.username == credentials.username).first()
        if admin_user:
            return admin_user
        # Создаем если не существует
        admin = AdminUser(
            username=settings.ADMIN_USERNAME,
            first_name='System',
            last_name='Administrator',
            email='admin@system.local',
            role='owner',
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.set_password(settings.ADMIN_PASSWORD)
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    
    # Проверяем других админов
    admin_user = db.query(AdminUser).filter(AdminUser.username == credentials.username).first()
    if admin_user and admin_user.check_password(credentials.password):
        return admin_user
    
    raise HTTPException(
        status_code=401,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Basic"},
    )

logger = get_logger(__name__)
router = APIRouter(tags=["transactions"])

# Pydantic модели
class TransactionCreate(BaseModel):
    transaction_type: str = Field(..., description="income или expense")
    project_id: Optional[int] = None
    contractor_id: Optional[int] = None
    user_id: Optional[int] = None
    amount: float = Field(..., gt=0)
    currency: str = "RUB"
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    status: str = "completed"
    transaction_date: datetime
    transaction_metadata: dict = {}

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    transaction_date: Optional[datetime] = None

@router.get("/", response_model=dict)
async def get_transactions(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
    transaction_type: Optional[str] = None,
    project_id: Optional[int] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Получить список транзакций с фильтрами"""
    try:
        query = db.query(Transaction)
        
        # Фильтры
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        if project_id:
            query = query.filter(Transaction.project_id == project_id)
        if category:
            query = query.filter(Transaction.category == category)
        if status:
            query = query.filter(Transaction.status == status)
        if date_from:
            query = query.filter(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(Transaction.transaction_date <= date_to)
        
        # Общее количество
        total = query.count()
        
        # Получаем транзакции
        transactions = query.order_by(Transaction.transaction_date.desc()).offset(offset).limit(limit).all()
        
        # Считаем суммы
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == "income",
            Transaction.status == "completed"
        ).scalar() or 0
        
        total_expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == "expense",
            Transaction.status == "completed"
        ).scalar() or 0
        
        return {
            "success": True,
            "data": [t.to_dict() for t in transactions],
            "total": total,
            "summary": {
                "total_income": total_income,
                "total_expense": total_expense,
                "balance": total_income - total_expense
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении транзакций: {str(e)}")
        return {"success": False, "message": str(e)}

@router.post("/income", response_model=dict)
async def create_income(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Создать доход (обязательно привязан к проекту)"""
    try:
        # Проверяем, что указан проект
        if not transaction_data.project_id:
            return {"success": False, "message": "Доход должен быть привязан к проекту"}
        
        # Проверяем существование проекта
        project = db.query(Project).filter(Project.id == transaction_data.project_id).first()
        if not project:
            return {"success": False, "message": "Проект не найден"}
        
        # Создаем транзакцию
        transaction = Transaction(
            transaction_type="income",
            project_id=transaction_data.project_id,
            user_id=project.user_id,  # Берем клиента из проекта
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            category="Оплата проекта",
            description=transaction_data.description or f"Оплата по проекту: {project.title}",
            payment_method=transaction_data.payment_method,
            reference_number=transaction_data.reference_number,
            status=transaction_data.status,
            transaction_date=transaction_data.transaction_date,
            created_by_id=current_user.id,
            transaction_metadata=transaction_data.transaction_metadata
        )
        
        db.add(transaction)
        
        # Обновляем сумму оплаты клиента в проекте
        project.client_paid_total = (project.client_paid_total or 0) + transaction_data.amount
        project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transaction)
        
        # Вычисляем остаток
        remaining = (project.estimated_cost or 0) - project.client_paid_total
        
        logger.info(f"Создан доход: {transaction_data.amount} для проекта {project.id}")
        
        return {
            "success": True,
            "message": f"Доход {transaction_data.amount} {transaction_data.currency} успешно добавлен",
            "data": transaction.to_dict(),
            "project_finance": {
                "total_cost": project.estimated_cost,
                "paid": project.client_paid_total,
                "remaining": remaining
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка при создании дохода: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}

@router.post("/expense", response_model=dict)
async def create_expense(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Создать расход"""
    try:
        # Проверяем категорию
        if transaction_data.category:
            category = db.query(ExpenseCategory).filter(
                ExpenseCategory.name == transaction_data.category
            ).first()
            if not category:
                logger.warning(f"Категория не найдена: {transaction_data.category}")
        
        # Создаем транзакцию
        transaction = Transaction(
            transaction_type="expense",
            project_id=transaction_data.project_id,
            contractor_id=transaction_data.contractor_id,
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            category=transaction_data.category or "Прочие расходы",
            subcategory=transaction_data.subcategory,
            description=transaction_data.description,
            payment_method=transaction_data.payment_method,
            reference_number=transaction_data.reference_number,
            status=transaction_data.status,
            transaction_date=transaction_data.transaction_date,
            created_by_id=current_user.id,
            transaction_metadata=transaction_data.transaction_metadata
        )
        
        db.add(transaction)
        
        # Если расход привязан к проекту и исполнителю, обновляем выплаты
        if transaction_data.project_id and transaction_data.contractor_id:
            project = db.query(Project).filter(Project.id == transaction_data.project_id).first()
            if project:
                project.executor_paid_total = (project.executor_paid_total or 0) + transaction_data.amount
                project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Создан расход: {transaction_data.amount} в категории {transaction.category}")
        
        return {
            "success": True,
            "message": f"Расход {transaction_data.amount} {transaction_data.currency} успешно добавлен",
            "data": transaction.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка при создании расхода: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}

@router.get("/project/{project_id}/finance", response_model=dict)
async def get_project_finance(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить финансовую информацию по проекту"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"success": False, "message": "Проект не найден"}
        
        # Доходы по проекту
        income_total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.project_id == project_id,
            Transaction.transaction_type == "income",
            Transaction.status == "completed"
        ).scalar() or 0
        
        # Расходы по проекту
        expense_total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.project_id == project_id,
            Transaction.transaction_type == "expense",
            Transaction.status == "completed"
        ).scalar() or 0
        
        # Прибыль
        profit = income_total - expense_total
        
        # Рентабельность
        profitability = (profit / project.estimated_cost * 100) if project.estimated_cost else 0
        
        # Остаток к оплате от клиента
        client_remaining = (project.estimated_cost or 0) - income_total
        
        # Транзакции
        transactions = db.query(Transaction).filter(
            Transaction.project_id == project_id
        ).order_by(Transaction.transaction_date.desc()).all()
        
        return {
            "success": True,
            "project": {
                "id": project.id,
                "title": project.title,
                "estimated_cost": project.estimated_cost,
                "executor_cost": project.executor_cost
            },
            "finance": {
                "total_income": income_total,
                "total_expense": expense_total,
                "profit": profit,
                "profitability": round(profitability, 2),
                "client_remaining": client_remaining,
                "client_paid_percent": round((income_total / project.estimated_cost * 100) if project.estimated_cost else 0, 2)
            },
            "transactions": [t.to_dict() for t in transactions]
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении финансов проекта: {str(e)}")
        return {"success": False, "message": str(e)}

@router.get("/analytics/monthly", response_model=dict)
async def get_monthly_analytics(
    year: int = datetime.now().year,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить аналитику по месяцам"""
    try:
        monthly_data = []
        
        for month in range(1, 13):
            # Доходы за месяц
            income = db.query(func.sum(Transaction.amount)).filter(
                extract('year', Transaction.transaction_date) == year,
                extract('month', Transaction.transaction_date) == month,
                Transaction.transaction_type == "income",
                Transaction.status == "completed"
            ).scalar() or 0
            
            # Расходы за месяц
            expense = db.query(func.sum(Transaction.amount)).filter(
                extract('year', Transaction.transaction_date) == year,
                extract('month', Transaction.transaction_date) == month,
                Transaction.transaction_type == "expense",
                Transaction.status == "completed"
            ).scalar() or 0
            
            # Количество завершенных проектов
            completed_projects = db.query(func.count(Project.id)).filter(
                extract('year', Project.updated_at) == year,
                extract('month', Project.updated_at) == month,
                Project.status == "completed"
            ).scalar() or 0
            
            monthly_data.append({
                "month": month,
                "month_name": datetime(year, month, 1).strftime("%B"),
                "income": income,
                "expense": expense,
                "profit": income - expense,
                "completed_projects": completed_projects
            })
        
        # Итоги за год
        year_income = sum(m["income"] for m in monthly_data)
        year_expense = sum(m["expense"] for m in monthly_data)
        
        return {
            "success": True,
            "year": year,
            "monthly_data": monthly_data,
            "year_summary": {
                "total_income": year_income,
                "total_expense": year_expense,
                "total_profit": year_income - year_expense,
                "avg_monthly_income": year_income / 12,
                "avg_monthly_expense": year_expense / 12,
                "avg_monthly_profit": (year_income - year_expense) / 12
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении месячной аналитики: {str(e)}")
        return {"success": False, "message": str(e)}

@router.get("/categories", response_model=dict)
async def get_expense_categories(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Получить список категорий расходов"""
    try:
        categories = db.query(ExpenseCategory).filter(
            ExpenseCategory.is_active == True
        ).order_by(ExpenseCategory.order_index).all()
        
        # Добавляем статистику по каждой категории
        categories_with_stats = []
        for cat in categories:
            total_spent = db.query(func.sum(Transaction.amount)).filter(
                Transaction.category == cat.name,
                Transaction.transaction_type == "expense",
                Transaction.status == "completed"
            ).scalar() or 0
            
            cat_dict = cat.to_dict()
            cat_dict["total_spent"] = total_spent
            categories_with_stats.append(cat_dict)
        
        return {
            "success": True,
            "categories": categories_with_stats
        }
        
    except Exception as e:
        logger.error(f"Ошибка при получении категорий: {str(e)}")
        return {"success": False, "message": str(e)}

@router.delete("/{transaction_id}", response_model=dict)
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Удалить транзакцию"""
    try:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            return {"success": False, "message": "Транзакция не найдена"}
        
        # Если это доход по проекту, обновляем сумму оплаты
        if transaction.transaction_type == "income" and transaction.project_id:
            project = db.query(Project).filter(Project.id == transaction.project_id).first()
            if project:
                project.client_paid_total = (project.client_paid_total or 0) - transaction.amount
        
        # Если это расход по проекту для исполнителя, обновляем выплаты
        if transaction.transaction_type == "expense" and transaction.project_id and transaction.contractor_id:
            project = db.query(Project).filter(Project.id == transaction.project_id).first()
            if project:
                project.executor_paid_total = (project.executor_paid_total or 0) - transaction.amount
        
        db.delete(transaction)
        db.commit()
        
        logger.info(f"Транзакция {transaction_id} удалена")
        
        return {
            "success": True,
            "message": "Транзакция успешно удалена"
        }
        
    except Exception as e:
        logger.error(f"Ошибка при удалении транзакции: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}