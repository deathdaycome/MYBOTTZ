"""
Client ID Service - Автоматическое управление client_id
"""

import logging
import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import HostingServer, ClientBalance

logger = logging.getLogger(__name__)


class ClientIdService:
    """Сервис для автоматического управления client_id"""

    def generate_client_id(self, client_name: str) -> int:
        """
        Генерировать уникальный client_id на основе имени клиента

        Args:
            client_name: Имя клиента

        Returns:
            Уникальный числовой ID
        """
        # Создаем хеш от имени и берем первые 8 символов
        hash_object = hashlib.md5(client_name.lower().strip().encode())
        hash_hex = hash_object.hexdigest()

        # Берем первые 8 символов и конвертируем в число
        # Это даст нам число от 0 до 4294967295 (2^32 - 1)
        client_id = int(hash_hex[:8], 16)

        # Убеждаемся что это положительное число
        client_id = abs(client_id) % 2147483647  # MAX INT для SQLite

        # Минимум 1000 для визуального отличия от других ID
        if client_id < 1000:
            client_id += 1000

        return client_id

    def get_or_create_client_id(
        self,
        db: Session,
        client_name: str,
        client_telegram_id: Optional[int] = None,
        server_id: Optional[int] = None
    ) -> int:
        """
        Получить существующий или создать новый client_id для сервера

        ВАЖНО: Каждый сервер = отдельный клиент = отдельный баланс!

        Логика:
        1. Если у сервера уже есть client_id - используем его
        2. Если Telegram ID указан и есть сервер с таким ID - используем его client_id (объединение)
        3. Иначе генерируем УНИКАЛЬНЫЙ client_id для этого сервера

        Args:
            db: Сессия БД
            client_name: Имя клиента
            client_telegram_id: Telegram ID клиента (для объединения серверов)
            server_id: ID сервера (если обновляем существующий)

        Returns:
            client_id для сервера
        """
        # Если обновляем существующий сервер - проверяем его текущий client_id
        if server_id:
            existing_server = db.query(HostingServer).filter(
                HostingServer.id == server_id
            ).first()

            if existing_server and existing_server.client_id:
                logger.info(f"Using existing client_id {existing_server.client_id} for server {server_id}")
                return existing_server.client_id

        # ТОЛЬКО если указан Telegram ID - можем объединить серверы
        if client_telegram_id:
            existing_by_telegram = db.query(HostingServer).filter(
                HostingServer.client_telegram_id == client_telegram_id,
                HostingServer.client_id.isnot(None)
            ).first()

            if existing_by_telegram and existing_by_telegram.client_id:
                logger.info(f"Found existing client_id {existing_by_telegram.client_id} by telegram_id {client_telegram_id}")
                return existing_by_telegram.client_id

        # Генерируем УНИКАЛЬНЫЙ client_id для нового сервера
        # Используем timestamp + random для гарантии уникальности
        import time
        import random

        new_client_id = int(time.time() * 1000) + random.randint(1000, 9999)

        # Проверяем что такой ID еще не используется
        while db.query(HostingServer).filter(
            HostingServer.client_id == new_client_id
        ).first() is not None:
            new_client_id += 1

        logger.info(f"Generated new unique client_id {new_client_id} for '{client_name}'")
        return new_client_id

    def assign_client_ids_to_all_servers(self, db: Session) -> dict:
        """
        Присвоить client_id всем серверам без него

        Args:
            db: Сессия БД

        Returns:
            Статистика: количество обновленных серверов
        """
        servers_without_id = db.query(HostingServer).filter(
            HostingServer.client_id.is_(None)
        ).all()

        updated_count = 0
        client_groups = {}  # client_name -> client_id mapping

        logger.info(f"Found {len(servers_without_id)} servers without client_id")

        for server in servers_without_id:
            normalized_name = server.client_name.strip()

            # Проверяем, уже обрабатывали это имя?
            if normalized_name.lower() in client_groups:
                client_id = client_groups[normalized_name.lower()]
            else:
                # Получаем или создаем client_id для этого клиента
                client_id = self.get_or_create_client_id(
                    db,
                    server.client_name,
                    server.client_telegram_id
                )
                client_groups[normalized_name.lower()] = client_id

            # Присваиваем client_id серверу
            server.client_id = client_id
            updated_count += 1

            logger.info(f"Assigned client_id {client_id} to server '{server.server_name}' (client: {server.client_name})")

        if updated_count > 0:
            db.commit()
            logger.info(f"Successfully assigned client_id to {updated_count} servers")

            # Обновляем затраты для всех клиентов
            from app.services.balance_service import balance_service

            for client_name_lower, client_id in client_groups.items():
                # Получаем оригинальное имя (с правильным регистром)
                server = db.query(HostingServer).filter(
                    HostingServer.client_id == client_id
                ).first()

                if server:
                    balance_service.update_client_costs(db, client_id, server.client_name)

        return {
            "total_servers": len(servers_without_id),
            "updated": updated_count,
            "unique_clients": len(client_groups)
        }


# Global instance
client_id_service = ClientIdService()
