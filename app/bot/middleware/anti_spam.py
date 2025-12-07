"""
Middleware для защиты бота от спама
"""
from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AntiSpamMiddleware(BaseMiddleware):
    """
    Middleware для защиты от спама
    - Ограничивает количество сообщений от пользователя
    - Блокирует спам-ссылки
    - Блокирует пользователей за флуд
    """

    def __init__(self):
        super().__init__()
        # Хранилище для отслеживания сообщений {user_id: [timestamps]}
        self.user_messages: Dict[int, list] = defaultdict(list)
        # Заблокированные пользователи {user_id: unblock_time}
        self.blocked_users: Dict[int, datetime] = {}

        # Настройки
        self.max_messages_per_minute = 10  # Макс сообщений в минуту
        self.block_duration = timedelta(hours=1)  # Длительность блокировки

        # Спам-паттерны
        self.spam_patterns = [
            't.me/',
            'telegram.me/',
            '@',  # Ссылки на каналы
            'http://',
            'https://',
        ]

        # Белый список (админы, разрешенные пользователи)
        self.whitelist = set()

    def add_to_whitelist(self, user_id: int):
        """Добавить пользователя в белый список"""
        self.whitelist.add(user_id)

    def is_spam(self, text: str) -> bool:
        """Проверка текста на спам"""
        if not text:
            return False

        text_lower = text.lower()

        # Проверка на спам-паттерны
        spam_count = sum(1 for pattern in self.spam_patterns if pattern in text_lower)

        # Если в сообщении 2+ спам-паттернов - это спам
        if spam_count >= 2:
            return True

        # Проверка на известные спам-ссылки
        spam_links = ['barztbot', 'love', 'sexy', 'dating']
        if any(link in text_lower for link in spam_links):
            return True

        return False

    def is_user_blocked(self, user_id: int) -> bool:
        """Проверка заблокирован ли пользователь"""
        if user_id in self.blocked_users:
            unblock_time = self.blocked_users[user_id]
            if datetime.now() < unblock_time:
                return True
            else:
                # Время блокировки истекло
                del self.blocked_users[user_id]
        return False

    def check_flood(self, user_id: int) -> bool:
        """
        Проверка на флуд
        Возвращает True если пользователь флудит
        """
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Очищаем старые сообщения
        self.user_messages[user_id] = [
            ts for ts in self.user_messages[user_id]
            if ts > minute_ago
        ]

        # Добавляем текущее сообщение
        self.user_messages[user_id].append(now)

        # Проверяем превышен ли лимит
        if len(self.user_messages[user_id]) > self.max_messages_per_minute:
            return True

        return False

    def block_user(self, user_id: int):
        """Заблокировать пользователя"""
        self.blocked_users[user_id] = datetime.now() + self.block_duration
        logger.warning(f"🚫 User {user_id} blocked for spam/flood")

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """Проверка сообщений на спам"""

        # Получаем сообщение
        message: Message = event.message
        if not message or not message.from_user:
            return await handler(event, data)

        user_id = message.from_user.id

        # Пропускаем белый список
        if user_id in self.whitelist:
            return await handler(event, data)

        # Проверка блокировки
        if self.is_user_blocked(user_id):
            logger.info(f"🚫 Blocked user {user_id} tried to send message")
            await message.answer(
                "⛔️ Вы временно заблокированы за флуд/спам.\n"
                "Попробуйте позже."
            )
            return

        # Проверка флуда
        if self.check_flood(user_id):
            self.block_user(user_id)
            await message.answer(
                "⛔️ Вы отправляете слишком много сообщений!\n"
                "Вы заблокированы на 1 час."
            )
            return

        # Проверка на спам (если есть текст)
        if message.text and self.is_spam(message.text):
            logger.warning(
                f"🚫 Spam detected from user {user_id}: {message.text[:50]}"
            )
            self.block_user(user_id)
            await message.answer(
                "⛔️ Обнаружен спам! Вы заблокированы."
            )
            return

        # Проверка на спам в подписи к фото
        if message.caption and self.is_spam(message.caption):
            logger.warning(
                f"🚫 Spam in caption from user {user_id}: {message.caption[:50]}"
            )
            self.block_user(user_id)
            await message.answer(
                "⛔️ Обнаружен спам! Вы заблокированы."
            )
            return

        # Все проверки пройдены - передаем дальше
        return await handler(event, data)
