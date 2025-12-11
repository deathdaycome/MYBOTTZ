"""
Роутер для управления лидами (потенциальными сделками)
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ...core.database import get_db
from ...database.models import AdminUser
from ...database.crm_models import Lead, LeadStatus, Client, Deal, DealStatus
from ...database.audit_models import AuditLog, AuditActionType, AuditEntityType
from ...services.rbac_service import RBACService
from ...config.logging import get_logger
from ..middleware.auth import get_current_admin_user

logger = get_logger(__name__)
router = APIRouter(prefix="/leads", tags=["leads"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("", response_class=HTMLResponse)
async def leads_page(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Страница управления лидами"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "leads.view"):
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра лидов")
    
    # Получаем элементы навигации
    from ..navigation import get_navigation_items
    navigation_items = get_navigation_items(current_user, db)
    
    # Получаем статистику
    total_leads = db.query(Lead).count()
    new_leads = db.query(Lead).filter(Lead.status == LeadStatus.NEW).count()
    in_progress = db.query(Lead).filter(Lead.status.in_([
        LeadStatus.CONTACT_MADE, 
        LeadStatus.QUALIFICATION,
        LeadStatus.PROPOSAL_SENT,
        LeadStatus.NEGOTIATION
    ])).count()
    
    # Конверсия за текущий месяц
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    won_this_month = db.query(Lead).filter(
        Lead.status == LeadStatus.WON,
        Lead.converted_at >= month_start
    ).count()
    
    lost_this_month = db.query(Lead).filter(
        Lead.status == LeadStatus.LOST,
        Lead.updated_at >= month_start
    ).count()
    
    conversion_rate = 0
    if (won_this_month + lost_this_month) > 0:
        conversion_rate = round((won_this_month / (won_this_month + lost_this_month)) * 100, 1)
    
    return templates.TemplateResponse("leads_improved.html", {
        "request": request,
        "user": current_user,
        "username": current_user.get("username") if isinstance(current_user, dict) else current_user.username,
        "password": current_user.get("password", "") if isinstance(current_user, dict) else current_user.password if hasattr(current_user, 'password') else "",
        "user_role": current_user.get("role", "admin") if isinstance(current_user, dict) else current_user.role,
        "navigation_items": navigation_items,
        "stats": {
            "total": total_leads,
            "new": new_leads,
            "in_progress": in_progress,
            "won_month": won_this_month,
            "lost_month": lost_this_month,
            "conversion_rate": conversion_rate
        }
    })


@router.get("/api", response_class=JSONResponse)
async def get_leads(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    manager_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Получить список лидов с фильтрацией"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "leads.view"):
            return {"success": False, "message": "Недостаточно прав"}
        
        # Базовый запрос
        query = db.query(Lead)
        
        # Фильтрация по правилам доступа
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        if not rbac.check_permission(current_user, "leads.view_all"):
            # Показываем только доступные лиды
            query = query.filter(Lead.manager_id == user_id)
        
        # Поиск
        if search:
            search_filter = or_(
                Lead.title.ilike(f"%{search}%"),
                Lead.contact_name.ilike(f"%{search}%"),
                Lead.contact_email.ilike(f"%{search}%"),
                Lead.contact_phone.ilike(f"%{search}%"),
                Lead.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Фильтры
        if status:
            try:
                status_enum = LeadStatus[status.upper()]
                query = query.filter(Lead.status == status_enum)
            except KeyError:
                pass
        
        if source:
            query = query.filter(Lead.source == source)
        
        if manager_id:
            query = query.filter(Lead.manager_id == manager_id)
        
        if client_id:
            query = query.filter(Lead.client_id == client_id)
        
        # Сортировка - новые сверху, затем по приоритету
        query = query.order_by(Lead.created_at.desc())
        
        # Подсчет
        total = query.count()
        
        # Пагинация
        offset = (page - 1) * limit
        leads = query.offset(offset).limit(limit).all()
        
        # Формируем ответ
        leads_data = []
        for lead in leads:
            lead_dict = lead.to_dict()
            
            # Добавляем информацию о клиенте
            if lead.client:
                lead_dict["client_name"] = lead.client.name
                lead_dict["client_type"] = lead.client.type.value if lead.client.type else None
            
            # Информация о менеджере
            if lead.manager:
                lead_dict["manager_name"] = lead.manager.username
            
            # Информация о создателе (продажнике)
            if lead.created_by:
                lead_dict["created_by_name"] = lead.created_by.username
            
            # Рассчитываем время в воронке
            if lead.created_at:
                days_in_funnel = (datetime.utcnow() - lead.created_at).days
                lead_dict["days_in_funnel"] = days_in_funnel
            
            leads_data.append(lead_dict)
        
        return {
            "success": True,
            "leads": leads_data,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения лидов: {str(e)}")
        return {"success": False, "message": str(e)}


@router.post("/api", response_class=JSONResponse)
async def create_lead(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Создать новый лид"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "leads.create"):
            return {"success": False, "message": "Недостаточно прав для создания лидов"}
        
        data = await request.json()
        
        # Валидация
        if not data.get("title"):
            return {"success": False, "message": "Название лида обязательно"}
        
        # Если указан клиент, проверяем его существование
        if data.get("client_id"):
            client = db.query(Client).filter(Client.id == data["client_id"]).first()
            if not client:
                return {"success": False, "message": "Клиент не найден"}
        
        # Создаем лид
        lead = Lead(
            title=data["title"],
            status=LeadStatus.NEW,
            source=data.get("source"),
            client_id=data.get("client_id"),
            contact_name=data.get("contact_name"),
            contact_phone=data.get("contact_phone"),
            contact_email=data.get("contact_email"),
            contact_telegram=data.get("contact_telegram"),
            contact_whatsapp=data.get("contact_whatsapp"),
            description=data.get("description"),
            requirements=data.get("requirements"),
            budget=data.get("budget"),
            probability=data.get("probability", 50),
            expected_close_date=datetime.fromisoformat(data["expected_close_date"]) if data.get("expected_close_date") else None,
            next_action_date=datetime.fromisoformat(data["next_action_date"]) if data.get("next_action_date") else None,
            notes=data.get("notes"),
            manager_id=data.get("manager_id") or (current_user.id if hasattr(current_user, 'id') else current_user.get('id')),
            created_by_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        )
        
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        # Логируем действие
        audit_log = AuditLog(
            action_type=AuditActionType.CREATE,
            entity_type=AuditEntityType.LEAD,
            entity_id=lead.id,
            new_values=lead.to_dict(),
            description=f"Создан лид: {lead.title}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_email=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Лид успешно создан",
            "lead": lead.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания лида: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.get("/api/{lead_id}", response_class=JSONResponse)
async def get_lead_by_id(
    lead_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить конкретный лид по ID"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "leads", lead_id, "view"):
            return {"success": False, "message": "Нет прав на просмотр данного лида"}
        
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"success": False, "message": "Лид не найден"}
        
        lead_dict = lead.to_dict()
        
        # Добавляем информацию о клиенте
        if lead.client:
            lead_dict["client_name"] = lead.client.name
            lead_dict["client_type"] = lead.client.type.value if lead.client.type else None
        
        # Информация о менеджере
        if lead.manager:
            lead_dict["manager_name"] = lead.manager.username
        
        # Информация о создателе
        if lead.created_by:
            lead_dict["created_by_name"] = lead.created_by.username
        
        # Рассчитываем время в воронке
        if lead.created_at:
            days_in_funnel = (datetime.utcnow() - lead.created_at).days
            lead_dict["days_in_funnel"] = days_in_funnel
        
        return {
            "success": True,
            "lead": lead_dict
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения лида: {str(e)}")
        return {"success": False, "message": str(e)}


@router.put("/api/{lead_id}", response_class=JSONResponse)
async def update_lead(
    lead_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновить лид"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "leads", lead_id, "edit"):
            return {"success": False, "message": "Нет прав на редактирование данного лида"}
        
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"success": False, "message": "Лид не найден"}
        
        data = await request.json()
        
        # Сохраняем старые значения для аудита
        old_values = lead.to_dict()
        
        # Обновляем поля
        if "title" in data:
            lead.title = data["title"]
        if "status" in data:
            try:
                lead.status = LeadStatus[data["status"].upper()]
            except KeyError:
                pass
        if "source" in data:
            lead.source = data["source"]
        if "client_id" in data:
            lead.client_id = data["client_id"]
        if "contact_name" in data:
            lead.contact_name = data["contact_name"]
        if "contact_phone" in data:
            lead.contact_phone = data["contact_phone"]
        if "contact_email" in data:
            lead.contact_email = data["contact_email"]
        if "contact_telegram" in data:
            lead.contact_telegram = data["contact_telegram"]
        if "contact_whatsapp" in data:
            lead.contact_whatsapp = data["contact_whatsapp"]
        if "description" in data:
            lead.description = data["description"]
        if "requirements" in data:
            lead.requirements = data["requirements"]
        if "budget" in data:
            lead.budget = data["budget"]
        if "probability" in data:
            lead.probability = data["probability"]
        if "expected_close_date" in data and data["expected_close_date"]:
            lead.expected_close_date = datetime.fromisoformat(data["expected_close_date"])
        if "next_action_date" in data and data["next_action_date"]:
            lead.next_action_date = datetime.fromisoformat(data["next_action_date"])
        if "notes" in data:
            lead.notes = data["notes"]
        if "manager_id" in data:
            lead.manager_id = data["manager_id"]
        
        lead.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(lead)
        
        # Логируем действие
        audit_log = AuditLog(
            action_type=AuditActionType.UPDATE,
            entity_type=AuditEntityType.LEAD,
            entity_id=lead.id,
            old_values=old_values,
            new_values=lead.to_dict(),
            description=f"Обновлен лид: {lead.title}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_email=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Лид успешно обновлен",
            "lead": lead.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления лида: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.put("/api/{lead_id}/status", response_class=JSONResponse)
async def update_lead_status(
    lead_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновить статус лида"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "leads", lead_id, "edit"):
            return {"success": False, "message": "Нет прав на редактирование данного лида"}
        
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"success": False, "message": "Лид не найден"}
        
        data = await request.json()
        new_status = data.get("status")
        
        if not new_status:
            return {"success": False, "message": "Статус не указан"}
        
        try:
            status_enum = LeadStatus[new_status.upper()]
        except KeyError:
            return {"success": False, "message": "Неверный статус"}
        
        old_status = lead.status
        lead.status = status_enum
        lead.updated_at = datetime.utcnow()
        
        # Добавляем в историю взаимодействий
        interaction = {
            "date": datetime.utcnow().isoformat(),
            "type": "status_change",
            "old_status": old_status.value if old_status else None,
            "new_status": status_enum.value,
            "user_id": current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            "user_name": current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        }
        
        if not lead.interactions:
            lead.interactions = []
        lead.interactions.append(interaction)
        
        # Если статус LOST, сохраняем причину
        if status_enum == LeadStatus.LOST and data.get("lost_reason"):
            lead.lost_reason = data["lost_reason"]

        # Автоматически создаём сделку при переводе лида в статус WON
        if status_enum == LeadStatus.WON and old_status != LeadStatus.WON:
            # Проверяем, нет ли уже созданной сделки для этого лида
            existing_deal = db.query(Deal).filter(Deal.lead_id == lead.id).first()

            if not existing_deal:
                # Создаём новую сделку
                new_deal = Deal(
                    title=lead.title,
                    description=f"Автоматически создано из лида: {lead.title}",
                    client_id=lead.client_id,
                    lead_id=lead.id,
                    amount=lead.estimated_value,
                    status=DealStatus.NEW,
                    created_by_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_deal)
                db.flush()  # Получаем ID без коммита

                # Обновляем лид - добавляем ссылку на сделку
                lead.converted_at = datetime.utcnow()

                # Логируем создание сделки
                audit_log_deal = AuditLog(
                    action_type=AuditActionType.CREATE,
                    entity_type=AuditEntityType.DEAL,
                    entity_id=new_deal.id,
                    old_values={},
                    new_values={"title": new_deal.title, "status": DealStatus.NEW.value},
                    description=f"Автоматически создана сделка из лида '{lead.title}'",
                    user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
                    user_email=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
                )
                db.add(audit_log_deal)

                logger.info(f"Автоматически создана сделка ID={new_deal.id} из лида ID={lead.id}")

        db.commit()
        
        # Логируем действие
        audit_log = AuditLog(
            action_type=AuditActionType.UPDATE,
            entity_type=AuditEntityType.LEAD,
            entity_id=lead.id,
            old_values={"status": old_status.value if old_status else None},
            new_values={"status": status_enum.value},
            description=f"Изменен статус лида '{lead.title}': {old_status.value if old_status else 'Новый'} → {status_enum.value}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_email=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Статус лида обновлен",
            "lead": lead.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления статуса лида: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.post("/api/{lead_id}/convert", response_class=JSONResponse)
async def convert_lead_to_deal(
    lead_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Конвертировать лид в сделку через IntegrationService"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "leads.convert"):
            return {"success": False, "message": "Недостаточно прав для конвертации лидов"}
        
        data = await request.json()
        
        # Используем IntegrationService для конвертации
        try:
            from ...services.integration_service import IntegrationService
            integration_service = IntegrationService(db)
        except ImportError as e:
            logger.error(f"Ошибка импорта IntegrationService: {e}")
            # Fallback к простой логике
            return await convert_lead_to_deal_fallback(lead_id, data, current_user, db)
        
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        result = integration_service.convert_lead_to_deal(
            lead_id=lead_id,
            deal_data=data,
            current_user_id=user_id
        )
        
        if result["success"]:
            # Логируем действие
            audit_log = AuditLog(
                action_type=AuditActionType.LEAD_CONVERT,
                entity_type=AuditEntityType.LEAD,
                entity_id=lead_id,
                new_values=result["data"],
                description=f"Лид конвертирован в сделку через IntegrationService",
                user_id=user_id,
                user_email=current_user.username if hasattr(current_user, 'username') else current_user.get('username')
            )
            db.add(audit_log)
            db.commit()
        
        return {
            "success": result["success"],
            "message": "Лид успешно конвертирован в сделку" if result["success"] else result.get("error", "Ошибка конвертации"),
            "data": result.get("data")
        }
        
    except Exception as e:
        logger.error(f"Ошибка конвертации лида: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.get("/api/stats/funnel", response_class=JSONResponse)
async def get_funnel_stats(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    period: str = Query("month")  # day, week, month, quarter, year
):
    """Получить статистику воронки продаж"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "leads.view"):
            return {"success": False, "message": "Недостаточно прав"}
        
        # Определяем период
        now = datetime.utcnow()
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        # Базовый запрос
        query = db.query(Lead).filter(Lead.created_at >= start_date)
        
        # Фильтрация по доступу
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        if not rbac.check_permission(current_user, "leads.view_all"):
            query = query.filter(Lead.manager_id == user_id)
        
        leads = query.all()
        
        # Статистика по статусам
        funnel_stats = {
            "new": 0,
            "contact_made": 0,
            "qualification": 0,
            "proposal_sent": 0,
            "negotiation": 0,
            "won": 0,
            "lost": 0,
            "postponed": 0
        }
        
        total_value = 0
        won_value = 0
        lost_value = 0
        
        for lead in leads:
            if lead.status:
                status_key = lead.status.value
                if status_key in funnel_stats:
                    funnel_stats[status_key] += 1
                
                # Считаем стоимость
                if lead.budget:
                    if lead.status == LeadStatus.WON:
                        won_value += lead.budget
                    elif lead.status == LeadStatus.LOST:
                        lost_value += lead.budget
                    else:
                        total_value += lead.budget
        
        # Рассчитываем конверсии
        total_leads = len(leads)
        conversion_rates = {}
        
        if total_leads > 0:
            for status, count in funnel_stats.items():
                conversion_rates[status] = round((count / total_leads) * 100, 1)
        
        # Средние показатели
        avg_budget = 0
        avg_probability = 0
        avg_days_to_close = 0
        
        if leads:
            budgets = [l.budget for l in leads if l.budget]
            if budgets:
                avg_budget = sum(budgets) / len(budgets)
            
            probabilities = [l.probability for l in leads if l.probability]
            if probabilities:
                avg_probability = sum(probabilities) / len(probabilities)
            
            # Время закрытия для выигранных сделок
            won_leads = [l for l in leads if l.status == LeadStatus.WON and l.converted_at]
            if won_leads:
                close_times = [(l.converted_at - l.created_at).days for l in won_leads]
                avg_days_to_close = sum(close_times) / len(close_times)
        
        return {
            "success": True,
            "period": period,
            "funnel": funnel_stats,
            "conversion_rates": conversion_rates,
            "values": {
                "potential": total_value,
                "won": won_value,
                "lost": lost_value
            },
            "metrics": {
                "total_leads": total_leads,
                "avg_budget": round(avg_budget, 2),
                "avg_probability": round(avg_probability, 1),
                "avg_days_to_close": round(avg_days_to_close, 1),
                "win_rate": conversion_rates.get("won", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики воронки: {str(e)}")
        return {"success": False, "message": str(e)}


async def convert_lead_to_deal_fallback(lead_id: int, data: dict, current_user, db):
    """Простая fallback функция для конвертации лида в сделку"""
    try:
        from ...database.crm_models import Lead, Deal, Client, LeadStatus, DealStatus, ClientStatus
        
        # Получаем лид
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"success": False, "message": "Лид не найден"}
        
        # Обновляем статус лида на "выиграно"
        lead.status = LeadStatus.WON
        lead.converted_at = datetime.utcnow()
        
        # Создаем или получаем клиента
        client = None
        if lead.client_id:
            client = db.query(Client).filter(Client.id == lead.client_id).first()
        
        if not client:
            # Создаем нового клиента из данных лида
            from ...database.crm_models import ClientType
            client = Client(
                name=lead.contact_name or lead.company_name or "Клиент",
                type=ClientType.COMPANY if lead.company_name else ClientType.INDIVIDUAL,
                phone=lead.contact_phone,
                email=lead.contact_email,
                telegram=lead.contact_telegram,
                company_name=lead.company_name,
                source=lead.source,
                status=ClientStatus.NEW,
                created_at=datetime.utcnow()
            )
            db.add(client)
            db.flush()
            lead.client_id = client.id
        
        # Создаем сделку
        deal = Deal(
            title=data.get("title", lead.title),
            client_id=client.id,
            amount=data.get("amount", lead.budget or 0),
            status=DealStatus.NEW,
            description=data.get("description", lead.description),
            end_date=data.get("expected_close_date", lead.expected_close_date),
            created_by_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            created_at=datetime.utcnow()
        )
        
        db.add(deal)
        db.flush()
        
        # Обновляем лид
        lead.converted_to_deal_id = deal.id
        db.commit()
        
        return {
            "success": True,
            "message": "Лид успешно конвертирован в сделку",
            "data": {
                "deal_id": deal.id,
                "client_id": client.id,
                "lead_id": lead.id
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка fallback конвертации лида: {e}")
        return {"success": False, "message": str(e)}