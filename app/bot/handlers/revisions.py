from typing import List, Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
import os
import uuid
import asyncio
from pathlib import Path

from ..keyboards.main import (
    get_project_revisions_keyboard, 
    get_revision_actions_keyboard,
    get_revision_priority_keyboard,
    get_confirm_revision_keyboard,
    get_file_type_keyboard
)
from ...database.database import get_db_context
from ...database.models import User, Project, ProjectRevision, RevisionMessage, RevisionFile, RevisionMessageFile
from ...config.logging import get_logger, log_user_action
from ...utils.decorators import standard_handler
from ...utils.helpers import format_datetime, format_currency, time_ago

logger = get_logger(__name__)

class RevisionsHandler:
    """Обработчик управления правками проектов"""
    
    def __init__(self):
        self.revisions_per_page = 5
        # Директория для загрузки файлов правок
        self.upload_dir = Path("uploads/revisions/bot")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    @standard_handler
    async def show_project_revisions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать правки проекта"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            project_id = int(query.data.replace('project_revisions_', ''))
            
            log_user_action(user_id, "show_project_revisions", str(project_id))
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                
                # Проверяем, что проект принадлежит пользователю
                project = db.query(Project).filter(
                    Project.id == project_id,
                    Project.user_id == user.id
                ).first()
                
                if not project:
                    await query.answer("Проект не найден")
                    return
                
                # Получаем правки проекта
                revisions = db.query(ProjectRevision).filter(
                    ProjectRevision.project_id == project_id,
                    ProjectRevision.created_by_id == user.id
                ).order_by(ProjectRevision.created_at.desc()).all()
                
                # Извлекаем данные проекта и правок пока сессия активна
                project_data = {
                    'id': project.id,
                    'title': project.title
                }
                
                revisions_data = []
                for revision in revisions:
                    revisions_data.append({
                        'id': revision.id,
                        'revision_number': revision.revision_number,
                        'title': revision.title,
                        'status': revision.status,
                        'priority': revision.priority,
                        'created_at': revision.created_at
                    })
            
            if not revisions_data:
                text = f"""
📋 <b>Правки проекта "{project_data['title']}"</b>

❌ <b>У вас пока нет правок по этому проекту</b>

💡 <i>Если нужно что-то исправить или добавить в проект, создайте правку.</i>

<b>Как создать правку:</b>
• Нажмите "📝 Создать правку"
• Опишите, что нужно изменить
• Приложите скриншоты или файлы (по желанию)
• Выберите приоритет
• Отправьте правку

После отправки исполнитель и администратор получат уведомление и начнут работу над исправлениями.
                """
            else:
                # Статистика по правкам
                stats = self._calculate_revision_stats_from_data(revisions_data)
                
                text = f"""
📋 <b>Правки проекта "{project_data['title']}"</b>

📊 <b>Статистика:</b>
• Всего правок: {stats['total']}
• В ожидании: {stats['pending']}
• В работе: {stats['in_progress']}
• Выполнено: {stats['completed']}

📝 <b>Последние правки:</b>
                """
                
                # Показываем последние 3 правки
                for revision_data in revisions_data[:3]:
                    status_emoji = self._get_revision_status_emoji(revision_data['status'])
                    priority_emoji = self._get_revision_priority_emoji(revision_data['priority'])
                    
                    text += f"""
{status_emoji} <b>#{revision_data['revision_number']}</b> - {revision_data['title']}
{priority_emoji} Приоритет: {self._get_revision_priority_name(revision_data['priority'])}
📅 {time_ago(revision_data['created_at'])}
                    """
                
                if len(revisions_data) > 3:
                    text += f"\n<i>... и еще {len(revisions_data) - 3} правок</i>"
            
            keyboard = get_project_revisions_keyboard(project_id, len(revisions_data))
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_project_revisions: {e}")
            await query.answer("Произошла ошибка при загрузке правок")
    
    @standard_handler
    async def list_project_revisions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список всех правок проекта"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            project_id = int(query.data.replace('list_revisions_', ''))
            
            log_user_action(user_id, "list_project_revisions", str(project_id))
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                
                # Получаем все правки проекта
                revisions = db.query(ProjectRevision).filter(
                    ProjectRevision.project_id == project_id,
                    ProjectRevision.created_by_id == user.id
                ).order_by(ProjectRevision.created_at.desc()).all()
                
                project = db.query(Project).filter(Project.id == project_id).first()
                
                if not project:
                    await query.answer("Проект не найден")
                    return
                
                # Извлекаем данные проекта и правок пока сессия активна
                project_data = {
                    'id': project.id,
                    'title': project.title
                }
                
                revisions_data = []
                for revision in revisions:
                    revisions_data.append({
                        'id': revision.id,
                        'revision_number': revision.revision_number,
                        'title': revision.title,
                        'status': revision.status,
                        'priority': revision.priority,
                        'description': revision.description,
                        'created_at': revision.created_at
                    })
            
            if not revisions_data:
                await query.answer("Правки не найдены")
                return
            
            text = f"""
📋 <b>Все правки проекта "{project_data['title']}"</b>

            """
            
            for revision_data in revisions_data:
                status_emoji = self._get_revision_status_emoji(revision_data['status'])
                priority_emoji = self._get_revision_priority_emoji(revision_data['priority'])
                
                text += f"""
{status_emoji} <b>#{revision_data['revision_number']}</b> - {revision_data['title']}
{priority_emoji} {self._get_revision_priority_name(revision_data['priority'])} | 📅 {time_ago(revision_data['created_at'])}
💬 {revision_data['description'][:50]}{'...' if len(revision_data['description']) > 50 else ''}

"""
            
            # Создаем клавиатуру для выбора правки
            keyboard = []
            for revision_data in revisions_data[:10]:  # Показываем до 10 правок
                status_emoji = self._get_revision_status_emoji(revision_data['status'])
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status_emoji} #{revision_data['revision_number']} - {revision_data['title'][:20]}...",
                        callback_data=f"revision_details_{revision_data['id']}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 К правкам", callback_data=f"project_revisions_{project_id}")])
            keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в list_project_revisions: {e}")
            await query.answer("Произошла ошибка при загрузке списка правок")
    
    @standard_handler
    async def start_create_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать создание правки"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            project_id = int(query.data.replace('create_revision_', ''))
            
            log_user_action(user_id, "start_create_revision", str(project_id))
            
            # Сохраняем ID проекта в контексте
            context.user_data['creating_revision_project_id'] = project_id
            context.user_data['creating_revision_step'] = 'title'
            
            with get_db_context() as db:
                project = db.query(Project).filter(Project.id == project_id).first()
                
                if not project:
                    await query.answer("Проект не найден")
                    return
                
                # Извлекаем данные проекта пока сессия активна
                project_data = {
                    'id': project.id,
                    'title': project.title
                }
            
            text = f"""
📝 <b>Создание правки для проекта "{project_data['title']}"</b>

<b>Шаг 1 из 3: Заголовок правки</b>

Введите короткий заголовок, который описывает суть правки.

<b>Примеры:</b>
• "Исправить цвет кнопки"
• "Добавить функцию поиска"  
• "Изменить текст на главной"
• "Исправить баг с авторизацией"

💡 <i>Заголовок должен быть коротким, но понятным.</i>
            """
            
            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data=f"project_revisions_{project_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в start_create_revision: {e}")
            await query.answer("Произошла ошибка при создании правки")
    
    @standard_handler
    async def handle_revision_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать заголовок правки"""
        try:
            if not update.message or not update.message.text:
                return
            
            user_id = update.effective_user.id
            
            # Проверяем, что пользователь находится в процессе создания правки
            if (context.user_data.get('creating_revision_step') != 'title' or 
                'creating_revision_project_id' not in context.user_data):
                return
            
            title = update.message.text.strip()
            
            if len(title) < 5:
                await update.message.reply_text(
                    "❌ Заголовок слишком короткий. Минимум 5 символов."
                )
                return
            
            if len(title) > 200:
                await update.message.reply_text(
                    "❌ Заголовок слишком длинный. Максимум 200 символов."
                )
                return
            
            # Сохраняем заголовок
            context.user_data['creating_revision_title'] = title
            context.user_data['creating_revision_step'] = 'description'
            
            log_user_action(user_id, "revision_title_entered", title)
            
            project_id = context.user_data['creating_revision_project_id']
            
            text = f"""
📝 <b>Создание правки</b>

✅ <b>Заголовок:</b> {title}

<b>Шаг 2 из 3: Описание правки</b>

Теперь подробно опишите, что именно нужно исправить или изменить.

<b>Хорошее описание включает:</b>
• Что именно не работает или не нравится
• Как это должно работать/выглядеть
• На какой странице/в каком разделе проблема
• Дополнительные детали

<b>Пример:</b>
"На главной странице синяя кнопка 'Заказать' слишком яркая и режет глаза. Нужно сделать её более мягкого оттенка, например, как на странице контактов. Также кнопка слишком большая - можно уменьшить на 20%."

💡 <i>Чем подробнее опишете - тем точнее исполним!</i>
            """
            
            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data=f"project_revisions_{project_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_revision_title: {e}")
    
    @standard_handler
    async def handle_revision_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать описание правки"""
        try:
            logger.info(f"🔍 handle_revision_description called with update: {update}")
            
            if not update.message or not update.message.text:
                logger.info(f"🔍 No message or text in update")
                return
            
            user_id = update.effective_user.id
            
            # Проверяем, что пользователь находится в процессе создания правки
            if (context.user_data.get('creating_revision_step') != 'description' or 
                'creating_revision_project_id' not in context.user_data):
                logger.info(f"🔍 Wrong step or no project id: step={context.user_data.get('creating_revision_step')}, project_id={context.user_data.get('creating_revision_project_id')}")
                return
            
            description = update.message.text.strip()
            
            logger.info(f"🔍 Revision description received: '{description}' (length: {len(description)})")
            
            if len(description) < 10:
                logger.info(f"🔍 Revision description too short: {len(description)} < 10")
                await update.message.reply_text(
                    "❌ Описание слишком короткое. Минимум 10 символов."
                )
                return
            
            # Сохраняем описание
            context.user_data['creating_revision_description'] = description
            context.user_data['creating_revision_step'] = 'files'
            
            logger.info(f"🔍 Revision description saved, step changed to 'files'")
            
            log_user_action(user_id, "revision_description_entered", description[:100])
            
            project_id = context.user_data['creating_revision_project_id']
            title = context.user_data['creating_revision_title']
            
            text = f"""
📝 <b>Создание правки</b>

✅ <b>Заголовок:</b> {title}
✅ <b>Описание:</b> {description[:100]}{'...' if len(description) > 100 else ''}

<b>Шаг 3 из 4: Файлы (необязательно)</b>

Приложите скриншоты или файлы, которые помогут лучше понять проблему:

📷 <b>Скриншоты</b> - изображения проблемы
📄 <b>Документы</b> - технические документы
🎥 <b>Видео</b> - запись экрана с проблемой

💡 <i>Файлы помогут исполнителю быстрее понять задачу. Вы можете пропустить этот шаг, если файлы не нужны.</i>
            """
            
            keyboard = [
                [InlineKeyboardButton("➡️ Пропустить", callback_data=f"skip_files_{project_id}")],
                [InlineKeyboardButton("❌ Отмена", callback_data=f"project_revisions_{project_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_revision_description: {e}")
    
    @standard_handler
    async def handle_revision_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать файлы правки"""
        try:
            logger.info(f"🔍 Revision files handler called: user_data={context.user_data}")
            
            if not update.message:
                logger.info(f"🔍 Revision files handler: no message")
                return
            
            user_id = update.effective_user.id
            
            # Проверяем, что пользователь находится в процессе создания правки
            if (context.user_data.get('creating_revision_step') != 'files' or 
                'creating_revision_project_id' not in context.user_data):
                logger.info(f"🔍 Revision files handler: wrong step or no project id")
                return
            
            # Инициализируем список файлов если его нет
            if 'creating_revision_files' not in context.user_data:
                context.user_data['creating_revision_files'] = []
            
            # Обрабатываем файл
            file_info = None
            if update.message.photo:
                # Получаем самое качественное фото
                file_info = update.message.photo[-1]
                file_type = "image"
            elif update.message.document:
                file_info = update.message.document
                file_type = "document"
            elif update.message.video:
                file_info = update.message.video
                file_type = "video"
            
            if file_info:
                # Сохраняем информацию о файле
                context.user_data['creating_revision_files'].append({
                    'file_id': file_info.file_id,
                    'file_type': file_type,
                    'file_name': getattr(file_info, 'file_name', f"{file_type}_{len(context.user_data['creating_revision_files']) + 1}"),
                    'file_size': getattr(file_info, 'file_size', 0)
                })
                
                log_user_action(user_id, "revision_file_added", f"{file_type}_{len(context.user_data['creating_revision_files'])}")
                
                files_count = len(context.user_data['creating_revision_files'])
                project_id = context.user_data['creating_revision_project_id']
                
                text = f"""
📝 <b>Создание правки</b>

✅ <b>Файлов добавлено:</b> {files_count}

Вы можете добавить еще файлы или перейти к следующему шагу.

💡 <i>Максимум 10 файлов. Поддерживаются: изображения, документы, видео.</i>
                """
                
                keyboard = [
                    [InlineKeyboardButton("➡️ Далее", callback_data=f"files_done_{project_id}")],
                    [InlineKeyboardButton("❌ Отмена", callback_data=f"project_revisions_{project_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                
                logger.info(f"🔍 Revision file processed successfully: {file_type}, total files: {files_count}")
            else:
                await update.message.reply_text(
                    "❌ Неподдерживаемый тип файла. Пожалуйста, отправьте изображение, документ или видео."
                )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_revision_files: {e}")
    
    @standard_handler
    async def skip_revision_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Пропустить добавление файлов"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            project_id = int(query.data.replace('skip_files_', ''))
            
            # Проверяем, что пользователь находится в процессе создания правки
            if (context.user_data.get('creating_revision_step') != 'files' or 
                context.user_data.get('creating_revision_project_id') != project_id):
                await query.answer("Ошибка: данные не найдены")
                return
            
            # Переходим к выбору приоритета
            context.user_data['creating_revision_step'] = 'priority'
            
            log_user_action(user_id, "revision_files_skipped")
            
            title = context.user_data['creating_revision_title']
            description = context.user_data['creating_revision_description']
            
            text = f"""
📝 <b>Создание правки</b>

✅ <b>Заголовок:</b> {title}
✅ <b>Описание:</b> {description[:100]}{'...' if len(description) > 100 else ''}
✅ <b>Файлы:</b> Не добавлены

<b>Шаг 4 из 4: Приоритет</b>

Выберите приоритет для этой правки:

🟢 <b>Низкий</b> - мелкие улучшения, не срочно
🔵 <b>Обычный</b> - стандартные правки  
🟡 <b>Высокий</b> - важные исправления
🔴 <b>Срочный</b> - критические ошибки

💡 <i>От приоритета зависит очередность выполнения.</i>
            """
            
            keyboard = get_revision_priority_keyboard(project_id)
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в skip_revision_files: {e}")
            await query.answer("Произошла ошибка")
    
    @standard_handler
    async def files_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Завершить добавление файлов"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            project_id = int(query.data.replace('files_done_', ''))
            
            # Проверяем, что пользователь находится в процессе создания правки
            if (context.user_data.get('creating_revision_step') != 'files' or 
                context.user_data.get('creating_revision_project_id') != project_id):
                await query.answer("Ошибка: данные не найдены")
                return
            
            # Переходим к выбору приоритета
            context.user_data['creating_revision_step'] = 'priority'
            
            log_user_action(user_id, "revision_files_done")
            
            title = context.user_data['creating_revision_title']
            description = context.user_data['creating_revision_description']
            files_count = len(context.user_data.get('creating_revision_files', []))
            
            text = f"""
📝 <b>Создание правки</b>

✅ <b>Заголовок:</b> {title}
✅ <b>Описание:</b> {description[:100]}{'...' if len(description) > 100 else ''}
✅ <b>Файлы:</b> {files_count} шт.

<b>Шаг 4 из 4: Приоритет</b>

Выберите приоритет для этой правки:

🟢 <b>Низкий</b> - мелкие улучшения, не срочно
🔵 <b>Обычный</b> - стандартные правки  
🟡 <b>Высокий</b> - важные исправления
🔴 <b>Срочный</b> - критические ошибки

💡 <i>От приоритета зависит очередность выполнения.</i>
            """
            
            keyboard = get_revision_priority_keyboard(project_id)
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в files_done: {e}")
            await query.answer("Произошла ошибка")
    
    @standard_handler
    async def handle_revision_priority(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать выбор приоритета правки"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            # Извлекаем приоритет из callback_data
            callback_parts = query.data.split('_')
            priority = callback_parts[1]  # low, normal, high, urgent
            project_id = int(callback_parts[2])
            
            # Проверяем, что пользователь находится в процессе создания правки
            if (context.user_data.get('creating_revision_step') != 'priority' or 
                context.user_data.get('creating_revision_project_id') != project_id):
                await query.answer("Ошибка: данные не найдены")
                return
            
            # Сохраняем приоритет
            context.user_data['creating_revision_priority'] = priority
            
            log_user_action(user_id, "revision_priority_selected", priority)
            
            title = context.user_data['creating_revision_title']
            description = context.user_data['creating_revision_description']
            
            text = f"""
📝 <b>Создание правки - Подтверждение</b>

✅ <b>Заголовок:</b> {title}
✅ <b>Описание:</b> {description}
✅ <b>Приоритет:</b> {self._get_revision_priority_emoji(priority)} {self._get_revision_priority_name(priority)}

<b>Что дальше:</b>
1. Ваша правка будет отправлена исполнителю и администратору
2. Они получат уведомление и возьмут правку в работу
3. Вы получите уведомление, когда правка будет выполнена
4. После выполнения вы сможете проверить результат

💡 <i>После создания правки вы сможете добавить файлы и комментарии.</i>
            """
            
            keyboard = get_confirm_revision_keyboard(project_id)
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_revision_priority: {e}")
            await query.answer("Произошла ошибка при выборе приоритета")
    
    @standard_handler
    async def confirm_create_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтвердить создание правки"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            project_id = int(query.data.replace('confirm_revision_', ''))
            
            # Проверяем данные в контексте
            if (context.user_data.get('creating_revision_project_id') != project_id or
                'creating_revision_title' not in context.user_data or
                'creating_revision_description' not in context.user_data):
                await query.answer("Ошибка: данные не найдены")
                return
            
            # Если приоритет не установлен, устанавливаем по умолчанию
            if 'creating_revision_priority' not in context.user_data:
                context.user_data['creating_revision_priority'] = 'normal'
            
            title = context.user_data['creating_revision_title']
            description = context.user_data['creating_revision_description']
            priority = context.user_data['creating_revision_priority']
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                
                # Проверяем проект
                project = db.query(Project).filter(
                    Project.id == project_id,
                    Project.user_id == user.id
                ).first()
                
                if not project:
                    await query.answer("Проект не найден")
                    return
                
                # Получаем номер следующей правки для проекта
                max_revision_number = db.query(ProjectRevision.revision_number).filter(
                    ProjectRevision.project_id == project_id
                ).order_by(ProjectRevision.revision_number.desc()).first()
                
                next_revision_number = (max_revision_number[0] if max_revision_number else 0) + 1
                
                # Создаем правку
                revision = ProjectRevision(
                    project_id=project_id,
                    revision_number=next_revision_number,
                    title=title,
                    description=description,
                    priority=priority,
                    status='pending',
                    created_by_id=user.id
                )
                
                db.add(revision)
                db.commit()
                db.refresh(revision)
                
                # Сохраняем файлы правки
                files_data = context.user_data.get('revision_files', [])
                logger.info(f"📁 Сохранение файлов правки: {len(files_data)} файлов")
                
                for file_data in files_data:
                    try:
                        logger.info(f"📁 Обработка файла: {file_data['original_filename']}")
                        
                        # Создаем папку для файлов правки
                        revision_dir = self.upload_dir / f"revision_{revision.id}"
                        revision_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Файл уже скачан, нужно только переместить его
                        current_file_path = Path(file_data['file_path'])
                        
                        # Генерируем новое имя файла
                        file_extension = Path(file_data['original_filename']).suffix or '.file'
                        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                        new_file_path = revision_dir / unique_filename
                        
                        # Перемещаем файл
                        if current_file_path.exists():
                            try:
                                import shutil
                                shutil.move(str(current_file_path), str(new_file_path))
                                logger.info(f"📁 Файл перемещен: {current_file_path} -> {new_file_path}")
                            except Exception as move_error:
                                logger.error(f"❌ Ошибка перемещения файла: {move_error}")
                                continue
                        else:
                            logger.error(f"❌ Файл не найден: {current_file_path}")
                            continue
                        
                        # Создаем запись в БД
                        revision_file = RevisionFile(
                            revision_id=revision.id,
                            filename=unique_filename,
                            original_filename=file_data['original_filename'],
                            file_type=file_data['file_type'],
                            file_size=file_data.get('file_size', 0),
                            file_path=str(new_file_path),
                            uploaded_by_type='client',
                            uploaded_by_user_id=user.id,
                            description=f"Файл загружен при создании правки"
                        )
                        
                        db.add(revision_file)
                        logger.info(f"📁 Файл сохранен: {unique_filename}")
                        
                    except Exception as e:
                        logger.error(f"Ошибка сохранения файла правки: {e}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        continue
                
                db.commit()
                
                # Создаем первое сообщение в чате с описанием правки и файлами
                await self._create_initial_revision_message(revision, user)
                
                # Сохраняем данные правки для уведомления
                revision_data = {
                    'id': revision.id,
                    'revision_number': revision.revision_number,
                    'title': revision.title,
                    'status': revision.status,
                    'priority': revision.priority
                }
                
                # Очищаем данные создания правки
                for key in list(context.user_data.keys()):
                    if key.startswith('creating_revision'):
                        del context.user_data[key]
                
                log_user_action(user_id, "revision_created", f"#{revision.revision_number}")
            
            # Отправляем уведомление исполнителю и администратору
            await self._send_revision_notification(revision)
            
            text = f"""
✅ <b>Правка создана успешно!</b>

📋 <b>#{revision_data['revision_number']}</b> - {title}
📅 <b>Создана:</b> Только что
📊 <b>Статус:</b> В ожидании
🎯 <b>Приоритет:</b> {self._get_revision_priority_emoji(priority)} {self._get_revision_priority_name(priority)}

<b>Что дальше:</b>
• Исполнитель и администратор получили уведомление
• Правка будет обработана в ближайшее время
• Вы получите уведомление о начале работы
• После выполнения вы получите уведомление

💡 <i>Вы можете добавить файлы и комментарии к правке.</i>
            """
            
            keyboard = get_revision_actions_keyboard(revision_data['id'], project_id, revision_data['status'])
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            # Очищаем данные из контекста
            context.user_data.pop('creating_revision_project_id', None)
            context.user_data.pop('creating_revision_title', None)
            context.user_data.pop('creating_revision_description', None)
            context.user_data.pop('creating_revision_priority', None)
            context.user_data.pop('creating_revision_step', None)
            context.user_data.pop('revision_files', None)
            
        except Exception as e:
            logger.error(f"Ошибка в confirm_create_revision: {e}")
            await query.answer("Произошла ошибка при создании правки")
    
    @standard_handler
    async def show_revision_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать детали правки"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id
            
            revision_id = int(query.data.replace('revision_details_', ''))
            
            log_user_action(user_id, "show_revision_details", str(revision_id))
            
            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)
                
                # Получаем правку
                revision = db.query(ProjectRevision).filter(
                    ProjectRevision.id == revision_id,
                    ProjectRevision.created_by_id == user.id
                ).first()
                
                if not revision:
                    await query.answer("Правка не найдена")
                    return
                
                # Извлекаем данные правки пока сессия активна
                revision_data = {
                    'id': revision.id,
                    'revision_number': revision.revision_number,
                    'title': revision.title,
                    'description': revision.description,
                    'status': revision.status,
                    'priority': revision.priority,
                    'project_id': revision.project_id,
                    'created_at': revision.created_at,
                    'updated_at': revision.updated_at,
                    'completed_at': revision.completed_at,
                    'estimated_time': revision.estimated_time,
                    'actual_time': revision.actual_time,
                    'project_title': revision.project.title if revision.project else 'Неизвестно',
                    'assigned_to_username': revision.assigned_to.username if revision.assigned_to else 'Не назначен'
                }
                
                # Получаем количество сообщений и файлов
                messages_count = len(revision.messages) if revision.messages else 0
                files_count = len(revision.files) if revision.files else 0
            
            text = f"""
📋 <b>Правка #{revision_data['revision_number']}</b>

<b>📝 Заголовок:</b> {revision_data['title']}

<b>📄 Описание:</b>
{revision_data['description']}

<b>📊 Информация:</b>
• Статус: {self._get_revision_status_emoji(revision_data['status'])} {self._get_revision_status_name(revision_data['status'])}
• Приоритет: {self._get_revision_priority_emoji(revision_data['priority'])} {self._get_revision_priority_name(revision_data['priority'])}
• Проект: {revision_data['project_title']}
• Исполнитель: {revision_data['assigned_to_username']}

<b>📅 Время:</b>
• Создана: {format_datetime(revision_data['created_at'])}
• Обновлена: {format_datetime(revision_data['updated_at'])}
{f'• Завершена: {format_datetime(revision_data["completed_at"])}' if revision_data['completed_at'] else ''}

<b>💬 Активность:</b>
• Сообщений: {messages_count}
• Файлов: {files_count}
{f'• Оценочное время: {revision_data["estimated_time"]} ч.' if revision_data['estimated_time'] else ''}
{f'• Фактическое время: {revision_data["actual_time"]} ч.' if revision_data['actual_time'] else ''}
            """
            
            keyboard = get_revision_actions_keyboard(revision_data['id'], revision_data['project_id'], revision_data['status'])
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в show_revision_details: {e}")
            await query.answer("Произошла ошибка при загрузке деталей правки")
    
    # Вспомогательные методы
    def _calculate_revision_stats(self, revisions: List[ProjectRevision]) -> Dict[str, int]:
        """Подсчитать статистику по правкам"""
        stats = {
            'total': len(revisions),
            'pending': 0,
            'in_progress': 0,
            'completed': 0,
            'rejected': 0
        }
        
        for revision in revisions:
            if revision.status in stats:
                stats[revision.status] += 1
        
        return stats
    
    def _calculate_revision_stats_from_data(self, revisions_data: List[dict]) -> Dict[str, int]:
        """Подсчитать статистику по правкам из данных"""
        stats = {
            'total': len(revisions_data),
            'pending': 0,
            'in_progress': 0,
            'completed': 0,
            'rejected': 0
        }
        
        for revision_data in revisions_data:
            if revision_data['status'] in stats:
                stats[revision_data['status']] += 1
        
        return stats
    
    def _get_revision_status_emoji(self, status: str) -> str:
        """Получить эмодзи для статуса правки"""
        emojis = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'rejected': '❌'
        }
        return emojis.get(status, '❓')
    
    def _get_revision_status_name(self, status: str) -> str:
        """Получить название статуса правки"""
        names = {
            'pending': 'В ожидании',
            'in_progress': 'В работе',
            'completed': 'Выполнено',
            'rejected': 'Отклонено'
        }
        return names.get(status, status)
    
    def _get_revision_priority_emoji(self, priority: str) -> str:
        """Получить эмодзи для приоритета правки"""
        emojis = {
            'low': '🟢',
            'normal': '🔵',
            'high': '🟡',
            'urgent': '🔴'
        }
        return emojis.get(priority, '⚪')
    
    def _get_revision_priority_name(self, priority: str) -> str:
        """Получить название приоритета правки"""
        names = {
            'low': 'Низкий',
            'normal': 'Обычный',
            'high': 'Высокий',
            'urgent': 'Срочный'
        }
        return names.get(priority, priority)
    
    async def _create_initial_revision_message(self, revision: ProjectRevision, user: User):
        """Создать первое сообщение в чате с описанием правки"""
        try:
            from ...database.database import get_db_context
            
            with get_db_context() as db:
                # Формируем сообщение с описанием правки
                priority_emoji = self._get_revision_priority_emoji(revision.priority)
                priority_name = self._get_revision_priority_name(revision.priority)
                
                message_text = f"""📝 Новая правка #{revision.revision_number}

🎯 Заголовок: {revision.title}

📋 Описание:
{revision.description}

{priority_emoji} Приоритет: {priority_name}

👤 Создал: {user.first_name or user.username or 'Клиент'}"""
                
                # Создаем сообщение в чате
                revision_message = RevisionMessage(
                    revision_id=revision.id,
                    sender_type="client",
                    sender_user_id=user.id,
                    message=message_text,
                    is_internal=False
                )
                
                db.add(revision_message)
                db.commit()
                db.refresh(revision_message)
                
                # Добавляем файлы к сообщению, если они есть
                if revision.files:
                    for revision_file in revision.files:
                        try:
                            # Создаем файл сообщения на основе файла правки
                            message_file = RevisionMessageFile(
                                message_id=revision_message.id,
                                filename=revision_file.filename,
                                original_filename=revision_file.original_filename,
                                file_type=revision_file.file_type,
                                file_size=revision_file.file_size,
                                file_path=revision_file.file_path
                            )
                            
                            db.add(message_file)
                            
                        except Exception as e:
                            logger.error(f"Ошибка добавления файла к сообщению: {e}")
                            continue
                
                db.commit()
                
                logger.info(f"🎯 Создано первое сообщение в чате для правки #{revision.revision_number}")
                
        except Exception as e:
            logger.error(f"Ошибка создания первого сообщения в чате: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    async def _send_revision_notification(self, revision: ProjectRevision):
        """Отправить уведомление о создании правки"""
        try:
            from ...services.notification_service import notification_service
            from ...database.database import get_db_context
            
            with get_db_context() as db:
                # Получаем данные проекта и клиента
                project = db.get(Project, revision.project_id)
                client_user = db.get(User, project.user_id)
                
                # Отправляем уведомление о новой правке
                logger.info(f"📢 Отправляем уведомление о новой правке #{revision.revision_number}")
                try:
                    result = await notification_service.notify_new_revision(revision, project, client_user)
                    logger.info(f"📢 Результат отправки уведомления: {result}")
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки уведомления: {e}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                
            logger.info(f"Revision notification sent for revision #{revision.revision_number}")
            
        except Exception as e:
            logger.error(f"Error sending revision notification: {e}")

    async def handle_revision_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка фотографий при создании правки"""
        try:
            user_id = update.effective_user.id
            
            logger.info(f"📸 REVISION PHOTO HANDLER: user_id={user_id}")
            
            # Проверяем, что пользователь на этапе добавления файлов
            if context.user_data.get('creating_revision_step') != 'files':
                logger.warning(f"📸 User {user_id} sent photo but not in files step")
                await update.message.reply_text(
                    "📷 Фотография получена, но вы сейчас не создаете правку. Используйте /start для возврата в меню."
                )
                return
            
            # Получаем наибольшее фото
            photo = update.message.photo[-1]
            
            # Получаем информацию о файле
            file = await context.bot.get_file(photo.file_id)
            
            # Создаем имя файла
            file_extension = file.file_path.split('.')[-1] if '.' in file.file_path else 'jpg'
            filename = f"photo_{uuid.uuid4().hex}.{file_extension}"
            
            # Сохраняем файл
            file_path = self.upload_dir / filename
            await file.download_to_drive(str(file_path))
            
            # Сохраняем информацию о файле в context
            if 'revision_files' not in context.user_data:
                context.user_data['revision_files'] = []
            
            context.user_data['revision_files'].append({
                'filename': filename,
                'original_filename': f"photo.{file_extension}",
                'file_path': str(file_path),
                'file_type': 'image',
                'file_size': file.file_size
            })
            
            project_id = context.user_data.get('creating_revision_project_id')
            await update.message.reply_text(
                f"📷 Фотография добавлена!\n\n"
                f"📎 Файлов прикреплено: {len(context.user_data['revision_files'])}\n\n"
                f"Можете добавить еще файлы или нажать 'Завершить' для завершения создания правки.",
                reply_markup=get_confirm_revision_keyboard(project_id)
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_revision_photo: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке фотографии. Попробуйте еще раз."
            )

    async def handle_revision_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка документов при создании правки"""
        try:
            user_id = update.effective_user.id
            document = update.message.document
            
            logger.info(f"📄 REVISION DOCUMENT HANDLER: user_id={user_id}, filename={document.file_name}")
            
            # Проверяем, что пользователь на этапе добавления файлов
            if context.user_data.get('creating_revision_step') != 'files':
                logger.warning(f"📄 User {user_id} sent document but not in files step")
                await update.message.reply_text(
                    f"📄 Документ '{document.file_name}' получен, но вы сейчас не создаете правку. Используйте /start для возврата в меню."
                )
                return
            
            # Получаем информацию о файле
            file = await context.bot.get_file(document.file_id)
            
            # Создаем имя файла
            file_extension = document.file_name.split('.')[-1] if '.' in document.file_name else 'file'
            filename = f"doc_{uuid.uuid4().hex}.{file_extension}"
            
            # Сохраняем файл
            file_path = self.upload_dir / filename
            await file.download_to_drive(str(file_path))
            
            # Определяем тип файла
            file_type = self._get_file_type(document.file_name)
            
            # Сохраняем информацию о файле в context
            if 'revision_files' not in context.user_data:
                context.user_data['revision_files'] = []
            
            context.user_data['revision_files'].append({
                'filename': filename,
                'original_filename': document.file_name,
                'file_path': str(file_path),
                'file_type': file_type,
                'file_size': file.file_size
            })
            
            project_id = context.user_data.get('creating_revision_project_id')
            await update.message.reply_text(
                f"📄 Документ '{document.file_name}' добавлен!\n\n"
                f"📎 Файлов прикреплено: {len(context.user_data['revision_files'])}\n\n"
                f"Можете добавить еще файлы или нажать 'Завершить' для завершения создания правки.",
                reply_markup=get_confirm_revision_keyboard(project_id)
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка в handle_revision_document: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке документа. Попробуйте еще раз."
            )

    def _get_file_type(self, filename: str) -> str:
        """Определить тип файла по расширению"""
        if not filename:
            return 'other'
        
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
            return 'image'
        elif extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv']:
            return 'video'
        elif extension in ['pdf', 'doc', 'docx', 'txt', 'rtf']:
            return 'document'
        else:
            return 'other'

# Создаем экземпляр обработчика
revisions_handler = RevisionsHandler()
