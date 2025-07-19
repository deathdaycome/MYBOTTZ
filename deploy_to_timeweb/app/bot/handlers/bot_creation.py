"""
Обработчик гайда по созданию бота через BotFather
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import Session

from ..keyboards.main import (
    get_bot_creation_guide_keyboard, 
    get_bot_guide_steps_keyboard,
    get_back_to_main_keyboard
)
from ...database.database import get_db_context, get_or_create_user
from ...database.models import Project
from ...config.logging import get_logger, log_user_action

logger = get_logger(__name__)

# Состояния для ConversationHandler
ENTER_BOT_TOKEN = 1

class BotCreationHandler:
    """Обработчик создания бота через BotFather"""

    async def show_bot_creation_guide(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать главное меню гайда по созданию бота"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "bot_creation_guide", "Показ гайда по созданию бота")

            message_text = """
🎯 **Создание Telegram бота**

Создать собственного Telegram бота очень просто! 
Следуйте нашему пошаговому руководству:

🔹 Откройте BotFather (официальный бот Telegram)
🔹 Следуйте инструкциям для создания бота
🔹 Получите API токен
🔹 Введите токен в нашем боте для сохранения

✨ После этого ваш API ключ будет отображаться в информации о проекте!
            """

            keyboard = get_bot_creation_guide_keyboard()

            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text=message_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    text=message_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Ошибка показа гайда по созданию бота: {e}")
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже.",
                reply_markup=get_back_to_main_keyboard()
            )

    async def show_bot_creation_steps(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать пошаговую инструкцию создания бота"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "bot_creation_steps", "Показ пошаговой инструкции")

            message_text = """
📖 **Пошаговая инструкция создания бота**

**Шаг 1:** Откройте @BotFather
👆 Нажмите кнопку ниже или найдите @BotFather в поиске

**Шаг 2:** Отправьте команду `/newbot`
📱 BotFather попросит ввести имя бота

**Шаг 3:** Введите имя вашего бота
💬 Например: "Мой Первый Бот"

**Шаг 4:** Введите username бота
🔗 Должен заканчиваться на "bot", например: my_first_bot

**Шаг 5:** Получите API токен
🔑 BotFather пришлет вам токен вида: `123456789:ABCdef...`

**Шаг 6:** Скопируйте токен и введите его здесь
💾 Мы сохраним его в информации о вашем проекте

⚠️ **Важно:** Никому не сообщайте ваш API токен!
            """

            keyboard = get_bot_guide_steps_keyboard()

            await update.callback_query.edit_message_text(
                text=message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Ошибка показа пошаговой инструкции: {e}")
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже.",
                reply_markup=get_back_to_main_keyboard()
            )

    async def start_bot_token_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать ввод API токена бота"""
        try:
            user_id = update.effective_user.id
            log_user_action(user_id, "bot_token_entry_start", "Начало ввода API токена")

            message_text = """
🔑 **Ввод API токена бота**

Пожалуйста, отправьте ваш API токен, который вы получили от @BotFather.

Токен должен выглядеть примерно так:
`123456789:ABCdef1234567890abcdef1234567890abc`

⚠️ **Внимание:** 
• Токен должен быть скопирован полностью
• Никому не показывайте ваш токен
• После ввода токен будет сохранен в вашем проекте

Отправьте токен следующим сообщением:
            """

            await update.callback_query.edit_message_text(
                text=message_text,
                parse_mode='Markdown'
            )

            return ENTER_BOT_TOKEN

        except Exception as e:
            logger.error(f"Ошибка начала ввода токена: {e}")
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже.",
                reply_markup=get_back_to_main_keyboard()
            )
            return ConversationHandler.END

    async def save_bot_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранить API токен бота"""
        try:
            user_id = update.effective_user.id
            token = update.message.text.strip()

            log_user_action(user_id, "bot_token_save", f"Сохранение API токена: {token[:10]}...")

            # Базовая валидация токена
            if not self.validate_bot_token(token):
                await update.message.reply_text(
                    "❌ **Неверный формат токена!**\n\n"
                    "Токен должен выглядеть примерно так:\n"
                    "`123456789:ABCdef1234567890abcdef1234567890abc`\n\n"
                    "Пожалуйста, проверьте токен и отправьте его снова:",
                    parse_mode='Markdown'
                )
                return ENTER_BOT_TOKEN

            # Сохраняем токен в последний активный проект пользователя
            with get_db_context() as db:
                db_user = get_or_create_user(
                    db=db,
                    telegram_id=user_id,
                    username=update.effective_user.username,
                    first_name=update.effective_user.first_name,
                    last_name=update.effective_user.last_name
                )

                # Находим последний проект пользователя или создаем новый
                project = db.query(Project).filter(
                    Project.user_id == db_user.id
                ).order_by(Project.created_at.desc()).first()

                if not project:
                    # Создаем новый проект для бота
                    project = Project(
                        user_id=db_user.id,
                        title="Telegram бот",
                        description="Проект Telegram бота, созданный через BotFather",
                        project_type="bot",
                        status="new",
                        complexity="medium",
                        priority="medium"
                    )
                    db.add(project)
                    db.flush()

                # Сохраняем токен в метаданных проекта
                if not project.project_metadata:
                    project.project_metadata = {}

                project.project_metadata['bot_token'] = token
                project.project_metadata['bot_token_added_at'] = str(update.message.date)

                db.commit()

                success_message = f"""
✅ **API токен успешно сохранен!**

🤖 Ваш токен добавлен к проекту: "{project.title}"
📊 Теперь вы можете увидеть его в разделе "Мои проекты"

🎉 **Поздравляем с созданием бота!**

Что дальше?
• Просмотрите информацию о проекте
• Создайте техническое задание
• Обратитесь за консультацией по доработке

                """

                keyboard = get_back_to_main_keyboard()
                await update.message.reply_text(
                    text=success_message,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )

                return ConversationHandler.END

        except Exception as e:
            logger.error(f"Ошибка сохранения токена: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при сохранении токена. Попробуйте позже.",
                reply_markup=get_back_to_main_keyboard()
            )
            return ConversationHandler.END

    async def cancel_bot_token_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отменить ввод токена"""
        user_id = update.effective_user.id
        log_user_action(user_id, "bot_token_entry_cancel", "Отмена ввода токена")

        await update.message.reply_text(
            "❌ Ввод токена отменен.",
            reply_markup=get_back_to_main_keyboard()
        )
        return ConversationHandler.END

    def validate_bot_token(self, token: str) -> bool:
        """Базовая валидация токена бота"""
        if not token:
            return False
        
        # Токен должен содержать : и иметь определенную длину
        if ':' not in token:
            return False
        
        parts = token.split(':')
        if len(parts) != 2:
            return False
        
        # Первая часть должна быть числом
        try:
            int(parts[0])
        except ValueError:
            return False
        
        # Вторая часть должна быть не пустой
        if len(parts[1]) < 10:
            return False
        
        return True

    def get_conversation_handler(self):
        """Получить ConversationHandler для ввода токена"""
        return ConversationHandler(
            entry_points=[],  # Будет добавлен в основном обработчике
            states={
                ENTER_BOT_TOKEN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_bot_token)
                ]
            },
            fallbacks=[
                MessageHandler(filters.COMMAND, self.cancel_bot_token_entry)
            ]
        )
