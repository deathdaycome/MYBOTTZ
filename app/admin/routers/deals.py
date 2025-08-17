"""
Роутер для управления сделками CRM
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ...database.database import get_db
from ...database.models import AdminUser, Project
from ...database.crm_models import Deal, DealStatus, Client, Lead, Document, ServiceCatalog
from ...database.audit_models import AuditLog
from ...services.rbac_service import RBACService
from ...config.logging import get_logger
from ..auth import get_current_admin_user

logger = get_logger(__name__)
router = APIRouter(prefix="/deals", tags=["deals"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("", response_class=HTMLResponse)
async def deals_page(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Страница управления сделками"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "deals.view"):
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра сделок")
    
    # Получаем элементы навигации
    from ..app import get_navigation_items
    navigation_items = get_navigation_items(current_user.get("role", "admin") if isinstance(current_user, dict) else current_user.role)
    
    # Получаем статистику
    total_deals = db.query(Deal).count()
    active_deals = db.query(Deal).filter(Deal.status.in_([
        DealStatus.NEW,
        DealStatus.DISCUSSION,
        DealStatus.CONTRACT_PREP,
        DealStatus.CONTRACT_SIGNED,
        DealStatus.PREPAYMENT,
        DealStatus.IN_WORK,
        DealStatus.TESTING,
        DealStatus.ACCEPTANCE,
        DealStatus.PAYMENT
    ])).count()
    
    # Сделки текущего месяца
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    deals_this_month = db.query(Deal).filter(Deal.created_at >= month_start).all()
    
    # Статистика по суммам
    total_amount = sum([d.amount for d in deals_this_month if d.amount])
    paid_amount = sum([d.paid_amount for d in deals_this_month if d.paid_amount])
    
    # Завершенные сделки
    completed_month = db.query(Deal).filter(
        Deal.status == DealStatus.COMPLETED,
        Deal.closed_at >= month_start
    ).count()
    
    return templates.TemplateResponse("deals.html", {
        "request": request,
        "user": current_user,
        "username": current_user.get("username") if isinstance(current_user, dict) else current_user.username,
        "user_role": current_user.get("role", "admin") if isinstance(current_user, dict) else current_user.role,
        "navigation_items": navigation_items,
        "stats": {
            "total": total_deals,
            "active": active_deals,
            "completed_month": completed_month,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "payment_progress": round((paid_amount / total_amount * 100) if total_amount > 0 else 0, 1)
        }
    })


@router.get("/api", response_class=JSONResponse)
async def get_deals(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
    manager_id: Optional[int] = Query(None),
    executor_id: Optional[int] = Query(None),
    priority: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Получить список сделок с фильтрацией"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "deals.view"):
            return {"success": False, "message": "Недостаточно прав"}
        
        # Базовый запрос
        query = db.query(Deal)
        
        # Фильтрация по правилам доступа
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        if not rbac.check_permission(current_user, "deals.view_all"):
            # Показываем только доступные сделки
            query = query.filter(or_(
                Deal.manager_id == user_id,
                Deal.executor_id == user_id
            ))
        
        # Поиск
        if search:
            search_filter = or_(
                Deal.title.ilike(f"%{search}%"),
                Deal.description.ilike(f"%{search}%"),
                Deal.contract_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Фильтры
        if status:
            try:
                status_enum = DealStatus[status.upper()]
                query = query.filter(Deal.status == status_enum)
            except KeyError:
                pass
        
        if client_id:
            query = query.filter(Deal.client_id == client_id)
        
        if manager_id:
            query = query.filter(Deal.manager_id == manager_id)
        
        if executor_id:
            query = query.filter(Deal.executor_id == executor_id)
        
        if priority:
            query = query.filter(Deal.priority == priority)
        
        # Сортировка - приоритетные и новые сверху
        query = query.order_by(
            Deal.priority.desc(),
            Deal.created_at.desc()
        )
        
        # Подсчет
        total = query.count()
        
        # Пагинация
        offset = (page - 1) * limit
        deals = query.offset(offset).limit(limit).all()
        
        # Формируем ответ
        deals_data = []
        for deal in deals:
            deal_dict = deal.to_dict()
            
            # Добавляем информацию о клиенте
            if deal.client:
                deal_dict["client_name"] = deal.client.name
                deal_dict["client_phone"] = deal.client.phone
            
            # Информация о менеджере и исполнителе
            if deal.manager:
                deal_dict["manager_name"] = deal.manager.username
            
            if deal.executor:
                deal_dict["executor_name"] = deal.executor.username
            
            # Прогресс оплаты
            if deal.amount:
                deal_dict["payment_progress"] = round((deal.paid_amount / deal.amount * 100) if deal.paid_amount else 0, 1)
            
            # Статус оплаты
            if deal.amount and deal.paid_amount:
                if deal.paid_amount >= deal.amount:
                    deal_dict["payment_status"] = "paid"
                elif deal.paid_amount >= deal.prepayment_amount:
                    deal_dict["payment_status"] = "prepaid"
                else:
                    deal_dict["payment_status"] = "pending"
            else:
                deal_dict["payment_status"] = "pending"
            
            deals_data.append(deal_dict)
        
        return {
            "success": True,
            "deals": deals_data,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения сделок: {str(e)}")
        return {"success": False, "message": str(e)}


@router.post("/api", response_class=JSONResponse)
async def create_deal(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Создать новую сделку"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "deals.create"):
            return {"success": False, "message": "Недостаточно прав для создания сделок"}
        
        data = await request.json()
        
        # Валидация
        if not data.get("title"):
            return {"success": False, "message": "Название сделки обязательно"}
        
        if not data.get("client_id"):
            return {"success": False, "message": "Клиент обязателен"}
        
        if not data.get("amount"):
            return {"success": False, "message": "Сумма сделки обязательна"}
        
        # Проверяем клиента
        client = db.query(Client).filter(Client.id == data["client_id"]).first()
        if not client:
            return {"success": False, "message": "Клиент не найден"}
        
        # Создаем сделку
        deal = Deal(
            title=data["title"],
            status=DealStatus.NEW,
            client_id=data["client_id"],
            description=data.get("description"),
            technical_requirements=data.get("technical_requirements"),
            amount=float(data["amount"]),
            cost=float(data["cost"]) if data.get("cost") else None,
            discount=float(data["discount"]) if data.get("discount") else 0,
            prepayment_percent=int(data.get("prepayment_percent", 50)),
            start_date=datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            manager_id=data.get("manager_id") or (current_user.id if hasattr(current_user, 'id') else current_user.get('id')),
            executor_id=data.get("executor_id"),
            priority=data.get("priority", "normal"),
            tags=data.get("tags", []),
            created_by_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        )
        
        # Рассчитываем предоплату и маржу
        if deal.amount:
            deal.prepayment_amount = deal.amount * deal.prepayment_percent / 100
            
            if deal.cost:
                deal.margin = deal.amount - deal.cost
        
        db.add(deal)
        db.commit()
        db.refresh(deal)
        
        # Обновляем статистику клиента
        client.total_revenue += deal.amount
        if client.deals:
            client.average_check = client.total_revenue / len(client.deals)
        db.commit()
        
        # Логируем действие
        audit_log = AuditLog(
            action="create",
            entity_type="deal",
            entity_id=deal.id,
            new_data=deal.to_dict(),
            description=f"Создана сделка: {deal.title}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_name=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Сделка успешно создана",
            "deal": deal.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания сделки: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.put("/api/{deal_id}/status", response_class=JSONResponse)
async def update_deal_status(
    deal_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновить статус сделки"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "deals", deal_id, "edit"):
            return {"success": False, "message": "Нет прав на редактирование данной сделки"}
        
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            return {"success": False, "message": "Сделка не найдена"}
        
        data = await request.json()
        new_status = data.get("status")
        
        if not new_status:
            return {"success": False, "message": "Статус не указан"}
        
        try:
            status_enum = DealStatus[new_status.upper()]
        except KeyError:
            return {"success": False, "message": "Неверный статус"}
        
        old_status = deal.status
        deal.status = status_enum
        deal.updated_at = datetime.utcnow()
        
        # Обновляем даты в зависимости от статуса
        if status_enum == DealStatus.IN_WORK and not deal.actual_start_date:
            deal.actual_start_date = datetime.utcnow()
        
        if status_enum in [DealStatus.COMPLETED, DealStatus.CANCELLED]:
            deal.closed_at = datetime.utcnow()
            if status_enum == DealStatus.COMPLETED:
                deal.actual_end_date = datetime.utcnow()
        
        db.commit()
        
        # Логируем действие
        audit_log = AuditLog(
            action="update_status",
            entity_type="deal",
            entity_id=deal.id,
            old_data={"status": old_status.value if old_status else None},
            new_data={"status": status_enum.value},
            description=f"Изменен статус сделки '{deal.title}': {old_status.value if old_status else 'Новая'} → {status_enum.value}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_name=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Статус сделки обновлен",
            "deal": deal.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления статуса сделки: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.post("/api/{deal_id}/payment", response_class=JSONResponse)
async def add_payment(
    deal_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Добавить платеж по сделке"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "deals", deal_id, "edit"):
            return {"success": False, "message": "Нет прав на редактирование данной сделки"}
        
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            return {"success": False, "message": "Сделка не найдена"}
        
        data = await request.json()
        amount = float(data.get("amount", 0))
        
        if amount <= 0:
            return {"success": False, "message": "Сумма платежа должна быть больше 0"}
        
        # Обновляем оплаченную сумму
        old_paid = deal.paid_amount
        deal.paid_amount = (deal.paid_amount or 0) + amount
        deal.updated_at = datetime.utcnow()
        
        # Обновляем график платежей
        if not deal.payment_schedule:
            deal.payment_schedule = []
        
        payment_record = {
            "date": datetime.utcnow().isoformat(),
            "amount": amount,
            "type": data.get("type", "payment"),
            "description": data.get("description", ""),
            "user_id": current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            "user_name": current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        }
        
        deal.payment_schedule.append(payment_record)
        
        # Проверяем статус оплаты
        if deal.paid_amount >= deal.amount:
            # Полная оплата
            if deal.status in [DealStatus.PAYMENT, DealStatus.ACCEPTANCE]:
                deal.status = DealStatus.COMPLETED
                deal.closed_at = datetime.utcnow()
        elif deal.paid_amount >= deal.prepayment_amount:
            # Предоплата получена
            if deal.status == DealStatus.PREPAYMENT:
                deal.status = DealStatus.IN_WORK
                deal.actual_start_date = datetime.utcnow()
        
        db.commit()
        
        # Обновляем статистику клиента
        if deal.client:
            # Пересчитываем средний чек
            completed_deals = db.query(Deal).filter(
                Deal.client_id == deal.client_id,
                Deal.status == DealStatus.COMPLETED
            ).all()
            
            if completed_deals:
                total = sum([d.amount for d in completed_deals if d.amount])
                deal.client.average_check = total / len(completed_deals)
                db.commit()
        
        # Логируем действие
        audit_log = AuditLog(
            action="add_payment",
            entity_type="deal",
            entity_id=deal.id,
            old_data={"paid_amount": old_paid},
            new_data={"paid_amount": deal.paid_amount, "payment": amount},
            description=f"Добавлен платеж {amount:,.0f} ₽ к сделке '{deal.title}'",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_name=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": f"Платеж {amount:,.0f} ₽ успешно добавлен",
            "deal": deal.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка добавления платежа: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.post("/api/{deal_id}/convert-to-project", response_class=JSONResponse)
async def convert_deal_to_project(
    deal_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Конвертировать сделку в проект"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "projects.create"):
            return {"success": False, "message": "Недостаточно прав для создания проектов"}
        
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            return {"success": False, "message": "Сделка не найдена"}
        
        # Проверяем, не создан ли уже проект
        if deal.project_id:
            return {"success": False, "message": "Для этой сделки уже создан проект"}
        
        # Проверяем статус сделки
        if deal.status not in [DealStatus.CONTRACT_SIGNED, DealStatus.PREPAYMENT, DealStatus.IN_WORK]:
            return {"success": False, "message": "Сделка должна быть в статусе 'Договор подписан' или позже"}
        
        data = await request.json()
        
        # Создаем проект на основе сделки
        project = Project(
            title=data.get("title") or deal.title,
            description=data.get("description") or deal.description,
            user_id=deal.client.telegram_user_id if deal.client and deal.client.telegram_user_id else None,
            status="in_progress",
            priority=deal.priority or "normal",
            project_type=data.get("project_type", "telegram_bot"),
            complexity=data.get("complexity", "medium"),
            estimated_cost=deal.amount,
            executor_cost=deal.cost,
            prepayment_amount=deal.prepayment_amount,
            client_paid_total=deal.paid_amount,
            estimated_hours=data.get("estimated_hours", 0),
            start_date=deal.actual_start_date or deal.start_date or datetime.utcnow(),
            planned_end_date=deal.end_date or (datetime.utcnow() + timedelta(days=30)),
            responsible_manager_id=deal.manager_id,
            assigned_executor_id=deal.executor_id,
            assigned_at=datetime.utcnow() if deal.executor_id else None,
            structured_tz=deal.technical_requirements or {},
            project_metadata={
                "deal_id": deal.id,
                "client_id": deal.client_id,
                "contract_number": deal.contract_number
            }
        )
        
        db.add(project)
        db.flush()
        
        # Связываем сделку с проектом
        deal.project_id = project.id
        deal.status = DealStatus.IN_WORK
        deal.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Логируем действие
        audit_log = AuditLog(
            action="convert_to_project",
            entity_type="deal",
            entity_id=deal.id,
            new_data={"project_id": project.id, "project_title": project.title},
            description=f"Сделка '{deal.title}' конвертирована в проект '{project.title}'",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_name=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Сделка успешно конвертирована в проект",
            "project": {
                "id": project.id,
                "title": project.title,
                "status": project.status
            },
            "deal": deal.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка конвертации сделки в проект: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.get("/api/pipeline", response_class=JSONResponse)
async def get_pipeline(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить данные для канбан-доски сделок"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "deals.view"):
            return {"success": False, "message": "Недостаточно прав"}
        
        # Базовый запрос
        query = db.query(Deal)
        
        # Фильтрация по доступу
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        if not rbac.check_permission(current_user, "deals.view_all"):
            query = query.filter(or_(
                Deal.manager_id == user_id,
                Deal.executor_id == user_id
            ))
        
        # Получаем только активные сделки
        deals = query.filter(Deal.status.notin_([
            DealStatus.COMPLETED,
            DealStatus.CANCELLED
        ])).all()
        
        # Группируем по статусам
        pipeline = {
            "new": [],
            "discussion": [],
            "contract_prep": [],
            "contract_signed": [],
            "prepayment": [],
            "in_work": [],
            "testing": [],
            "acceptance": [],
            "payment": []
        }
        
        for deal in deals:
            if deal.status:
                status_key = deal.status.value
                if status_key in pipeline:
                    deal_data = {
                        "id": deal.id,
                        "title": deal.title,
                        "client_name": deal.client.name if deal.client else "Не указан",
                        "amount": deal.amount,
                        "priority": deal.priority,
                        "manager_name": deal.manager.username if deal.manager else None,
                        "executor_name": deal.executor.username if deal.executor else None,
                        "days_in_status": (datetime.utcnow() - deal.updated_at).days if deal.updated_at else 0,
                        "payment_progress": round((deal.paid_amount / deal.amount * 100) if deal.amount and deal.paid_amount else 0, 1)
                    }
                    pipeline[status_key].append(deal_data)
        
        # Добавляем статистику по колонкам
        stats = {}
        for status, deals_list in pipeline.items():
            stats[status] = {
                "count": len(deals_list),
                "total_amount": sum([d["amount"] for d in deals_list if d["amount"]])
            }
        
        return {
            "success": True,
            "pipeline": pipeline,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения pipeline: {str(e)}")
        return {"success": False, "message": str(e)}