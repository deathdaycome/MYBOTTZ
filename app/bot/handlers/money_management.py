"""
Обработчики для системы учета средств с OCR
"""

from telegram import Update, File
from telegram.ext import ContextTypes
from telegram.error import BadRequest
import logging
import os
import io
from PIL import Image
import pytesseract
import json
from datetime import datetime
import uuid
import mimetypes

from ...config.settings import settings
from ...database.database import get_db_context
from ...database.models import MoneyTransaction, MoneyCategory, ReceiptFile, AdminUser
from ...utils.decorators import standard_handler
from ..keyboards.main import get_admin_console_keyboard, get_admin_money_keyboard

logger = logging.getLogger(__name__)

class MoneyManagementHandler:
    """Обработчик системы учета средств"""
    
    def __init__(self):
        # Настройки OCR
        self.allowed_file_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Создаем директорию для чеков если её нет
        self.receipts_dir = "uploads/receipts"
        os.makedirs(self.receipts_dir, exist_ok=True)
        
        # Состояния пользователей
        self.user_states = {}
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка прав администратора"""
        return user_id in settings.ADMIN_IDS
    
    @standard_handler
    async def handle_admin_console(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главное меню админ консоли"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к админ консоли")
            return
        
        await update.callback_query.answer()
        
        text = """
🔧 <b>Админ консоль</b>

Добро пожаловать в панель управления!

Доступные функции:
💰 <b>Управление финансами</b> - учет доходов и расходов
📊 <b>Статистика</b> - общая статистика проектов
📱 <b>Уведомления</b> - настройка уведомлений
⚙️ <b>Настройки бота</b> - конфигурация бота
📁 <b>Файлы проектов</b> - управление файлами
👥 <b>Пользователи</b> - управление пользователями
        """
        
        keyboard = get_admin_console_keyboard()
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    @standard_handler
    async def handle_admin_money(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню управления финансами"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к этой функции")
            return
        
        await update.callback_query.answer()
        
        # Получаем статистику
        with get_db_context() as db:
            total_income = db.query(MoneyTransaction).filter(
                MoneyTransaction.type == "income"
            ).count()
            
            total_expenses = db.query(MoneyTransaction).filter(
                MoneyTransaction.type == "expense"
            ).count()
            
            total_receipts = db.query(ReceiptFile).count()
        
        text = f"""
💰 <b>Управление финансами</b>

📈 <b>Доходы:</b> {total_income} транзакций
📉 <b>Расходы:</b> {total_expenses} транзакций  
📄 <b>Чеков загружено:</b> {total_receipts}

<b>Функции:</b>
📄 <b>Загрузить чек</b> - автоматическое распознавание
💼 <b>Мои транзакции</b> - просмотр всех операций
📊 <b>Аналитика</b> - графики и отчеты
🏷️ <b>Категории</b> - управление категориями

<i>💡 Загрузите фото чека - бот автоматически распознает сумму и дату!</i>
        """
        
        keyboard = get_admin_money_keyboard()
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    @standard_handler
    async def handle_upload_receipt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало загрузки чека"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к этой функции")
            return
        
        await update.callback_query.answer()
        
        # Устанавливаем состояние пользователя
        self.user_states[user_id] = "waiting_for_receipt"
        
        text = """
📄 <b>Загрузка чека</b>

Отправьте фото чека или документ (PDF, JPG, PNG)

Бот автоматически:
✅ Распознает сумму
✅ Определит дату
✅ Сохранит чек
✅ Предложит выбрать тип операции

<b>Поддерживаемые форматы:</b>
• JPG, PNG, GIF
• PDF документы  
• Максимальный размер: 10MB

📸 Пришлите фото чека сейчас...
        """
        
        await update.callback_query.edit_message_text(
            text=text,
            parse_mode='HTML'
        )
    
    @standard_handler
    async def handle_document_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка загруженного документа/фото"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            return
        
        # Проверяем состояние пользователя
        if self.user_states.get(user_id) != "waiting_for_receipt":
            return
        
        # Определяем тип файла
        file_obj = None
        file_name = None
        file_size = None
        
        if update.message.photo:
            # Фото
            file_obj = update.message.photo[-1]  # Берем самое большое разрешение
            file_name = f"receipt_{user_id}_{int(datetime.now().timestamp())}.jpg"
            file_size = file_obj.file_size
        elif update.message.document:
            # Документ
            file_obj = update.message.document
            file_name = file_obj.file_name or f"receipt_{user_id}_{int(datetime.now().timestamp())}"
            file_size = file_obj.file_size
            
            # Проверяем MIME-тип
            mime_type, _ = mimetypes.guess_type(file_name)
            if mime_type not in self.allowed_file_types:
                await update.message.reply_text(
                    "❌ Неподдерживаемый тип файла. Используйте JPG, PNG, GIF или PDF."
                )
                return
        else:
            await update.message.reply_text(
                "❌ Пожалуйста, отправьте фото или документ с чеком."
            )
            return
        
        # Проверяем размер файла
        if file_size and file_size > self.max_file_size:
            await update.message.reply_text(
                "❌ Файл слишком большой. Максимальный размер: 10MB."
            )
            return
        
        try:
            # Отправляем уведомление о начале обработки
            processing_msg = await update.message.reply_text(
                "⏳ Обрабатываю документ...\n📄 Распознаю текст..."
            )
            
            # Получаем файл
            telegram_file = await file_obj.get_file()
            
            # Сохраняем файл
            file_path = os.path.join(self.receipts_dir, file_name)
            await telegram_file.download_to_drive(file_path)
            
            # Выполняем OCR
            ocr_result = await self._process_ocr(file_path)
            
            # Сохраняем в базу данных
            with get_db_context() as db:
                # Получаем админ пользователя
                admin_user = db.query(AdminUser).filter(
                    AdminUser.username == "admin"  # Предполагаем, что главный админ имеет username "admin"
                ).first()
                
                if not admin_user:
                    # Создаем запись админа если её нет
                    admin_user = AdminUser(
                        username="admin",
                        password_hash="dummy",  # Заглушка
                        role="owner"
                    )
                    db.add(admin_user)
                    db.commit()
                    db.refresh(admin_user)
                
                # Создаем запись файла чека
                receipt_file = ReceiptFile(
                    filename=file_name,
                    original_filename=file_obj.file_name if hasattr(file_obj, 'file_name') else file_name,
                    file_path=file_path,
                    file_size=file_size or 0,
                    file_type=file_name.split('.')[-1].lower(),
                    ocr_status="completed" if ocr_result['success'] else "failed",
                    ocr_result=ocr_result,
                    ocr_confidence=ocr_result.get('confidence', 0.0),
                    ocr_error=ocr_result.get('error'),
                    uploaded_by_id=admin_user.id,
                    processed_at=datetime.utcnow()
                )
                db.add(receipt_file)
                db.commit()
                db.refresh(receipt_file)
            
            # Обновляем сообщение с результатом
            await processing_msg.edit_text(
                "✅ Документ принят и обработан!\n🔍 Анализирую содержимое..."
            )
            
            # Показываем результат OCR и просим выбрать тип операции
            await self._show_ocr_result(update, context, receipt_file, ocr_result)
            
            # Сбрасываем состояние
            self.user_states[user_id] = f"confirm_transaction_{receipt_file.id}"
            
        except Exception as e:
            logger.error(f"Ошибка обработки файла: {e}")
            await update.message.reply_text(
                f"❌ Ошибка обработки файла: {str(e)}\n\nПопробуйте еще раз или загрузите другой файл."
            )
            # Сбрасываем состояние при ошибке
            self.user_states.pop(user_id, None)
    
    async def _process_ocr(self, file_path: str) -> dict:
        """Обработка файла с помощью OCR"""
        try:
            # Для изображений используем pytesseract
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image, lang='rus+eng')
                
                # Ищем сумму в тексте
                import re
                
                # Паттерны для поиска сумм
                amount_patterns = [
                    r'(?:итого|сумма|к оплате|total)[:\s]*(\d+[.,]\d{2})',
                    r'(\d+[.,]\d{2})\s*(?:руб|₽|rub)',
                    r'(\d{1,6}[.,]\d{2})',  # Общий паттерн для суммы
                ]
                
                # Паттерны для поиска даты
                date_patterns = [
                    r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
                    r'(\d{1,2}\.\d{1,2}\.\d{2,4})',
                    r'(\d{4}-\d{1,2}-\d{1,2})',
                ]
                
                amounts = []
                dates = []
                
                # Ищем суммы
                for pattern in amount_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    amounts.extend(matches)
                
                # Ищем даты
                for pattern in date_patterns:
                    matches = re.findall(pattern, text)
                    dates.extend(matches)
                
                # Берем наибольшую сумму (скорее всего итоговая)
                parsed_amount = None
                if amounts:
                    try:
                        float_amounts = [float(amt.replace(',', '.')) for amt in amounts]
                        parsed_amount = max(float_amounts)
                    except:
                        pass
                
                # Берем первую найденную дату
                parsed_date = None
                if dates:
                    try:
                        date_str = dates[0]
                        # Пытаемся распарсить дату в разных форматах
                        for date_format in ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%y']:
                            try:
                                parsed_date = datetime.strptime(date_str, date_format)
                                break
                            except:
                                continue
                    except:
                        pass
                
                return {
                    'success': True,
                    'raw_text': text,
                    'amount': parsed_amount,
                    'date': parsed_date.isoformat() if parsed_date else None,
                    'confidence': 0.8 if parsed_amount else 0.3,
                    'extracted_amounts': amounts,
                    'extracted_dates': dates
                }
            
            else:
                # Для PDF используем другие методы (пока заглушка)
                return {
                    'success': False,
                    'error': 'PDF обработка пока не поддерживается',
                    'confidence': 0.0
                }
                
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _show_ocr_result(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                              receipt_file: ReceiptFile, ocr_result: dict):
        """Показать результат OCR и запросить подтверждение"""
        
        if ocr_result['success'] and ocr_result.get('amount'):
            amount = ocr_result['amount']
            date_str = ocr_result.get('date', 'не определена')
            
            if date_str != 'не определена':
                try:
                    date_obj = datetime.fromisoformat(date_str)
                    date_str = date_obj.strftime('%d.%m.%Y')
                except:
                    pass
            
            text = f"""
✅ <b>Документ принят и обработан!</b>

📄 <b>Результат распознавания:</b>
💰 <b>Сумма:</b> {amount:,.2f} ₽
📅 <b>Дата:</b> {date_str}
🎯 <b>Уверенность:</b> {ocr_result.get('confidence', 0) * 100:.1f}%

<b>Это доход или расход?</b>
            """
            
            # Создаем клавиатуру для выбора типа операции
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            keyboard = [
                [
                    InlineKeyboardButton("📈 Доход", callback_data=f"transaction_income_{receipt_file.id}"),
                    InlineKeyboardButton("📉 Расход", callback_data=f"transaction_expense_{receipt_file.id}")
                ],
                [
                    InlineKeyboardButton("✏️ Изменить сумму", callback_data=f"edit_amount_{receipt_file.id}"),
                    InlineKeyboardButton("📅 Изменить дату", callback_data=f"edit_date_{receipt_file.id}")
                ],
                [
                    InlineKeyboardButton("❌ Отмена", callback_data="admin_money")
                ]
            ]
            
            await update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            
        else:
            # OCR не смог распознать данные
            error_msg = ocr_result.get('error', 'Не удалось распознать данные')
            
            text = f"""
⚠️ <b>Документ принят, но не полностью обработан</b>

❌ <b>Ошибка распознавания:</b> {error_msg}

Вы можете:
• Попробовать загрузить другое фото
• Ввести данные вручную
            """
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            keyboard = [
                [
                    InlineKeyboardButton("✏️ Ввести вручную", callback_data=f"manual_entry_{receipt_file.id}")
                ],
                [
                    InlineKeyboardButton("🔄 Загрузить другой чек", callback_data="upload_receipt"),
                    InlineKeyboardButton("❌ Отмена", callback_data="admin_money")
                ]
            ]
            
            await update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
    
    @standard_handler
    async def handle_transaction_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора типа транзакции"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к этой функции")
            return
        
        await update.callback_query.answer()
        
        callback_data = update.callback_query.data
        
        # Парсим callback_data: transaction_{type}_{receipt_id}
        parts = callback_data.split('_')
        if len(parts) != 3:
            return
        
        transaction_type = parts[1]  # income или expense
        receipt_id = int(parts[2])
        
        # Получаем данные чека
        with get_db_context() as db:
            receipt_file = db.query(ReceiptFile).filter(ReceiptFile.id == receipt_id).first()
            
            if not receipt_file:
                await update.callback_query.edit_message_text("❌ Чек не найден")
                return
            
            # Создаем транзакцию
            ocr_data = receipt_file.ocr_result
            amount = ocr_data.get('amount', 0)
            
            # Парсим дату
            transaction_date = datetime.utcnow()
            if ocr_data.get('date'):
                try:
                    transaction_date = datetime.fromisoformat(ocr_data['date'])
                except:
                    pass
            
            # Определяем категорию по умолчанию
            default_category = "Прочие доходы" if transaction_type == "income" else "Прочие расходы"
            
            # Создаем транзакцию
            transaction = MoneyTransaction(
                amount=amount,
                type=transaction_type,
                category=default_category,
                description=f"Транзакция из чека {receipt_file.filename}",
                date=transaction_date,
                receipt_file_path=receipt_file.file_path,
                ocr_data=ocr_data,
                is_ocr_processed=True,
                source="ocr",
                created_by_id=receipt_file.uploaded_by_id
            )
            
            db.add(transaction)
            
            # Связываем чек с транзакцией
            receipt_file.transaction_id = transaction.id
            
            db.commit()
            
            # Показываем подтверждение
            type_emoji = "📈" if transaction_type == "income" else "📉"
            type_name = "Доход" if transaction_type == "income" else "Расход"
            
            text = f"""
✅ <b>Транзакция создана!</b>

{type_emoji} <b>Тип:</b> {type_name}
💰 <b>Сумма:</b> {amount:,.2f} ₽
📅 <b>Дата:</b> {transaction_date.strftime('%d.%m.%Y')}
🏷️ <b>Категория:</b> {default_category}
📄 <b>Чек:</b> сохранен

Транзакция добавлена в вашу базу данных.
            """
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            keyboard = [
                [
                    InlineKeyboardButton("💼 Мои транзакции", callback_data="my_transactions"),
                    InlineKeyboardButton("📊 Аналитика", callback_data="money_analytics")
                ],
                [
                    InlineKeyboardButton("📄 Загрузить еще", callback_data="upload_receipt"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]
            ]
            
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            
            # Сбрасываем состояние пользователя
            self.user_states.pop(user_id, None)


    @standard_handler
    async def handle_my_transactions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр всех транзакций"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к этой функции")
            return
        
        await update.callback_query.answer()
        
        with get_db_context() as db:
            # Получаем последние 10 транзакций
            transactions = db.query(MoneyTransaction).order_by(
                MoneyTransaction.created_at.desc()
            ).limit(10).all()
            
            if not transactions:
                text = """
💼 <b>Мои транзакции</b>

📭 Транзакций пока нет.

Загрузите первый чек или создайте транзакцию вручную!
                """
                
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = [
                    [InlineKeyboardButton("📄 Загрузить чек", callback_data="upload_receipt")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="admin_money")]
                ]
                
                await update.callback_query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
                return
            
            # Формируем список транзакций
            text = "💼 <b>Последние транзакции</b>\n\n"
            
            total_income = 0
            total_expense = 0
            
            for transaction in transactions:
                emoji = "📈" if transaction.type == "income" else "📉"
                amount_str = f"+{transaction.amount:,.0f}" if transaction.type == "income" else f"-{transaction.amount:,.0f}"
                date_str = transaction.date.strftime('%d.%m.%Y') if transaction.date else "—"
                
                if transaction.type == "income":
                    total_income += transaction.amount
                else:
                    total_expense += transaction.amount
                
                text += f"{emoji} <b>{amount_str} ₽</b> - {transaction.category}\n"
                text += f"📅 {date_str}"
                if transaction.description:
                    text += f" | {transaction.description[:50]}{'...' if len(transaction.description) > 50 else ''}"
                text += "\n\n"
            
            text += f"💰 <b>Итого за период:</b>\n"
            text += f"📈 Доходы: +{total_income:,.0f} ₽\n"
            text += f"📉 Расходы: -{total_expense:,.0f} ₽\n"
            text += f"💵 Баланс: {total_income - total_expense:+,.0f} ₽"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("📈 Доходы", callback_data="view_income"),
                InlineKeyboardButton("📉 Расходы", callback_data="view_expenses")
            ],
            [
                InlineKeyboardButton("📊 Аналитика", callback_data="money_analytics"),
                InlineKeyboardButton("🏷️ Категории", callback_data="money_categories")
            ],
            [
                InlineKeyboardButton("🔙 Назад", callback_data="admin_money"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    @standard_handler
    async def handle_view_income(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр доходов"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к этой функции")
            return
        
        await update.callback_query.answer()
        
        with get_db_context() as db:
            # Получаем доходы за последний месяц
            from datetime import datetime, timedelta
            last_month = datetime.now() - timedelta(days=30)
            
            income_transactions = db.query(MoneyTransaction).filter(
                MoneyTransaction.type == "income",
                MoneyTransaction.date >= last_month
            ).order_by(MoneyTransaction.date.desc()).all()
            
            if not income_transactions:
                text = """
📈 <b>Доходы за последний месяц</b>

📭 Доходов пока нет.

Создайте первую транзакцию дохода!
                """
            else:
                text = "📈 <b>Доходы за последний месяц</b>\n\n"
                
                total = 0
                category_totals = {}
                
                for transaction in income_transactions:
                    total += transaction.amount
                    
                    if transaction.category not in category_totals:
                        category_totals[transaction.category] = 0
                    category_totals[transaction.category] += transaction.amount
                    
                    date_str = transaction.date.strftime('%d.%m.%Y') if transaction.date else "—"
                    text += f"💰 <b>+{transaction.amount:,.0f} ₽</b> - {transaction.category}\n"
                    text += f"📅 {date_str}"
                    if transaction.description:
                        text += f" | {transaction.description[:40]}{'...' if len(transaction.description) > 40 else ''}"
                    text += "\n\n"
                
                text += f"💵 <b>Общий доход: +{total:,.0f} ₽</b>\n\n"
                
                # Топ категорий
                if category_totals:
                    text += "<b>🏆 Топ категории:</b>\n"
                    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
                    for i, (category, amount) in enumerate(sorted_categories, 1):
                        text += f"{i}. {category}: +{amount:,.0f} ₽\n"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("📄 Загрузить чек", callback_data="upload_receipt"),
                InlineKeyboardButton("💼 Все транзакции", callback_data="my_transactions")
            ],
            [
                InlineKeyboardButton("📊 Аналитика", callback_data="money_analytics"),
                InlineKeyboardButton("🔙 Назад", callback_data="admin_money")
            ]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    @standard_handler
    async def handle_view_expenses(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр расходов"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к этой функции")
            return
        
        await update.callback_query.answer()
        
        with get_db_context() as db:
            # Получаем расходы за последний месяц
            from datetime import datetime, timedelta
            last_month = datetime.now() - timedelta(days=30)
            
            expense_transactions = db.query(MoneyTransaction).filter(
                MoneyTransaction.type == "expense",
                MoneyTransaction.date >= last_month
            ).order_by(MoneyTransaction.date.desc()).all()
            
            if not expense_transactions:
                text = """
📉 <b>Расходы за последний месяц</b>

📭 Расходов пока нет.

Загрузите чек или создайте транзакцию расхода!
                """
            else:
                text = "📉 <b>Расходы за последний месяц</b>\n\n"
                
                total = 0
                category_totals = {}
                
                for transaction in expense_transactions:
                    total += transaction.amount
                    
                    if transaction.category not in category_totals:
                        category_totals[transaction.category] = 0
                    category_totals[transaction.category] += transaction.amount
                    
                    date_str = transaction.date.strftime('%d.%m.%Y') if transaction.date else "—"
                    text += f"💸 <b>-{transaction.amount:,.0f} ₽</b> - {transaction.category}\n"
                    text += f"📅 {date_str}"
                    if transaction.description:
                        text += f" | {transaction.description[:40]}{'...' if len(transaction.description) > 40 else ''}"
                    text += "\n\n"
                
                text += f"💸 <b>Общий расход: -{total:,.0f} ₽</b>\n\n"
                
                # Топ категорий трат
                if category_totals:
                    text += "<b>💸 Топ категории трат:</b>\n"
                    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
                    for i, (category, amount) in enumerate(sorted_categories, 1):
                        text += f"{i}. {category}: -{amount:,.0f} ₽\n"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("📄 Загрузить чек", callback_data="upload_receipt"),
                InlineKeyboardButton("💼 Все транзакции", callback_data="my_transactions")
            ],
            [
                InlineKeyboardButton("📊 Аналитика", callback_data="money_analytics"),
                InlineKeyboardButton("🔙 Назад", callback_data="admin_money")
            ]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    @standard_handler
    async def handle_money_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр категорий"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к этой функции")
            return
        
        await update.callback_query.answer()
        
        with get_db_context() as db:
            income_categories = db.query(MoneyCategory).filter(
                MoneyCategory.type == "income", 
                MoneyCategory.is_active == True
            ).order_by(MoneyCategory.sort_order).all()
            
            expense_categories = db.query(MoneyCategory).filter(
                MoneyCategory.type == "expense", 
                MoneyCategory.is_active == True
            ).order_by(MoneyCategory.sort_order).all()
        
        text = "🏷️ <b>Категории доходов и расходов</b>\n\n"
        
        if income_categories:
            text += "📈 <b>Доходы:</b>\n"
            for cat in income_categories[:10]:  # Показываем первые 10
                text += f"• {cat.name}\n"
            if len(income_categories) > 10:
                text += f"... и еще {len(income_categories) - 10}\n"
            text += "\n"
        
        if expense_categories:
            text += "📉 <b>Расходы:</b>\n"
            for cat in expense_categories[:10]:  # Показываем первые 10
                text += f"• {cat.name}\n"
            if len(expense_categories) > 10:
                text += f"... и еще {len(expense_categories) - 10}\n"
        
        text += "\n💡 <i>Категории используются для автоматической классификации транзакций.</i>"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("📄 Загрузить чек", callback_data="upload_receipt"),
                InlineKeyboardButton("💼 Транзакции", callback_data="my_transactions")
            ],
            [
                InlineKeyboardButton("🔙 Назад", callback_data="admin_money"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    @standard_handler
    async def handle_money_analytics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Аналитика доходов и расходов"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ У вас нет доступа к этой функции")
            return
        
        await update.callback_query.answer()
        
        with get_db_context() as db:
            from datetime import datetime, timedelta
            
            # Данные за разные периоды
            now = datetime.now()
            last_month = now - timedelta(days=30)
            last_week = now - timedelta(days=7)
            
            # Общая статистика
            total_transactions = db.query(MoneyTransaction).count()
            total_income = db.query(MoneyTransaction).filter(
                MoneyTransaction.type == "income"
            ).count()
            total_expenses = db.query(MoneyTransaction).filter(
                MoneyTransaction.type == "expense"
            ).count()
            
            # Суммы за месяц
            month_income_sum = db.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM money_transactions WHERE type = 'income' AND date >= ?",
                (last_month,)
            ).scalar() or 0
            
            month_expense_sum = db.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM money_transactions WHERE type = 'expense' AND date >= ?",
                (last_month,)
            ).scalar() or 0
            
            # Суммы за неделю
            week_income_sum = db.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM money_transactions WHERE type = 'income' AND date >= ?",
                (last_week,)
            ).scalar() or 0
            
            week_expense_sum = db.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM money_transactions WHERE type = 'expense' AND date >= ?",
                (last_week,)
            ).scalar() or 0
            
            # Топ категории за месяц
            top_income_categories = db.execute("""
                SELECT category, SUM(amount) as total
                FROM money_transactions 
                WHERE type = 'income' AND date >= ?
                GROUP BY category 
                ORDER BY total DESC 
                LIMIT 3
            """, (last_month,)).fetchall()
            
            top_expense_categories = db.execute("""
                SELECT category, SUM(amount) as total
                FROM money_transactions 
                WHERE type = 'expense' AND date >= ?
                GROUP BY category 
                ORDER BY total DESC 
                LIMIT 3
            """, (last_month,)).fetchall()
        
        text = "📊 <b>Аналитика финансов</b>\n\n"
        
        # Общая статистика
        text += f"📈 <b>Общая статистика:</b>\n"
        text += f"• Всего транзакций: {total_transactions}\n"
        text += f"• Доходы: {total_income} транзакций\n"
        text += f"• Расходы: {total_expenses} транзакций\n\n"
        
        # За месяц
        month_balance = month_income_sum - month_expense_sum
        text += f"📅 <b>За последний месяц:</b>\n"
        text += f"📈 Доходы: +{month_income_sum:,.0f} ₽\n"
        text += f"📉 Расходы: -{month_expense_sum:,.0f} ₽\n"
        text += f"💰 Баланс: {month_balance:+,.0f} ₽\n\n"
        
        # За неделю
        week_balance = week_income_sum - week_expense_sum
        text += f"📅 <b>За последнюю неделю:</b>\n"
        text += f"📈 Доходы: +{week_income_sum:,.0f} ₽\n"
        text += f"📉 Расходы: -{week_expense_sum:,.0f} ₽\n"
        text += f"💰 Баланс: {week_balance:+,.0f} ₽\n\n"
        
        # Топ категории доходов
        if top_income_categories:
            text += f"🏆 <b>Топ доходы (месяц):</b>\n"
            for i, (category, amount) in enumerate(top_income_categories, 1):
                text += f"{i}. {category}: +{amount:,.0f} ₽\n"
            text += "\n"
        
        # Топ категории расходов
        if top_expense_categories:
            text += f"💸 <b>Топ расходы (месяц):</b>\n"
            for i, (category, amount) in enumerate(top_expense_categories, 1):
                text += f"{i}. {category}: -{amount:,.0f} ₽\n"
            text += "\n"
        
        # Прогноз
        if month_income_sum > 0 and month_expense_sum > 0:
            text += f"📊 <b>Прогноз:</b>\n"
            avg_daily_income = month_income_sum / 30
            avg_daily_expense = month_expense_sum / 30
            monthly_forecast = (avg_daily_income - avg_daily_expense) * 30
            text += f"• Средний доход/день: +{avg_daily_income:,.0f} ₽\n"
            text += f"• Средний расход/день: -{avg_daily_expense:,.0f} ₽\n"
            text += f"• Прогноз на месяц: {monthly_forecast:+,.0f} ₽\n"
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("📈 Доходы", callback_data="view_income"),
                InlineKeyboardButton("📉 Расходы", callback_data="view_expenses")
            ],
            [
                InlineKeyboardButton("💼 Транзакции", callback_data="my_transactions"),
                InlineKeyboardButton("🏷️ Категории", callback_data="money_categories")
            ],
            [
                InlineKeyboardButton("🔙 Назад", callback_data="admin_money"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]
        ]
        
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )


# Создаем экземпляр обработчика
money_handler = MoneyManagementHandler()