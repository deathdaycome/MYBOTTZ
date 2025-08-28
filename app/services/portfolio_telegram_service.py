"""
Сервис для публикации портфолио в Telegram канал
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, List
import telegram
from telegram.constants import ParseMode
from sqlalchemy.orm import Session

from ..database.models import Portfolio
from ..config.settings import settings
from ..config.logging import get_logger

logger = get_logger(__name__)

class PortfolioTelegramService:
    def __init__(self):
        self.bot_token = settings.BOT_TOKEN
        self.portfolio_channel_id = settings.PORTFOLIO_CHANNEL_ID if hasattr(settings, 'PORTFOLIO_CHANNEL_ID') else None
        self.bot = None
        
        if self.bot_token:
            self.bot = telegram.Bot(token=self.bot_token)
    
    async def publish_portfolio_item(self, portfolio_item: Portfolio, db: Session) -> dict:
        """
        Публикует элемент портфолио в Telegram канал
        
        Args:
            portfolio_item: Объект портфолио для публикации
            db: Сессия базы данных
            
        Returns:
            dict: Результат публикации
        """
        try:
            if not self.bot:
                return {"success": False, "error": "Telegram bot не настроен"}
            
            if not self.portfolio_channel_id:
                return {"success": False, "error": "ID канала портфолио не настроен"}
            
            # Формируем текст сообщения
            message_text = self._format_portfolio_message(portfolio_item)
            
            # Публикуем в канал
            if portfolio_item.main_image and os.path.exists(f"uploads/portfolio/{portfolio_item.main_image}"):
                # Если есть главное изображение - отправляем с фото
                with open(f"uploads/portfolio/{portfolio_item.main_image}", 'rb') as photo:
                    message = await self.bot.send_photo(
                        chat_id=self.portfolio_channel_id,
                        photo=photo,
                        caption=message_text,
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
            else:
                # Отправляем только текст
                message = await self.bot.send_message(
                    chat_id=self.portfolio_channel_id,
                    text=message_text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=False
                )
            
            # Отправляем дополнительные изображения если есть
            if portfolio_item.image_paths and len(portfolio_item.image_paths) > 0:
                await self._send_additional_images(portfolio_item.image_paths, message.message_id)
            
            # Обновляем запись в БД
            portfolio_item.is_published = True
            portfolio_item.telegram_message_id = message.message_id
            portfolio_item.published_at = datetime.utcnow()
            portfolio_item.telegram_channel_id = self.portfolio_channel_id
            db.commit()
            
            logger.info(f"Portfolio item {portfolio_item.id} опубликован в канал {self.portfolio_channel_id}")
            
            return {
                "success": True, 
                "message_id": message.message_id,
                "channel_id": self.portfolio_channel_id
            }
            
        except Exception as e:
            logger.error(f"Ошибка публикации портфолио в Telegram: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_additional_images(self, image_paths: List[str], reply_to_message_id: int):
        """Отправляет дополнительные изображения как ответ на основное сообщение"""
        try:
            media_group = []
            for image_path in image_paths[:9]:  # Telegram позволяет максимум 10 изображений в группе
                if os.path.exists(f"uploads/portfolio/{image_path}"):
                    with open(f"uploads/portfolio/{image_path}", 'rb') as photo:
                        media_group.append(telegram.InputMediaPhoto(media=photo))
            
            if media_group:
                await self.bot.send_media_group(
                    chat_id=self.portfolio_channel_id,
                    media=media_group,
                    reply_to_message_id=reply_to_message_id
                )
                
        except Exception as e:
            logger.error(f"Ошибка отправки дополнительных изображений: {e}")
    
    def _format_portfolio_message(self, portfolio_item: Portfolio) -> str:
        """Форматирует текст сообщения для публикации в канале"""
        
        # Экранируем специальные символы для Markdown V2
        def escape_markdown(text: str) -> str:
            if not text:
                return ""
            # Экранируем специальные символы Markdown V2
            escape_chars = r'_*[]()~`>#+-=|{}.!'
            for char in escape_chars:
                text = text.replace(char, f'\\{char}')
            return text
        
        title = escape_markdown(portfolio_item.title)
        description = escape_markdown(portfolio_item.description[:300] + "..." if len(portfolio_item.description) > 300 else portfolio_item.description)
        
        # Формируем текст
        text_parts = [
            f"🚀 *{title}*",
            "",
            f"📝 {description}",
            ""
        ]
        
        # Добавляем технологии
        if portfolio_item.technologies:
            technologies = escape_markdown(portfolio_item.technologies)
            text_parts.extend([
                f"⚙️ *Технологии:* {technologies}",
                ""
            ])
        
        # Добавляем клиента если указан
        if portfolio_item.client_name:
            client_name = escape_markdown(portfolio_item.client_name)
            text_parts.extend([
                f"👤 *Клиент:* @{client_name}" if client_name.startswith('@') else f"👤 *Клиент:* {client_name}",
                ""
            ])
        
        # Добавляем время разработки
        if portfolio_item.development_time:
            text_parts.extend([
                f"⏱ *Время разработки:* {portfolio_item.development_time} дней",
                ""
            ])
        
        # Добавляем ссылки
        links = []
        if portfolio_item.demo_link:
            demo_link = escape_markdown(portfolio_item.demo_link)
            links.append(f"[🔗 Демо]({portfolio_item.demo_link})")
        
        if portfolio_item.repository_link:
            repo_link = escape_markdown(portfolio_item.repository_link)
            links.append(f"[📁 Код]({portfolio_item.repository_link})")
        
        if links:
            text_parts.append(" | ".join(links))
            text_parts.append("")
        
        # Добавляем категорию
        category_icons = {
            'telegram_bots': '🤖',
            'web_development': '🌐', 
            'mobile_apps': '📱',
            'ai_integration': '🧠',
            'automation': '⚡',
            'ecommerce': '🛒',
            'other': '🔧'
        }
        
        category_icon = category_icons.get(portfolio_item.category, '🔧')
        category_name = portfolio_item.category.replace('_', ' ').title()
        category_name = escape_markdown(category_name)
        
        text_parts.extend([
            f"{category_icon} *Категория:* {category_name}",
            "",
            "📞 *Заказать похожий проект:* @your\\_username"
        ])
        
        return "\n".join(text_parts)
    
    async def update_published_item(self, portfolio_item: Portfolio, db: Session) -> dict:
        """
        Обновляет уже опубликованный элемент портфолио в канале
        """
        try:
            if not portfolio_item.is_published or not portfolio_item.telegram_message_id:
                return {"success": False, "error": "Элемент не опубликован в канале"}
            
            message_text = self._format_portfolio_message(portfolio_item)
            
            # Обновляем сообщение в канале
            await self.bot.edit_message_text(
                chat_id=self.portfolio_channel_id,
                message_id=portfolio_item.telegram_message_id,
                text=message_text,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            
            # Обновляем дату в БД
            portfolio_item.published_at = datetime.utcnow()
            db.commit()
            
            return {"success": True, "message": "Сообщение в канале обновлено"}
            
        except Exception as e:
            logger.error(f"Ошибка обновления сообщения в канале: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_published_item(self, portfolio_item: Portfolio, db: Session) -> dict:
        """
        Удаляет опубликованный элемент из канала
        """
        try:
            if not portfolio_item.is_published or not portfolio_item.telegram_message_id:
                return {"success": False, "error": "Элемент не опубликован в канале"}
            
            # Удаляем сообщение из канала
            await self.bot.delete_message(
                chat_id=self.portfolio_channel_id,
                message_id=portfolio_item.telegram_message_id
            )
            
            # Обновляем запись в БД
            portfolio_item.is_published = False
            portfolio_item.telegram_message_id = None
            portfolio_item.published_at = None
            db.commit()
            
            return {"success": True, "message": "Сообщение удалено из канала"}
            
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения из канала: {e}")
            return {"success": False, "error": str(e)}

# Создаем глобальный экземпляр сервиса
portfolio_telegram_service = PortfolioTelegramService()