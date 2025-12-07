"""
WildBerries Webhooks Handlers
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import Request, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .models import WBWebhookLog, WBProduct, WBOrder
from .schemas import WBWebhookPayload


class WildberriesWebhookHandler:
    """Обработчик вебхуков от WildBerries"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка входящего вебхука

        Args:
            payload: Payload вебхука

        Returns:
            Результат обработки
        """
        event_type = payload.get("eventType") or payload.get("type")

        if not event_type:
            raise HTTPException(status_code=400, detail="Missing event_type")

        # Логируем вебхук
        webhook_log = WBWebhookLog(
            event_type=event_type,
            payload=payload,
            processed=False
        )
        self.db.add(webhook_log)
        await self.db.commit()

        try:
            # Обрабатываем по типу события
            handler = self._get_handler(event_type)
            result = await handler(payload)

            # Обновляем лог
            webhook_log.processed = True
            webhook_log.processed_at = datetime.utcnow()
            await self.db.commit()

            logger.info(f"Webhook {event_type} processed successfully")
            return {"status": "success", "event_type": event_type, "result": result}

        except Exception as e:
            logger.error(f"Webhook processing error: {e}", exc_info=True)

            # Сохраняем ошибку
            webhook_log.error = str(e)
            await self.db.commit()

            raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

    def _get_handler(self, event_type: str):
        """Получить обработчик для типа события"""
        handlers = {
            "order.created": self._handle_order_created,
            "order.updated": self._handle_order_updated,
            "order.cancelled": self._handle_order_cancelled,
            "stock.updated": self._handle_stock_updated,
            "product.created": self._handle_product_created,
            "product.updated": self._handle_product_updated,
        }

        handler = handlers.get(event_type)
        if not handler:
            logger.warning(f"No handler for event type: {event_type}")
            return self._handle_unknown_event

        return handler

    async def _handle_order_created(self, payload: Dict) -> Dict:
        """Обработка создания заказа"""
        order_data = payload.get("data", {})
        order_id = order_data.get("orderId")

        if not order_id:
            raise ValueError("Missing orderId in payload")

        # Создаем или обновляем заказ
        # TODO: Реализовать логику создания заказа

        logger.info(f"Order created: {order_id}")
        return {"order_id": order_id, "action": "created"}

    async def _handle_order_updated(self, payload: Dict) -> Dict:
        """Обработка обновления заказа"""
        order_data = payload.get("data", {})
        order_id = order_data.get("orderId")
        new_status = order_data.get("status")

        if not order_id:
            raise ValueError("Missing orderId in payload")

        # Обновляем статус заказа
        # TODO: Реализовать логику обновления заказа

        logger.info(f"Order updated: {order_id}, new status: {new_status}")
        return {"order_id": order_id, "status": new_status, "action": "updated"}

    async def _handle_order_cancelled(self, payload: Dict) -> Dict:
        """Обработка отмены заказа"""
        order_data = payload.get("data", {})
        order_id = order_data.get("orderId")

        if not order_id:
            raise ValueError("Missing orderId in payload")

        # Обновляем статус заказа на отменен
        # TODO: Реализовать логику отмены заказа

        logger.info(f"Order cancelled: {order_id}")
        return {"order_id": order_id, "action": "cancelled"}

    async def _handle_stock_updated(self, payload: Dict) -> Dict:
        """Обработка обновления остатков"""
        stock_data = payload.get("data", {})
        article = stock_data.get("article")
        quantity = stock_data.get("quantity")

        if not article:
            raise ValueError("Missing article in payload")

        # Обновляем остатки товара
        # TODO: Реализовать логику обновления остатков

        logger.info(f"Stock updated for article {article}: {quantity}")
        return {"article": article, "quantity": quantity, "action": "stock_updated"}

    async def _handle_product_created(self, payload: Dict) -> Dict:
        """Обработка создания товара"""
        product_data = payload.get("data", {})
        article = product_data.get("article")

        if not article:
            raise ValueError("Missing article in payload")

        # Создаем товар
        # TODO: Реализовать логику создания товара

        logger.info(f"Product created: {article}")
        return {"article": article, "action": "created"}

    async def _handle_product_updated(self, payload: Dict) -> Dict:
        """Обработка обновления товара"""
        product_data = payload.get("data", {})
        article = product_data.get("article")

        if not article:
            raise ValueError("Missing article in payload")

        # Обновляем товар
        # TODO: Реализовать логику обновления товара

        logger.info(f"Product updated: {article}")
        return {"article": article, "action": "updated"}

    async def _handle_unknown_event(self, payload: Dict) -> Dict:
        """Обработка неизвестного события"""
        logger.warning(f"Unknown event type, payload: {payload}")
        return {"action": "logged", "note": "unknown event type"}


async def process_wb_webhook(
    request: Request,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Обработка вебхука от WildBerries

    Args:
        request: FastAPI request
        db: Database session

    Returns:
        Результат обработки
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    handler = WildberriesWebhookHandler(db)
    return await handler.handle_webhook(payload)
