"""
Роутер для управления клиентами CRM
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ...database.database import get_db
from ...database.models import AdminUser, User
from ...database.crm_models import Client, ClientType, ClientStatus, Lead, Deal, Document, ClientTag
from ...services.rbac_service import RBACService, require_permission
from ...config.logging import get_logger
from ..middleware.auth import get_current_admin_user

logger = get_logger(__name__)
router = APIRouter(prefix="/clients", tags=["clients"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.get("", response_class=HTMLResponse)
async def clients_page(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Страница управления клиентами"""
    # Проверяем права доступа
    rbac = RBACService(db)
    if not rbac.check_permission(current_user, "clients.view"):
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра клиентов")
    
    # Получаем элементы навигации
    from ..navigation import get_navigation_items
    navigation_items = get_navigation_items(current_user, db)
    
    # Получаем статистику
    total_clients = db.query(Client).count()
    active_clients = db.query(Client).filter(Client.status == ClientStatus.ACTIVE).count()
    vip_clients = db.query(Client).filter(Client.status == ClientStatus.VIP).count()
    new_clients_month = db.query(Client).filter(
        Client.created_at >= datetime.now().replace(day=1, hour=0, minute=0, second=0)
    ).count()
    
    return templates.TemplateResponse("clients.html", {
        "request": request,
        "user": current_user,
        "username": current_user.get("username") if isinstance(current_user, dict) else current_user.username,
        "user_role": current_user.get("role", "admin") if isinstance(current_user, dict) else current_user.role,
        "navigation_items": navigation_items,
        "stats": {
            "total": total_clients,
            "active": active_clients,
            "vip": vip_clients,
            "new_month": new_clients_month
        }
    })


@router.get("/api", response_class=JSONResponse)
async def get_clients(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    manager_id: Optional[int] = Query(None),
    segment: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Получить список клиентов с фильтрацией и пагинацией"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "clients.view"):
            return {"success": False, "message": "Недостаточно прав"}
        
        # Базовый запрос
        query = db.query(Client)
        
        # Фильтрация по правилам доступа
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        if not rbac.check_permission(current_user, "clients.view_all"):
            # Показываем только клиентов, доступных пользователю
            if rbac.check_permission(current_user, "clients.view_team"):
                # Доступ к клиентам команды
                from ...database.rbac_models import TeamMembership
                team_members = db.query(TeamMembership.user_id).filter(
                    TeamMembership.team_id.in_(
                        db.query(TeamMembership.team_id).filter(
                            TeamMembership.user_id == user_id
                        )
                    )
                ).subquery()
                query = query.filter(Client.manager_id.in_(team_members))
            else:
                # Только свои клиенты
                query = query.filter(Client.manager_id == user_id)
        
        # Поиск
        if search:
            search_filter = or_(
                Client.name.ilike(f"%{search}%"),
                Client.email.ilike(f"%{search}%"),
                Client.phone.ilike(f"%{search}%"),
                Client.telegram.ilike(f"%{search}%"),
                Client.company_name.ilike(f"%{search}%"),
                Client.inn.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Фильтры
        if status:
            try:
                status_enum = ClientStatus[status.upper()]
                query = query.filter(Client.status == status_enum)
            except KeyError:
                pass
        
        if type:
            try:
                type_enum = ClientType[type.upper()]
                query = query.filter(Client.type == type_enum)
            except KeyError:
                pass
        
        if manager_id:
            query = query.filter(Client.manager_id == manager_id)
        
        if segment:
            query = query.filter(Client.segment == segment)
        
        # Подсчет общего количества
        total = query.count()
        
        # Пагинация
        offset = (page - 1) * limit
        clients = query.offset(offset).limit(limit).all()
        
        # Формируем ответ
        clients_data = []
        for client in clients:
            client_dict = client.to_dict()
            
            # Добавляем дополнительную информацию
            client_dict["leads_count"] = len(client.leads) if client.leads else 0
            client_dict["deals_count"] = len(client.deals) if client.deals else 0
            client_dict["active_deals"] = len([d for d in client.deals if d.status not in ['completed', 'cancelled']]) if client.deals else 0
            
            # Информация о менеджере
            if client.manager:
                client_dict["manager_name"] = client.manager.username
            
            clients_data.append(client_dict)
        
        return {
            "success": True,
            "clients": clients_data,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения клиентов: {str(e)}")
        return {"success": False, "message": str(e)}


@router.post("/api", response_class=JSONResponse)
async def create_client(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Создать нового клиента"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "clients.create"):
            return {"success": False, "message": "Недостаточно прав для создания клиентов"}
        
        data = await request.json()
        
        # Валидация обязательных полей
        if not data.get("name"):
            return {"success": False, "message": "Имя клиента обязательно"}
        
        # Проверяем уникальность ИНН если указан
        if data.get("inn"):
            existing = db.query(Client).filter(Client.inn == data["inn"]).first()
            if existing:
                return {"success": False, "message": f"Клиент с ИНН {data['inn']} уже существует"}
        
        # Определяем тип клиента
        client_type = ClientType.INDIVIDUAL
        if data.get("type"):
            try:
                client_type = ClientType[data["type"].upper()]
            except KeyError:
                pass
        
        # Создаем клиента
        client = Client(
            name=data["name"],
            type=client_type,
            status=ClientStatus.NEW,
            phone=data.get("phone"),
            email=data.get("email"),
            telegram=data.get("telegram"),
            whatsapp=data.get("whatsapp"),
            website=data.get("website"),
            address=data.get("address"),
            company_name=data.get("company_name"),
            inn=data.get("inn"),
            kpp=data.get("kpp"),
            ogrn=data.get("ogrn"),
            bank_details=data.get("bank_details"),
            source=data.get("source"),
            description=data.get("description"),
            payment_terms=data.get("payment_terms"),
            credit_limit=data.get("credit_limit"),
            manager_id=data.get("manager_id") or (current_user.id if hasattr(current_user, 'id') else current_user.get('id')),
            created_by_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        )
        
        # Связываем с пользователем Telegram если указан
        if data.get("telegram_user_id"):
            telegram_user = db.query(User).filter(User.id == data["telegram_user_id"]).first()
            if telegram_user:
                client.telegram_user_id = telegram_user.id
        
        db.add(client)
        db.commit()
        db.refresh(client)
        
        # Логируем действие
        from ...database.audit_models import AuditLog, AuditActionType, AuditEntityType
        audit_log = AuditLog(
            action_type=AuditActionType.CREATE,
            entity_type=AuditEntityType.CLIENT,
            entity_id=client.id,
            new_values=client.to_dict(),
            description=f"Создан клиент: {client.name}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_email=current_user.email if hasattr(current_user, 'email') else current_user.get('email')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Клиент успешно создан",
            "client": client.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания клиента: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.get("/api/{client_id}", response_class=JSONResponse)
async def get_client(
    client_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о клиенте"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "clients", client_id, "view"):
            return {"success": False, "message": "Нет доступа к данному клиенту"}
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"success": False, "message": "Клиент не найден"}
        
        client_dict = client.to_dict()
        
        # Добавляем связанные данные
        client_dict["leads"] = [lead.to_dict() for lead in client.leads]
        client_dict["deals"] = [deal.to_dict() for deal in client.deals]
        client_dict["documents"] = [doc.to_dict() for doc in client.documents]
        
        # История коммуникаций
        if client.communication_history:
            client_dict["communication_history"] = client.communication_history
        
        # Статистика
        client_dict["statistics"] = {
            "total_leads": len(client.leads),
            "converted_leads": len([l for l in client.leads if l.status == 'won']),
            "total_deals": len(client.deals),
            "active_deals": len([d for d in client.deals if d.status not in ['completed', 'cancelled']]),
            "completed_deals": len([d for d in client.deals if d.status == 'completed']),
            "total_revenue": client.total_revenue,
            "average_check": client.average_check
        }
        
        # Информация о менеджере
        if client.manager:
            client_dict["manager"] = {
                "id": client.manager.id,
                "username": client.manager.username,
                "email": client.manager.email
            }
        
        return {
            "success": True,
            "client": client_dict
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения клиента: {str(e)}")
        return {"success": False, "message": str(e)}


@router.put("/api/{client_id}", response_class=JSONResponse)
async def update_client(
    client_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновить данные клиента"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "clients", client_id, "edit"):
            return {"success": False, "message": "Нет прав на редактирование данного клиента"}
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"success": False, "message": "Клиент не найден"}
        
        data = await request.json()
        old_data = client.to_dict()
        
        # Обновляем поля
        update_fields = [
            'name', 'phone', 'email', 'telegram', 'whatsapp', 'website',
            'address', 'company_name', 'inn', 'kpp', 'ogrn', 'bank_details',
            'source', 'description', 'preferences', 'payment_terms',
            'credit_limit', 'rating', 'segment', 'loyalty_level'
        ]
        
        for field in update_fields:
            if field in data:
                setattr(client, field, data[field])
        
        # Обновляем тип и статус
        if "type" in data:
            try:
                client.type = ClientType[data["type"].upper()]
            except KeyError:
                pass
        
        if "status" in data:
            try:
                client.status = ClientStatus[data["status"].upper()]
            except KeyError:
                pass
        
        # Обновляем менеджера
        if "manager_id" in data:
            client.manager_id = data["manager_id"]
        
        client.updated_at = datetime.utcnow()
        db.commit()
        
        # Логируем действие
        from ...database.audit_models import AuditLog, AuditActionType, AuditEntityType
        audit_log = AuditLog(
            action_type=AuditActionType.UPDATE,
            entity_type=AuditEntityType.CLIENT,
            entity_id=client.id,
            old_values=old_data,
            new_values=client.to_dict(),
            description=f"Обновлен клиент: {client.name}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_email=current_user.email if hasattr(current_user, 'email') else current_user.get('email')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Клиент успешно обновлен",
            "client": client.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления клиента: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.delete("/api/{client_id}", response_class=JSONResponse)
async def delete_client(
    client_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Удалить клиента"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "clients", client_id, "delete"):
            return {"success": False, "message": "Нет прав на удаление данного клиента"}
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"success": False, "message": "Клиент не найден"}
        
        # Проверяем наличие активных сделок
        active_deals = [d for d in client.deals if d.status not in ['completed', 'cancelled']]
        if active_deals:
            return {
                "success": False,
                "message": f"Невозможно удалить клиента с активными сделками ({len(active_deals)} шт.)"
            }
        
        old_data = client.to_dict()
        client_name = client.name
        
        # Удаляем клиента (связанные лиды и сделки удалятся каскадно)
        db.delete(client)
        db.commit()
        
        # Логируем действие
        from ...database.audit_models import AuditLog, AuditActionType, AuditEntityType
        audit_log = AuditLog(
            action_type=AuditActionType.DELETE,
            entity_type=AuditEntityType.CLIENT,
            entity_id=client_id,
            old_values=old_data,
            description=f"Удален клиент: {client_name}",
            user_id=current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            user_email=current_user.email if hasattr(current_user, 'email') else current_user.get('email')
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "success": True,
            "message": "Клиент успешно удален"
        }
        
    except Exception as e:
        logger.error(f"Ошибка удаления клиента: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.post("/api/{client_id}/communication", response_class=JSONResponse)
async def add_communication(
    client_id: int,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Добавить запись о коммуникации с клиентом"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "clients", client_id, "edit"):
            return {"success": False, "message": "Нет прав на редактирование данного клиента"}
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"success": False, "message": "Клиент не найден"}
        
        data = await request.json()
        
        # Создаем запись о коммуникации
        communication = {
            "date": datetime.utcnow().isoformat(),
            "type": data.get("type", "note"),  # call, email, meeting, note
            "subject": data.get("subject", ""),
            "content": data.get("content", ""),
            "user_id": current_user.id if hasattr(current_user, 'id') else current_user.get('id'),
            "user_name": current_user.username if hasattr(current_user, 'username') else current_user.get('username')
        }
        
        # Добавляем в историю
        if not client.communication_history:
            client.communication_history = []
        
        client.communication_history.append(communication)
        client.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Запись о коммуникации добавлена",
            "communication": communication
        }
        
    except Exception as e:
        logger.error(f"Ошибка добавления коммуникации: {str(e)}")
        db.rollback()
        return {"success": False, "message": str(e)}


@router.get("/api/{client_id}/timeline", response_class=JSONResponse)
async def get_client_timeline(
    client_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить временную шкалу активности клиента"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_data_access(current_user, "clients", client_id, "view"):
            return {"success": False, "message": "Нет доступа к данному клиенту"}
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"success": False, "message": "Клиент не найден"}
        
        timeline = []
        
        # Добавляем создание клиента
        timeline.append({
            "date": client.created_at.isoformat() if client.created_at else None,
            "type": "client_created",
            "title": "Клиент создан",
            "description": f"Клиент {client.name} добавлен в систему",
            "icon": "user-plus"
        })
        
        # Добавляем лиды
        for lead in client.leads:
            timeline.append({
                "date": lead.created_at.isoformat() if lead.created_at else None,
                "type": "lead_created",
                "title": f"Лид: {lead.title}",
                "description": f"Статус: {lead.status.value if lead.status else 'Новый'}",
                "icon": "lightbulb",
                "entity_id": lead.id
            })
            
            if lead.converted_to_deal_id:
                timeline.append({
                    "date": lead.converted_at.isoformat() if lead.converted_at else None,
                    "type": "lead_converted",
                    "title": "Лид конвертирован в сделку",
                    "description": f"Лид '{lead.title}' успешно конвертирован",
                    "icon": "exchange-alt",
                    "entity_id": lead.id
                })
        
        # Добавляем сделки
        for deal in client.deals:
            timeline.append({
                "date": deal.created_at.isoformat() if deal.created_at else None,
                "type": "deal_created",
                "title": f"Сделка: {deal.title}",
                "description": f"Сумма: {deal.amount:,.0f} ₽",
                "icon": "handshake",
                "entity_id": deal.id
            })
            
            if deal.status == 'completed' and deal.closed_at:
                timeline.append({
                    "date": deal.closed_at.isoformat(),
                    "type": "deal_completed",
                    "title": "Сделка завершена",
                    "description": f"Сделка '{deal.title}' успешно завершена",
                    "icon": "check-circle",
                    "entity_id": deal.id
                })
        
        # Добавляем коммуникации
        if client.communication_history:
            for comm in client.communication_history:
                icon_map = {
                    "call": "phone",
                    "email": "envelope",
                    "meeting": "users",
                    "note": "sticky-note"
                }
                timeline.append({
                    "date": comm.get("date"),
                    "type": f"communication_{comm.get('type', 'note')}",
                    "title": comm.get("subject", "Коммуникация"),
                    "description": comm.get("content", ""),
                    "icon": icon_map.get(comm.get("type", "note"), "comment"),
                    "user": comm.get("user_name", "")
                })
        
        # Сортируем по дате
        timeline.sort(key=lambda x: x.get("date") or "", reverse=True)
        
        return {
            "success": True,
            "timeline": timeline
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения timeline клиента: {str(e)}")
        return {"success": False, "message": str(e)}


@router.get("/api/stats/segments", response_class=JSONResponse)
async def get_segments_stats(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получить статистику по сегментам клиентов"""
    try:
        # Проверяем права
        rbac = RBACService(db)
        if not rbac.check_permission(current_user, "clients.view"):
            return {"success": False, "message": "Недостаточно прав"}
        
        # Статистика по сегментам
        segments = db.query(
            Client.segment,
            func.count(Client.id).label("count"),
            func.sum(Client.total_revenue).label("total_revenue"),
            func.avg(Client.average_check).label("avg_check")
        ).group_by(Client.segment).all()
        
        segments_data = []
        for segment, count, revenue, avg_check in segments:
            segments_data.append({
                "segment": segment or "Не указан",
                "count": count,
                "total_revenue": float(revenue) if revenue else 0,
                "average_check": float(avg_check) if avg_check else 0
            })
        
        # Статистика по типам
        types = db.query(
            Client.type,
            func.count(Client.id).label("count")
        ).group_by(Client.type).all()
        
        types_data = []
        for client_type, count in types:
            types_data.append({
                "type": client_type.value if client_type else "Не указан",
                "count": count
            })
        
        # Статистика по статусам
        statuses = db.query(
            Client.status,
            func.count(Client.id).label("count")
        ).group_by(Client.status).all()
        
        statuses_data = []
        for status, count in statuses:
            statuses_data.append({
                "status": status.value if status else "Не указан",
                "count": count
            })
        
        return {
            "success": True,
            "segments": segments_data,
            "types": types_data,
            "statuses": statuses_data
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики по сегментам: {str(e)}")
        return {"success": False, "message": str(e)}