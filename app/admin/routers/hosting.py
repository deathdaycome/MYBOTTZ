"""
Роутер для управления Timeweb хостингом
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, or_, select
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from ...core.database import get_db
from ...database.models import AdminUser, HostingServer, HostingPayment, Project, User
from ...database.crm_models import Client
from ..middleware.auth import get_current_admin_user
from ..navigation import get_navigation_items

router = APIRouter(prefix="/hosting", tags=["hosting"])
templates = Jinja2Templates(directory="app/admin/templates")


# === Pydantic Models ===

class ServerCreate(BaseModel):
    project_id: Optional[int] = None
    client_id: Optional[int] = None
    client_name: str
    client_company: Optional[str] = None
    client_telegram_id: Optional[int] = None
    server_name: str
    configuration: Optional[str] = None
    ip_address: Optional[str] = None
    cost_price: float
    client_price: float
    service_fee: float = 0
    start_date: datetime
    next_payment_date: datetime
    payment_period: str = "monthly"
    notes: Optional[str] = None


class PaymentCreate(BaseModel):
    server_id: int
    amount: float
    payment_date: Optional[datetime] = None
    expected_date: datetime
    period_start: datetime
    period_end: datetime
    status: str = "pending"
    payment_method: Optional[str] = None
    notes: Optional[str] = None


# === HTML Pages ===

@router.get("/", response_class=HTMLResponse)
async def hosting_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Страница управления хостингом"""
    try:
        return templates.TemplateResponse(
            "hosting.html",
            {
                "request": request,
                "user": current_user,
                "navigation_items": get_navigation_items("/admin/hosting")
            }
        )
    except Exception as e:
        return f"Ошибка загрузки страницы хостинга: {e}"


# === API Endpoints ===

@router.get("/api/stats")
async def get_hosting_stats(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить статистику по хостингу"""
    try:
        now = datetime.utcnow()

        # Общее количество активных серверов
        result = await db.execute(
            select(func.count()).select_from(HostingServer).where(
                HostingServer.status == "active"
            )
        )
        active_servers = result.scalar()

        # Прибыль за текущий месяц
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Получаем все активные серверы для расчета прибыли
        result = await db.execute(
            select(HostingServer).where(HostingServer.status == "active")
        )
        servers = result.scalars().all()

        total_profit_month = sum([
            (s.client_price + (s.service_fee or 0) - s.cost_price)
            for s in servers
        ])

        # Прибыль за всё время (из платежей)
        result = await db.execute(
            select(HostingPayment).where(HostingPayment.status == "paid")
        )
        all_payments = result.scalars().all()

        total_profit_all_time = 0
        for payment in all_payments:
            result = await db.execute(
                select(HostingServer).where(HostingServer.id == payment.server_id)
            )
            server = result.scalar_one_or_none()
            if server:
                # Прибыль = платеж - себестоимость
                profit = payment.amount - server.cost_price
                total_profit_all_time += profit

        # Просрочки
        result = await db.execute(
            select(func.count()).select_from(HostingServer).where(
                HostingServer.next_payment_date < now,
                HostingServer.status.in_(["active", "overdue"])
            )
        )
        overdue_count = result.scalar()

        overdue_sum = 0
        result = await db.execute(
            select(HostingServer).where(
                HostingServer.next_payment_date < now,
                HostingServer.status.in_(["active", "overdue"])
            )
        )
        overdue_servers = result.scalars().all()

        for server in overdue_servers:
            overdue_sum += server.client_price + (server.service_fee or 0)

        return {
            "success": True,
            "stats": {
                "active_servers": active_servers,
                "profit_month": round(total_profit_month, 2),
                "profit_all_time": round(total_profit_all_time, 2),
                "overdue_count": overdue_count,
                "overdue_sum": round(overdue_sum, 2)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


@router.get("/api/servers")
async def get_servers(
    status: Optional[str] = None,
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить список серверов"""
    try:
        query = select(HostingServer)

        # Фильтр по статусу
        if status:
            query = query.where(HostingServer.status == status)

        # Фильтр по проекту
        if project_id:
            query = query.where(HostingServer.project_id == project_id)

        query = query.order_by(HostingServer.next_payment_date.asc())
        result = await db.execute(query)
        servers = result.scalars().all()

        return {
            "success": True,
            "servers": [server.to_dict() for server in servers],
            "total": len(servers)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения серверов: {str(e)}")


@router.get("/api/server/{server_id}")
async def get_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить информацию о сервере"""
    result = await db.execute(
        select(HostingServer).where(HostingServer.id == server_id)
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(status_code=404, detail="Сервер не найден")

    # Получаем платежи
    result = await db.execute(
        select(HostingPayment).where(
            HostingPayment.server_id == server_id
        ).order_by(HostingPayment.expected_date.desc())
    )
    payments = result.scalars().all()

    return {
        "success": True,
        "server": server.to_dict(),
        "payments": [payment.to_dict() for payment in payments]
    }


@router.post("/api/server")
async def create_server(
    data: ServerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Создать новый сервер"""
    try:
        # Автоматически получаем или создаем client_id на основе имени клиента
        from app.services.client_id_service import client_id_service
        auto_client_id = client_id_service.get_or_create_client_id(
            db,
            data.client_name,
            data.client_telegram_id
        )

        server = HostingServer(
            project_id=data.project_id,
            client_id=auto_client_id,  # Используем автоматически присвоенный ID
            client_name=data.client_name,
            client_company=data.client_company,
            client_telegram_id=data.client_telegram_id,
            server_name=data.server_name,
            configuration=data.configuration,
            ip_address=data.ip_address,
            cost_price=data.cost_price,
            client_price=data.client_price,
            service_fee=data.service_fee,
            start_date=data.start_date,
            next_payment_date=data.next_payment_date,
            payment_period=data.payment_period,
            status="active",
            notes=data.notes
        )

        db.add(server)
        await db.commit()
        await db.refresh(server)

        # Создаем первый платеж (ожидается)
        payment = HostingPayment(
            server_id=server.id,
            amount=data.client_price + data.service_fee,
            expected_date=data.next_payment_date,
            period_start=data.start_date,
            period_end=data.next_payment_date,
            status="pending"
        )
        db.add(payment)
        await db.commit()

        # Обновляем затраты клиента если указан client_id
        if server.client_id:
            from app.services.balance_service import balance_service
            balance_service.update_client_costs(db, server.client_id, server.client_name)

        return {
            "success": True,
            "server": server.to_dict(),
            "message": "Сервер успешно добавлен"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания сервера: {str(e)}")


@router.put("/api/server/{server_id}")
async def update_server(
    server_id: int,
    data: ServerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Обновить информацию о сервере"""
    result = await db.execute(
        select(HostingServer).where(HostingServer.id == server_id)
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(status_code=404, detail="Сервер не найден")

    try:
        # Автоматически получаем или создаем client_id
        # Передаем server_id чтобы сохранить существующий client_id при обновлении
        from app.services.client_id_service import client_id_service
        auto_client_id = client_id_service.get_or_create_client_id(
            db,
            data.client_name,
            data.client_telegram_id,
            server_id=server_id  # ВАЖНО: сохраняем существующий client_id
        )

        server.project_id = data.project_id
        server.client_id = auto_client_id  # Используем автоматически присвоенный ID
        server.client_name = data.client_name
        server.client_company = data.client_company
        server.client_telegram_id = data.client_telegram_id
        server.server_name = data.server_name
        server.configuration = data.configuration
        server.ip_address = data.ip_address
        server.cost_price = data.cost_price
        server.client_price = data.client_price
        server.service_fee = data.service_fee
        server.start_date = data.start_date
        server.next_payment_date = data.next_payment_date
        server.payment_period = data.payment_period
        server.notes = data.notes
        server.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(server)

        # Обновляем затраты клиента если указан client_id
        if server.client_id:
            from app.services.balance_service import balance_service
            balance_service.update_client_costs(db, server.client_id, server.client_name)

        return {
            "success": True,
            "server": server.to_dict(),
            "message": "Сервер успешно обновлен"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка обновления сервера: {str(e)}")


@router.delete("/api/server/{server_id}")
async def delete_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Удалить сервер"""
    result = await db.execute(
        select(HostingServer).where(HostingServer.id == server_id)
    )
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(status_code=404, detail="Сервер не найден")

    try:
        await db.delete(server)
        await db.commit()

        return {
            "success": True,
            "message": "Сервер удален"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка удаления сервера: {str(e)}")


@router.post("/api/payment")
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Зарегистрировать платеж"""
    try:
        payment = HostingPayment(
            server_id=data.server_id,
            amount=data.amount,
            payment_date=data.payment_date or datetime.utcnow(),
            expected_date=data.expected_date,
            period_start=data.period_start,
            period_end=data.period_end,
            status=data.status,
            payment_method=data.payment_method,
            notes=data.notes
        )

        db.add(payment)

        # Обновляем дату следующего платежа у сервера
        if data.status == "paid":
            result = await db.execute(
                select(HostingServer).where(HostingServer.id == data.server_id)
            )
            server = result.scalar_one_or_none()
            if server:
                # Рассчитываем следующий платеж в зависимости от периодичности
                if server.payment_period == "monthly":
                    next_date = data.period_end + timedelta(days=30)
                elif server.payment_period == "quarterly":
                    next_date = data.period_end + timedelta(days=90)
                elif server.payment_period == "yearly":
                    next_date = data.period_end + timedelta(days=365)
                else:
                    next_date = data.period_end + timedelta(days=30)

                server.next_payment_date = next_date
                server.status = "active"

        await db.commit()
        await db.refresh(payment)

        return {
            "success": True,
            "payment": payment.to_dict(),
            "message": "Платеж зарегистрирован"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка регистрации платежа: {str(e)}")


@router.get("/api/calendar")
async def get_payment_calendar(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить данные для календаря платежей"""
    try:
        now = datetime.utcnow()
        target_month = month or now.month
        target_year = year or now.year

        # Диапазон дат для выбранного месяца
        month_start = datetime(target_year, target_month, 1)
        if target_month == 12:
            month_end = datetime(target_year + 1, 1, 1)
        else:
            month_end = datetime(target_year, target_month + 1, 1)

        # Получаем платежи за месяц
        result = await db.execute(
            select(HostingPayment).where(
                and_(
                    HostingPayment.expected_date >= month_start,
                    HostingPayment.expected_date < month_end
                )
            )
        )
        payments = result.scalars().all()

        # Получаем информацию о серверах
        calendar_data = []
        for payment in payments:
            result = await db.execute(
                select(HostingServer).where(HostingServer.id == payment.server_id)
            )
            server = result.scalar_one_or_none()
            if server:
                # Определяем цвет
                if payment.status == "paid":
                    color = "green"
                elif payment.expected_date < now and payment.status != "paid":
                    color = "red"
                elif (payment.expected_date - now).days <= 3:
                    color = "yellow"
                else:
                    color = "blue"

                calendar_data.append({
                    "id": payment.id,
                    "title": f"{server.client_name} - {server.server_name}",
                    "date": payment.expected_date.strftime("%Y-%m-%d"),
                    "amount": payment.amount,
                    "status": payment.status,
                    "color": color,
                    "server_id": server.id
                })

        return {
            "success": True,
            "calendar": calendar_data,
            "month": target_month,
            "year": target_year
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения календаря: {str(e)}")


@router.get("/api/clients/search")
async def search_clients(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Поиск клиентов для автодополнения"""
    try:
        result = await db.execute(
            select(Client).where(
                or_(
                    Client.name.ilike(f"%{q}%"),
                    Client.company.ilike(f"%{q}%")
                )
            ).limit(10)
        )
        clients = result.scalars().all()

        return {
            "success": True,
            "clients": [{
                "id": client.id,
                "name": client.name,
                "company": client.company,
                "telegram_id": client.telegram_id
            } for client in clients]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска клиентов: {str(e)}")


@router.get("/api/projects")
async def get_active_projects(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить список активных проектов для выбора"""
    try:
        result = await db.execute(
            select(Project).where(
                Project.status.in_(["in_progress", "new", "review", "accepted", "testing"])
            ).order_by(Project.created_at.desc())
        )
        projects = result.scalars().all()

        return {
            "success": True,
            "projects": [{
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "user_id": p.user_id,
                "client_telegram_id": p.client_telegram_id
            } for p in projects]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения проектов: {str(e)}")


@router.get("/api/project/{project_id}")
async def get_project_data(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить данные проекта для автозаполнения формы сервера"""
    try:
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")

        # Получаем данные клиента (пользователя) из проекта
        result = await db.execute(
            select(User).where(User.id == project.user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return {
                "success": False,
                "error": "Клиент проекта не найден"
            }

        # Формируем имя клиента из first_name и last_name
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        client_name = full_name or user.username or f"Клиент #{user.telegram_id}"

        return {
            "success": True,
            "project": {
                "id": project.id,
                "title": project.title,
                "user_id": project.user_id,
                "client_name": client_name,
                "client_telegram_id": project.client_telegram_id or user.telegram_id,
                "estimated_cost": project.estimated_cost
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных проекта: {str(e)}")


# === Timeweb Cloud Integration Endpoints ===

@router.get("/api/timeweb/status")
async def get_timeweb_status(
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Проверить статус интеграции с Timeweb Cloud"""
    try:
        from ...services.timeweb_service import timeweb_service

        is_configured = timeweb_service.is_configured()

        return {
            "success": True,
            "configured": is_configured,
            "message": "Timeweb API token configured" if is_configured else "Timeweb API token not configured"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка проверки статуса Timeweb: {str(e)}")


@router.get("/api/timeweb/servers")
async def get_timeweb_servers(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить список серверов из Timeweb Cloud"""
    try:
        from ...services.timeweb_service import timeweb_service
        import json

        if not timeweb_service.is_configured():
            raise HTTPException(
                status_code=400,
                detail="Timeweb API token не настроен. Добавьте TIMEWEB_API_TOKEN в .env"
            )

        # Получаем серверы из Timeweb
        timeweb_servers = await timeweb_service.get_servers()

        # Получаем существующие серверы в CRM
        result = await db.execute(
            select(HostingServer).where(HostingServer.timeweb_id.isnot(None))
        )
        existing_servers = result.scalars().all()

        existing_ids = {server.timeweb_id for server in existing_servers}

        # Обрабатываем данные серверов
        servers_data = []
        for tw_server in timeweb_servers:
            server_id = tw_server.get("id")
            is_imported = server_id in existing_ids

            # Парсим данные
            configuration = timeweb_service.parse_server_configuration(tw_server)
            ip_address = timeweb_service.get_primary_ip(tw_server)

            servers_data.append({
                "timeweb_id": server_id,
                "name": tw_server.get("name"),
                "status": tw_server.get("status"),
                "configuration": configuration,
                "ip_address": ip_address,
                "preset_id": tw_server.get("preset_id"),
                "created_at": tw_server.get("created_at"),
                "is_imported": is_imported,
                "raw_data": json.dumps(tw_server, ensure_ascii=False)
            })

        return {
            "success": True,
            "servers": servers_data,
            "total": len(servers_data),
            "imported_count": len(existing_ids)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения серверов из Timeweb: {str(e)}")


@router.post("/api/timeweb/import")
async def import_timeweb_servers(
    server_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    Импортировать выбранные серверы из Timeweb Cloud

    Тело запроса:
    {
        "server_ids": [123456, 789012]
    }
    """
    try:
        from ...services.timeweb_service import timeweb_service
        import json

        if not timeweb_service.is_configured():
            raise HTTPException(
                status_code=400,
                detail="Timeweb API token не настроен"
            )

        imported = []
        errors = []

        for server_id in server_ids:
            try:
                # Проверяем, не импортирован ли уже
                result = await db.execute(
                    select(HostingServer).where(HostingServer.timeweb_id == server_id)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    errors.append({
                        "server_id": server_id,
                        "error": "Сервер уже импортирован"
                    })
                    continue

                # Получаем детали сервера из Timeweb
                tw_server = await timeweb_service.get_server_details(server_id)

                if not tw_server:
                    errors.append({
                        "server_id": server_id,
                        "error": "Сервер не найден в Timeweb"
                    })
                    continue

                # Получаем цену сервера (автоматически определяет preset или configurator)
                cost_price = await timeweb_service.get_server_price(tw_server) or 0

                # Парсим конфигурацию
                configuration = timeweb_service.parse_server_configuration(tw_server)
                ip_address = timeweb_service.get_primary_ip(tw_server)

                # Создаем сервер в CRM
                # Пользователь должен будет вручную привязать к проекту и указать цену клиента
                server = HostingServer(
                    server_name=tw_server.get("name", f"Server-{server_id}"),
                    configuration=configuration,
                    ip_address=ip_address,
                    cost_price=cost_price or 0,
                    client_price=0,  # Нужно установить вручную
                    service_fee=0,
                    start_date=datetime.utcnow(),
                    next_payment_date=datetime.utcnow(),
                    payment_period="monthly",
                    status="active" if tw_server.get("status") == "on" else "suspended",
                    client_name="Не указан",  # Нужно установить вручную
                    # Timeweb данные
                    timeweb_id=server_id,
                    timeweb_status=tw_server.get("status"),
                    timeweb_preset_id=preset_id,
                    timeweb_data=json.dumps(tw_server, ensure_ascii=False),
                    auto_sync=False,
                    last_sync_at=datetime.utcnow(),
                    notes=f"Импортирован из Timeweb Cloud {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
                )

                db.add(server)
                db.commit()
                db.refresh(server)

                imported.append({
                    "server_id": server_id,
                    "crm_id": server.id,
                    "name": server.server_name
                })

            except Exception as e:
                db.rollback()
                errors.append({
                    "server_id": server_id,
                    "error": str(e)
                })

        return {
            "success": True,
            "imported": imported,
            "errors": errors,
            "imported_count": len(imported),
            "error_count": len(errors)
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка импорта серверов: {str(e)}")


@router.post("/api/server/{server_id}/sync")
async def sync_server_with_timeweb(
    server_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Синхронизировать сервер с Timeweb Cloud (обновить данные)"""
    try:
        from ...services.timeweb_service import timeweb_service
        import json

        result = await db.execute(
            select(HostingServer).where(HostingServer.id == server_id)
        )
        server = result.scalar_one_or_none()

        if not server:
            raise HTTPException(status_code=404, detail="Сервер не найден")

        if not server.timeweb_id:
            raise HTTPException(status_code=400, detail="Сервер не связан с Timeweb Cloud")

        if not timeweb_service.is_configured():
            raise HTTPException(status_code=400, detail="Timeweb API token не настроен")

        # Получаем актуальные данные из Timeweb
        tw_server = await timeweb_service.get_server_details(server.timeweb_id)

        if not tw_server:
            raise HTTPException(status_code=404, detail="Сервер не найден в Timeweb Cloud")

        # Обновляем данные
        server.configuration = timeweb_service.parse_server_configuration(tw_server)
        server.ip_address = timeweb_service.get_primary_ip(tw_server)
        server.timeweb_status = tw_server.get("status")
        server.timeweb_preset_id = tw_server.get("preset_id")
        server.timeweb_data = json.dumps(tw_server, ensure_ascii=False)
        server.last_sync_at = datetime.utcnow()

        # Обновляем статус если изменился
        if tw_server.get("status") == "off":
            server.status = "suspended"
        elif tw_server.get("status") == "on" and server.status == "suspended":
            server.status = "active"

        # Обновляем себестоимость (проверяем и preset, и configurator)
        new_cost = await timeweb_service.get_server_price(tw_server)
        if new_cost and new_cost != server.cost_price:
            server.notes = (server.notes or "") + f"\n\nЦена изменена: {server.cost_price} → {new_cost} (синхронизация {datetime.utcnow().strftime('%Y-%m-%d %H:%M')})"
            server.cost_price = new_cost

        server.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(server)

        return {
            "success": True,
            "server": server.to_dict(),
            "message": "Сервер успешно синхронизирован с Timeweb Cloud"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации: {str(e)}")


@router.post("/api/timeweb/sync-all")
async def sync_all_timeweb_servers(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    Автоматическая синхронизация ВСЕХ серверов из Timeweb Cloud

    - Создает новые серверы, которых нет в CRM
    - Обновляет существующие серверы (конфигурация, IP, статус, цена)
    - Не требует ручного выбора серверов
    """
    try:
        from ...services.timeweb_service import timeweb_service
        import json

        if not timeweb_service.is_configured():
            raise HTTPException(
                status_code=400,
                detail="Timeweb API token не настроен"
            )

        # Получаем все серверы из Timeweb
        tw_servers = await timeweb_service.get_servers()

        if not tw_servers:
            return {
                "success": True,
                "message": "Нет серверов в Timeweb Cloud",
                "created": [],
                "updated": [],
                "errors": [],
                "created_count": 0,
                "updated_count": 0,
                "error_count": 0
            }

        created = []
        updated = []
        errors = []

        for tw_server in tw_servers:
            try:
                server_id = tw_server.get("id")

                if not server_id:
                    continue

                # Проверяем, существует ли сервер в CRM
                result = await db.execute(
                    select(HostingServer).where(HostingServer.timeweb_id == server_id)
                )
                existing = result.scalar_one_or_none()

                # Парсим данные из Timeweb
                configuration = timeweb_service.parse_server_configuration(tw_server)
                ip_address = timeweb_service.get_primary_ip(tw_server)
                preset_id = tw_server.get("preset_id")
                configurator_id = tw_server.get("configurator_id")
                cost_price = await timeweb_service.get_server_price(tw_server) or 0

                if existing:
                    # Обновляем существующий сервер
                    existing.server_name = tw_server.get("name", existing.server_name)
                    existing.configuration = configuration
                    existing.ip_address = ip_address
                    existing.timeweb_status = tw_server.get("status")
                    existing.timeweb_preset_id = preset_id
                    existing.timeweb_data = json.dumps(tw_server, ensure_ascii=False)
                    existing.last_sync_at = datetime.utcnow()
                    existing.updated_at = datetime.utcnow()

                    # Обновляем статус
                    if tw_server.get("status") == "off":
                        existing.status = "suspended"
                    elif tw_server.get("status") == "on" and existing.status == "suspended":
                        existing.status = "active"

                    # Обновляем себестоимость если изменилась
                    if cost_price and cost_price != existing.cost_price:
                        existing.notes = (existing.notes or "") + f"\n\nЦена обновлена: {existing.cost_price} → {cost_price} (автосинхронизация {datetime.utcnow().strftime('%Y-%m-%d %H:%M')})"
                        existing.cost_price = cost_price

                    db.commit()
                    db.refresh(existing)

                    updated.append({
                        "timeweb_id": server_id,
                        "crm_id": existing.id,
                        "name": existing.server_name
                    })

                else:
                    # Создаем новый сервер
                    # Автоматически: имя, конфигурация, IP, себестоимость
                    # Вручную (пустые): цена клиента, имя клиента, проект, дата оплаты

                    # Автоматически присваиваем client_id на основе имени
                    from app.services.client_id_service import client_id_service
                    auto_client_id = client_id_service.get_or_create_client_id(
                        db,
                        "Не указан",
                        None
                    )

                    server = HostingServer(
                        server_name=tw_server.get("name", f"Server-{server_id}"),
                        configuration=configuration,
                        ip_address=ip_address,
                        cost_price=cost_price or 0,
                        client_price=0,  # Устанавливается вручную
                        service_fee=0,
                        start_date=datetime.utcnow(),
                        next_payment_date=datetime.utcnow(),
                        payment_period="monthly",
                        status="active" if tw_server.get("status") == "on" else "suspended",
                        client_name="Не указан",  # Устанавливается вручную
                        client_id=auto_client_id,  # Автоматически присвоенный ID
                        # Timeweb данные
                        timeweb_id=server_id,
                        timeweb_status=tw_server.get("status"),
                        timeweb_preset_id=preset_id,
                        timeweb_data=json.dumps(tw_server, ensure_ascii=False),
                        auto_sync=True,  # Включаем автосинхронизацию для новых серверов
                        last_sync_at=datetime.utcnow(),
                        notes=f"Автоматически импортирован из Timeweb Cloud {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
                    )

                    db.add(server)
                    db.commit()
                    db.refresh(server)

                    created.append({
                        "timeweb_id": server_id,
                        "crm_id": server.id,
                        "name": server.server_name
                    })

            except Exception as e:
                db.rollback()
                errors.append({
                    "server_id": tw_server.get("id"),
                    "server_name": tw_server.get("name"),
                    "error": str(e)
                })

        return {
            "success": True,
            "message": f"Синхронизация завершена: создано {len(created)}, обновлено {len(updated)}",
            "created": created,
            "updated": updated,
            "errors": errors,
            "created_count": len(created),
            "updated_count": len(updated),
            "error_count": len(errors),
            "total_processed": len(created) + len(updated)
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка автоматической синхронизации: {str(e)}")


# === Balance Management Endpoints ===

@router.get("/api/balance/low")
async def get_low_balance_clients(
    days_threshold: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить клиентов с низким балансом"""
    try:
        from ...services.balance_service import balance_service

        clients = balance_service.get_clients_with_low_balance(db, days_threshold)

        return {
            "success": True,
            "clients": [c.to_dict() for c in clients],
            "total": len(clients),
            "threshold_days": days_threshold
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения клиентов: {str(e)}")


@router.get("/api/balance/summary")
async def get_balance_summary(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить общую статистику по балансам"""
    try:
        from ...services.balance_service import balance_service

        summary = balance_service.get_balance_summary(db)

        return {
            "success": True,
            **summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


@router.get("/api/balance/{client_id}")
async def get_client_balance(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить баланс клиента"""
    try:
        from ...services.balance_service import balance_service

        # Получаем имя клиента из серверов
        result = await db.execute(
            select(HostingServer).where(
                HostingServer.client_id == client_id
            )
        )
        server = result.scalar_one_or_none()

        if not server:
            raise HTTPException(status_code=404, detail="Клиент не найден")

        # Обновляем стоимость серверов перед возвратом
        balance = balance_service.update_client_costs(
            db, client_id, server.client_name
        )

        return {
            "success": True,
            "balance": balance.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения баланса: {str(e)}")


@router.post("/api/balance/{client_id}/add")
async def add_client_balance(
    client_id: int,
    amount: float,
    description: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """
    Пополнить баланс клиента

    Тело запроса:
    {
        "amount": 4000.0,
        "description": "Пополнение баланса"
    }
    """
    try:
        from ...services.balance_service import balance_service

        if amount <= 0:
            raise HTTPException(status_code=400, detail="Сумма должна быть положительной")

        # Получаем данные клиента
        result = await db.execute(
            select(HostingServer).where(HostingServer.client_id == client_id)
        )
        server = result.scalar_one_or_none()

        if not server:
            raise HTTPException(status_code=404, detail="Клиент не найден")

        # Пополняем баланс
        balance, transaction = balance_service.add_balance(
            db=db,
            client_id=client_id,
            client_name=server.client_name,
            amount=amount,
            description=description,
            created_by=current_user.get("username"),
            client_telegram_id=server.client_telegram_id
        )

        # Обновляем стоимость серверов
        balance = balance_service.update_client_costs(
            db, client_id, server.client_name
        )

        return {
            "success": True,
            "message": f"Баланс пополнен на {amount}₽",
            "balance": balance.to_dict(),
            "transaction": transaction.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка пополнения баланса: {str(e)}")


@router.get("/api/balance/{client_id}/transactions")
async def get_client_transactions(
    client_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user),
):
    """Получить историю транзакций клиента"""
    try:
        from ...services.balance_service import balance_service

        transactions = balance_service.get_transactions(db, client_id, limit)

        return {
            "success": True,
            "transactions": [t.to_dict() for t in transactions],
            "total": len(transactions)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения транзакций: {str(e)}")
