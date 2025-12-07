"""
WildBerries Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# ============ Product Schemas ============

class WBProductBase(BaseModel):
    """Базовая схема товара WB"""
    wb_article: str = Field(..., description="Артикул WB")
    nm_id: Optional[int] = Field(None, description="Номенклатура ID")
    name: str = Field(..., description="Название товара")
    brand: Optional[str] = Field(None, description="Бренд")
    category: Optional[str] = Field(None, description="Категория")
    price: float = Field(..., gt=0, description="Цена")
    discount_price: Optional[float] = Field(None, description="Цена со скидкой")
    stock_quantity: int = Field(0, ge=0, description="Остаток")
    reserved_quantity: int = Field(0, ge=0, description="Зарезервировано")
    is_active: bool = Field(True, description="Активен")


class WBProductCreate(WBProductBase):
    """Создание товара WB"""
    data: dict = Field(default_factory=dict, description="Дополнительные данные")


class WBProductUpdate(BaseModel):
    """Обновление товара WB"""
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    discount_price: Optional[float] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    reserved_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    data: Optional[dict] = None


class WBProductResponse(WBProductBase):
    """Ответ с товаром WB"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_sync: datetime
    created_at: datetime
    updated_at: datetime


# ============ Order Schemas ============

class WBOrderBase(BaseModel):
    """Базовая схема заказа WB"""
    wb_order_id: str = Field(..., description="ID заказа WB")
    order_number: str = Field(..., description="Номер заказа")
    status: str = Field(..., description="Статус заказа")
    quantity: int = Field(..., gt=0, description="Количество")
    total_price: float = Field(..., gt=0, description="Общая сумма")
    order_date: datetime = Field(..., description="Дата заказа")
    delivery_date: Optional[datetime] = Field(None, description="Дата доставки")


class WBOrderCreate(WBOrderBase):
    """Создание заказа WB"""
    product_id: Optional[int] = Field(None, description="ID товара")
    data: dict = Field(default_factory=dict, description="Дополнительные данные")


class WBOrderUpdate(BaseModel):
    """Обновление заказа WB"""
    status: Optional[str] = None
    delivery_date: Optional[datetime] = None
    data: Optional[dict] = None


class WBOrderResponse(WBOrderBase):
    """Ответ с заказом WB"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: Optional[int]
    created_at: datetime
    updated_at: datetime


# ============ Webhook Schemas ============

class WBWebhookPayload(BaseModel):
    """Payload вебхука WB"""
    event_type: str = Field(..., description="Тип события")
    data: dict = Field(..., description="Данные события")
    timestamp: Optional[str] = Field(None, description="Временная метка")


class WBWebhookLogResponse(BaseModel):
    """Ответ лога вебхука"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    payload: dict
    processed: bool
    processed_at: Optional[datetime]
    error: Optional[str]
    created_at: datetime


# ============ Sync Schemas ============

class WBSyncRequest(BaseModel):
    """Запрос синхронизации"""
    sync_type: str = Field(..., description="Тип синхронизации: products, orders, stock")
    force: bool = Field(False, description="Принудительная синхронизация")


class WBSyncStatus(BaseModel):
    """Статус синхронизации"""
    sync_type: str
    status: str = Field(..., description="pending, running, completed, failed")
    items_processed: int = Field(0, ge=0)
    items_created: int = Field(0, ge=0)
    items_updated: int = Field(0, ge=0)
    items_failed: int = Field(0, ge=0)
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class WBSyncLogResponse(WBSyncStatus):
    """Ответ лога синхронизации"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    details: dict


# ============ API Response Schemas ============

class WBAPIProduct(BaseModel):
    """Товар из WB API"""
    nmId: int
    vendorCode: str
    title: str
    brand: Optional[str] = None
    price: float
    discount: Optional[float] = None
    quantity: int


class WBAPIOrder(BaseModel):
    """Заказ из WB API"""
    orderId: str
    orderUid: str
    article: str
    status: str
    quantity: int
    totalPrice: float
    createdAt: str
    warehouseName: Optional[str] = None


class WBStockUpdate(BaseModel):
    """Обновление остатков"""
    wb_article: str
    stock_quantity: int = Field(..., ge=0)
    reserved_quantity: int = Field(0, ge=0)


# ============ Statistics Schemas ============

class WBStatistics(BaseModel):
    """Статистика WB интеграции"""
    total_products: int = Field(0, ge=0, description="Всего товаров")
    active_products: int = Field(0, ge=0, description="Активных товаров")
    total_orders: int = Field(0, ge=0, description="Всего заказов")
    orders_today: int = Field(0, ge=0, description="Заказов сегодня")
    pending_orders: int = Field(0, ge=0, description="Заказов в обработке")
    completed_orders: int = Field(0, ge=0, description="Завершенных заказов")
    total_revenue: float = Field(0, ge=0, description="Общая выручка")
    last_sync: Optional[datetime] = Field(None, description="Последняя синхронизация")
