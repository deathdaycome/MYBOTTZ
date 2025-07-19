from typing import List, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
import requests
import json
import os
from urllib.parse import urljoin

from ..keyboards.main import get_portfolio_categories_keyboard, get_pagination_keyboard
from ...database.database import get_db_context
from ...database.models import Portfolio
from ...config.logging import get_logger, log_user_action
from ...utils.decorators import standard_handler
from ...config.settings import settings

logger = get_logger(__name__)

class PortfolioHandler:
    """Обработчик портфолио с новым функционалом"""
    
    def __init__(self):
        self.items_per_page = 3
        self.base_url = f"http://localhost:{settings.ADMIN_PORT}"
        self.media_base_url = f"http://localhost:{settings.ADMIN_PORT}/uploads/portfolio"
    
    def get_image_url(self, image_path: str) -> str:
        """Получить полный URL изображения"""
        if not image_path:
            return ""
        return urljoin(self.media_base_url + "/", image_path)
    
    @standard_handler
    async def show_portfolio_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать категории портфолио"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "show_portfolio_categories")
            
            # Получаем категории через API
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/categories", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    categories = data.get("categories", [])
                else:
                    # Fallback: получаем из базы напрямую
                    categories = await self._get_categories_from_db()
            except:
                # Fallback: получаем из базы напрямую
                categories = await self._get_categories_from_db()
            
            if not categories:
                text = """
💼 <b>Портфолио разработчика ботов</b>

К сожалению, портфолио пока пусто.
Следите за обновлениями!
                """
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
                ]])
            else:
                text = """
💼 <b>Портфолио разработчика ботов</b>

Здесь вы можете ознакомиться с нашими работами и оценить качество разработки.

<b>Каждый проект включает:</b>
• 📋 Описание функционала
• 📸 Скриншоты интерфейса  
• 🛠 Использованные технологии
• ⏱ Время разработки
• 🚀 Демо-версию (если доступно)
• 👍 Возможность оценить работу

<b>Выберите категорию для просмотра:</b>
                """
                
                # Создаем клавиатуру с категориями
                keyboard_buttons = []
                
                # Добавляем кнопку "Рекомендуемые"
                keyboard_buttons.append([
                    InlineKeyboardButton("⭐ Рекомендуемые работы", callback_data="portfolio_featured")
                ])
                
                for category in categories:
                    category_id = category.get("id", "")
                    category_name = category.get("name", category_id)
                    keyboard_buttons.append([
                        InlineKeyboardButton(
                            category_name,
                            callback_data=f"portfolio_category_{category_id}"
                        )
                    ])
                
                # Добавляем кнопку "Назад"
                keyboard_buttons.append([
                    InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
                ])
                
                keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка в show_portfolio_categories: {e}")
            await self._send_error_message(update, "Ошибка загрузки портфолио")
    
    async def _get_categories_from_db(self):
        """Получить категории напрямую из базы данных"""
        try:
            with get_db_context() as db:
                categories = db.query(Portfolio.category).filter(
                    Portfolio.is_visible == True
                ).distinct().all()
                
                category_names = {
                    "telegram_bots": "🤖 Telegram боты",
                    "web_development": "🌐 Веб-разработка", 
                    "mobile_apps": "📱 Мобильные приложения",
                    "ai_integration": "🧠 AI интеграции",
                    "automation": "⚙️ Автоматизация",
                    "ecommerce": "🛒 E-commerce",
                    "other": "🔧 Другое"
                }
                
                return [
                    {"id": cat[0], "name": category_names.get(cat[0], cat[0])}
                    for cat in categories
                ]
        except Exception as e:
            logger.error(f"Ошибка получения категорий из БД: {e}")
            return []
    
    @standard_handler
    async def show_featured_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать рекомендуемые работы"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "show_featured_portfolio")
            
            # Получаем рекомендуемые работы через API
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/featured", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                else:
                    # Fallback: получаем из базы напрямую
                    items = await self._get_featured_from_db()
            except:
                # Fallback: получаем из базы напрямую
                items = await self._get_featured_from_db()
            
            if not items:
                text = """
⭐ <b>Рекомендуемые работы</b>

Пока нет рекомендуемых работ.
Выберите другую категорию или посмотрите все проекты.
                """
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К категориям", callback_data="portfolio")
                ]])
            else:
                text = f"""
⭐ <b>Рекомендуемые работы</b>

Наши лучшие проекты, которые мы особенно рекомендуем к просмотру:

<i>Найдено проектов: {len(items)}</i>
                """
                
                # Показываем первые 3 проекта
                for i, item in enumerate(items[:3]):
                    text += await self._format_portfolio_item(item, i + 1)
                
                # Создаем клавиатуру
                keyboard_buttons = []
                
                # Кнопки для проектов
                for i, item in enumerate(items[:3]):
                    keyboard_buttons.append([
                        InlineKeyboardButton(
                            f"👀 Подробнее о проекте {i + 1}",
                            callback_data=f"portfolio_item_{item['id']}"
                        )
                    ])
                
                # Кнопка назад
                keyboard_buttons.append([
                    InlineKeyboardButton("🔙 К категориям", callback_data="portfolio")
                ])
                
                keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
                
        except Exception as e:
            logger.error(f"Ошибка в show_featured_portfolio: {e}")
            await self._send_error_message(update, "Ошибка загрузки рекомендуемых работ")
    
    async def _get_featured_from_db(self):
        """Получить рекомендуемые работы напрямую из базы данных"""
        try:
            with get_db_context() as db:
                items = db.query(Portfolio).filter(
                    Portfolio.is_featured == True,
                    Portfolio.is_visible == True
                ).order_by(
                    Portfolio.sort_order.asc(),
                    Portfolio.views_count.desc()
                ).limit(3).all()
                
                return [item.to_bot_dict() for item in items]
        except Exception as e:
            logger.error(f"Ошибка получения рекомендуемых из БД: {e}")
            return []
    
    @standard_handler
    async def show_category_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать портфолио по категории"""
        try:
            user_id = update.effective_user.id
            callback_data = update.callback_query.data
            category = callback_data.split("_")[-1]
            page = context.user_data.get(f"portfolio_page_{category}", 1)
            
            log_user_action(user_id, "show_category_portfolio", {"category": category, "page": page})
            
            # Получаем проекты по категории через API
            try:
                response = requests.get(
                    f"{self.base_url}/admin/api/portfolio/public/category/{category}",
                    params={"page": page, "limit": self.items_per_page},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    total = data.get("total", 0)
                    pages = data.get("pages", 1)
                else:
                    # Fallback: получаем из базы напрямую
                    items, total, pages = await self._get_category_from_db(category, page)
            except:
                # Fallback: получаем из базы напрямую
                items, total, pages = await self._get_category_from_db(category, page)
            
            # Название категории
            category_names = {
                "telegram_bots": "🤖 Telegram боты",
                "web_development": "🌐 Веб-разработка", 
                "mobile_apps": "📱 Мобильные приложения",
                "ai_integration": "🧠 AI интеграции",
                "automation": "⚙️ Автоматизация",
                "ecommerce": "🛒 E-commerce",
                "other": "🔧 Другое"
            }
            category_name = category_names.get(category, category)
            
            if not items:
                text = f"""
{category_name}

В этой категории пока нет проектов.
Выберите другую категорию или следите за обновлениями!
                """
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К категориям", callback_data="portfolio")
                ]])
            else:
                text = f"""
{category_name}

<i>Всего проектов: {total} • Страница {page} из {pages}</i>

                """
                
                # Показываем проекты
                for i, item in enumerate(items):
                    text += await self._format_portfolio_item(item, i + 1)
                
                # Создаем клавиатуру
                keyboard_buttons = []
                
                # Кнопки для проектов
                for i, item in enumerate(items):
                    keyboard_buttons.append([
                        InlineKeyboardButton(
                            f"👀 Подробнее о проекте {i + 1}",
                            callback_data=f"portfolio_item_{item['id']}"
                        )
                    ])
                
                # Кнопки пагинации
                if pages > 1:
                    pagination_buttons = []
                    if page > 1:
                        pagination_buttons.append(
                            InlineKeyboardButton("⬅️ Пред", callback_data=f"portfolio_page_{category}_{page-1}")
                        )
                    if page < pages:
                        pagination_buttons.append(
                            InlineKeyboardButton("➡️ След", callback_data=f"portfolio_page_{category}_{page+1}")
                        )
                    if pagination_buttons:
                        keyboard_buttons.append(pagination_buttons)
                
                # Кнопка назад
                keyboard_buttons.append([
                    InlineKeyboardButton("🔙 К категориям", callback_data="portfolio")
                ])
                
                keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
                
        except Exception as e:
            logger.error(f"Ошибка в show_category_portfolio: {e}")
            await self._send_error_message(update, "Ошибка загрузки проектов")
    
    async def _get_category_from_db(self, category: str, page: int):
        """Получить проекты по категории напрямую из базы данных"""
        try:
            with get_db_context() as db:
                query = db.query(Portfolio).filter(
                    Portfolio.category == category,
                    Portfolio.is_visible == True
                ).order_by(
                    Portfolio.is_featured.desc(),
                    Portfolio.sort_order.asc(),
                    Portfolio.created_at.desc()
                )
                
                total = query.count()
                offset = (page - 1) * self.items_per_page
                items = query.offset(offset).limit(self.items_per_page).all()
                pages = (total + self.items_per_page - 1) // self.items_per_page
                
                return [item.to_bot_dict() for item in items], total, pages
        except Exception as e:
            logger.error(f"Ошибка получения проектов по категории из БД: {e}")
            return [], 0, 1
    
    @standard_handler
    async def handle_portfolio_pagination(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка пагинации портфолио"""
        try:
            callback_data = update.callback_query.data
            parts = callback_data.split("_")
            category = parts[2]
            page = int(parts[3])
            
            # Сохраняем текущую страницу
            context.user_data[f"portfolio_page_{category}"] = page
            
            # Перенаправляем на показ категории
            context.user_data['temp_callback'] = f"portfolio_category_{category}"
            await self.show_category_portfolio(update, context)
            
        except Exception as e:
            logger.error(f"Ошибка в handle_portfolio_pagination: {e}")
            await self._send_error_message(update, "Ошибка пагинации")
    
    @standard_handler
    async def show_portfolio_item(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детальную информацию о проекте"""
        try:
            user_id = update.effective_user.id
            callback_data = update.callback_query.data
            item_id = int(callback_data.split("_")[-1])
            
            log_user_action(user_id, "show_portfolio_item", {"item_id": item_id})
            
            # Получаем детали проекта через API
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/{item_id}", timeout=5)
                if response.status_code == 200:
                    item = response.json()
                else:
                    # Fallback: получаем из базы напрямую
                    item = await self._get_item_from_db(item_id)
            except:
                # Fallback: получаем из базы напрямую
                item = await self._get_item_from_db(item_id)
            
            if not item:
                text = "❌ Проект не найден или недоступен."
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="portfolio")
                ]])
            else:
                text = await self._format_portfolio_item_detail(item)
                
                # Создаем клавиатуру
                keyboard_buttons = []
                
                # Кнопка лайка
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        f"👍 Нравится ({item.get('likes_count', 0)})",
                        callback_data=f"portfolio_like_{item_id}"
                    )
                ])
                
                # Кнопка демо если есть
                if item.get('demo_link'):
                    keyboard_buttons.append([
                        InlineKeyboardButton("🚀 Попробовать демо", url=item['demo_link'])
                    ])
                
                # Кнопка заказать похожий
                keyboard_buttons.append([
                    InlineKeyboardButton("📝 Заказать похожий", callback_data="create_project")
                ])
                
                # Кнопка назад
                keyboard_buttons.append([
                    InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")
                ])
                
                keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            # Отправляем с изображением если есть
            if item and item.get('main_image'):
                try:
                    image_url = f"{self.base_url}/{item['main_image']}"
                    await update.callback_query.edit_message_media(
                        media=telegram.InputMediaPhoto(
                            media=image_url,
                            caption=text,
                            parse_mode='HTML'
                        ),
                        reply_markup=keyboard
                    )
                except:
                    # Если не удалось загрузить изображение, отправляем просто текст
                    await update.callback_query.edit_message_text(
                        text,
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )
            else:
                await update.callback_query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка в show_portfolio_item: {e}")
            await self._send_error_message(update, "Ошибка загрузки проекта")
    
    async def _get_item_from_db(self, item_id: int):
        """Получить проект напрямую из базы данных"""
        try:
            with get_db_context() as db:
                item = db.query(Portfolio).filter(
                    Portfolio.id == item_id,
                    Portfolio.is_visible == True
                ).first()
                
                if item:
                    # Увеличиваем счетчик просмотров
                    item.increment_views()
                    db.commit()
                    return item.to_bot_dict()
                return None
        except Exception as e:
            logger.error(f"Ошибка получения проекта из БД: {e}")
            return None
    
    @standard_handler
    async def handle_portfolio_like(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка лайка проекта"""
        try:
            user_id = update.effective_user.id
            callback_data = update.callback_query.data
            item_id = int(callback_data.split("_")[-1])
            
            log_user_action(user_id, "portfolio_like", {"item_id": item_id})
            
            # Проверяем, не ставил ли пользователь уже лайк
            user_likes = context.user_data.get('portfolio_likes', [])
            if item_id in user_likes:
                await update.callback_query.answer("Вы уже поставили лайк этому проекту!", show_alert=True)
                return
            
            # Ставим лайк через API
            try:
                response = requests.post(f"{self.base_url}/admin/api/portfolio/{item_id}/like", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    likes_count = data.get('likes_count', 0)
                    
                    # Сохраняем лайк пользователя
                    user_likes.append(item_id)
                    context.user_data['portfolio_likes'] = user_likes
                    
                    await update.callback_query.answer(f"Спасибо за лайк! 👍 ({likes_count})")
                    
                    # Обновляем кнопку
                    await self._update_like_button(update, item_id, likes_count)
                else:
                    await update.callback_query.answer("Ошибка при добавлении лайка")
            except:
                # Fallback: ставим лайк напрямую в БД
                await self._like_item_in_db(item_id, user_likes, context, update)
                
        except Exception as e:
            logger.error(f"Ошибка в handle_portfolio_like: {e}")
            await update.callback_query.answer("Ошибка при добавлении лайка")
    
    async def _like_item_in_db(self, item_id: int, user_likes: list, context, update):
        """Поставить лайк напрямую в базе данных"""
        try:
            with get_db_context() as db:
                item = db.query(Portfolio).filter(Portfolio.id == item_id).first()
                if item:
                    item.increment_likes()
                    db.commit()
                    
                    # Сохраняем лайк пользователя
                    user_likes.append(item_id)
                    context.user_data['portfolio_likes'] = user_likes
                    
                    await update.callback_query.answer(f"Спасибо за лайк! 👍 ({item.likes_count})")
                    await self._update_like_button(update, item_id, item.likes_count)
        except Exception as e:
            logger.error(f"Ошибка лайка в БД: {e}")
    
    async def _update_like_button(self, update, item_id: int, likes_count: int):
        """Обновить кнопку лайка"""
        try:
            # Получаем текущую клавиатуру
            current_keyboard = update.callback_query.message.reply_markup
            if not current_keyboard:
                return
            
            # Обновляем кнопку лайка
            new_buttons = []
            for row in current_keyboard.inline_keyboard:
                new_row = []
                for button in row:
                    if button.callback_data and f"portfolio_like_{item_id}" in button.callback_data:
                        new_row.append(InlineKeyboardButton(
                            f"👍 Нравится ({likes_count})",
                            callback_data=button.callback_data
                        ))
                    else:
                        new_row.append(button)
                new_buttons.append(new_row)
            
            new_keyboard = InlineKeyboardMarkup(new_buttons)
            
            await update.callback_query.edit_message_reply_markup(reply_markup=new_keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка обновления кнопки лайка: {e}")
    
    async def _format_portfolio_item(self, item: dict, index: int) -> str:
        """Форматирование элемента портфолио для списка"""
        try:
            text = f"""
<b>{index}. {item.get('title', 'Без названия')}</b>"""
            
            if item.get('subtitle'):
                text += f"\n<i>{item['subtitle']}</i>"
            
            # Краткое описание (первые 100 символов)
            description = item.get('description', '')
            if len(description) > 100:
                description = description[:100] + "..."
            text += f"\n{description}"
            
            # Технологии
            technologies = item.get('technologies', [])
            if technologies:
                tech_str = ", ".join(technologies[:3])  # Первые 3 технологии
                if len(technologies) > 3:
                    tech_str += f" и еще {len(technologies) - 3}"
                text += f"\n🛠 <b>Технологии:</b> {tech_str}"
            
            # Сложность
            complexity = item.get('complexity', '')
            complexity_names = {
                'simple': '🟢 Простой',
                'medium': '🟡 Средний', 
                'complex': '🔴 Сложный',
                'premium': '🟣 Премиум'
            }
            if complexity in complexity_names:
                text += f"\n📊 <b>Сложность:</b> {complexity_names[complexity]}"
            
            # Время разработки
            dev_time = item.get('development_time')
            if dev_time:
                if dev_time == 1:
                    text += f"\n⏱ <b>Срок:</b> {dev_time} день"
                elif dev_time < 5:
                    text += f"\n⏱ <b>Срок:</b> {dev_time} дня"
                else:
                    text += f"\n⏱ <b>Срок:</b> {dev_time} дней"
            
            # Стоимость (если показывается)
            cost_display = item.get('cost_display')
            if cost_display:
                text += f"\n💰 <b>Стоимость:</b> {cost_display} руб."
            
            # Статистика
            views = item.get('views_count', 0)
            likes = item.get('likes_count', 0)
            text += f"\n👀 {views} • 👍 {likes}"
            
            if item.get('is_featured'):
                text += " ⭐"
            
            text += "\n"
            
            return text
            
        except Exception as e:
            logger.error(f"Ошибка форматирования элемента портфолио: {e}")
            return f"\n<b>{index}. Ошибка загрузки проекта</b>\n"
    
    async def _format_portfolio_item_detail(self, item: dict) -> str:
        """Детальное форматирование элемента портфолио"""
        try:
            text = f"<b>{item.get('title', 'Без названия')}</b>\n"
            
            if item.get('subtitle'):
                text += f"<i>{item['subtitle']}</i>\n"
            
            text += "\n"
            
            # Описание
            description = item.get('description', '')
            text += f"{description}\n\n"
            
            # Технологии
            technologies = item.get('technologies', [])
            if technologies:
                text += f"🛠 <b>Технологии:</b> {', '.join(technologies)}\n"
            
            # Характеристики проекта
            text += "<b>📋 Характеристики проекта:</b>\n"
            
            # Сложность
            complexity = item.get('complexity', '')
            complexity_level = item.get('complexity_level', 0)
            complexity_names = {
                'simple': '🟢 Простой',
                'medium': '🟡 Средний', 
                'complex': '🔴 Сложный',
                'premium': '🟣 Премиум'
            }
            if complexity in complexity_names:
                text += f"• Сложность: {complexity_names[complexity]}"
                if complexity_level:
                    text += f" ({complexity_level}/10)"
                text += "\n"
            
            # Время разработки
            dev_time = item.get('development_time')
            if dev_time:
                if dev_time == 1:
                    text += f"• Время разработки: {dev_time} день\n"
                elif dev_time < 5:
                    text += f"• Время разработки: {dev_time} дня\n"
                else:
                    text += f"• Время разработки: {dev_time} дней\n"
            
            # Стоимость (если показывается)
            cost_display = item.get('cost_display')
            if cost_display:
                text += f"• Стоимость: {cost_display} руб.\n"
            
            # Статус проекта
            status = item.get('project_status', 'completed')
            status_names = {
                'completed': '✅ Завершен',
                'in_progress': '🔄 В разработке',
                'demo': '🚀 Демо-версия'
            }
            if status in status_names:
                text += f"• Статус: {status_names[status]}\n"
            
            # Клиент (если указан)
            client_name = item.get('client_name')
            if client_name:
                text += f"• Клиент: {client_name}\n"
            
            text += "\n"
            
            # Статистика
            views = item.get('views_count', 0)
            likes = item.get('likes_count', 0)
            text += f"📊 <b>Статистика:</b> 👀 {views} просмотров • 👍 {likes} лайков"
            
            if item.get('is_featured'):
                text += " ⭐ Рекомендуем"
            
            # Теги
            tags = item.get('tags', [])
            if tags:
                text += f"\n\n🏷 <b>Теги:</b> {', '.join(tags)}"
            
            return text
            
        except Exception as e:
            logger.error(f"Ошибка детального форматирования: {e}")
            return "❌ Ошибка загрузки информации о проекте"
    
    async def _send_error_message(self, update, message: str):
        """Отправить сообщение об ошибке"""
        try:
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="portfolio")
            ]])
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    f"❌ {message}\n\nПопробуйте позже или обратитесь к администратору.",
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    f"❌ {message}\n\nПопробуйте позже или обратитесь к администратору.",
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения об ошибке: {e}")


# Создаем экземпляр обработчика
portfolio_handler = PortfolioHandler()
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка в show_portfolio_categories: {e}")
    
    @standard_handler
    async def show_category_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать портфолио по категории"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Парсим категорию из callback_data
            category = query.data.replace('portfolio_', '')
            page = 1
            
            log_user_action(user_id, "show_category_portfolio", category)
            
            await self._display_portfolio_page(update, context, category, page)
            
        except Exception as e:
            logger.error(f"Ошибка в show_category_portfolio: {e}")
    
    @standard_handler
    async def show_portfolio_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать страницу портфолио"""
        try:
            query = update.callback_query
            callback_parts = query.data.split('_')
            
            if len(callback_parts) >= 3:
                category = callback_parts[1]
                page = int(callback_parts[3])
                
                await self._display_portfolio_page(update, context, category, page)
            
        except Exception as e:
            logger.error(f"Ошибка в show_portfolio_page: {e}")
    
    async def _display_portfolio_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                     category: str, page: int):
        """Отображение страницы портфолио"""
        try:
            with get_db_context() as db:
                # Формируем запрос
                query_filter = Portfolio.is_visible == True
                
                if category == 'featured':
                    query_filter = Portfolio.is_featured == True
                elif category != 'all':
                    query_filter = Portfolio.category == category
                
                # Получаем общее количество
                total_items = db.query(Portfolio).filter(query_filter).count()
                
                if total_items == 0:
                    await self._show_empty_portfolio(update, category)
                    return
                
                # Получаем элементы для текущей страницы
                offset = (page - 1) * self.items_per_page
                portfolio_items = db.query(Portfolio).filter(query_filter).order_by(
                    Portfolio.sort_order.asc(),
                    Portfolio.created_at.desc()
                ).offset(offset).limit(self.items_per_page).all()
                
                # Обновляем счетчики просмотров
                for item in portfolio_items:
                    item.views_count += 1
                db.commit()
            
            # Формируем текст
            category_names = {
                'telegram': 'Telegram боты',
                'whatsapp': 'WhatsApp боты',
                'web': 'Веб-боты',
                'integration': 'Интеграции',
                'featured': 'Рекомендуемые работы',
                'all': 'Все проекты'
            }
            
            category_name = category_names.get(category, 'Портфолио')
            
            text = f"💼 <b>{category_name}</b>\n\n"
            
            for i, item in enumerate(portfolio_items, 1):
                item_number = offset + i
                
                # Формируем описание проекта
                technologies = ', '.join(item.technologies) if item.technologies else 'Не указано'
                
                text += f"<b>{item_number}. {item.title}</b>\n"
                text += f"📝 {item.description[:150]}{'...' if len(item.description) > 150 else ''}\n"
                text += f"🔧 <i>{technologies}</i>\n"
                
                if item.complexity_level:
                    complexity_text = "🟢 Простой" if item.complexity_level <= 3 else \
                                    "🟡 Средний" if item.complexity_level <= 6 else \
                                    "🟠 Сложный" if item.complexity_level <= 8 else "🔴 Премиум"
                    text += f"📊 {complexity_text}\n"
                
                if item.development_time:
                    text += f"⏱ Время разработки: {item.development_time} дн.\n"
                
                if item.cost_range:
                    text += f"💰 Стоимость: {item.cost_range}₽\n"
                
                text += f"👀 Просмотров: {item.views_count}\n\n"
            
            # Создаем клавиатуру
            keyboard = self._create_portfolio_keyboard(portfolio_items, category, page, total_items)
            
            await update.callback_query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в _display_portfolio_page: {e}")
    
    def _create_portfolio_keyboard(self, items: List[Portfolio], category: str, 
                                  page: int, total_items: int) -> InlineKeyboardMarkup:
        """Создание клавиатуры для портфолио"""
        keyboard = []
        
        # Кнопки для детального просмотра проектов
        for item in items:
            keyboard.append([
                InlineKeyboardButton(
                    f"📋 {item.title[:30]}{'...' if len(item.title) > 30 else ''}",
                    callback_data=f"portfolio_details_{item.id}"
                )
            ])
        
        # Пагинация
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        
        if total_pages > 1:
            pagination_row = []
            
            if page > 1:
                pagination_row.append(
                    InlineKeyboardButton("⬅️", callback_data=f"portfolio_{category}_page_{page-1}")
                )
            
            pagination_row.append(
                InlineKeyboardButton(f"{page}/{total_pages}", callback_data="page_info")
            )
            
            if page < total_pages:
                pagination_row.append(
                    InlineKeyboardButton("➡️", callback_data=f"portfolio_{category}_page_{page+1}")
                )
            
            keyboard.append(pagination_row)
        
        # Дополнительные кнопки
        keyboard.append([
            InlineKeyboardButton("📊 Другие категории", callback_data="portfolio"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @standard_handler
    async def show_portfolio_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детали проекта из портфолио"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Извлекаем ID проекта
            portfolio_id = int(query.data.replace('portfolio_details_', ''))
            
            log_user_action(user_id, "show_portfolio_details", str(portfolio_id))
            
            with get_db_context() as db:
                portfolio_item = db.query(Portfolio).filter(
                    Portfolio.id == portfolio_id
                ).first()
                
                if not portfolio_item:
                    await query.answer("Проект не найден")
                    return
                
                # Увеличиваем счетчик просмотров
                portfolio_item.views_count += 1
                db.commit()
            
            # Формируем детальное описание
            text = f"💼 <b>{portfolio_item.title}</b>\n\n"
            text += f"📝 <b>Описание:</b>\n{portfolio_item.description}\n\n"
            
            if portfolio_item.technologies:
                tech_list = '\n'.join(f"• {tech}" for tech in portfolio_item.technologies)
                text += f"🔧 <b>Технологии:</b>\n{tech_list}\n\n"
            
            # Характеристики проекта
            text += "<b>📊 Характеристики:</b>\n"
            
            if portfolio_item.complexity_level:
                complexity_text = "Простой" if portfolio_item.complexity_level <= 3 else \
                                "Средний" if portfolio_item.complexity_level <= 6 else \
                                "Сложный" if portfolio_item.complexity_level <= 8 else "Премиум"
                text += f"• Сложность: {complexity_text} ({portfolio_item.complexity_level}/10)\n"
            
            if portfolio_item.development_time:
                text += f"• Время разработки: {portfolio_item.development_time} дней\n"
            
            if portfolio_item.cost_range:
                text += f"• Стоимость: {portfolio_item.cost_range}₽\n"
            
            text += f"• Просмотров: {portfolio_item.views_count}\n\n"
            
            # Создаем клавиатуру для действий
            keyboard = self._create_details_keyboard(portfolio_item)
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_portfolio_details: {e}")
    
    def _create_details_keyboard(self, portfolio_item: Portfolio) -> InlineKeyboardMarkup:
        """Создание клавиатуры для детального просмотра"""
        keyboard = []
        
        # Кнопка демо если есть ссылка
        if portfolio_item.demo_link:
            keyboard.append([
                InlineKeyboardButton("🎮 Попробовать демо", url=portfolio_item.demo_link)
            ])
        
        # Действия
        action_row = []
        action_row.append(
            InlineKeyboardButton("📤 Поделиться", callback_data=f"share_portfolio_{portfolio_item.id}")
        )
        action_row.append(
            InlineKeyboardButton("💬 Заказать похожий", callback_data=f"order_similar_{portfolio_item.id}")
        )
        
        keyboard.append(action_row)
        
        # Навигация
        keyboard.append([
            InlineKeyboardButton("⬅️ Назад к списку", callback_data=f"portfolio_{portfolio_item.category}"),
            InlineKeyboardButton("💼 Портфолио", callback_data="portfolio")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def _show_empty_portfolio(self, update: Update, category: str):
        """Показать сообщение о пустом портфолио"""
        category_names = {
            'telegram': 'Telegram ботов',
            'whatsapp': 'WhatsApp ботов',
            'web': 'веб-ботов',
            'integration': 'интеграций',
            'featured': 'рекомендуемых работ'
        }
        
        category_name = category_names.get(category, 'проектов')
        
        text = f"""
📭 <b>Пока нет примеров {category_name}</b>

Но мы активно работаем над пополнением портфолио!

Тем временем вы можете:
• 🤖 Проконсультироваться с AI
• 📝 Создать техническое задание
• 💬 Связаться с нами для обсуждения проекта
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Другие категории", callback_data="portfolio")],
            [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")],
            [InlineKeyboardButton("📝 Создать ТЗ", callback_data="create_tz")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])
        
        await update.callback_query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )

# Создаем глобальный экземпляр обработчика
portfolio_handler = PortfolioHandler()