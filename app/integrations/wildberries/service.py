"""
WildBerries Service Layer - Business Logic
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from .models import WBProduct, WBOrder, WBSyncLog
from .schemas import (
    WBProductCreate, WBProductUpdate, WBProductResponse,
    WBOrderCreate, WBOrderUpdate, WBOrderResponse,
    WBSyncRequest, WBSyncStatus, WBStatistics
)
from .client import WildberriesClient, get_wb_client


class WildberriesService:
    """Сервис для работы с WildBerries"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============ Products ============

    async def get_products(self, skip: int = 0, limit: int = 100) -> List[WBProductResponse]:
        """Получить список товаров"""
        result = await self.db.execute(
            select(WBProduct)
            .where(WBProduct.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        products = result.scalars().all()
        return [WBProductResponse.model_validate(p) for p in products]

    async def get_product(self, product_id: int) -> Optional[WBProductResponse]:
        """Получить товар по ID"""
        result = await self.db.execute(
            select(WBProduct).where(WBProduct.id == product_id)
        )
        product = result.scalar_one_or_none()
        return WBProductResponse.model_validate(product) if product else None

    async def create_product(self, product_data: WBProductCreate) -> WBProductResponse:
        """Создать товар"""
        product = WBProduct(**product_data.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return WBProductResponse.model_validate(product)

    async def update_product(self, product_id: int, product_data: WBProductUpdate) -> Optional[WBProductResponse]:
        """Обновить товар"""
        result = await self.db.execute(
            select(WBProduct).where(WBProduct.id == product_id)
        )
        product = result.scalar_one_or_none()

        if not product:
            return None

        for field, value in product_data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        await self.db.commit()
        await self.db.refresh(product)
        return WBProductResponse.model_validate(product)

    # ============ Orders ============

    async def get_orders(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[WBOrderResponse]:
        """Получить список заказов"""
        query = select(WBOrder)

        if status:
            query = query.where(WBOrder.status == status)

        query = query.offset(skip).limit(limit).order_by(WBOrder.created_at.desc())

        result = await self.db.execute(query)
        orders = result.scalars().all()
        return [WBOrderResponse.model_validate(o) for o in orders]

    async def get_order(self, order_id: int) -> Optional[WBOrderResponse]:
        """Получить заказ по ID"""
        result = await self.db.execute(
            select(WBOrder).where(WBOrder.id == order_id)
        )
        order = result.scalar_one_or_none()
        return WBOrderResponse.model_validate(order) if order else None

    # ============ Sync ============

    async def sync_products(self, force: bool = False) -> WBSyncStatus:
        """Синхронизация товаров с WB"""
        sync_log = WBSyncLog(
            sync_type="products",
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(sync_log)
        await self.db.commit()

        try:
            async with get_wb_client() as wb_client:
                wb_products = await wb_client.get_products()

                for wb_prod in wb_products:
                    # Поиск существующего товара
                    article = wb_prod.get("vendorCode")
                    result = await self.db.execute(
                        select(WBProduct).where(WBProduct.wb_article == article)
                    )
                    existing = result.scalar_one_or_none()

                    if existing:
                        # Обновление
                        existing.name = wb_prod.get("title", existing.name)
                        existing.stock_quantity = wb_prod.get("quantity", 0)
                        existing.last_sync = datetime.utcnow()
                        sync_log.items_updated += 1
                    else:
                        # Создание
                        new_product = WBProduct(
                            wb_article=article,
                            nm_id=wb_prod.get("nmId"),
                            name=wb_prod.get("title", ""),
                            brand=wb_prod.get("brand"),
                            price=wb_prod.get("price", 0),
                            stock_quantity=wb_prod.get("quantity", 0)
                        )
                        self.db.add(new_product)
                        sync_log.items_created += 1

                    sync_log.items_processed += 1

                await self.db.commit()

            sync_log.status = "completed"
            sync_log.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Product sync failed: {e}", exc_info=True)
            sync_log.status = "failed"
            sync_log.error = str(e)
            sync_log.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(sync_log)

        return WBSyncStatus(
            sync_type=sync_log.sync_type,
            status=sync_log.status,
            items_processed=sync_log.items_processed,
            items_created=sync_log.items_created,
            items_updated=sync_log.items_updated,
            items_failed=sync_log.items_failed,
            started_at=sync_log.started_at,
            completed_at=sync_log.completed_at,
            error=sync_log.error
        )

    async def sync_orders(self, days: int = 7) -> WBSyncStatus:
        """Синхронизация заказов с WB"""
        sync_log = WBSyncLog(
            sync_type="orders",
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(sync_log)
        await self.db.commit()

        try:
            async with get_wb_client() as wb_client:
                date_from = datetime.utcnow() - timedelta(days=days)
                wb_orders = await wb_client.get_orders(date_from=date_from)

                for wb_order in wb_orders:
                    order_id = wb_order.get("orderId")
                    result = await self.db.execute(
                        select(WBOrder).where(WBOrder.wb_order_id == order_id)
                    )
                    existing = result.scalar_one_or_none()

                    if existing:
                        existing.status = wb_order.get("status", existing.status)
                        sync_log.items_updated += 1
                    else:
                        new_order = WBOrder(
                            wb_order_id=order_id,
                            order_number=wb_order.get("orderUid", ""),
                            status=wb_order.get("status", ""),
                            quantity=wb_order.get("quantity", 1),
                            total_price=wb_order.get("totalPrice", 0),
                            order_date=datetime.fromisoformat(wb_order.get("createdAt"))
                        )
                        self.db.add(new_order)
                        sync_log.items_created += 1

                    sync_log.items_processed += 1

                await self.db.commit()

            sync_log.status = "completed"
            sync_log.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Order sync failed: {e}", exc_info=True)
            sync_log.status = "failed"
            sync_log.error = str(e)
            sync_log.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(sync_log)

        return WBSyncStatus(
            sync_type=sync_log.sync_type,
            status=sync_log.status,
            items_processed=sync_log.items_processed,
            items_created=sync_log.items_created,
            items_updated=sync_log.items_updated,
            items_failed=sync_log.items_failed,
            started_at=sync_log.started_at,
            completed_at=sync_log.completed_at,
            error=sync_log.error
        )

    # ============ Statistics ============

    async def get_statistics(self) -> WBStatistics:
        """Получить статистику WB интеграции"""
        # Товары
        total_products_result = await self.db.execute(select(func.count(WBProduct.id)))
        total_products = total_products_result.scalar() or 0

        active_products_result = await self.db.execute(
            select(func.count(WBProduct.id)).where(WBProduct.is_active == True)
        )
        active_products = active_products_result.scalar() or 0

        # Заказы
        total_orders_result = await self.db.execute(select(func.count(WBOrder.id)))
        total_orders = total_orders_result.scalar() or 0

        # Заказы сегодня
        today = datetime.utcnow().date()
        orders_today_result = await self.db.execute(
            select(func.count(WBOrder.id)).where(func.date(WBOrder.order_date) == today)
        )
        orders_today = orders_today_result.scalar() or 0

        # Выручка
        revenue_result = await self.db.execute(
            select(func.sum(WBOrder.total_price))
        )
        total_revenue = revenue_result.scalar() or 0.0

        # Последняя синхронизация
        last_sync_result = await self.db.execute(
            select(WBProduct.last_sync)
            .order_by(WBProduct.last_sync.desc())
            .limit(1)
        )
        last_sync = last_sync_result.scalar_one_or_none()

        return WBStatistics(
            total_products=total_products,
            active_products=active_products,
            total_orders=total_orders,
            orders_today=orders_today,
            pending_orders=0,  # TODO
            completed_orders=0,  # TODO
            total_revenue=float(total_revenue),
            last_sync=last_sync
        )
