"""
WildBerries API Client with Rate Limiting and Authentication
"""

import asyncio
import time
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import httpx
from loguru import logger

from app.core.config import get_settings


class RateLimiter:
    """Rate limiter для WB API (максимум 100 запросов в минуту)"""

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests: List[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Ожидание разрешения на выполнение запроса"""
        async with self._lock:
            now = time.time()

            # Удаляем старые запросы
            self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]

            if len(self.requests) >= self.max_requests:
                # Ждем до освобождения слота
                sleep_time = self.time_window - (now - self.requests[0]) + 0.1
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                return await self.acquire()

            self.requests.append(now)


class WildberriesClient:
    """
    Клиент для работы с WildBerries API

    Основные возможности:
    - Автоматический rate limiting
    - Retry логика с экспоненциальным backoff
    - Логирование всех запросов
    - Обработка ошибок WB API
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://suppliers-api.wildberries.ru",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

        # Rate limiter (100 requests per minute according to WB API limits)
        self.rate_limiter = RateLimiter(max_requests=100, time_window=60)

        # HTTP client
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Закрытие HTTP клиента"""
        await self.client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Выполнение HTTP запроса с rate limiting и retry

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Дополнительные параметры для httpx

        Returns:
            JSON ответ от API

        Raises:
            httpx.HTTPError: При ошибках HTTP
        """
        await self.rate_limiter.acquire()

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"WB API request: {method} {endpoint} (attempt {attempt + 1}/{self.max_retries})")

                response = await self.client.request(method, endpoint, **kwargs)
                response.raise_for_status()

                data = response.json() if response.text else {}
                logger.debug(f"WB API response: {response.status_code}")

                return data

            except httpx.HTTPStatusError as e:
                logger.error(f"WB API error {e.response.status_code}: {e.response.text}")

                # 429 Too Many Requests - ждем и повторяем
                if e.response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit exceeded, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue

                # 401 Unauthorized - не повторяем
                if e.response.status_code == 401:
                    logger.error("WB API authentication failed")
                    raise

                # Для остальных ошибок повторяем
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue

                raise

            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.error(f"WB API request error: {e}")

                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue

                raise

        raise Exception(f"Failed to make request after {self.max_retries} attempts")

    # ============ Products API ============

    async def get_products(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """
        Получить список товаров

        Args:
            limit: Максимальное количество товаров
            offset: Смещение для пагинации

        Returns:
            Список товаров
        """
        params = {"limit": limit, "offset": offset}
        response = await self._make_request("GET", "/api/v3/supplies/stocks", params=params)
        return response.get("stocks", [])

    async def get_product_by_article(self, article: str) -> Optional[Dict]:
        """
        Получить товар по артикулу

        Args:
            article: Артикул товара

        Returns:
            Данные товара или None
        """
        products = await self.get_products(limit=100)
        for product in products:
            if product.get("vendorCode") == article:
                return product
        return None

    async def update_product_stock(self, article: str, quantity: int, warehouse_id: int) -> Dict:
        """
        Обновить остатки товара

        Args:
            article: Артикул товара
            quantity: Новое количество
            warehouse_id: ID склада

        Returns:
            Результат обновления
        """
        payload = {
            "stocks": [
                {
                    "sku": article,
                    "amount": quantity,
                    "warehouseId": warehouse_id
                }
            ]
        }
        return await self._make_request("PUT", "/api/v3/stocks", json=payload)

    # ============ Orders API ============

    async def get_orders(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Получить список заказов

        Args:
            date_from: Дата начала периода
            date_to: Дата конца периода
            status: Статус заказа
            limit: Максимальное количество заказов

        Returns:
            Список заказов
        """
        params = {"limit": limit}

        if date_from:
            params["dateFrom"] = date_from.isoformat()
        if date_to:
            params["dateTo"] = date_to.isoformat()
        if status:
            params["status"] = status

        response = await self._make_request("GET", "/api/v3/orders", params=params)
        return response.get("orders", [])

    async def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """
        Получить заказ по ID

        Args:
            order_id: ID заказа

        Returns:
            Данные заказа или None
        """
        response = await self._make_request("GET", f"/api/v3/orders/{order_id}")
        return response

    async def update_order_status(self, order_id: str, status: str) -> Dict:
        """
        Обновить статус заказа

        Args:
            order_id: ID заказа
            status: Новый статус

        Returns:
            Результат обновления
        """
        payload = {"status": status}
        return await self._make_request("PUT", f"/api/v3/orders/{order_id}", json=payload)

    # ============ Analytics API ============

    async def get_sales_report(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> List[Dict]:
        """
        Получить отчет по продажам

        Args:
            date_from: Дата начала периода
            date_to: Дата конца периода

        Returns:
            Список продаж
        """
        params = {
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat()
        }
        response = await self._make_request("GET", "/api/v1/supplier/reportDetailByPeriod", params=params)
        return response

    async def get_warehouse_stocks(self, warehouse_id: Optional[int] = None) -> List[Dict]:
        """
        Получить остатки на складе

        Args:
            warehouse_id: ID склада (опционально)

        Returns:
            Список остатков
        """
        params = {}
        if warehouse_id:
            params["warehouseId"] = warehouse_id

        response = await self._make_request("GET", "/api/v3/stocks", params=params)
        return response.get("stocks", [])

    # ============ Health Check ============

    async def health_check(self) -> bool:
        """
        Проверка доступности API

        Returns:
            True если API доступен
        """
        try:
            await self._make_request("GET", "/ping")
            return True
        except Exception as e:
            logger.error(f"WB API health check failed: {e}")
            return False


def get_wb_client() -> WildberriesClient:
    """
    Получить настроенный WB API клиент

    Returns:
        Настроенный экземпляр WildberriesClient
    """
    settings = get_settings()

    # TODO: Добавить WB_API_KEY в settings
    api_key = getattr(settings, "WB_API_KEY", "your_api_key_here")

    return WildberriesClient(api_key=api_key)
