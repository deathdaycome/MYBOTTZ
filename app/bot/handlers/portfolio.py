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
        self.base_url = f"http://localhost:{settings.ADMIN_PORT}"
        self.media_base_url = f"http://localhost:{settings.ADMIN_PORT}/uploads/portfolio"
    
    def get_image_url(self, image_path: str) -> str:
        """Получить полный URL изображения"""
        if not image_path:
            return ""
        
        # Если путь уже содержит полный URL, возвращаем как есть
        if image_path.startswith("http://") or image_path.startswith("https://"):
            return image_path
        
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
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/categories", timeout=15)
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
                    category_key = category.get("key", "")
                    category_name = category.get("name", category_key)
                    keyboard_buttons.append([
                        InlineKeyboardButton(
                            category_name,
                            callback_data=f"portfolio_category_{category_key}"
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
                # Убираем префикс portfolio_ чтобы получить название категории
                category = query.data.replace('portfolio_', '')
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
            project_id = int(query.data.split('_')[1])
            user_id = update.effective_user.id
            
            log_user_action(user_id, "show_project_details", project_id)
            
            # Получаем проект из базы данных напрямую
            try:
                project = await self._get_project_from_db(project_id)
            except Exception as e:
                logger.error(f"Ошибка получения проекта {project_id} из БД: {e}")
                project = None
            
            if not project:
                await query.answer("❌ Проект не найден", show_alert=True)
                return
            
            # Формируем детальное описание проекта
            text = self._format_project_details(project)
            
            # Создаем клавиатуру для проекта
            keyboard = self._create_project_keyboard(project)
            
            # Всегда пытаемся показать с изображением
            image_url = None
            main_image = project.get("main_image")
            if main_image:
                image_url = self.get_image_url(main_image)
            
            # Если нет основного изображения, берем из галереи
            if not image_url:
                image_paths = project.get("image_paths", [])
                if image_paths:
                    image_url = self.get_image_url(image_paths[0])
            
            if image_url:
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
            project_id = int(query.data.split('_')[1])
            user_id = update.effective_user.id
            
            log_user_action(user_id, "show_project_gallery", project_id)
            
            # Получаем проект
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/{project_id}", timeout=15)
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
            project_id = int(query.data.split('_')[1])
            user_id = update.effective_user.id
            
            log_user_action(user_id, "like_project", project_id)
            
            # Отправляем лайк через API
            try:
                response = requests.post(f"{self.base_url}/admin/api/portfolio/public/{project_id}/like", timeout=15)
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
            
            # Используем прямое обращение к базе данных чтобы избежать проблем с HTTP запросами
            try:
                projects, pagination = await self._get_projects_from_db(category, page, featured_only)
            except Exception as e:
                logger.error(f"Ошибка получения проектов из БД: {e}")
                projects, pagination = [], {}
            
            if not projects:
                text = f"""
📂 <b>{category_name}</b>

К сожалению, в данной категории пока нет проектов.
                """
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К категориям", callback_data="portfolio")
                ]])
                
                # Отправляем сообщение об отсутствии проектов
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
            else:
                # Сохраняем данные для навигации
                context.user_data['portfolio_projects'] = projects
                context.user_data['portfolio_category'] = category or "featured"
                
                # Сразу показываем первый проект с изображением и навигацией
                await self._show_project_with_navigation(
                    update.callback_query, 
                    projects[0], 
                    projects, 
                    0, 
                    category or "featured"
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
        technologies = project.get("technologies", "")
        complexity = project.get("complexity", "medium")
        development_time = project.get("development_time")
        cost = project.get("cost")
        show_cost = project.get("show_cost", False)
        demo_link = project.get("demo_link")
        repository_link = project.get("repository_link")
        external_links = project.get("external_links", [])
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
        
        text += "\n" + "─" * 25 + "\n"
        
        # Описание
        if description:
            text += f"\n📝 <b>Описание:</b>\n{description}\n"
        
        # Технологии
        if technologies:
            tech_list = technologies.split(',') if isinstance(technologies, str) else technologies
            tech_formatted = [tech.strip() for tech in tech_list]
            text += f"\n🛠 <b>Технологии:</b>\n{', '.join(tech_formatted)}\n"
        
        # Характеристики проекта
        text += f"\n📊 <b>Характеристики:</b>"
        text += f"\n{complexity_emoji.get(complexity, '⚪')} Сложность: {complexity.title()}"
        
        if development_time:
            text += f"\n⏱ Время разработки: {development_time} дн."
        
        if show_cost and cost:
            text += f"\n💰 Стоимость: {cost:,.0f}₽"
        elif not show_cost:
            text += f"\n💰 Стоимость: По запросу"
        
        # Ссылки
        if demo_link or repository_link or external_links:
            text += f"\n\n🔗 <b>Ссылки:</b>"
            if demo_link:
                text += f"\n🚀 <a href='{demo_link}'>Демо-версия</a>"
            if repository_link:
                text += f"\n📂 <a href='{repository_link}'>Исходный код</a>"
            for link in external_links:
                if isinstance(link, dict):
                    link_title = link.get('title', 'Дополнительная ссылка')
                    link_url = link.get('url', '')
                    if link_url:
                        text += f"\n🌐 <a href='{link_url}'>{link_title}</a>"
        
        # Статистика
        text += f"\n\n📈 <b>Статистика:</b>"
        text += f"\n👀 Просмотров: {views_count}"
        text += f"\n👍 Лайков: {likes_count}"
        
        return text
    
    def _create_project_keyboard(self, project: dict) -> InlineKeyboardMarkup:
        """Создать клавиатуру для проекта"""
        keyboard_buttons = []
        project_id = project.get("id")
        
        # Первая строка - основные действия
        first_row = []
        
        # Убираем кнопку галереи, так как изображение теперь показывается сверху
        # image_paths = project.get("image_paths", [])
        # if image_paths:
        #     first_row.append(InlineKeyboardButton("📷 Галерея", callback_data=f"gallery_{project_id}"))
        
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
    
    @standard_handler
    async def show_project_gallery(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать галерею изображений проекта"""
        try:
            query = update.callback_query
            project_id = int(query.data.split('_')[1])
            user_id = update.effective_user.id
            
            log_user_action(user_id, "show_project_gallery", project_id)
            
            # Получаем проект через API
            try:
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/{project_id}", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        project = data.get("project")
                    else:
                        raise Exception("Проект не найден")
                else:
                    project = await self._get_project_from_db(project_id)
            except:
                project = await self._get_project_from_db(project_id)
            
            if not project:
                await query.answer("❌ Проект не найден", show_alert=True)
                return
            
            # Получаем все изображения проекта
            image_paths = project.get("image_paths", [])
            main_image = project.get("main_image")
            
            # Объединяем все изображения
            all_images = []
            if main_image:
                all_images.append(main_image)
            all_images.extend(image_paths)
            
            if not all_images:
                await query.answer("📷 У этого проекта нет изображений", show_alert=True)
                return
            
            # Создаем медиа-группу
            media_group = []
            title = project.get("title", "Проект")
            
            for i, image_path in enumerate(all_images):
                image_url = self.get_image_url(image_path)
                if i == 0:
                    # Первое изображение с описанием
                    caption = f"🎯 <b>{title}</b>\n\n📷 Галерея проекта ({i+1}/{len(all_images)})"
                    media_group.append(InputMediaPhoto(media=image_url, caption=caption, parse_mode='HTML'))
                else:
                    # Остальные изображения с номером
                    caption = f"📷 {i+1}/{len(all_images)}"
                    media_group.append(InputMediaPhoto(media=image_url, caption=caption))
            
            # Отправляем галерею
            try:
                await context.bot.send_media_group(
                    chat_id=query.message.chat_id,
                    media=media_group
                )
                
                # Отправляем кнопку возврата
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К проекту", callback_data=f"project_{project_id}")
                ]])
                
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="👆 Все изображения проекта",
                    reply_markup=keyboard
                )
                
                await query.answer("📷 Галерея загружена")
                
            except Exception as e:
                logger.error(f"Ошибка отправки галереи: {e}")
                await query.answer("❌ Ошибка загрузки галереи", show_alert=True)
            
        except Exception as e:
            logger.error(f"Ошибка в show_project_gallery: {e}")
            await query.answer("❌ Ошибка загрузки галереи", show_alert=True)
    
    @standard_handler
    async def like_project(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Лайкнуть проект"""
        try:
            query = update.callback_query
            project_id = int(query.data.split('_')[1])
            user_id = update.effective_user.id
            
            log_user_action(user_id, "like_project", project_id)
            
            # Отправляем лайк через API
            try:
                response = requests.post(f"{self.base_url}/admin/api/portfolio/public/{project_id}/like", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        likes_count = data.get("likes", 0)
                        message = data.get("message", "Спасибо за лайк!")
                        await query.answer(f"👍 {message} Всего лайков: {likes_count}")
                        
                        # Обновляем кнопку с новым количеством лайков
                        if query.message.reply_markup:
                            keyboard = query.message.reply_markup.inline_keyboard
                            for row in keyboard:
                                for button in row:
                                    if button.callback_data and button.callback_data.startswith(f"like_{project_id}"):
                                        button.text = f"👍 {likes_count}"
                                        break
                            
                            # Обновляем сообщение с новой клавиатурой
                            try:
                                await query.edit_message_reply_markup(
                                    reply_markup=InlineKeyboardMarkup(keyboard)
                                )
                            except:
                                pass  # Игнорируем ошибки обновления клавиатуры
                        
                        return
                    else:
                        error_msg = data.get("error", "Ошибка")
                        await query.answer(f"❌ {error_msg}", show_alert=True)
                        return
                else:
                    await query.answer("❌ Ошибка сервера", show_alert=True)
                    return
            except Exception as e:
                logger.error(f"Ошибка API лайка: {e}")
                await query.answer("❌ Ошибка отправки лайка", show_alert=True)
            
        except Exception as e:
            logger.error(f"Ошибка в like_project: {e}")
            await query.answer("❌ Ошибка", show_alert=True)
    
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
    
    def _get_category_emoji(self, category: str) -> str:
        """Получить эмодзи для категории"""
        category_emojis = {
            "telegram_bots": "🤖",
            "web_development": "🌐",
            "mobile_apps": "📱",
            "ai_integration": "🧠",
            "automation": "⚙️",
            "ecommerce": "🛒",
            "other": "🔧"
        }
        return category_emojis.get(category, "📦")
    
    async def _get_categories_from_db(self) -> list:
        """Fallback: получить категории из базы данных напрямую"""
        try:
            with get_db_context() as db:
                categories = db.query(Portfolio.category).filter(
                    Portfolio.category.isnot(None),
                    Portfolio.is_visible == True
                ).distinct().all()
                
                category_list = [cat[0] for cat in categories if cat[0]]
                
                result = []
                for cat in category_list:
                    result.append({
                        "key": cat,
                        "name": self._get_category_name(cat),
                        "emoji": self._get_category_emoji(cat)
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
        """Обработка выбора категории портфолио - показ первого проекта с навигацией."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            callback_data = query.data
            
            # Извлекаем категорию из callback_data
            category_map = {
                "portfolio_telegram": "telegram_bots",
                "portfolio_whatsapp": "whatsapp", 
                "portfolio_web": "web_development",
                "portfolio_integration": "ai_integration",
                "portfolio_featured": "featured",
                "portfolio_all": "all"
            }
            
            category = category_map.get(callback_data, "all")
            
            log_user_action(user_id, "select_portfolio_category", category)
            
            # Используем новую логику из show_category_portfolio
            # Преобразуем callback_data в новый формат
            new_callback_data = f"portfolio_{category}"
            
            # Временно изменяем query.data для совместимости
            original_data = query.data
            query.data = new_callback_data
            
            # Вызываем новую функцию
            await self.show_category_portfolio(update, context)
            
            # Восстанавливаем оригинальные данные
            query.data = original_data
            
        except Exception as e:
            logger.error(f"Ошибка в select_category: {e}")
            await query.edit_message_text(
                "❌ Произошла ошибка при загрузке проектов",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ])
            )

    async def _show_project_with_navigation(self, query, project, all_projects, current_index, category):
        """Показать проект с фото, описанием и кнопками навигации"""
        try:
            # Формируем красивое описание проекта
            title = project.get("title", "Без названия")
            description = project.get("description", "Описание отсутствует")
            technologies = project.get("technologies", "")
            demo_link = project.get("demo_link", "")
            repository_link = project.get("repository_link", "")
            development_time = project.get("development_time", "")
            cost = project.get("cost", "")
            show_cost = project.get("show_cost", False)
            
            # Получаем имя категории
            category_names = {
                "telegram_bots": "🤖 Telegram боты",
                "whatsapp": "💬 WhatsApp боты", 
                "web_development": "🌐 Веб-разработка",
                "ai_integration": "🧠 AI интеграции",
                "featured": "⭐ Рекомендуемые",
                "all": "📊 Все проекты"
            }
            category_name = category_names.get(category, category)
            
            # Формируем текст описания
            text = f"💼 <b>{category_name}</b>\n\n"
            text += f"🎯 <b>{title}</b>\n\n"
            text += f"📝 {description}\n\n"
            
            if technologies:
                # Обрабатываем как список (из to_bot_dict) или как строку (из других источников)
                if isinstance(technologies, list):
                    tech_list = technologies
                else:
                    tech_list = [tech.strip() for tech in technologies.split(',') if tech.strip()]
                
                if tech_list:
                    text += f"🛠 <b>Технологии:</b>\n"
                    text += f"{'  •  '.join(tech_list)}\n\n"
            
            if development_time:
                text += f"⏱ <b>Время разработки:</b> {development_time} дней\n"
            
            if cost and show_cost:
                text += f"💰 <b>Стоимость:</b> {cost:,.0f} ₽\n"
            elif not show_cost:
                text += f"💰 <b>Стоимость:</b> По запросу\n"
            
            text += f"\n📊 <b>Проект {current_index + 1} из {len(all_projects)}</b>"
            
            # Формируем кнопки навигации
            nav_buttons = []
            
            # Кнопки предыдущий/следующий
            nav_row = []
            if current_index > 0:
                nav_row.append(InlineKeyboardButton("⬅️ Предыдущий", callback_data=f"portfolio_nav_{current_index-1}"))
            if current_index < len(all_projects) - 1:
                nav_row.append(InlineKeyboardButton("➡️ Следующий", callback_data=f"portfolio_nav_{current_index+1}"))
            
            if nav_row:
                nav_buttons.append(nav_row)
            
            # Кнопки действий с проектом
            action_buttons = []
            if demo_link:
                action_buttons.append(InlineKeyboardButton("🌐 Демо", url=demo_link))
            if repository_link:
                action_buttons.append(InlineKeyboardButton("💻 Код", url=repository_link))
            
            project_id = project.get("id")
            if project_id:
                # Убираем кнопку галереи, так как изображение показывается сверху
                # action_buttons.append(InlineKeyboardButton("📷 Галерея", callback_data=f"gallery_{project_id}"))
                action_buttons.append(InlineKeyboardButton("❤️ Лайк", callback_data=f"like_{project_id}"))
            
            if action_buttons:
                # Разбиваем кнопки по 2 в ряд
                for i in range(0, len(action_buttons), 2):
                    nav_buttons.append(action_buttons[i:i+2])
            
            # Кнопки возврата
            nav_buttons.append([
                InlineKeyboardButton("🔙 К категориям", callback_data="portfolio"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ])
            
            keyboard = InlineKeyboardMarkup(nav_buttons)
            
            # Получаем изображение проекта
            main_image = project.get("main_image", "")
            
            # Всегда пытаемся показать с изображением
            image_url = None
            if main_image:
                logger.error(f"🖼️ ОТЛАДКА: main_image получен: {repr(main_image)}")
                image_url = self.get_image_url(main_image)
                logger.error(f"🔗 ОТЛАДКА: image_url после get_image_url: {repr(image_url)}")
            else:
                logger.error(f"❌ ОТЛАДКА: main_image пустой или None")
            
            # Если нет основного изображения, берем из галереи
            if not image_url:
                image_paths = project.get("image_paths", [])
                if image_paths:
                    image_url = self.get_image_url(image_paths[0])
            
            if image_url:
                try:
                    # Сначала пытаемся отредактировать как медиа
                    await query.edit_message_media(
                        media=InputMediaPhoto(media=image_url, caption=text, parse_mode='HTML'),
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logger.warning(f"Не удалось отредактировать сообщение как медиа: {e}")
                    try:
                        # Если не получилось отредактировать, удаляем старое и отправляем новое
                        await query.delete_message()
                        await query.message.reply_photo(
                            photo=image_url,
                            caption=text,
                            reply_markup=keyboard,
                            parse_mode='HTML'
                        )
                    except Exception as e2:
                        logger.error(f"Не удалось отправить изображение {image_url}: {e2}")
                        # В крайнем случае отправляем текстом
                        await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
            else:
                # Отправляем без фото
                await query.edit_message_text(text, reply_markup=keyboard, parse_mode='HTML')
                
        except Exception as e:
            logger.error(f"Ошибка в _show_project_with_navigation: {e}")
            await query.edit_message_text(
                "❌ Ошибка отображения проекта",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 К портфолио", callback_data="portfolio")]
                ])
            )

    @standard_handler
    async def navigate_project(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Навигация между проектами (предыдущий/следующий)"""
        try:
            query = update.callback_query
            
            # Безопасно извлекаем индекс
            try:
                data_parts = query.data.split('_')
                if len(data_parts) >= 3:
                    new_index = int(data_parts[2])
                else:
                    logger.error(f"Неверный формат callback_data: {query.data}")
                    await query.answer("❌ Ошибка навигации", show_alert=True)
                    return
            except (ValueError, AttributeError) as e:
                logger.error(f"Ошибка парсинга callback_data '{query.data}': {e}")
                await query.answer("❌ Ошибка навигации", show_alert=True)
                return
            
            # Получаем данные из контекста
            projects = context.user_data.get('portfolio_projects', [])
            category = context.user_data.get('portfolio_category', 'all')
            
            if not projects or new_index >= len(projects) or new_index < 0:
                await query.answer("❌ Проект не найден", show_alert=True)
                return
            
            # Обновляем индекс в контексте
            context.user_data['current_project_index'] = new_index
            
            # Показываем проект с новым индексом
            await self._show_project_with_navigation(query, projects[new_index], projects, new_index, category)
            
        except Exception as e:
            logger.error(f"Ошибка в navigate_project: {e}")
            await query.answer("❌ Ошибка навигации", show_alert=True)

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
                
                # Используем to_bot_dict() для правильного формирования URL
                projects = [item.to_bot_dict() for item in portfolio_items]
                
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
                response = requests.get(f"{self.base_url}/admin/api/portfolio/public/project/{project_id}", timeout=15)
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
                    # Увеличиваем счетчик просмотров
                    project.views_count = (project.views_count or 0) + 1
                    db.commit()
                    return project.to_bot_dict()
                
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
