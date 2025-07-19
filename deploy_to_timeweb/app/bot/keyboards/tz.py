from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional

def get_tz_actions_keyboard() -> InlineKeyboardMarkup:
    """Действия с созданным ТЗ"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Полное ТЗ", callback_data="tz_show_full"),
            InlineKeyboardButton("✏️ Редактировать", callback_data="tz_edit")
        ],
        [
            InlineKeyboardButton("💾 Сохранить проект", callback_data="tz_save"),
            InlineKeyboardButton("🔄 Пересоздать", callback_data="tz_recreate")  # ИСПРАВЛЕНО: InlineKeyirtualButton -> InlineKeyboardButton
        ],
        [
            InlineKeyboardButton("📤 Поделиться", callback_data="tz_share"),
            InlineKeyboardButton("📄 Экспорт PDF", callback_data="tz_export_pdf")
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_step_by_step_keyboard(step: int, total_steps: int) -> InlineKeyboardMarkup:
    """Клавиатура для пошагового создания"""
    keyboard = []
    
    # Индикатор прогресса
    progress_text = f"Шаг {step + 1} из {total_steps}"
    keyboard.append([InlineKeyboardButton(f"📊 {progress_text}", callback_data="progress_info")])
    
    # Кнопки навигации
    nav_buttons = []
    if step > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data="step_back"))
    
    nav_buttons.append(InlineKeyboardButton("❌ Отменить", callback_data="main_menu"))
    
    if step < total_steps - 1:
        nav_buttons.append(InlineKeyboardButton("⏭ Пропустить", callback_data="step_skip"))
    
    keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def get_tz_editing_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для редактирования ТЗ"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Название", callback_data="edit_title"),
            InlineKeyboardButton("📄 Описание", callback_data="edit_description")
        ],
        [
            InlineKeyboardButton("🎯 Цели", callback_data="edit_goals"),
            InlineKeyboardButton("👥 Аудитория", callback_data="edit_audience")
        ],
        [
            InlineKeyboardButton("⚙️ Функции", callback_data="edit_functions"),
            InlineKeyboardButton("🔗 Интеграции", callback_data="edit_integrations")
        ],
        [
            InlineKeyboardButton("📱 Платформы", callback_data="edit_platforms"),
            InlineKeyboardButton("💰 Бюджет", callback_data="edit_budget")
        ],
        [
            InlineKeyboardButton("✅ Готово", callback_data="edit_complete"),
            InlineKeyboardButton("❌ Отменить", callback_data="tz_show_preview")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_complexity_keyboard() -> InlineKeyboardMarkup:
    """Выбор сложности проекта"""
    keyboard = [
        [InlineKeyboardButton("🟢 Простой (до 25,000₽)", callback_data="complexity_simple")],
        [InlineKeyboardButton("🟡 Средний (25-50,000₽)", callback_data="complexity_medium")],
        [InlineKeyboardButton("🟠 Сложный (50-100,000₽)", callback_data="complexity_complex")],  # ИСПРАВЛЕНО: добавлено окончание строки
        [InlineKeyboardButton("🔴 Премиум (100,000₽+)", callback_data="complexity_premium")],
        [InlineKeyboardButton("🤔 Не знаю", callback_data="complexity_unknown")],
        [InlineKeyboardButton("🔙 Назад", callback_data="create_tz")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_project_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа проекта"""
    keyboard = [
        [
            InlineKeyboardButton("🤖 Telegram бот", callback_data="type_telegram"),
            InlineKeyboardButton("💬 WhatsApp бот", callback_data="type_whatsapp")
        ],
        [
            InlineKeyboardButton("🌐 Веб-бот", callback_data="type_web"),
            InlineKeyboardButton("🔗 Интеграция", callback_data="type_integration")
        ],
        [
            InlineKeyboardButton("📱 Мобильное приложение", callback_data="type_mobile"),
            InlineKeyboardButton("💼 CRM система", callback_data="type_crm")
        ],
        [
            InlineKeyboardButton("🤖 AI решение", callback_data="type_ai"),
            InlineKeyboardButton("📊 Аналитика", callback_data="type_analytics")
        ],
        [
            InlineKeyboardButton("🔄 Автоматизация", callback_data="type_automation"),
            InlineKeyboardButton("🆕 Другое", callback_data="type_other")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="create_tz")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_platforms_keyboard() -> InlineKeyboardMarkup:
    """Выбор платформ (множественный выбор)"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Telegram", callback_data="platform_telegram"),
            InlineKeyboardButton("💬 WhatsApp", callback_data="platform_whatsapp")
        ],
        [
            InlineKeyboardButton("🌐 Веб-сайт", callback_data="platform_web"),
            InlineKeyboardButton("📲 Мобильное приложение", callback_data="platform_mobile")
        ],
        [
            InlineKeyboardButton("💼 1C", callback_data="platform_1c"),
            InlineKeyboardButton("📊 Bitrix24", callback_data="platform_bitrix")
        ],
        [
            InlineKeyboardButton("🛒 Shopify", callback_data="platform_shopify"),
            InlineKeyboardButton("🎨 WordPress", callback_data="platform_wordpress")
        ],
        [
            InlineKeyboardButton("📧 Email системы", callback_data="platform_email"),
            InlineKeyboardButton("☁️ Облачные сервисы", callback_data="platform_cloud")
        ],
        [
            InlineKeyboardButton("✅ Выбрано", callback_data="platforms_selected"),
            InlineKeyboardButton("🔙 Назад", callback_data="create_tz")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_functions_keyboard() -> InlineKeyboardMarkup:
    """Выбор функций проекта"""
    keyboard = [
        [
            InlineKeyboardButton("💬 Чат-бот", callback_data="func_chatbot"),
            InlineKeyboardButton("🛒 Интернет-магазин", callback_data="func_ecommerce")
        ],
        [
            InlineKeyboardButton("📊 Аналитика", callback_data="func_analytics"),
            InlineKeyboardButton("🔔 Уведомления", callback_data="func_notifications")
        ],
        [
            InlineKeyboardButton("💳 Платежи", callback_data="func_payments"),
            InlineKeyboardButton("👤 Авторизация", callback_data="func_auth")
        ],
        [
            InlineKeyboardButton("📋 CRM функции", callback_data="func_crm"),
            InlineKeyboardButton("🗃️ База данных", callback_data="func_database")
        ],
        [
            InlineKeyboardButton("🔗 API интеграции", callback_data="func_api"),
            InlineKeyboardButton("🤖 AI/ML", callback_data="func_ai")
        ],
        [
            InlineKeyboardButton("📧 Email рассылка", callback_data="func_mailing"),
            InlineKeyboardButton("📱 Push уведомления", callback_data="func_push")
        ],
        [
            InlineKeyboardButton("✅ Выбрано", callback_data="functions_selected"),
            InlineKeyboardButton("🔙 Назад", callback_data="create_tz")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_budget_keyboard() -> InlineKeyboardMarkup:
    """Выбор бюджета проекта"""
    keyboard = [
        [InlineKeyboardButton("💰 До 25,000₽", callback_data="budget_25k")],
        [InlineKeyboardButton("💰 25,000 - 50,000₽", callback_data="budget_50k")],
        [InlineKeyboardButton("💰 50,000 - 100,000₽", callback_data="budget_100k")],
        [InlineKeyboardButton("💰 100,000 - 200,000₽", callback_data="budget_200k")],
        [InlineKeyboardButton("💰 200,000₽+", callback_data="budget_200k_plus")],
        [InlineKeyboardButton("🤔 Нужна консультация", callback_data="budget_consultation")],
        [InlineKeyboardButton("🔙 Назад", callback_data="create_tz")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_timeline_keyboard() -> InlineKeyboardMarkup:
    """Выбор временных рамок"""
    keyboard = [
        [InlineKeyboardButton("⚡ Срочно (1-3 дня)", callback_data="timeline_urgent")],
        [InlineKeyboardButton("🏃 Быстро (1 неделя)", callback_data="timeline_fast")],
        [InlineKeyboardButton("📅 Стандартно (2-4 недели)", callback_data="timeline_standard")],
        [InlineKeyboardButton("🗓️ Не спеша (1-2 месяца)", callback_data="timeline_relaxed")],
        [InlineKeyboardButton("🤷 Без ограничений", callback_data="timeline_flexible")],
        [InlineKeyboardButton("🔙 Назад", callback_data="create_tz")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_audience_keyboard() -> InlineKeyboardMarkup:
    """Выбор целевой аудитории"""
    keyboard = [
        [
            InlineKeyboardButton("👨‍💼 B2B клиенты", callback_data="audience_b2b"),
            InlineKeyboardButton("👥 B2C клиенты", callback_data="audience_b2c")
        ],
        [
            InlineKeyboardButton("🏢 Сотрудники компании", callback_data="audience_employees"),
            InlineKeyboardButton("🎓 Студенты", callback_data="audience_students")
        ],
        [
            InlineKeyboardButton("👴 Пожилые люди", callback_data="audience_elderly"),
            InlineKeyboardButton("👶 Молодежь", callback_data="audience_youth")
        ],
        [
            InlineKeyboardButton("🔧 IT специалисты", callback_data="audience_it"),
            InlineKeyboardButton("🏥 Медработники", callback_data="audience_medical")
        ],
        [
            InlineKeyboardButton("🏫 Образование", callback_data="audience_education"),
            InlineKeyboardButton("🌍 Широкая аудитория", callback_data="audience_general")
        ],
        [
            InlineKeyboardButton("✅ Выбрано", callback_data="audience_selected"),
            InlineKeyboardButton("🔙 Назад", callback_data="create_tz")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_integrations_keyboard() -> InlineKeyboardMarkup:
    """Выбор интеграций"""
    keyboard = [
        [
            InlineKeyboardButton("💳 Платежные системы", callback_data="int_payments"),
            InlineKeyboardButton("📧 Email сервисы", callback_data="int_email")
        ],
        [
            InlineKeyboardButton("📊 Google Analytics", callback_data="int_analytics"),
            InlineKeyboardButton("☁️ Облачные хранилища", callback_data="int_cloud")
        ],
        [
            InlineKeyboardButton("📱 Социальные сети", callback_data="int_social"),
            InlineKeyboardButton("💼 CRM системы", callback_data="int_crm")
        ],
        [
            InlineKeyboardButton("🗃️ Базы данных", callback_data="int_databases"),
            InlineKeyboardButton("🔗 REST API", callback_data="int_api")
        ],
        [
            InlineKeyboardButton("📋 Google Sheets", callback_data="int_sheets"),
            InlineKeyboardButton("📞 Телефония", callback_data="int_telephony")
        ],
        [
            InlineKeyboardButton("🤖 AI сервисы", callback_data="int_ai"),
            InlineKeyboardButton("📦 Логистика", callback_data="int_logistics")
        ],
        [
            InlineKeyboardButton("✅ Выбрано", callback_data="integrations_selected"),
            InlineKeyboardButton("🔙 Назад", callback_data="create_tz")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tz_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение создания ТЗ"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Создать проект", callback_data="tz_confirm"),
            InlineKeyboardButton("✏️ Редактировать", callback_data="tz_edit")
        ],
        [
            InlineKeyboardButton("👀 Предпросмотр", callback_data="tz_preview"),
            InlineKeyboardButton("💬 Консультация", callback_data="tz_consultation")
        ],
        [
            InlineKeyboardButton("📄 Экспорт PDF", callback_data="tz_export"),
            InlineKeyboardButton("📤 Отправить email", callback_data="tz_email")
        ],
        [
            InlineKeyboardButton("🔄 Пересоздать", callback_data="tz_restart"),
            InlineKeyboardButton("❌ Отменить", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_file_type_keyboard() -> InlineKeyboardMarkup:
    """Выбор типа загружаемого файла"""
    keyboard = [
        [
            InlineKeyboardButton("📄 Техническое задание", callback_data="file_tz"),
            InlineKeyboardButton("📋 Бриф", callback_data="file_brief")
        ],
        [
            InlineKeyboardButton("🎨 Дизайн-макеты", callback_data="file_design"),
            InlineKeyboardButton("📊 Схемы/диаграммы", callback_data="file_schemes")
        ],
        [
            InlineKeyboardButton("📝 Текстовый документ", callback_data="file_text"),
            InlineKeyboardButton("🖼️ Изображения", callback_data="file_images")
        ],
        [
            InlineKeyboardButton("📋 Другой документ", callback_data="file_other"),
            InlineKeyboardButton("🔙 Назад", callback_data="create_tz")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_voice_processing_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для обработки голосового сообщения"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Использовать текст", callback_data="voice_accept"),
            InlineKeyboardButton("🎤 Записать заново", callback_data="voice_retry")
        ],
        [
            InlineKeyboardButton("✏️ Редактировать текст", callback_data="voice_edit"),
            InlineKeyboardButton("➕ Добавить детали", callback_data="voice_add_details")
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="create_tz"),
            InlineKeyboardButton("❌ Отменить", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tz_templates_keyboard() -> InlineKeyboardMarkup:
    """Выбор шаблона ТЗ"""
    keyboard = [
        [
            InlineKeyboardButton("🤖 Telegram бот", callback_data="template_telegram_bot"),
            InlineKeyboardButton("🛒 Интернет-магазин", callback_data="template_ecommerce")
        ],
        [
            InlineKeyboardButton("💼 CRM система", callback_data="template_crm"),
            InlineKeyboardButton("📱 Мобильное приложение", callback_data="template_mobile")
        ],
        [
            InlineKeyboardButton("🌐 Веб-сайт", callback_data="template_website"),
            InlineKeyboardButton("🔗 API интеграция", callback_data="template_api")
        ],
        [
            InlineKeyboardButton("🤖 AI решение", callback_data="template_ai"),
            InlineKeyboardButton("📊 Аналитическая система", callback_data="template_analytics")
        ],
        [
            InlineKeyboardButton("📝 Пустой шаблон", callback_data="template_blank"),
            InlineKeyboardButton("🔙 Назад", callback_data="create_tz")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tz_sharing_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для шаринга ТЗ"""
    keyboard = [
        [
            InlineKeyboardButton("📧 Email", callback_data="share_email"),
            InlineKeyboardButton("💬 Telegram", callback_data="share_telegram")
        ],
        [
            InlineKeyboardButton("📋 Скопировать ссылку", callback_data="share_link"),
            InlineKeyboardButton("📄 Скачать PDF", callback_data="share_pdf")
        ],
        [
            InlineKeyboardButton("📤 WhatsApp", callback_data="share_whatsapp"),
            InlineKeyboardButton("💼 Slack", callback_data="share_slack")
        ],
        [
            InlineKeyboardButton("🔙 Назад к ТЗ", callback_data="tz_show_preview"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tz_export_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для экспорта ТЗ"""
    keyboard = [
        [
            InlineKeyboardButton("📄 PDF документ", callback_data="export_pdf"),
            InlineKeyboardButton("📝 Word документ", callback_data="export_docx")
        ],
        [
            InlineKeyboardButton("📧 Отправить на email", callback_data="export_email"),
            InlineKeyboardButton("💾 Сохранить в проекте", callback_data="export_save")
        ],
        [
            InlineKeyboardButton("📋 Копировать текст", callback_data="export_text"),
            InlineKeyboardButton("🔗 Создать ссылку", callback_data="export_link")
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="tz_show_preview"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)