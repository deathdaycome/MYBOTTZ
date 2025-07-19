#!/usr/bin/env python3
"""
Простой бот для тестирования сохранения токена
"""
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from app.config.settings import get_settings
from app.database.database import get_db_context, get_or_create_user

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь для хранения состояний пользователей
user_states = {}

async def start(update: Update, context):
    """Команда /start"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Сохранить токен", callback_data="save_token")]
    ])
    
    await update.message.reply_text(
        "Привет! Нажми кнопку чтобы сохранить токен:",
        reply_markup=keyboard
    )

async def callback_handler(update: Update, context):
    """Обработка callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "save_token":
        user_id = query.from_user.id
        user_states[user_id] = "waiting_token"
        
        await query.edit_message_text(
            "🔑 Отправьте токен от @BotFather:\n\n"
            "Формат: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        )

async def message_handler(update: Update, context):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    logger.info(f"Получено сообщение от {user_id}: {message_text}")
    
    if user_states.get(user_id) == "waiting_token":
        # Валидация токена
        if ":" not in message_text or len(message_text) < 20:
            await update.message.reply_text("❌ Неверный формат токена")
            return
        
        # Сохранение в базу
        try:
            with get_db_context() as db:
                user = get_or_create_user(
                    db=db,
                    telegram_id=user_id,
                    username=update.effective_user.username,
                    first_name=update.effective_user.first_name
                )
                
                if not user.preferences:
                    user.preferences = {}
                
                user.preferences['bot_token'] = message_text
                db.commit()
                
                logger.info(f"Токен сохранен для пользователя {user_id}")
        
        except Exception as e:
            logger.error(f"Ошибка сохранения токена: {e}")
            await update.message.reply_text("❌ Ошибка сохранения токена")
            return
        
        # Очищаем состояние
        user_states.pop(user_id, None)
        
        # Подтверждение
        await update.message.reply_text(
            f"✅ Токен сохранен!\n\n"
            f"Первые 10 символов: {message_text[:10]}...\n"
            f"Токен сохранен в базе данных."
        )
    else:
        await update.message.reply_text("Отправьте /start для начала")

async def main():
    """Основная функция"""
    settings = get_settings()
    
    app = Application.builder().token(settings.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    logger.info("Простой бот запущен")
    
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())