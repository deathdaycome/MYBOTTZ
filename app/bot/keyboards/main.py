from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional
from ...config.settings import settings

def get_main_menu_keyboard(user_id: int = None) -> InlineKeyboardMarkup:
    """Главное меню бота"""
    keyboard = [
        [
            InlineKeyboardButton("🚀 Создать ТЗ", callback_data="create_tz"),
            InlineKeyboardButton("📊 Мои проекты", callback_data="my_projects")
        ],
        [
            InlineKeyboardButton("🧮 Калькулятор", callback_data="calculator"),
            InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")
        ],
        [
            InlineKeyboardButton("❓ FAQ", callback_data="faq"),
            InlineKeyboardButton("📞 Контакты", callback_data="contacts")
        ],
        [
            InlineKeyboardButton("💼 Портфолио", url=f"https://t.me/{settings.PORTFOLIO_CHANNEL_ID}" if settings.PORTFOLIO_CHANNEL_ID else "https://t.me/your_portfolio_channel")
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
        ]
    ]
    
    # Добавляем кнопку "Админ консоль" только для главного админа
    if user_id and user_id in settings.ADMIN_IDS:
        keyboard.append([
            InlineKeyboardButton("🔧 Админ консоль", callback_data="admin_console")
        ])
    
    return InlineKeyboardMarkup(keyboard)

def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

def get_create_tz_methods_keyboard() -> InlineKeyboardMarkup:
    """Методы создания ТЗ"""
    keyboard = [
        [InlineKeyboardButton("📝 Описать текстом", callback_data="tz_text")],
        [InlineKeyboardButton("🎤 Голосовое сообщение", callback_data="tz_voice")],
        [InlineKeyboardButton("📋 Пошаговое создание", callback_data="tz_step_by_step")],
        [InlineKeyboardButton("📄 Загрузить документ", callback_data="tz_upload")],
        [InlineKeyboardButton("📋 Собственное ТЗ", callback_data="tz_own")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_portfolio_categories_keyboard() -> InlineKeyboardMarkup:
    """Категории портфолио"""
    keyboard = [
        [
            InlineKeyboardButton("🤖 Telegram боты", callback_data="portfolio_telegram"),
            InlineKeyboardButton("💬 WhatsApp боты", callback_data="portfolio_whatsapp")
        ],
        [
            InlineKeyboardButton("🌐 Веб-боты", callback_data="portfolio_web"),
            InlineKeyboardButton("🔗 Интеграции", callback_data="portfolio_integration")
        ],
        [
            InlineKeyboardButton("⭐ Рекомендуемые", callback_data="portfolio_featured"),
            InlineKeyboardButton("📊 Все проекты", callback_data="portfolio_all")
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_project_actions_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Действия с проектом"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Детали", callback_data=f"project_details_{project_id}"),
            InlineKeyboardButton("💬 Чат", callback_data=f"project_chat_{project_id}")
        ],
        [
            InlineKeyboardButton("✏️ Правки", callback_data=f"project_revisions_{project_id}")
        ],
        [
            InlineKeyboardButton("📊 Мои проекты", callback_data="my_projects"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_project_status_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Изменение статуса проекта (для админа)"""
    keyboard = [
        [
            InlineKeyboardButton("🆕 Новый", callback_data=f"status_new_{project_id}"),
            InlineKeyboardButton("👀 Рассмотрение", callback_data=f"status_review_{project_id}")
        ],
        [
            InlineKeyboardButton("✅ Принят", callback_data=f"status_accepted_{project_id}"),
            InlineKeyboardButton("🔄 В работе", callback_data=f"status_in_progress_{project_id}")
        ],
        [
            InlineKeyboardButton("🧪 Тестирование", callback_data=f"status_testing_{project_id}"),
            InlineKeyboardButton("🎉 Завершен", callback_data=f"status_completed_{project_id}")
        ],
        [InlineKeyboardButton("❌ Отменен", callback_data=f"status_cancelled_{project_id}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_calculator_keyboard() -> InlineKeyboardMarkup:
    """Калькулятор стоимости"""
    keyboard = [
        [
            InlineKeyboardButton("🟢 Простой бот", callback_data="calc_simple"),
            InlineKeyboardButton("🟡 Средний бот", callback_data="calc_medium")
        ],
        [
            InlineKeyboardButton("🟠 Сложный бот", callback_data="calc_complex"),
            InlineKeyboardButton("🔴 Премиум бот", callback_data="calc_premium")
        ],
        [InlineKeyboardButton("⚙️ Настроить детально", callback_data="calc_detailed")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_faq_categories_keyboard() -> InlineKeyboardMarkup:
    """Категории FAQ"""
    keyboard = [
        [
            InlineKeyboardButton("💰 Ценообразование", callback_data="faq_pricing"),
            InlineKeyboardButton("⏰ Сроки", callback_data="faq_timeline")
        ],
        [
            InlineKeyboardButton("🛠 Поддержка", callback_data="faq_support"),
            InlineKeyboardButton("🔗 Интеграции", callback_data="faq_integration")
        ],
        [
            InlineKeyboardButton("📱 Платформы", callback_data="faq_platforms"),
            InlineKeyboardButton("📊 Все вопросы", callback_data="faq_all")
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_consultation_keyboard() -> InlineKeyboardMarkup:
    """Консультации"""
    keyboard = [
        [InlineKeyboardButton("📅 Записаться на консультацию", callback_data="book_consultation")],
        [InlineKeyboardButton("📞 Связаться сейчас", callback_data="contact_now")],
        [InlineKeyboardButton("📋 Оставить заявку", callback_data="leave_request")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_contacts_keyboard() -> InlineKeyboardMarkup:
    """Контакты"""
    keyboard = [
        [InlineKeyboardButton("💬 Написать в Telegram", url="https://t.me/your_username")],
        [InlineKeyboardButton("📧 Email", callback_data="contact_email")],
        [InlineKeyboardButton("📞 Телефон", callback_data="contact_phone")],
        [InlineKeyboardButton("🌐 Сайт", url="https://your-website.com")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_yes_no_keyboard(action: str, item_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Универсальная клавиатура Да/Нет"""
    suffix = f"_{item_id}" if item_id else ""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=f"yes_{action}{suffix}"),
            InlineKeyboardButton("❌ Нет", callback_data=f"no_{action}{suffix}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str,
    additional_buttons: List[List[InlineKeyboardButton]] = None
) -> InlineKeyboardMarkup:
    """Универсальная пагинация"""
    keyboard = []
    
    # Добавляем дополнительные кнопки если есть
    if additional_buttons:
        keyboard.extend(additional_buttons)
    
    # Кнопки пагинации
    pagination_row = []
    
    if current_page > 1:
        pagination_row.append(
            InlineKeyboardButton("⬅️", callback_data=f"{callback_prefix}_page_{current_page - 1}")
        )
    
    pagination_row.append(
        InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="page_info")
    )
    
    if current_page < total_pages:
        pagination_row.append(
            InlineKeyboardButton("➡️", callback_data=f"{callback_prefix}_page_{current_page + 1}")
        )
    
    if len(pagination_row) > 1:  # Показываем пагинацию только если есть что показывать
        keyboard.append(pagination_row)
    
    # Кнопка в главное меню
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def get_rating_keyboard(callback_prefix: str, item_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Клавиатура для оценки (1-5 звезд)"""
    suffix = f"_{item_id}" if item_id else ""
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data=f"{callback_prefix}_rate_1{suffix}"),
            InlineKeyboardButton("⭐⭐", callback_data=f"{callback_prefix}_rate_2{suffix}"),
            InlineKeyboardButton("⭐⭐⭐", callback_data=f"{callback_prefix}_rate_3{suffix}"),
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data=f"{callback_prefix}_rate_4{suffix}"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"{callback_prefix}_rate_5{suffix}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_share_keyboard(project_title: str = "проект") -> InlineKeyboardMarkup:
    """Клавиатура для шаринга"""
    keyboard = [
        [InlineKeyboardButton("📤 Поделиться в Telegram", 
                             switch_inline_query=f"Посмотрите мой {project_title}!")],
        [InlineKeyboardButton("📋 Скопировать ссылку", callback_data="copy_link")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Вспомогательные функции для создания динамических клавиатур

def create_items_keyboard(
    items: List[dict],
    callback_prefix: str,
    title_field: str = "title",
    id_field: str = "id",
    items_per_row: int = 1,
    show_back_button: bool = True
) -> InlineKeyboardMarkup:
    """Создание клавиатуры из списка элементов"""
    keyboard = []
    
    # Группируем элементы по строкам
    for i in range(0, len(items), items_per_row):
        row = []
        for j in range(items_per_row):
            if i + j < len(items):
                item = items[i + j]
                title = item.get(title_field, "Без названия")
                item_id = item.get(id_field, 0)
                row.append(
                    InlineKeyboardButton(
                        title[:30] + "..." if len(title) > 30 else title,
                        callback_data=f"{callback_prefix}_{item_id}"
                    )
                )
        if row:
            keyboard.append(row)
    
    # Кнопка назад
    if show_back_button:
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def get_project_revisions_keyboard(project_id: int, revisions_count: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для управления правками проекта"""
    keyboard = [
        [InlineKeyboardButton("📝 Создать правку", callback_data=f"create_revision_{project_id}")],
    ]
    
    if revisions_count > 0:
        keyboard.append([
            InlineKeyboardButton(f"📋 Мои правки ({revisions_count})", callback_data=f"list_revisions_{project_id}")
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("🔙 К проекту", callback_data=f"project_details_{project_id}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_revision_actions_keyboard(revision_id: int, project_id: int, status: str) -> InlineKeyboardMarkup:
    """Клавиатура для управления конкретной правкой"""
    keyboard = []
    
    # Кнопки в зависимости от статуса
    if status == "pending":
        keyboard.append([
            InlineKeyboardButton("💬 Добавить комментарий", callback_data=f"revision_comment_{revision_id}"),
            InlineKeyboardButton("📎 Прикрепить файл", callback_data=f"revision_file_{revision_id}")
        ])
    elif status == "in_progress":
        keyboard.append([
            InlineKeyboardButton("💬 Добавить комментарий", callback_data=f"revision_comment_{revision_id}"),
            InlineKeyboardButton("📎 Прикрепить файл", callback_data=f"revision_file_{revision_id}")
        ])
    elif status == "completed":
        keyboard.append([
            InlineKeyboardButton("💬 Комментировать", callback_data=f"revision_comment_{revision_id}")
        ])
    
    # Навигационные кнопки
    keyboard.extend([
        [InlineKeyboardButton("🔙 К правкам", callback_data=f"project_revisions_{project_id}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_revision_priority_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для выбора приоритета правки"""
    keyboard = [
        [
            InlineKeyboardButton("🟢 Низкий", callback_data=f"priority_low_{project_id}"),
            InlineKeyboardButton("🔵 Обычный", callback_data=f"priority_normal_{project_id}")
        ],
        [
            InlineKeyboardButton("🟡 Высокий", callback_data=f"priority_high_{project_id}"),
            InlineKeyboardButton("🔴 Срочный", callback_data=f"priority_urgent_{project_id}")
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data=f"project_revisions_{project_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_revision_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения создания правки"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Создать правку", callback_data=f"confirm_revision_{project_id}"),
            InlineKeyboardButton("❌ Отмена", callback_data=f"project_revisions_{project_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_file_type_keyboard(revision_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа файла для правки"""
    keyboard = [
        [
            InlineKeyboardButton("🖼️ Изображение", callback_data=f"file_type_image_{revision_id}"),
            InlineKeyboardButton("📄 Документ", callback_data=f"file_type_document_{revision_id}")
        ],
        [
            InlineKeyboardButton("🎥 Видео", callback_data=f"file_type_video_{revision_id}"),
            InlineKeyboardButton("🎵 Аудио", callback_data=f"file_type_audio_{revision_id}")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"revision_details_{revision_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_bot_creation_guide_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для гайда по созданию бота"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Открыть BotFather", url="https://t.me/BotFather")
        ],
        [
            InlineKeyboardButton("📖 Пошаговая инструкция", callback_data="bot_guide_steps")
        ],
        [
            InlineKeyboardButton("🔑 Ввести API токен", callback_data="bot_enter_token")
        ],
        [
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_bot_guide_steps_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для пошагового гайда"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Открыть BotFather", url="https://t.me/BotFather")
        ],
        [
            InlineKeyboardButton("🔑 Ввести API токен", callback_data="bot_enter_token")
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="create_bot_guide")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_console_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура админ консоли"""
    keyboard = [
        [
            InlineKeyboardButton("💰 Управление финансами", callback_data="admin_money"),
            InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("📱 Уведомления", callback_data="admin_notifications"),
            InlineKeyboardButton("⚙️ Настройки бота", callback_data="admin_bot_settings")
        ],
        [
            InlineKeyboardButton("📁 Файлы проектов", callback_data="admin_project_files"),
            InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_money_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления финансами"""
    keyboard = [
        [
            InlineKeyboardButton("📄 Загрузить чек", callback_data="upload_receipt"),
            InlineKeyboardButton("💼 Мои транзакции", callback_data="my_transactions")
        ],
        [
            InlineKeyboardButton("📈 Доходы", callback_data="view_income"),
            InlineKeyboardButton("📉 Расходы", callback_data="view_expenses")
        ],
        [
            InlineKeyboardButton("📊 Аналитика", callback_data="money_analytics"),
            InlineKeyboardButton("🏷️ Категории", callback_data="money_categories")
        ],
        [
            InlineKeyboardButton("🔙 Админ консоль", callback_data="admin_console"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)