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
    
    # Определяем состояния для ConversationHandler
    CATEGORY, PROJECT = range(2)

    def __init__(self):
        self.items_per_page = 3
        self.base_url = f"http://147.45.215.199:{settings.ADMIN_PORT}"
        self.media_base_url = f"http://147.45.215.199:{settings.ADMIN_PORT}/uploads/portfolio"
    
    def get_image_url(self, image_path: str) -> str:
        """Получить полный URL изображения"""
        if not image_path:
            return ""
        # Удаляем префикс uploads/ если он есть в пути
        clean_path = image_path.replace("uploads/portfolio/", "").replace("uploads/", "")
        return f"{self.base_url}/uploads/portfolio/{clean_path}"
    
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
            error_text = "⚠️ Произошла ошибка при загрузке портфолио. Попробуйте позже."
            error_keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
            ]])
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    error_text,
                    reply_markup=error_keyboard
                )
            else:
                await update.message.reply_text(
                    error_text,
                    reply_markup=error_keyboard
                )
    
    @standard_handler
    async def show_category_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать портфолио по категории"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Парсим категорию из callback_data
            if query.data == "portfolio_featured":
                category = None
                featured_only = True
                category_name = "⭐ Рекомендуемые работы"
            else:
                category = query.data.replace('portfolio_category_', '')
                featured_only = False
                category_name = self._get_category_name(category)
            
            page = 1
            
            log_user_action(user_id, "show_category_portfolio", category or "featured")
            
            await self._display_portfolio_page(update, context, category, page, featured_only, category_name)
            
        except Exception as e:
            logger.error(f"Ошибка в show_category_portfolio: {e}")
            await self._send_error_message(update)
    
    @standard_handler
    async def show_portfolio_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
        """Показывает страницу портфолио с пагинацией"""
        try:
            query = update.callback_query
            data_parts = query.data.split('_')
            
            if len(data_parts) < 3:
                return
            
            category = data_parts[2] if data_parts[2] != "featured" else None
            featured_only = data_parts[2] == "featured"
            page = int(data_parts[3]) if len(data_parts) > 3 else 1
            
            category_name = self._get_category_name(category) if category else "⭐ Рекомендуемые работы"
            
            await self._display_portfolio_page(update, context, category, page, featured_only, category_name)
            
        except Exception as e:
            logger.error(f"Ошибка в show_portfolio_page: {e}")
            await self._send_error_message(update)
    
    @standard_handler
    async def show_project_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детали проекта"""
        try:
            query = update.callback_query
            project_id = int(query.data.split('_')[2])
            user_id = update.effective_user.id
            
            log_user_action(user_id, "show_project_details", project_id)
            
            # Получаем проект через API
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/{project_id}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        project = data.get("data")
                    else:
                        raise Exception("Проект не найден")
                else:
                    # Fallback: получаем из базы напрямую
                    project = await self._get_project_from_db(project_id)
            except:
                # Fallback: получаем из базы напрямую
                project = await self._get_project_from_db(project_id)
            
            if not project:
                await query.answer("❌ Проект не найден", show_alert=True)
                return
            
            # Формируем детальное описание проекта
            text = self._format_project_details(project)
            
            # Создаем клавиатуру для проекта
            keyboard = self._create_project_keyboard(project)
            
            # Если есть главное изображение, отправляем с фото
            main_image = project.get("main_image")
            if main_image:
                image_url = self.get_image_url(main_image)
                try:
                    await query.edit_message_media(
                        media=InputMediaPhoto(
                            media=image_url,
                            caption=text,
                            parse_mode='HTML'
                        ),
                        reply_markup=keyboard
                    )
                except:
                    # Если не получилось отправить изображение, отправляем текстом
                    await query.edit_message_text(
                        text,
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )
            else:
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"Ошибка в show_project_details: {e}")
            await self._send_error_message(update)
    
    @standard_handler
    async def show_project_gallery(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать галерею проекта"""
        try:
            query = update.callback_query
            project_id = int(query.data.split('_')[2])
            user_id = update.effective_user.id
            
            log_user_action(user_id, "show_project_gallery", project_id)
            
            # Получаем проект
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/{project_id}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        project = data.get("data")
                    else:
                        raise Exception("Проект не найден")
                else:
                    project = await self._get_project_from_db(project_id)
            except:
                project = await self._get_project_from_db(project_id)
            
            if not project:
                await query.answer("❌ Проект не найден", show_alert=True)
                return
            
            # Собираем все изображения
            images = []
            
            # Главное изображение
            if project.get("main_image"):
                images.append(self.get_image_url(project["main_image"]))
            
            # Дополнительные изображения
            image_paths = project.get("image_paths", [])
            for image_path in image_paths:
                images.append(self.get_image_url(image_path))
            
            if not images:
                await query.answer("📷 У этого проекта нет изображений", show_alert=True)
                return
            
            # Создаем медиа группу
            media_group = []
            for i, image_url in enumerate(images[:10]):  # Максимум 10 изображений
                if i == 0:
                    # Первое изображение с описанием
                    caption = f"🖼 <b>{project.get('title', 'Проект')}</b>\n\n{project.get('subtitle', '')}"
                    media_group.append(InputMediaPhoto(media=image_url, caption=caption, parse_mode='HTML'))
                else:
                    media_group.append(InputMediaPhoto(media=image_url))
            
            # Отправляем галерею
            await query.message.reply_media_group(media_group)
            
            # Отправляем кнопку возврата
            back_keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Вернуться к проекту", callback_data=f"project_{project_id}")
            ]])
            
            await query.message.reply_text(
                "📷 Галерея проекта выше",
                reply_markup=back_keyboard
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_project_gallery: {e}")
            await query.answer("❌ Ошибка загрузки галереи", show_alert=True)
    
    @standard_handler
    async def like_project(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Поставить лайк проекту"""
        try:
            query = update.callback_query
            project_id = int(query.data.split('_')[2])
            user_id = update.effective_user.id
            
            log_user_action(user_id, "like_project", project_id)
            
            # Отправляем лайк через API
            try:
                response = requests.post(f"{self.base_url}/admin/api/portfolio/public/{project_id}/like", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        likes_count = data.get("likes_count", 0)
                        await query.answer(f"👍 Спасибо за оценку! Всего лайков: {likes_count}", show_alert=True)
                    else:
                        await query.answer("❌ Ошибка при обработке лайка", show_alert=True)
                else:
                    await query.answer("❌ Ошибка сервера", show_alert=True)
            except:
                # Fallback: обновляем в базе напрямую
                await self._like_project_in_db(project_id)
                await query.answer("👍 Спасибо за оценку!", show_alert=True)
                
        except Exception as e:
            logger.error(f"Ошибка в like_project: {e}")
            await query.answer("❌ Ошибка при обработке лайка", show_alert=True)
    
    async def _display_portfolio_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    category: str = None, page: int = 1, featured_only: bool = False,
                                    category_name: str = "Портфолио"):
        """Отобразить страницу портфолио"""
        try:
            # Получаем проекты через API
            params = {
                "page": page,
                "per_page": self.items_per_page,
                "featured_only": featured_only
            }
            
            if category:
                params["category"] = category
            
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/list", 
                                      params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        projects = data.get("data", [])
                        pagination = data.get("pagination", {})
                    else:
                        projects = []
                        pagination = {}
                else:
                    # Fallback: получаем из базы напрямую
                    projects, pagination = await self._get_projects_from_db(category, page, featured_only)
            except:
                # Fallback: получаем из базы напрямую
                projects, pagination = await self._get_projects_from_db(category, page, featured_only)
            
            if not projects:
                text = f"""
📂 <b>{category_name}</b>

К сожалению, в данной категории пока нет проектов.
                """
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К категориям", callback_data="portfolio")
                ]])
            else:
                # Формируем текст с проектами
                text = f"📂 <b>{category_name}</b>\n\n"
                
                for i, project in enumerate(projects, 1):
                    text += self._format_project_brief(project, (page - 1) * self.items_per_page + i)
                    text += "\n" + "─" * 30 + "\n\n"
                
                # Создаем клавиатуру с проектами и пагинацией
                keyboard = self._create_portfolio_keyboard(projects, category, page, pagination, featured_only)
            
            # Отправляем сообщение
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
            logger.error(f"Ошибка в _display_portfolio_page: {e}")
            await self._send_error_message(update)
    
    def _format_project_brief(self, project: dict, index: int) -> str:
        """Форматировать краткое описание проекта"""
        title = project.get("title", "Без названия")
        subtitle = project.get("subtitle", "")
        complexity = project.get("complexity", "medium")
        development_time = project.get("development_time")
        technologies = project.get("technologies", [])
        views_count = project.get("views_count", 0)
        likes_count = project.get("likes_count", 0)
        
        # Эмодзи для сложности
        complexity_emoji = {
            "simple": "🟢",
            "medium": "🟡", 
            "complex": "🔴",
            "premium": "🟣"
        }
        
        text = f"<b>{index}. {title}</b>"
        
        if subtitle:
            text += f"\n<i>{subtitle}</i>"
        
        # Краткое описание (первые 150 символов)
        description = project.get("description", "")
        if description:
            short_desc = (description[:147] + "...") if len(description) > 150 else description
            text += f"\n\n{short_desc}"
        
        # Технологии
        if technologies:
            tech_list = technologies[:3]  # Первые 3 технологии
            text += f"\n\n🛠 <b>Технологии:</b> {', '.join(tech_list)}"
            if len(technologies) > 3:
                text += f" и еще {len(technologies) - 3}"
        
        # Сложность и время
        info_line = f"\n\n{complexity_emoji.get(complexity, '⚪')} <b>Сложность:</b> {complexity.title()}"
        
        if development_time:
            info_line += f" | ⏱ <b>Время:</b> {development_time} дн."
        
        text += info_line
        
        # Статистика
        if views_count or likes_count:
            text += f"\n👀 {views_count} | 👍 {likes_count}"
        
        return text
    
    def _format_project_details(self, project: dict) -> str:
        """Форматировать детальное описание проекта"""
        title = project.get("title", "Без названия")
        subtitle = project.get("subtitle", "")
        description = project.get("description", "")
        technologies = project.get("technologies", [])
        complexity = project.get("complexity", "medium")
        complexity_level = project.get("complexity_level", 5)
        development_time = project.get("development_time")
        cost_display = project.get("cost_display")
        demo_link = project.get("demo_link")
        views_count = project.get("views_count", 0)
        likes_count = project.get("likes_count", 0)
        
        # Эмодзи для сложности
        complexity_emoji = {
            "simple": "🟢",
            "medium": "🟡", 
            "complex": "🔴",
            "premium": "🟣"
        }
        
        text = f"🎯 <b>{title}</b>"
        
        if subtitle:
            text += f"\n<i>{subtitle}</i>"
        
        text += "\n" + "=" * 30 + "\n"
        
        # Описание
        if description:
            text += f"\n📋 <b>Описание:</b>\n{description}\n"
        
        # Технологии
        if technologies:
            text += f"\n🛠 <b>Технологии:</b>\n"
            for tech in technologies[:8]:  # Максимум 8 технологий
                text += f"• {tech}\n"
            if len(technologies) > 8:
                text += f"• и еще {len(technologies) - 8} технологий\n"
        
        # Характеристики проекта
        text += f"\n📊 <b>Характеристики:</b>\n"
        text += f"• {complexity_emoji.get(complexity, '⚪')} Сложность: {complexity.title()} ({complexity_level}/10)\n"
        
        if development_time:
            text += f"• ⏱ Время разработки: {development_time} дней\n"
        
        if cost_display:
            text += f"• 💰 Стоимость: {cost_display} ₽\n"
        
        # Демо и ссылки
        if demo_link:
            text += f"\n🚀 <b>Демо доступно!</b>\n"
        
        # Статистика
        text += f"\n📈 <b>Статистика:</b>\n"
        text += f"• 👀 Просмотров: {views_count}\n"
        text += f"• 👍 Лайков: {likes_count}"
        
        return text
    
    def _create_project_keyboard(self, project: dict) -> InlineKeyboardMarkup:
        """Создать клавиатуру для проекта"""
        keyboard_buttons = []
        project_id = project.get("id")
        
        # Первая строка - основные действия
        first_row = []
        
        # Кнопка галереи (если есть дополнительные изображения)
        image_paths = project.get("image_paths", [])
        if image_paths:
            first_row.append(InlineKeyboardButton("📷 Галерея", callback_data=f"gallery_{project_id}"))
        
        # Кнопка демо (если доступно)
        demo_link = project.get("demo_link")
        if demo_link:
            first_row.append(InlineKeyboardButton("🚀 Демо", url=demo_link))
        
        # Кнопка лайка
        likes_count = project.get("likes_count", 0)
        first_row.append(InlineKeyboardButton(f"👍 {likes_count}", callback_data=f"like_{project_id}"))
        
        if first_row:
            keyboard_buttons.append(first_row)
        
        # Вторая строка - навигация
        keyboard_buttons.append([
            InlineKeyboardButton("📂 К категориям", callback_data="portfolio"),
            InlineKeyboardButton("🔙 Назад", callback_data="portfolio_back")
        ])
        
        return InlineKeyboardMarkup(keyboard_buttons)
    
    def _create_portfolio_keyboard(self, projects: list, category: str = None, page: int = 1, 
                                 pagination: dict = None, featured_only: bool = False) -> InlineKeyboardMarkup:
        """Создать клавиатуру для списка портфолио"""
        keyboard_buttons = []
        
        # Кнопки проектов
        for project in projects:
            project_id = project.get("id")
            title = project.get("title", "Проект")
            keyboard_buttons.append([
                InlineKeyboardButton(f"📋 {title}", callback_data=f"project_{project_id}")
            ])
        
        # Пагинация
        if pagination:
            nav_buttons = []
            has_prev = page > 1
            has_next = pagination.get("has_next", False)
            
            if has_prev:
                prev_callback = f"page_{category or 'featured'}_{page - 1}"
                nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=prev_callback))
            
            # Показываем текущую страницу
            total_pages = pagination.get("pages", 1)
            nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))
            
            if has_next:
                next_callback = f"page_{category or 'featured'}_{page + 1}"
                nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=next_callback))
            
            if nav_buttons:
                keyboard_buttons.append(nav_buttons)
        
        # Кнопка возврата к категориям
        keyboard_buttons.append([
            InlineKeyboardButton("📂 К категориям", callback_data="portfolio")
        ])
        
        return InlineKeyboardMarkup(keyboard_buttons)
    
    def _get_category_name(self, category: str) -> str:
        """Получить название категории"""
        category_map = {
            "telegram_bots": "🤖 Telegram боты",
            "web_development": "🌐 Веб-разработка", 
            "mobile_apps": "📱 Мобильные приложения",
            "ai_integration": "🧠 AI интеграции",
            "automation": "⚡ Автоматизация",
            "ecommerce": "🛒 E-commerce",
            "other": "📦 Другое"
        }
        return category_map.get(category, category.replace("_", " ").title())
    
    async def _get_categories_from_db(self) -> list:
        """Fallback: получить категории из базы данных напрямую"""
        try:
            async with get_db_context() as db:
                categories = db.query(Portfolio.category).filter(
                    Portfolio.category.isnot(None),
                    Portfolio.is_visible == True
                ).distinct().all()
                
                category_list = [cat[0] for cat in categories if cat[0]]
                
                result = []
                for cat in category_list:
                    result.append({
                        "id": cat,
                        "name": self._get_category_name(cat)
                    })
                
                return result
        except Exception as e:
            logger.error(f"Ошибка получения категорий из БД: {e}")
            return []
    
    async def _get_projects_from_db(self, category: str = None, page: int = 1, 
                                  featured_only: bool = False) -> tuple:
        """Fallback: получить проекты из базы данных напрямую"""
        try:
            async with get_db_context() as db:
                query = db.query(Portfolio).filter(Portfolio.is_visible == True)
                
                if featured_only:
                    query = query.filter(Portfolio.is_featured == True)
                
                if category:
                    query = query.filter(Portfolio.category == category)
                
                # Сортировка
                query = query.order_by(
                    Portfolio.sort_order.desc(),
                    Portfolio.is_featured.desc(),
                    Portfolio.created_at.desc()
                )
                
                # Подсчитываем общее количество
                total = query.count()
                
                # Применяем пагинацию
                offset = (page - 1) * self.items_per_page
                projects = query.offset(offset).limit(self.items_per_page).all()
                
                # Преобразуем в словари
                projects_data = [project.to_bot_dict() for project in projects]
                
                pagination = {
                    "page": page,
                    "per_page": self.items_per_page,
                    "total": total,
                    "has_next": offset + self.items_per_page < total
                }
                
                return projects_data, pagination
                
        except Exception as e:
            logger.error(f"Ошибка получения проектов из БД: {e}")
            return [], {}
    
    async def _get_project_from_db(self, project_id: int) -> dict:
        """Fallback: получить проект из базы данных напрямую"""
        try:
            async with get_db_context() as db:
                project = db.query(Portfolio).filter(
                    Portfolio.id == project_id,
                    Portfolio.is_visible == True
                ).first()
                
                if project:
                    # Увеличиваем счетчик просмотров
                    project.views_count += 1
                    db.commit()
                    return project.to_bot_dict()
                
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения проекта из БД: {e}")
            return None
    
    async def _like_project_in_db(self, project_id: int):
        """Fallback: поставить лайк проекту в базе данных напрямую"""
        try:
            async with get_db_context() as db:
                project = db.query(Portfolio).filter(Portfolio.id == project_id).first()
                if project:
                    project.likes_count += 1
                    db.commit()
        except Exception as e:
            logger.error(f"Ошибка лайка проекта в БД: {e}")
    
    async def _send_error_message(self, update: Update):
        """Отправить сообщение об ошибке"""
        try:
            error_text = "⚠️ Произошла ошибка. Попробуйте позже."
            error_keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Назад", callback_data="main_menu")
            ]])
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    error_text,
                    reply_markup=error_keyboard
                )
            else:
                await update.message.reply_text(
                    error_text,
                    reply_markup=error_keyboard
                )
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения об ошибке: {e}")
    
    @standard_handler
    async def select_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора категории портфолио."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            callback_data = query.data
            
            # Извлекаем категорию из callback_data
            category_map = {
                "portfolio_telegram": "telegram_bot",
                "portfolio_whatsapp": "whatsapp", 
                "portfolio_web": "web",
                "portfolio_integration": "ai_integration",
                "portfolio_featured": "featured",
                "portfolio_all": "all"
            }
            
            category = category_map.get(callback_data, "all")
            
            log_user_action(user_id, "select_portfolio_category", category)
            
            # Получаем проекты из выбранной категории
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/list", 
                                      params={"category": category}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    projects = data.get("data", [])
                else:
                    # Fallback: получаем из базы напрямую
                    projects = await self._get_projects_from_db(category)
            except Exception as e:
                logger.error(f"Ошибка получения проектов: {e}")
                projects = await self._get_projects_from_db(category)
            
            if not projects:
                category_names = {
                    "telegram_bot": "🤖 Telegram боты",
                    "whatsapp": "💬 WhatsApp боты",
                    "web": "🌐 Веб-боты",
                    "ai_integration": "🧠 AI интеграции",
                    "featured": "⭐ Рекомендуемые",
                    "all": "📊 Все проекты"
                }
                
                text = f"""
💼 <b>{category_names.get(category, 'Портфолио')}</b>

В этой категории пока нет проектов.

Перейдите в другую категорию или свяжитесь с нами для создания нового проекта!
                """
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К категориям", callback_data="portfolio")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
                
                await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
                return
            
            # Показываем первую страницу проектов
            context.user_data['portfolio_category'] = category
            context.user_data['portfolio_projects'] = projects
            context.user_data['portfolio_page'] = 0
            
            await self._show_projects_page(query, projects, category, 0)
            
        except Exception as e:
            logger.error(f"Ошибка в select_category: {e}")
            await query.edit_message_text(
                "❌ Произошла ошибка при загрузке проектов",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            )

    async def _get_projects_from_db(self, category: str) -> List[Dict]:
        """Получить проекты из базы данных"""
        try:
            with get_db_context() as db:
                query = db.query(Portfolio).filter(Portfolio.is_visible == True)
                
                if category != "all":
                    if category == "featured":
                        query = query.filter(Portfolio.is_featured == True)
                    else:
                        query = query.filter(Portfolio.category == category)
                
                portfolio_items = query.order_by(Portfolio.created_at.desc()).all()
                
                projects = []
                for item in portfolio_items:
                    projects.append({
                        "id": item.id,
                        "title": item.title,
                        "description": item.description,
                        "category": item.category,
                        "image_url": self.get_image_url(item.main_image),
                        "technologies": item.technologies,
                        "link": item.link,
                        "is_featured": item.is_featured
                    })
                
                return projects
                
        except Exception as e:
            logger.error(f"Ошибка получения проектов из БД: {e}")
            return []
    
    async def _show_projects_page(self, query, projects: List[Dict], category: str, page: int):
        """Показать страницу проектов"""
        try:
            total_pages = (len(projects) + self.items_per_page - 1) // self.items_per_page
            start_idx = page * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_projects = projects[start_idx:end_idx]
            
            category_names = {
                "telegram_bot": "🤖 Telegram боты",
                "whatsapp": "💬 WhatsApp боты", 
                "web": "🌐 Веб-боты",
                "ai_integration": "🧠 AI интеграции",
                "featured": "⭐ Рекомендуемые",
                "all": "📊 Все проекты"
            }
            
            text = f"""
💼 <b>{category_names.get(category, 'Портфолио')}</b>

Страница {page + 1} из {total_pages}
Всего проектов: {len(projects)}

"""
            
            keyboard = []
            
            # Добавляем проекты с изображениями
            for project in page_projects:
                tech_str = ', '.join(project.get('technologies', [])[:3])
                if not tech_str:
                    tech_str = 'Не указаны'
                    
                text += f"""
<b>{project['title']}</b>
{project['description'][:100]}{'...' if len(project['description']) > 100 else ''}

🛠 Технологии: {tech_str}
{'⭐ Рекомендуемый проект' if project.get('is_featured') else ''}

"""
                
                keyboard.append([
                    InlineKeyboardButton(f"👁 {project['title']}", callback_data=f"project_{project['id']}")
                ])
            
            # Если у первого проекта есть изображение, отправляем с фото
            first_project = page_projects[0] if page_projects else None
            if first_project and first_project.get('main_image'):
                image_url = self.get_image_url(first_project['main_image'])
                try:
                    await query.edit_message_media(
                        media=InputMediaPhoto(
                            media=image_url,
                            caption=text,
                            parse_mode='HTML'
                        )
                    )
                    # Обновляем клавиатуру отдельно
                    keyboard.append([
                        InlineKeyboardButton("🔙 К категориям", callback_data="portfolio"),
                        InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                    ])
                    
                    await query.edit_message_reply_markup(
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    return
                except Exception as e:
                    logger.error(f"Ошибка отправки изображения: {e}")
                    # Продолжаем с текстовым сообщением
            
            # Кнопки навигации
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"portfolio_page_{page-1}"))
            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("▶️ Вперед", callback_data=f"portfolio_page_{page+1}"))
            
            if nav_buttons:
                keyboard.append(nav_buttons)
            
            # Кнопки управления
            keyboard.extend([
                [InlineKeyboardButton("🔙 К категориям", callback_data="portfolio")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Ошибка показа страницы проектов: {e}")
            await query.edit_message_text(
                "❌ Ошибка отображения проектов",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            )

    @standard_handler
    async def select_project(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора проекта портфолио."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            callback_data = query.data
            
            # Извлекаем ID проекта из callback_data (формат: project_123)
            project_id = int(callback_data.split('_')[1])
            
            log_user_action(user_id, "select_portfolio_project", str(project_id))
            
            # Получаем детали проекта
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/project/{project_id}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    project = data.get("project")
                else:
                    # Fallback: получаем из базы напрямую
                    project = await self._get_project_from_db(project_id)
            except Exception as e:
                logger.error(f"Ошибка получения проекта: {e}")
                project = await self._get_project_from_db(project_id)
            
            if not project:
                await query.edit_message_text(
                    "❌ Проект не найден",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")],
                        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                    ])
                )
                return
            
            # Формируем сообщение с деталями проекта
            text = f"""
💼 <b>{project['title']}</b>

📝 <b>Описание:</b>
{project['description']}

🛠 <b>Технологии:</b>
{project.get('technologies', 'Не указаны')}

📂 <b>Категория:</b>
{project.get('category', 'Общая').title()}

{'⭐ <b>Рекомендуемый проект!</b>' if project.get('is_featured') else ''}

"""
            
            keyboard = []
            
            # Если есть ссылка на проект
            if project.get('link'):
                keyboard.append([
                    InlineKeyboardButton("🔗 Посмотреть проект", url=project['link'])
                ])
            
            # Кнопки действий
            keyboard.extend([
                [InlineKeyboardButton("💬 Обсудить проект", callback_data="consultation")],
                [InlineKeyboardButton("🚀 Создать похожий", callback_data="create_tz")],
                [InlineKeyboardButton("🔙 К списку", callback_data=f"portfolio_{project.get('category', 'all')}")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            # Если есть изображение, отправляем с картинкой
            if project.get('image_url'):
                try:
                    await query.delete_message()
                    await update.effective_chat.send_photo(
                        photo=project['image_url'],
                        caption=text,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='HTML'
                    )
                    return
                except Exception as e:
                    logger.error(f"Ошибка отправки изображения: {e}")
                    # Продолжаем без изображения
            
            # Отправляем без изображения
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Ошибка в select_project: {e}")
            await query.edit_message_text(
                "❌ Произошла ошибка при загрузке проекта",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            )
    
    async def _get_project_from_db(self, project_id: int) -> Dict:
        """Получить проект из базы данных"""
        try:
            with get_db_context() as db:
                project = db.query(Portfolio).filter(
                    Portfolio.id == project_id,
                    Portfolio.is_visible == True
                ).first()
                
                if project:
                    return {
                        "id": project.id,
                        "title": project.title,
                        "description": project.description,
                        "category": project.category,
                        "image_url": self.get_image_url(project.main_image),
                        "technologies": project.technologies,
                        "link": project.link,
                        "is_featured": project.is_featured
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения проекта из БД: {e}")
            return None

    @standard_handler
    async def handle_portfolio_navigation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка навигации по страницам портфолио"""
        try:
            query = update.callback_query
            await query.answer()
            
            # Извлекаем номер страницы из callback_data (формат: portfolio_page_1)
            page = int(query.data.split('_')[-1])
            
            # Получаем сохраненные данные
            category = context.user_data.get('portfolio_category', 'all')
            projects = context.user_data.get('portfolio_projects', [])
            
            if not projects:
                await query.edit_message_text(
                    "❌ Данные сессии потеряны. Попробуйте снова.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")],
                        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                    ])
                )
                return
            
            # Обновляем номер страницы
            context.user_data['portfolio_page'] = page
            
            # Показываем новую страницу
            await self._show_projects_page(query, projects, category, page)
            
        except Exception as e:
            logger.error(f"Ошибка навигации портфолио: {e}")
            await query.edit_message_text(
                "❌ Ошибка навигации",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            )


# Создаем экземпляр обработчика
portfolio_handler = PortfolioHandler()
