"""
Сервис для мониторинга новых сообщений Avito и отправки уведомлений
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from ..services.avito_service import get_avito_service
from ..services.notification_service import NotificationService
from ..config.settings import settings

logger = logging.getLogger(__name__)

class AvitoPollingService:
    """Сервис для polling новых сообщений Avito"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.last_check: Dict[str, datetime] = {}
        self.known_messages: Dict[str, set] = {}  # chat_id -> set of message IDs
        self.auto_response_enabled = False
        self.polling_active = False
        self._initialize_bot()
    
    def _initialize_bot(self):
        """Инициализация Telegram бота для уведомлений"""
        try:
            if not settings.BOT_TOKEN:
                logger.error("BOT_TOKEN не установлен в переменных окружения")
                return
                
            if not settings.ADMIN_CHAT_ID:
                logger.error("ADMIN_CHAT_ID не установлен в переменных окружения")
                return
                
            from telegram import Bot
            bot = Bot(token=settings.BOT_TOKEN)
            self.notification_service.set_bot(bot)
            logger.info(f"Telegram бот для уведомлений инициализирован. ADMIN_CHAT_ID: {settings.ADMIN_CHAT_ID}")
        except Exception as e:
            logger.error(f"Ошибка инициализации Telegram бота: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
    async def start_polling(self, interval: int = 30):
        """Запуск polling с указанным интервалом (секунды)"""
        self.polling_active = True
        logger.info(f"Запускаем Avito polling с интервалом {interval} секунд")
        
        while self.polling_active:
            try:
                await self.check_new_messages()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Ошибка в polling: {e}")
                await asyncio.sleep(5)  # Короткая пауза при ошибке
    
    def stop_polling(self):
        """Остановка polling"""
        self.polling_active = False
        logger.info("Avito polling остановлен")
    
    async def check_new_messages(self):
        """Проверка новых сообщений во всех чатах"""
        try:
            avito_service = get_avito_service()  # Убираем await - это обычная функция
            if not avito_service:
                logger.warning("Avito service не инициализирован")
                return
                
            # Получаем список чатов
            chats = await avito_service.get_chats()
            if not chats:
                logger.info("Чаты не найдены")
                return
                
            logger.info(f"Проверяем {len(chats)} чатов на новые сообщения")
            
            for chat in chats:
                await self.check_chat_for_new_messages(chat)
                
        except Exception as e:
            logger.error(f"Ошибка при проверке новых сообщений: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    async def check_chat_for_new_messages(self, chat):
        """Проверка новых сообщений в конкретном чате"""
        chat_id = chat.id  # Используем атрибут объекта, а не индекс словаря
        
        try:
            # Получаем сообщения чата БЕЗ кэширования (для polling)
            avito_service = get_avito_service()  # Убираем await
            messages = await avito_service.get_chat_messages_no_cache(chat_id)
            
            if not messages:
                return
                
            # Инициализируем set известных сообщений для чата
            if chat_id not in self.known_messages:
                self.known_messages[chat_id] = set()
                # При первом запуске просто запоминаем все текущие сообщения
                for msg in messages:
                    self.known_messages[chat_id].add(msg.id)  # Используем атрибут объекта
                return
            
            # Ищем новые сообщения
            new_messages = []
            for msg in messages:
                if msg.id not in self.known_messages[chat_id]:  # Используем атрибут объекта
                    new_messages.append(msg)
                    self.known_messages[chat_id].add(msg.id)  # Используем атрибут объекта
            
            # Обрабатываем новые сообщения
            if new_messages:
                logger.info(f"Найдено {len(new_messages)} новых сообщений в чате {chat_id}")
                for message in new_messages:
                    await self.process_new_message(chat, message)
            else:
                logger.debug(f"Новых сообщений в чате {chat_id} нет")
                
        except Exception as e:
            logger.error(f"Ошибка при проверке чата {chat_id}: {e}")
    
    async def process_new_message(self, chat, message):
        """Обработка нового сообщения"""
        chat_id = chat.id  # Используем атрибут объекта
        current_user_id = 216012096  # ID текущего пользователя
        
        # Проверяем что сообщение от клиента (не от нас)
        if message.author_id == current_user_id:  # Используем атрибут объекта
            return
            
        logger.info(f"Новое сообщение в чате {chat_id} от {message.author_id}")
        
        # Отправляем Telegram уведомление
        await self.send_telegram_notification(chat, message)
        
        # Автоответ если включен
        if self.auto_response_enabled:
            await self.send_auto_response(chat_id, message)
    
    async def send_telegram_notification(self, chat, message):
        """Отправка Telegram уведомления о новом сообщении"""
        try:
            # Получаем имя пользователя
            user_name = "Неизвестный"
            current_user_id = 216012096
            
            for user in chat.users:  # Используем атрибут объекта
                if user['id'] != current_user_id:
                    user_name = user.get('name', 'Неизвестный')
                    break
            
            # Текст сообщения (обрезаем если слишком длинный)
            message_text = message.content.get('text', 'Без текста')  # Используем атрибут объекта
            if len(message_text) > 100:
                message_text = message_text[:100] + "..."
            
            # Формируем уведомление
            notification_text = f"""
🔔 <b>Новое сообщение Avito</b>

👤 <b>От:</b> {user_name}
💬 <b>Сообщение:</b> {message_text}

🔗 <a href="http://147.45.215.199:8001/admin/avito/">Открыть чат</a>
            """
            
            await self.notification_service.send_admin_notification(notification_text.strip())
            
        except Exception as e:
            logger.error(f"Ошибка отправки Telegram уведомления: {e}")
    
    async def send_auto_response(self, chat_id: str, message):
        """Отправка автоматического ответа"""
        try:
            message_text = message.content.get('text', '')  # Используем атрибут объекта
            if not message_text:
                return
                
            logger.info(f"Генерируем автоответ для чата {chat_id}")
            
            # Генерируем ответ через AI (используем существующий endpoint)
            from ..services.openai_service import OpenAIService
            
            ai_service = OpenAIService()
            
            # Формируем промпт для автоответа
            prompt = f"""Ты - профессиональный консультант по разработке Telegram ботов и веб-приложений.

Клиент написал: "{message_text}"

Напиши краткий профессиональный ответ (до 100 слов). Будь дружелюбным и готовым помочь.
Если это приветствие - поздоровайся.
Если вопрос о услугах - кратко опиши возможности.
Если нужны детали - предложи обсудить подробнее.
"""
            
            ai_response = await ai_service.generate_response_with_model(
                prompt,
                model="openai/gpt-4o-mini"
            )
            
            # Отправляем ответ через Avito API
            avito_service = get_avito_service()  # Убираем await
            if avito_service:
                success = await avito_service.send_message(chat_id, ai_response)
                if success:
                    logger.info(f"Автоответ отправлен в чат {chat_id}")
                else:
                    logger.error(f"Не удалось отправить автоответ в чат {chat_id}")
                    
        except Exception as e:
            logger.error(f"Ошибка автоответа: {e}")
    
    def set_auto_response(self, enabled: bool):
        """Включение/выключение автоответов"""
        self.auto_response_enabled = enabled
        logger.info(f"Автоответы {'включены' if enabled else 'выключены'}")

# Глобальный экземпляр сервиса
polling_service = AvitoPollingService()