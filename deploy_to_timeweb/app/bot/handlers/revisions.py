from typing import List, Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
import os
import uuid
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
            
            if not revisions:
                text = f"""
📋 <b>Правки проекта "{project.title}"</b>

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
                stats = self._calculate_revision_stats(revisions)
                
                text = f"""
📋 <b>Правки проекта "{project.title}"</b>

📊 <b>Статистика:</b>
• Всего правок: {stats['total']}
• В ожидании: {stats['pending']}
• В работе: {stats['in_progress']}
• Выполнено: {stats['completed']}

📝 <b>Последние правки:</b>
                """
                
                # Показываем последние 3 правки
                for revision in revisions[:3]:
                    status_emoji = self._get_revision_status_emoji(revision.status)
                    priority_emoji = self._get_revision_priority_emoji(revision.priority)
                    
                    text += f"""
{status_emoji} <b>#{revision.revision_number}</b> - {revision.title}
{priority_emoji} Приоритет: {self._get_revision_priority_name(revision.priority)}
📅 {time_ago(revision.created_at)}
                    """
                
                if len(revisions) > 3:
                    text += f"\n<i>... и еще {len(revisions) - 3} правок</i>"
            
            keyboard = get_project_revisions_keyboard(project_id, len(revisions))
            
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
            
            if not revisions:
                await query.answer("Правки не найдены")
                return
            
            text = f"""
📋 <b>Все правки проекта "{project.title}"</b>

            """
            
            for revision in revisions:
                status_emoji = self._get_revision_status_emoji(revision.status)
                priority_emoji = self._get_revision_priority_emoji(revision.priority)
                
                text += f"""
{status_emoji} <b>#{revision.revision_number}</b> - {revision.title}
{priority_emoji} {self._get_revision_priority_name(revision.priority)} | 📅 {time_ago(revision.created_at)}
💬 {revision.description[:50]}{'...' if len(revision.description) > 50 else ''}

"""
            
            # Создаем клавиатуру для выбора правки
            keyboard = []
            for revision in revisions[:10]:  # Показываем до 10 правок
                status_emoji = self._get_revision_status_emoji(revision.status)
                keyboard.append([
                    InlineKeyboardButton(
                        f"{status_emoji} #{revision.revision_number} - {revision.title[:20]}...",
                        callback_data=f"revision_details_{revision.id}"
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
            
            text = f"""
📝 <b>Создание правки для проекта "{project.title}"</b>

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
            if not update.message or not update.message.text:
                return
            
            user_id = update.effective_user.id
            
            # Проверяем, что пользователь находится в процессе создания правки
            if (context.user_data.get('creating_revision_step') != 'description' or 
                'creating_revision_project_id' not in context.user_data):
                return
            
            description = update.message.text.strip()
            
            if len(description) < 10:
                await update.message.reply_text(
                    "❌ Описание слишком короткое. Минимум 10 символов."
                )
                return
            
            # Сохраняем описание
            context.user_data['creating_revision_description'] = description
            context.user_data['creating_revision_step'] = 'priority'
            
            log_user_action(user_id, "revision_description_entered", description[:100])
            
            project_id = context.user_data['creating_revision_project_id']
            title = context.user_data['creating_revision_title']
            
            text = f"""
📝 <b>Создание правки</b>

✅ <b>Заголовок:</b> {title}
✅ <b>Описание:</b> {description[:100]}{'...' if len(description) > 100 else ''}

<b>Шаг 3 из 3: Приоритет</b>

Выберите приоритет для этой правки:

🟢 <b>Низкий</b> - мелкие улучшения, не срочно
🔵 <b>Обычный</b> - стандартные правки  
🟡 <b>Высокий</b> - важные исправления
🔴 <b>Срочный</b> - критические ошибки

💡 <i>От приоритета зависит очередность выполнения.</i>
            """
            
            keyboard = get_revision_priority_keyboard(project_id)
            
            await update.message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_revision_description: {e}")
    
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
                'creating_revision_description' not in context.user_data or
                'creating_revision_priority' not in context.user_data):
                await query.answer("Ошибка: данные не найдены")
                return
            
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
                
                # Очищаем данные создания правки
                for key in list(context.user_data.keys()):
                    if key.startswith('creating_revision'):
                        del context.user_data[key]
                
                log_user_action(user_id, "revision_created", f"#{revision.revision_number}")
            
            # TODO: Отправить уведомление исполнителю и администратору
            await self._send_revision_notification(revision)
            
            text = f"""
✅ <b>Правка создана успешно!</b>

📋 <b>#{revision.revision_number}</b> - {title}
📅 <b>Создана:</b> {format_datetime(revision.created_at)}
📊 <b>Статус:</b> В ожидании
🎯 <b>Приоритет:</b> {self._get_revision_priority_emoji(priority)} {self._get_revision_priority_name(priority)}

<b>Что дальше:</b>
• Исполнитель и администратор получили уведомление
• Правка будет обработана в ближайшее время
• Вы получите уведомление о начале работы
• После выполнения вы получите уведомление

💡 <i>Вы можете добавить файлы и комментарии к правке.</i>
            """
            
            keyboard = get_revision_actions_keyboard(revision.id, project_id, revision.status)
            
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
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
                
                # Получаем количество сообщений и файлов
                messages_count = len(revision.messages) if revision.messages else 0
                files_count = len(revision.files) if revision.files else 0
            
            text = f"""
📋 <b>Правка #{revision.revision_number}</b>

<b>📝 Заголовок:</b> {revision.title}

<b>📄 Описание:</b>
{revision.description}

<b>📊 Информация:</b>
• Статус: {self._get_revision_status_emoji(revision.status)} {self._get_revision_status_name(revision.status)}
• Приоритет: {self._get_revision_priority_emoji(revision.priority)} {self._get_revision_priority_name(revision.priority)}
• Проект: {revision.project.title if revision.project else 'Неизвестно'}
• Исполнитель: {revision.assigned_to.username if revision.assigned_to else 'Не назначен'}

<b>📅 Время:</b>
• Создана: {format_datetime(revision.created_at)}
• Обновлена: {format_datetime(revision.updated_at)}
{f'• Завершена: {format_datetime(revision.completed_at)}' if revision.completed_at else ''}

<b>💬 Активность:</b>
• Сообщений: {messages_count}
• Файлов: {files_count}
{f'• Оценочное время: {revision.estimated_time} ч.' if revision.estimated_time else ''}
{f'• Фактическое время: {revision.actual_time} ч.' if revision.actual_time else ''}
            """
            
            keyboard = get_revision_actions_keyboard(revision.id, revision.project_id, revision.status)
            
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
                await notification_service.notify_new_revision(revision, project, client_user)
                
            logger.info(f"Revision notification sent for revision #{revision.revision_number}")
            
        except Exception as e:
            logger.error(f"Error sending revision notification: {e}")

# Создаем экземпляр обработчика
revisions_handler = RevisionsHandler()
