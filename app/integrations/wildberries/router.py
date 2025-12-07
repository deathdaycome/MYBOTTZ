"""
WildBerries API Router
"""

from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from .schemas import (
    WBProductResponse, WBProductCreate, WBProductUpdate,
    WBOrderResponse, WBSyncRequest, WBSyncStatus, WBStatistics
)
from .service import WildberriesService
from .webhooks import process_wb_webhook

router = APIRouter(prefix="/wildberries", tags=["WildBerries Integration"])


# ============ Products ============

@router.get("/products", response_model=List[WBProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить список товаров WB"""
    service = WildberriesService(db)
    return await service.get_products(skip=skip, limit=limit)


@router.get("/products/{product_id}", response_model=WBProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Получить товар по ID"""
    service = WildberriesService(db)
    return await service.get_product(product_id)


@router.post("/products", response_model=WBProductResponse, status_code=201)
async def create_product(
    product: WBProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать товар"""
    service = WildberriesService(db)
    return await service.create_product(product)


@router.put("/products/{product_id}", response_model=WBProductResponse)
async def update_product(
    product_id: int,
    product: WBProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить товар"""
    service = WildberriesService(db)
    return await service.update_product(product_id, product)


# ============ Orders ============

@router.get("/orders", response_model=List[WBOrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Получить список заказов WB"""
    service = WildberriesService(db)
    return await service.get_orders(skip=skip, limit=limit, status=status)


@router.get("/orders/{order_id}", response_model=WBOrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Получить заказ по ID"""
    service = WildberriesService(db)
    return await service.get_order(order_id)


# ============ Sync ============

@router.post("/sync/products", response_model=WBSyncStatus)
async def sync_products(
    sync_request: WBSyncRequest,
    db: AsyncSession = Depends(get_db)
):
    """Синхронизация товаров с WB"""
    service = WildberriesService(db)
    return await service.sync_products(force=sync_request.force)


@router.post("/sync/orders", response_model=WBSyncStatus)
async def sync_orders(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Синхронизация заказов с WB"""
    service = WildberriesService(db)
    return await service.sync_orders(days=days)


# ============ Webhooks ============

@router.post("/webhooks")
async def receive_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Прием вебхуков от WildBerries"""
    return await process_wb_webhook(request, db)


# ============ Statistics ============

@router.get("/statistics", response_model=WBStatistics)
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """Получить статистику WB интеграции"""
    service = WildberriesService(db)
    return await service.get_statistics()
