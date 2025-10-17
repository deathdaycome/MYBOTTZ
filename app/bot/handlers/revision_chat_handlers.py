"""
Дополнительные обработчики для чата правок
"""
from typing import List, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

from ...database.database import get_db_context
from ...database.models import ProjectRevision, RevisionMessage, User, Project
from ...config.logging import get_logger, log_user_action
from ...utils.decorators import standard_handler
from ...utils.helpers import format_datetime, time_ago

logger = get_logger(__name__)


class RevisionChatHandlers:
    """Обработчики чата правок"""

    @standard_handler
    async def show_revision_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать чат правки"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            revision_id = int(query.data.replace('revision_chat_', ''))

            log_user_action(user_id, "show_revision_chat", str(revision_id))

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                # Получаем правку с проверкой через проект
                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await query.answer("Правка не найдена")
                    return

                # Получаем сообщения
                messages = db.query(RevisionMessage).filter(
                    RevisionMessage.revision_id == revision_id,
                    RevisionMessage.is_internal == False  # Только публичные сообщения
                ).order_by(RevisionMessage.created_at.desc()).limit(10).all()

                # Извлекаем данные
                revision_data = {
                    'id': revision.id,
                    'revision_number': revision.revision_number,
                    'title': revision.title,
                    'project_id': revision.project_id,
                    'status': revision.status
                }

                messages_data = []
                for msg in reversed(messages):  # Показываем от старых к новым
                    sender_name = "Неизвестно"
                    if msg.sender_type == "client" and msg.sender_user:
                        sender_name = msg.sender_user.first_name or msg.sender_user.username or "Вы"
                    elif msg.sender_type in ["admin", "executor"] and msg.sender_admin:
                        sender_name = f"{msg.sender_admin.first_name or ''} {msg.sender_admin.last_name or ''}".strip() or msg.sender_admin.username or "Команда"

                    messages_data.append({
                        'sender_name': sender_name,
                        'sender_type': msg.sender_type,
                        'message': msg.message,
                        'created_at': msg.created_at,
                        'files_count': len(msg.files) if msg.files else 0
                    })

            if not messages_data:
                text = f"""
💬 <b>Чат правки #{revision_data['revision_number']}</b>

<i>Сообщений пока нет.</i>

Напишите сообщение исполнителю - он получит уведомление и ответит вам.

Можно:
• Задать вопрос
• Уточнить детали
• Прикрепить файлы
• Отслеживать прогресс
                """
            else:
                text = f"""
💬 <b>Чат правки #{revision_data['revision_number']}</b>

<b>Последние {len(messages_data)} сообщений:</b>

"""
                for msg_data in messages_data:
                    sender_emoji = "👤" if msg_data['sender_type'] == "client" else "👨‍💼"
                    files_info = f" 📎 {msg_data['files_count']} файл(ов)" if msg_data['files_count'] > 0 else ""

                    text += f"""
{sender_emoji} <b>{msg_data['sender_name']}</b> • {time_ago(msg_data['created_at'])}
{msg_data['message'][:200]}{'...' if len(msg_data['message']) > 200 else ''}{files_info}

"""

            keyboard = [
                [InlineKeyboardButton("✍️ Написать сообщение", callback_data=f"revision_write_{revision_id}")],
                [InlineKeyboardButton("📎 Прикрепить файл", callback_data=f"revision_attach_{revision_id}")],
                [InlineKeyboardButton("🔄 Обновить", callback_data=f"revision_chat_{revision_id}")],
                [InlineKeyboardButton("🔙 К правке", callback_data=f"revision_details_{revision_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Пытаемся редактировать сообщение, если не получается - отправляем новое
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except Exception as edit_error:
                logger.warning(f"Cannot edit message, sending new one: {edit_error}")
                await query.answer()
                await query.message.reply_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )

        except Exception as e:
            logger.error(f"Ошибка в show_revision_chat: {e}")
            await query.answer("Произошла ошибка при загрузке чата")

    @standard_handler
    async def start_write_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать написание сообщения"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            logger.info(f"🔵 START_WRITE_MESSAGE вызван! user={user_id}, callback_data={query.data}")

            revision_id = int(query.data.replace('revision_write_', ''))
            logger.info(f"🔵 Извлечен revision_id={revision_id}")

            # Сохраняем ID правки в контексте
            context.user_data['writing_message_revision_id'] = revision_id
            context.user_data['writing_message_step'] = 'text'

            text = """
✍️ <b>Написать сообщение</b>

Введите текст сообщения, который хотите отправить исполнителю.

Исполнитель получит уведомление и ответит вам в этом чате.

<i>Для отмены используйте кнопку ниже.</i>
            """

            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data=f"revision_chat_{revision_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в start_write_message: {e}")
            await query.answer("Произошла ошибка")

    @standard_handler
    async def close_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Закрыть чат правки"""
        try:
            query = update.callback_query
            revision_id = int(query.data.replace('revision_close_chat_', ''))

            # Очищаем контекст
            context.user_data.pop('writing_message_revision_id', None)
            context.user_data.pop('writing_message_step', None)

            await query.answer("Чат закрыт")

            # Возвращаемся к деталям правки
            from .revisions import revisions_handler
            await revisions_handler.show_revision_details(update, context)

        except Exception as e:
            logger.error(f"Ошибка в close_chat: {e}")
            await query.answer("Произошла ошибка")

    @standard_handler
    async def handle_chat_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать текст сообщения в чат"""
        try:
            if not update.message or not update.message.text:
                return

            user_id = update.effective_user.id

            # Проверяем что пользователь пишет сообщение
            if (context.user_data.get('writing_message_step') != 'text' or
                'writing_message_revision_id' not in context.user_data):
                return

            message_text = update.message.text.strip()
            revision_id = context.user_data['writing_message_revision_id']

            if len(message_text) < 1:
                await update.message.reply_text("❌ Сообщение не может быть пустым.")
                return

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                # Проверяем правку через проект
                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await update.message.reply_text("❌ Правка не найдена.")
                    return

                # Создаем сообщение
                revision_message = RevisionMessage(
                    revision_id=revision_id,
                    sender_type="client",
                    sender_user_id=user.id,
                    message=message_text,
                    is_internal=False,
                    created_at=datetime.utcnow()
                )

                db.add(revision_message)
                db.commit()
                db.refresh(revision_message)

                # Логируем для отладки
                logger.info(f"💬 Сообщение сохранено в БД: message_id={revision_message.id}, revision_id={revision_id}, sender_type=client, sender_user_id={user.id}")
                logger.info(f"💬 Текст сообщения: {message_text[:100]}...")

                # Получаем данные проекта для уведомления
                project = db.get(Project, revision.project_id)

                log_user_action(user_id, "revision_message_sent", f"#{revision.revision_number}")

            # Отправляем уведомление админу/исполнителю
            await self._send_message_notification(revision, revision_message, user, project)

            # НЕ очищаем контекст - пользователь может отправить еще сообщения
            # context.user_data остается с writing_message_revision_id и writing_message_step

            text = f"""
✅ <b>Сообщение отправлено!</b>

Исполнитель получил уведомление и ответит вам в ближайшее время.

💬 <i>Вы можете продолжить писать сообщения, отправлять фото или видео.</i>
            """

            keyboard = [
                [InlineKeyboardButton("🔙 К правке", callback_data=f"revision_details_{revision_id}")],
                [InlineKeyboardButton("❌ Закрыть чат", callback_data=f"revision_close_chat_{revision_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в handle_chat_message: {e}")
            await update.message.reply_text("❌ Произошла ошибка при отправке сообщения.")

    @standard_handler
    async def handle_chat_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать фото в чате правки"""
        try:
            user_id = update.effective_user.id

            # Если ожидается причина отклонения, сохраняем фото и просим текст
            if context.user_data.get('waiting_for_rejection_reason'):
                # Сохраняем фото в user_data для последующей отправки
                if 'rejection_files' not in context.user_data:
                    context.user_data['rejection_files'] = []

                photo = update.message.photo[-1]
                context.user_data['rejection_files'].append({
                    'type': 'photo',
                    'file_id': photo.file_id
                })

                await update.message.reply_text(
                    "📸 Фото сохранено!\n\n"
                    "Теперь напишите текстовое описание причины отклонения.\n"
                    "Фото будет прикреплено к вашему сообщению."
                )
                return

            # Проверяем что пользователь в режиме чата
            if (context.user_data.get('writing_message_step') != 'text' or
                'writing_message_revision_id' not in context.user_data):
                return

            revision_id = context.user_data['writing_message_revision_id']

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                # Проверяем правку
                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await update.message.reply_text("❌ Правка не найдена.")
                    return

                # Сохраняем фото
                photo = update.message.photo[-1]  # Берем фото наибольшего размера
                file = await context.bot.get_file(photo.file_id)

                # Создаем директорию для файлов правок
                from pathlib import Path
                upload_dir = Path("uploads/revisions/messages")
                upload_dir.mkdir(parents=True, exist_ok=True)

                import uuid
                file_extension = '.jpg'
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                file_path = upload_dir / unique_filename

                await file.download_to_drive(file_path)

                # Создаем сообщение с подписью к фото (если есть)
                caption = update.message.caption or "📷 Фото"

                revision_message = RevisionMessage(
                    revision_id=revision_id,
                    sender_type="client",
                    sender_user_id=user.id,
                    message=caption,
                    is_internal=False,
                    created_at=datetime.utcnow()
                )

                db.add(revision_message)
                db.commit()
                db.refresh(revision_message)

                # Создаем запись о файле
                message_file = RevisionMessageFile(
                    message_id=revision_message.id,
                    filename=unique_filename,
                    original_filename=f"photo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg",
                    file_type='image',
                    file_size=photo.file_size,
                    file_path=str(file_path),
                    created_at=datetime.utcnow()
                )

                db.add(message_file)
                db.commit()

                logger.info(f"📸 Фото сохранено в БД: message_id={revision_message.id}, file_id={message_file.id}")

                # Получаем данные проекта для уведомления
                project = db.get(Project, revision.project_id)

            # Отправляем уведомление
            await self._send_message_notification(revision, revision_message, user, project)

            text = f"""
✅ <b>Фото отправлено!</b>

Исполнитель получил уведомление.

💬 <i>Вы можете продолжить писать сообщения.</i>
            """

            keyboard = [
                [InlineKeyboardButton("🔙 К правке", callback_data=f"revision_details_{revision_id}")],
                [InlineKeyboardButton("❌ Закрыть чат", callback_data=f"revision_close_chat_{revision_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в handle_chat_photo: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await update.message.reply_text("❌ Произошла ошибка при отправке фото.")

    @standard_handler
    async def handle_chat_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать видео в чате правки"""
        try:
            user_id = update.effective_user.id

            # Если ожидается причина отклонения, сохраняем видео и просим текст
            if context.user_data.get('waiting_for_rejection_reason'):
                # Сохраняем видео в user_data для последующей отправки
                if 'rejection_files' not in context.user_data:
                    context.user_data['rejection_files'] = []

                video = update.message.video
                context.user_data['rejection_files'].append({
                    'type': 'video',
                    'file_id': video.file_id
                })

                await update.message.reply_text(
                    "🎥 Видео сохранено!\n\n"
                    "Теперь напишите текстовое описание причины отклонения.\n"
                    "Видео будет прикреплено к вашему сообщению."
                )
                return

            # Проверяем что пользователь в режиме чата
            if (context.user_data.get('writing_message_step') != 'text' or
                'writing_message_revision_id' not in context.user_data):
                return

            revision_id = context.user_data['writing_message_revision_id']

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                # Проверяем правку
                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await update.message.reply_text("❌ Правка не найдена.")
                    return

                # Сохраняем видео
                video = update.message.video
                file = await context.bot.get_file(video.file_id)

                from pathlib import Path
                upload_dir = Path("uploads/revisions/messages")
                upload_dir.mkdir(parents=True, exist_ok=True)

                import uuid
                file_extension = '.mp4'
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                file_path = upload_dir / unique_filename

                await file.download_to_drive(file_path)

                # Создаем сообщение с подписью к видео (если есть)
                caption = update.message.caption or "🎥 Видео"

                revision_message = RevisionMessage(
                    revision_id=revision_id,
                    sender_type="client",
                    sender_user_id=user.id,
                    message=caption,
                    is_internal=False,
                    created_at=datetime.utcnow()
                )

                db.add(revision_message)
                db.commit()
                db.refresh(revision_message)

                # Создаем запись о файле
                message_file = RevisionMessageFile(
                    message_id=revision_message.id,
                    filename=unique_filename,
                    original_filename=f"video_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4",
                    file_type='video',
                    file_size=video.file_size,
                    file_path=str(file_path),
                    created_at=datetime.utcnow()
                )

                db.add(message_file)
                db.commit()

                logger.info(f"🎥 Видео сохранено в БД: message_id={revision_message.id}, file_id={message_file.id}")

                # Получаем данные проекта для уведомления
                project = db.get(Project, revision.project_id)

            # Отправляем уведомление
            await self._send_message_notification(revision, revision_message, user, project)

            text = f"""
✅ <b>Видео отправлено!</b>

Исполнитель получил уведомление.

💬 <i>Вы можете продолжить писать сообщения.</i>
            """

            keyboard = [
                [InlineKeyboardButton("🔙 К правке", callback_data=f"revision_details_{revision_id}")],
                [InlineKeyboardButton("❌ Закрыть чат", callback_data=f"revision_close_chat_{revision_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в handle_chat_video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await update.message.reply_text("❌ Произошла ошибка при отправке видео.")

    @standard_handler
    async def approve_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Принять выполненную правку"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            revision_id = int(query.data.replace('revision_approve_', ''))

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await query.answer("Правка не найдена")
                    return

                if revision.status != "completed":
                    await query.answer("Правка еще не завершена")
                    return

                # Обновляем статус
                old_status = revision.status
                revision.status = "approved"
                revision.updated_at = datetime.utcnow()

                # Добавляем сообщение об одобрении
                approval_message = RevisionMessage(
                    revision_id=revision_id,
                    sender_type="client",
                    sender_user_id=user.id,
                    message="✅ Клиент принял работу. Правка одобрена!",
                    is_internal=False,
                    created_at=datetime.utcnow()
                )

                db.add(approval_message)
                db.commit()

                revision_data = {
                    'id': revision.id,
                    'revision_number': revision.revision_number,
                    'title': revision.title,
                    'project_id': revision.project_id
                }

                project = db.get(Project, revision.project_id)

            # Отправляем уведомление
            await self._send_status_notification(revision, old_status, project, user)

            log_user_action(user_id, "revision_approved", f"#{revision_data['revision_number']}")

            text = f"""
✅ <b>Правка принята!</b>

Правка #{revision_data['revision_number']} успешно одобрена.

Исполнитель получил уведомление об одобрении.

Спасибо что работаете с нами! 🎉
            """

            keyboard = [
                [InlineKeyboardButton("⭐️ Оценить качество работы", callback_data=f"revision_rate_{revision_id}")],
                [InlineKeyboardButton("💬 Открыть чат", callback_data=f"revision_chat_{revision_id}")],
                [InlineKeyboardButton("🔙 К правке", callback_data=f"revision_details_{revision_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в approve_revision: {e}")
            await query.answer("Произошла ошибка")

    @standard_handler
    async def reject_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запросить доработку правки"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            revision_id = int(query.data.replace('revision_reject_', ''))

            # Сохраняем ID в контексте для запроса причины
            context.user_data['rejecting_revision_id'] = revision_id
            context.user_data['rejecting_revision_step'] = 'reason'

            text = """
❌ <b>Запрос доработки</b>

Опишите что нужно доработать или исправить.

Будьте максимально конкретны чтобы исполнитель понял что именно нужно изменить.

<b>Пример:</b>
"Кнопка должна быть синей а не зеленой. Размер шрифта слишком маленький - увеличить до 16px."
            """

            keyboard = [
                [InlineKeyboardButton("❌ Отмена", callback_data=f"revision_details_{revision_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в reject_revision: {e}")
            await query.answer("Произошла ошибка")

    @standard_handler
    async def handle_rejection_reason(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать причину отклонения"""
        try:
            if not update.message or not update.message.text:
                return

            user_id = update.effective_user.id

            if (context.user_data.get('rejecting_revision_step') != 'reason' or
                'rejecting_revision_id' not in context.user_data):
                return

            reason = update.message.text.strip()
            revision_id = context.user_data['rejecting_revision_id']

            if len(reason) < 10:
                await update.message.reply_text("❌ Описание слишком короткое. Минимум 10 символов.")
                return

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await update.message.reply_text("❌ Правка не найдена.")
                    return

                # Обновляем статус
                old_status = revision.status
                revision.status = "needs_rework"
                revision.updated_at = datetime.utcnow()

                # Добавляем сообщение с причиной
                rejection_message = RevisionMessage(
                    revision_id=revision_id,
                    sender_type="client",
                    sender_user_id=user.id,
                    message=f"❌ Запрошена доработка:\n\n{reason}",
                    is_internal=False,
                    created_at=datetime.utcnow()
                )

                db.add(rejection_message)
                db.commit()

                revision_data = {
                    'id': revision.id,
                    'revision_number': revision.revision_number,
                    'project_id': revision.project_id
                }

                project = db.get(Project, revision.project_id)

            # Отправляем уведомление
            await self._send_status_notification(revision, old_status, project, user)

            # Очищаем контекст
            context.user_data.pop('rejecting_revision_id', None)
            context.user_data.pop('rejecting_revision_step', None)

            log_user_action(user_id, "revision_rejected", f"#{revision_data['revision_number']}")

            text = """
✅ <b>Запрос отправлен!</b>

Исполнитель получил уведомление о необходимости доработки.

Он увидит ваш комментарий и внесет необходимые изменения.

Вы получите уведомление когда правка будет готова снова.
            """

            keyboard = [
                [InlineKeyboardButton("💬 Открыть чат", callback_data=f"revision_chat_{revision_id}")],
                [InlineKeyboardButton("🔙 К правке", callback_data=f"revision_details_{revision_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        except Exception as e:
            logger.error(f"Ошибка в handle_rejection_reason: {e}")
            await update.message.reply_text("❌ Произошла ошибка.")

    async def _send_message_notification(self, revision, message, user, project):
        """Отправить уведомление о новом сообщении"""
        try:
            from ...services.notification_service import notification_service

            await notification_service.notify_revision_message(
                revision, project, message, user, None
            )

        except Exception as e:
            logger.error(f"Error sending message notification: {e}")

    async def _send_status_notification(self, revision, old_status, project, user):
        """Отправить уведомление об изменении статуса"""
        try:
            from ...services.notification_service import notification_service

            await notification_service.notify_revision_status_changed(
                revision, project, user, old_status
            )

        except Exception as e:
            logger.error(f"Error sending status notification: {e}")

    @standard_handler
    async def show_all_my_revisions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать все правки пользователя"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            log_user_action(user_id, "show_all_my_revisions", "")

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                # Получаем все правки пользователя через JOIN с Project
                revisions = db.query(ProjectRevision).join(Project).filter(
                    Project.user_id == user.id
                ).order_by(ProjectRevision.created_at.desc()).limit(20).all()

                if not revisions:
                    await query.answer("У вас пока нет правок", show_alert=True)
                    return

                # Извлекаем данные правок
                revisions_data = []
                for revision in revisions:
                    project = revision.project
                    revisions_data.append({
                        'id': revision.id,
                        'revision_number': revision.revision_number,
                        'title': revision.title,
                        'status': revision.status,
                        'priority': revision.priority,
                        'project_title': project.title,
                        'created_at': revision.created_at
                    })

            # Эмодзи статусов
            status_emoji = {
                'open': '🆕',
                'in_progress': '🔄',
                'completed': '✅',
                'rejected': '❌'
            }

            text = f"📋 <b>Ваши правки</b>\n\n"

            # Создаем клавиатуру
            keyboard = []
            for rev_data in revisions_data:
                emoji = status_emoji.get(rev_data['status'], '📝')
                button_text = f"{emoji} #{rev_data['revision_number']}: {rev_data['title'][:25]}"
                keyboard.append([
                    InlineKeyboardButton(
                        button_text,
                        callback_data=f"revision_details_{rev_data['id']}"
                    )
                ])

            keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Пытаемся редактировать сообщение
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except Exception:
                await query.answer()
                await query.message.reply_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )

        except Exception as e:
            logger.error(f"Ошибка в show_all_my_revisions: {e}")
            await query.answer("Произошла ошибка при загрузке правок")

    @standard_handler
    async def client_approve_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Клиент принимает правку"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            revision_id = int(query.data.replace('revision_client_approve_', ''))

            log_user_action(user_id, "client_approve_revision", str(revision_id))

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                # Получаем правку с проверкой доступа
                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await query.answer("Правка не найдена")
                    return

                # Обновляем статус
                old_status = revision.status
                revision.status = "approved"
                revision.completed_at = datetime.utcnow()
                revision.updated_at = datetime.utcnow()

                # Сохраняем в историю (добавляем сообщение)
                approval_message = RevisionMessage(
                    revision_id=revision_id,
                    sender_type="client",
                    sender_user_id=user.id,
                    message="✅ Правка принята клиентом",
                    is_internal=False
                )
                db.add(approval_message)
                db.commit()

                # Уведомляем исполнителя
                from ...services.notification_service import notification_service
                if revision.assigned_to:
                    admin_message = f"""
✅ <b>Правка #{revision.revision_number} принята!</b>

👤 <b>Клиент:</b> {user.first_name or user.username or 'Клиент'}
📋 <b>Проект:</b> {revision.project.title}
🔧 <b>Правка:</b> {revision.title}

Отличная работа! 🎉
                    """
                    # Отправляем уведомление исполнителю (если у него есть telegram_id)
                    if hasattr(revision.assigned_to, 'telegram_id') and revision.assigned_to.telegram_id:
                        await notification_service.send_user_notification(
                            revision.assigned_to.telegram_id,
                            admin_message
                        )

                await query.answer("✅ Правка принята!")

                # Обновляем сообщение
                await query.edit_message_text(
                    text=f"""
✅ <b>Правка принята!</b>

📋 <b>Проект:</b> {revision.project.title}
🔧 <b>Правка #{revision.revision_number}:</b> {revision.title}

<b>Статус:</b> Принято
<b>Дата принятия:</b> {format_datetime(revision.completed_at)}

Спасибо за обратную связь! 🎉
                    """,
                    parse_mode='HTML'
                )

        except Exception as e:
            logger.error(f"Ошибка в client_approve_revision: {e}", exc_info=True)
            await query.answer("Произошла ошибка при принятии правки")

    @standard_handler
    async def client_reject_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Клиент отправляет правку на доработку"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            revision_id = int(query.data.replace('revision_client_reject_', ''))

            log_user_action(user_id, "client_reject_revision", str(revision_id))

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                # Получаем правку с проверкой доступа
                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await query.answer("Правка не найдена")
                    return

                # Сохраняем ID правки для последующего ввода причины
                context.user_data['rejecting_revision_id'] = revision_id
                context.user_data['waiting_for_rejection_reason'] = True

                await query.answer()

                # Создаем клавиатуру с кнопкой отмены
                keyboard = [
                    [InlineKeyboardButton("❌ Отмена", callback_data=f"revision_cancel_reject_{revision_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Просим указать причину
                await query.edit_message_text(
                    text=f"""
❌ <b>Отправка на доработку</b>

📋 <b>Проект:</b> {revision.project.title}
🔧 <b>Правка #{revision.revision_number}:</b> {revision.title}

Пожалуйста, опишите, что именно нужно доработать.
Ваше сообщение будет отправлено исполнителю.

💬 <i>Напишите причину отправки на доработку текстом...</i>
                    """,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )

        except Exception as e:
            logger.error(f"Ошибка в client_reject_revision: {e}", exc_info=True)
            await query.answer("Произошла ошибка при отправке на доработку")

    @standard_handler
    async def cancel_reject_revision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отменить отправку правки на доработку"""
        try:
            query = update.callback_query
            user_id = update.effective_user.id

            revision_id = int(query.data.replace('revision_cancel_reject_', ''))

            # Очищаем флаги
            context.user_data.pop('waiting_for_rejection_reason', None)
            context.user_data.pop('rejecting_revision_id', None)

            await query.answer("Отменено")

            with get_db_context() as db:
                from ...database.database import get_or_create_user
                user = get_or_create_user(db, user_id)

                # Получаем правку
                revision = db.query(ProjectRevision).join(Project).filter(
                    ProjectRevision.id == revision_id,
                    Project.user_id == user.id
                ).first()

                if not revision:
                    await query.edit_message_text("Правка не найдена")
                    return

                # Возвращаемся к оригинальному сообщению с кнопками
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "✅ Принять правку",
                            callback_data=f"revision_client_approve_{revision.id}"
                        ),
                        InlineKeyboardButton(
                            "❌ На доработку",
                            callback_data=f"revision_client_reject_{revision.id}"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    text=f"""
✅ <b>Правка готова к проверке!</b>

📋 <b>Проект:</b> {revision.project.title}
🔧 <b>Правка #{revision.revision_number}:</b> {revision.title}

Пожалуйста, проверьте выполненную работу.

После проверки выберите действие:
• <b>Принять</b> - если всё выполнено правильно
• <b>На доработку</b> - если требуются исправления
                    """,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )

        except Exception as e:
            logger.error(f"Ошибка в cancel_reject_revision: {e}", exc_info=True)
            await query.answer("Произошла ошибка")


# Создаем экземпляр
revision_chat_handlers = RevisionChatHandlers()
