"""
WildBerries Database Models
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WBProduct(Base):
    """WildBerries товар"""
    __tablename__ = "wb_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wb_article: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="Артикул WB")
    nm_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, comment="Номенклатура ID")

    # Основная информация
    name: Mapped[str] = mapped_column(String(500), comment="Название товара")
    brand: Mapped[Optional[str]] = mapped_column(String(200), comment="Бренд")
    category: Mapped[Optional[str]] = mapped_column(String(200), comment="Категория")

    # Цены
    price: Mapped[float] = mapped_column(Float, comment="Цена")
    discount_price: Mapped[Optional[float]] = mapped_column(Float, comment="Цена со скидкой")

    # Остатки
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, comment="Остаток на складе")
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, comment="Зарезервировано")

    # Метаданные
    data: Mapped[dict] = mapped_column(JSON, default=dict, comment="Дополнительные данные")

    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="Активен")
    last_sync: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="Последняя синхронизация")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders: Mapped[list["WBOrder"]] = relationship("WBOrder", back_populates="product")


class WBOrder(Base):
    """WildBerries заказ"""
    __tablename__ = "wb_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wb_order_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="ID заказа WB")

    # Связь с товаром
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("wb_products.id"))
    product: Mapped[Optional["WBProduct"]] = relationship("WBProduct", back_populates="orders")

    # Информация о заказе
    order_number: Mapped[str] = mapped_column(String(100), comment="Номер заказа")
    status: Mapped[str] = mapped_column(String(50), index=True, comment="Статус заказа")

    # Количество и суммы
    quantity: Mapped[int] = mapped_column(Integer, comment="Количество")
    total_price: Mapped[float] = mapped_column(Float, comment="Общая сумма")

    # Даты
    order_date: Mapped[datetime] = mapped_column(DateTime, comment="Дата заказа")
    delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="Дата доставки")

    # Метаданные
    data: Mapped[dict] = mapped_column(JSON, default=dict, comment="Дополнительные данные")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WBWebhookLog(Base):
    """Лог вебхуков WildBerries"""
    __tablename__ = "wb_webhook_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Информация о вебхуке
    event_type: Mapped[str] = mapped_column(String(100), index=True, comment="Тип события")
    payload: Mapped[dict] = mapped_column(JSON, comment="Payload вебхука")

    # Обработка
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, comment="Обработан")
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="Время обработки")
    error: Mapped[Optional[str]] = mapped_column(Text, comment="Ошибка обработки")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class WBSyncLog(Base):
    """Лог синхронизаций с WildBerries"""
    __tablename__ = "wb_sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Информация о синхронизации
    sync_type: Mapped[str] = mapped_column(String(50), index=True, comment="Тип синхронизации")
    status: Mapped[str] = mapped_column(String(50), index=True, comment="Статус")

    # Статистика
    items_processed: Mapped[int] = mapped_column(Integer, default=0, comment="Обработано элементов")
    items_created: Mapped[int] = mapped_column(Integer, default=0, comment="Создано")
    items_updated: Mapped[int] = mapped_column(Integer, default=0, comment="Обновлено")
    items_failed: Mapped[int] = mapped_column(Integer, default=0, comment="Ошибок")

    # Длительность
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Детали
    error: Mapped[Optional[str]] = mapped_column(Text, comment="Ошибка")
    details: Mapped[dict] = mapped_column(JSON, default=dict, comment="Детали синхронизации")
