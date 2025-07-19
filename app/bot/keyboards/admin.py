"""
Клавиатуры для админских функций
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional, Dict, Any

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Главное админское меню"""
    keyboard = [
        [
            InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton("📊 Проекты", callback_data="admin_projects")
        ],
        [
            InlineKeyboardButton("📈 Аналитика", callback_data="admin_analytics"),
            InlineKeyboardButton("💼 Портфолио", callback_data="admin_portfolio")
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings"),
            InlineKeyboardButton("🤖 AI Настройки", callback_data="admin_ai_settings")
        ],
        [
            InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
            InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("💾 Бекап", callback_data="admin_backup"),
            InlineKeyboardButton("🔧 Техподдержка", callback_data="admin_support")
        ],
        [InlineKeyboardButton("🔙 Выход из админки", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_users_keyboard() -> InlineKeyboardMarkup:
    """Управление пользователями"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Список пользователей", callback_data="admin_users_list"),
            InlineKeyboardButton("🔍 Поиск пользователя", callback_data="admin_users_search")
        ],
        [
            InlineKeyboardButton("📊 Статистика пользователей", callback_data="admin_users_stats"),
            InlineKeyboardButton("🚫 Заблокированные", callback_data="admin_users_blocked")
        ],
        [
            InlineKeyboardButton("⭐ VIP пользователи", callback_data="admin_users_vip"),
            InlineKeyboardButton("🆕 Новые пользователи", callback_data="admin_users_new")
        ],
        [
            InlineKeyboardButton("📈 Активность", callback_data="admin_users_activity"),
            InlineKeyboardButton("📤 Экспорт данных", callback_data="admin_users_export")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_projects_keyboard() -> InlineKeyboardMarkup:
    """Управление проектами"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Все проекты", callback_data="admin_projects_all"),
            InlineKeyboardButton("🆕 Новые заявки", callback_data="admin_projects_new")
        ],
        [
            InlineKeyboardButton("🔄 В работе", callback_data="admin_projects_progress"),
            InlineKeyboardButton("✅ Завершенные", callback_data="admin_projects_completed")
        ],
        [
            InlineKeyboardButton("⏳ Ожидают ответа", callback_data="admin_projects_pending"),
            InlineKeyboardButton("❌ Отмененные", callback_data="admin_projects_cancelled")
        ],
        [
            InlineKeyboardButton("💰 По стоимости", callback_data="admin_projects_by_cost"),
            InlineKeyboardButton("📊 Статистика", callback_data="admin_projects_stats")
        ],
        [
            InlineKeyboardButton("📤 Экспорт", callback_data="admin_projects_export"),
            InlineKeyboardButton("📥 Импорт", callback_data="admin_projects_import")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_settings_keyboard() -> InlineKeyboardMarkup:
    """Настройки бота"""
    keyboard = [
        [
            InlineKeyboardButton("💬 Сообщения", callback_data="admin_settings_messages"),
            InlineKeyboardButton("💰 Цены", callback_data="admin_settings_prices")
        ],
        [
            InlineKeyboardButton("📞 Контакты", callback_data="admin_settings_contacts"),
            InlineKeyboardButton("🕐 Рабочие часы", callback_data="admin_settings_hours")
        ],
        [
            InlineKeyboardButton("🔔 Уведомления", callback_data="admin_settings_notifications"),
            InlineKeyboardButton("🎨 Интерфейс", callback_data="admin_settings_ui")
        ],
        [
            InlineKeyboardButton("🔗 Интеграции", callback_data="admin_settings_integrations"),
            InlineKeyboardButton("📊 Лимиты", callback_data="admin_settings_limits")
        ],
        [
            InlineKeyboardButton("💾 Сохранить настройки", callback_data="admin_settings_save"),
            InlineKeyboardButton("🔄 Сброс к умолчанию", callback_data="admin_settings_reset")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Рассылка сообщений"""
    keyboard = [
        [
            InlineKeyboardButton("📢 Всем пользователям", callback_data="admin_broadcast_all"),
            InlineKeyboardButton("⭐ VIP пользователям", callback_data="admin_broadcast_vip")
        ],
        [
            InlineKeyboardButton("🔥 Активным пользователям", callback_data="admin_broadcast_active"),
            InlineKeyboardButton("😴 Неактивным", callback_data="admin_broadcast_inactive")
        ],
        [
            InlineKeyboardButton("🆕 Новым пользователям", callback_data="admin_broadcast_new"),
            InlineKeyboardButton("🎯 По сегментам", callback_data="admin_broadcast_segments")
        ],
        [
            InlineKeyboardButton("📝 Создать рассылку", callback_data="admin_broadcast_create"),
            InlineKeyboardButton("📋 Шаблоны", callback_data="admin_broadcast_templates")
        ],
        [
            InlineKeyboardButton("📊 История рассылок", callback_data="admin_broadcast_history"),
            InlineKeyboardButton("⏰ Отложенные", callback_data="admin_broadcast_scheduled")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_analytics_keyboard() -> InlineKeyboardMarkup:
    """Аналитика и отчеты"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Общая статистика", callback_data="admin_analytics_general"),
            InlineKeyboardButton("👥 Пользователи", callback_data="admin_analytics_users")
        ],
        [
            InlineKeyboardButton("💼 Проекты", callback_data="admin_analytics_projects"),
            InlineKeyboardButton("💰 Финансы", callback_data="admin_analytics_finance")
        ],
        [
            InlineKeyboardButton("🤖 AI Консультант", callback_data="admin_analytics_ai"),
            InlineKeyboardButton("📈 Конверсия", callback_data="admin_analytics_conversion")
        ],
        [
            InlineKeyboardButton("📅 За период", callback_data="admin_analytics_period"),
            InlineKeyboardButton("📋 Отчеты", callback_data="admin_analytics_reports")
        ],
        [
            InlineKeyboardButton("📤 Экспорт", callback_data="admin_analytics_export"),
            InlineKeyboardButton("📧 Отправить отчет", callback_data="admin_analytics_email")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_ai_settings_keyboard() -> InlineKeyboardMarkup:
    """Настройки AI"""
    keyboard = [
        [
            InlineKeyboardButton("🎭 Промпты", callback_data="admin_ai_prompts"),
            InlineKeyboardButton("🔧 Модели", callback_data="admin_ai_models")
        ],
        [
            InlineKeyboardButton("🌡️ Температура", callback_data="admin_ai_temperature"),
            InlineKeyboardButton("📏 Длина ответов", callback_data="admin_ai_length")
        ],
        [
            InlineKeyboardButton("🚫 Фильтры", callback_data="admin_ai_filters"),
            InlineKeyboardButton("💰 API ключи", callback_data="admin_ai_keys")
        ],
        [
            InlineKeyboardButton("📊 Статистика API", callback_data="admin_ai_stats"),
            InlineKeyboardButton("🧪 Тестирование", callback_data="admin_ai_test")
        ],
        [
            InlineKeyboardButton("💾 Сохранить", callback_data="admin_ai_save"),
            InlineKeyboardButton("🔄 Перезагрузить", callback_data="admin_ai_reload")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_actions_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Действия с пользователем"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Профиль", callback_data=f"admin_user_profile_{user_id}"),
            InlineKeyboardButton("📊 Проекты", callback_data=f"admin_user_projects_{user_id}")
        ],
        [
            InlineKeyboardButton("💬 Написать", callback_data=f"admin_user_message_{user_id}"),
            InlineKeyboardButton("📞 Связаться", callback_data=f"admin_user_contact_{user_id}")
        ],
        [
            InlineKeyboardButton("⭐ Сделать VIP", callback_data=f"admin_user_vip_{user_id}"),
            InlineKeyboardButton("🚫 Заблокировать", callback_data=f"admin_user_block_{user_id}")
        ],
        [
            InlineKeyboardButton("📈 Статистика", callback_data=f"admin_user_stats_{user_id}"),
            InlineKeyboardButton("📝 Заметки", callback_data=f"admin_user_notes_{user_id}")
        ],
        [
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"admin_user_delete_{user_id}"),
            InlineKeyboardButton("🔄 Сбросить данные", callback_data=f"admin_user_reset_{user_id}")
        ],
        [InlineKeyboardButton("🔙 К пользователям", callback_data="admin_users")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_project_admin_actions_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Админские действия с проектом"""
    keyboard = [
        [
            InlineKeyboardButton("👀 Просмотр", callback_data=f"admin_project_view_{project_id}"),
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"admin_project_edit_{project_id}")
        ],
        [
            InlineKeyboardButton("💰 Изменить цену", callback_data=f"admin_project_price_{project_id}"),
            InlineKeyboardButton("📅 Изменить срок", callback_data=f"admin_project_deadline_{project_id}")
        ],
        [
            InlineKeyboardButton("✅ Принять", callback_data=f"admin_project_accept_{project_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"admin_project_reject_{project_id}")
        ],
        [
            InlineKeyboardButton("💬 Написать клиенту", callback_data=f"admin_project_message_{project_id}"),
            InlineKeyboardButton("📄 Создать ТЗ", callback_data=f"admin_project_tz_{project_id}")
        ],
        [
            InlineKeyboardButton("📊 Аналитика", callback_data=f"admin_project_analytics_{project_id}"),
            InlineKeyboardButton("📤 Экспорт", callback_data=f"admin_project_export_{project_id}")
        ],
        [InlineKeyboardButton("🔙 К проектам", callback_data="admin_projects")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_project_status_admin_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Изменение статуса проекта (расширенная админская версия)"""
    keyboard = [
        [
            InlineKeyboardButton("🆕 Новый", callback_data=f"admin_status_new_{project_id}"),
            InlineKeyboardButton("👀 Рассмотрение", callback_data=f"admin_status_review_{project_id}")
        ],
        [
            InlineKeyboardButton("✅ Принят", callback_data=f"admin_status_accepted_{project_id}"),
            InlineKeyboardButton("💰 Оплачен", callback_data=f"admin_status_paid_{project_id}")
        ],
        [
            InlineKeyboardButton("🔄 В работе", callback_data=f"admin_status_in_progress_{project_id}"),
            InlineKeyboardButton("🧪 Тестирование", callback_data=f"admin_status_testing_{project_id}")
        ],
        [
            InlineKeyboardButton("🎉 Завершен", callback_data=f"admin_status_completed_{project_id}"),
            InlineKeyboardButton("📦 Доставлен", callback_data=f"admin_status_delivered_{project_id}")
        ],
        [
            InlineKeyboardButton("⏸️ Приостановлен", callback_data=f"admin_status_paused_{project_id}"),
            InlineKeyboardButton("❌ Отменен", callback_data=f"admin_status_cancelled_{project_id}")
        ],
        [
            InlineKeyboardButton("🔄 Переработка", callback_data=f"admin_status_revision_{project_id}"),
            InlineKeyboardButton("🆘 Проблема", callback_data=f"admin_status_issue_{project_id}")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"admin_project_view_{project_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_broadcast_confirmation_keyboard(broadcast_type: str) -> InlineKeyboardMarkup:
    """Подтверждение рассылки"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Отправить сейчас", callback_data=f"admin_broadcast_confirm_{broadcast_type}"),
            InlineKeyboardButton("⏰ Запланировать", callback_data=f"admin_broadcast_schedule_{broadcast_type}")
        ],
        [
            InlineKeyboardButton("👀 Предпросмотр", callback_data=f"admin_broadcast_preview_{broadcast_type}"),
            InlineKeyboardButton("🧪 Тест отправка", callback_data=f"admin_broadcast_test_{broadcast_type}")
        ],
        [
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"admin_broadcast_edit_{broadcast_type}"),
            InlineKeyboardButton("❌ Отмена", callback_data="admin_broadcast")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_backup_keyboard() -> InlineKeyboardMarkup:
    """Управление бекапами"""
    keyboard = [
        [
            InlineKeyboardButton("💾 Создать бекап", callback_data="admin_backup_create"),
            InlineKeyboardButton("📥 Восстановить", callback_data="admin_backup_restore")
        ],
        [
            InlineKeyboardButton("📋 Список бекапов", callback_data="admin_backup_list"),
            InlineKeyboardButton("🗑️ Удалить старые", callback_data="admin_backup_cleanup")
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="admin_backup_settings"),
            InlineKeyboardButton("📊 Статистика", callback_data="admin_backup_stats")
        ],
        [
            InlineKeyboardButton("☁️ Облачный бекап", callback_data="admin_backup_cloud"),
            InlineKeyboardButton("⏰ Расписание", callback_data="admin_backup_schedule")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_support_keyboard() -> InlineKeyboardMarkup:
    """Техподдержка"""
    keyboard = [
        [
            InlineKeyboardButton("🎫 Активные тикеты", callback_data="admin_support_active"),
            InlineKeyboardButton("✅ Закрытые тикеты", callback_data="admin_support_closed")
        ],
        [
            InlineKeyboardButton("🆕 Новые обращения", callback_data="admin_support_new"),
            InlineKeyboardButton("⏳ Ожидают ответа", callback_data="admin_support_pending")
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data="admin_support_stats"),
            InlineKeyboardButton("📋 Шаблоны ответов", callback_data="admin_support_templates")
        ],
        [
            InlineKeyboardButton("👥 Операторы", callback_data="admin_support_operators"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="admin_support_settings")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_portfolio_keyboard() -> InlineKeyboardMarkup:
    """Управление портфолио"""
    keyboard = [
        [
            InlineKeyboardButton("📋 Все проекты", callback_data="admin_portfolio_all"),
            InlineKeyboardButton("➕ Добавить проект", callback_data="admin_portfolio_add")
        ],
        [
            InlineKeyboardButton("⭐ Рекомендуемые", callback_data="admin_portfolio_featured"),
            InlineKeyboardButton("📊 По категориям", callback_data="admin_portfolio_categories")
        ],
        [
            InlineKeyboardButton("🎨 Настройки отображения", callback_data="admin_portfolio_display"),
            InlineKeyboardButton("📈 Статистика просмотров", callback_data="admin_portfolio_stats")
        ],
        [
            InlineKeyboardButton("📤 Экспорт", callback_data="admin_portfolio_export"),
            InlineKeyboardButton("📥 Импорт", callback_data="admin_portfolio_import")
        ],
        [
            InlineKeyboardButton("🔄 Сортировка", callback_data="admin_portfolio_sort"),
            InlineKeyboardButton("🗑️ Архивные", callback_data="admin_portfolio_archived")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_portfolio_item_admin_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Действия с элементом портфолио"""
    keyboard = [
        [
            InlineKeyboardButton("👀 Просмотр", callback_data=f"admin_portfolio_view_{item_id}"),
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"admin_portfolio_edit_{item_id}")
        ],
        [
            InlineKeyboardButton("⭐ Рекомендовать", callback_data=f"admin_portfolio_feature_{item_id}"),
            InlineKeyboardButton("📊 Статистика", callback_data=f"admin_portfolio_stats_{item_id}")
        ],
        [
            InlineKeyboardButton("🔄 Изменить порядок", callback_data=f"admin_portfolio_order_{item_id}"),
            InlineKeyboardButton("📋 Дублировать", callback_data=f"admin_portfolio_duplicate_{item_id}")
        ],
        [
            InlineKeyboardButton("🗃️ Архивировать", callback_data=f"admin_portfolio_archive_{item_id}"),
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"admin_portfolio_delete_{item_id}")
        ],
        [InlineKeyboardButton("🔙 К портфолио", callback_data="admin_portfolio")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Общая статистика"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Сегодня", callback_data="admin_stats_today"),
            InlineKeyboardButton("📅 Эта неделя", callback_data="admin_stats_week")
        ],
        [
            InlineKeyboardButton("🗓️ Этот месяц", callback_data="admin_stats_month"),
            InlineKeyboardButton("📈 Весь период", callback_data="admin_stats_all")
        ],
        [
            InlineKeyboardButton("💰 Финансовая сводка", callback_data="admin_stats_finance"),
            InlineKeyboardButton("👥 Пользователи", callback_data="admin_stats_users")
        ],
        [
            InlineKeyboardButton("📊 Проекты", callback_data="admin_stats_projects"),
            InlineKeyboardButton("🤖 AI Использование", callback_data="admin_stats_ai")
        ],
        [
            InlineKeyboardButton("📧 Отправить отчет", callback_data="admin_stats_email"),
            InlineKeyboardButton("📤 Экспорт", callback_data="admin_stats_export")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard(
    action: str, 
    item_id: Optional[int] = None,
    confirm_text: str = "✅ Подтвердить",
    cancel_text: str = "❌ Отмена"
) -> InlineKeyboardMarkup:
    """Универсальная клавиатура подтверждения для админских действий"""
    suffix = f"_{item_id}" if item_id else ""
    keyboard = [
        [
            InlineKeyboardButton(confirm_text, callback_data=f"admin_confirm_{action}{suffix}"),
            InlineKeyboardButton(cancel_text, callback_data=f"admin_cancel_{action}{suffix}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str,
    additional_buttons: List[List[InlineKeyboardButton]] = None,
    back_callback: str = "admin_main"
) -> InlineKeyboardMarkup:
    """Пагинация для админских списков"""
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
    
    if len(pagination_row) > 1:
        keyboard.append(pagination_row)
    
    # Дополнительные админские кнопки
    admin_row = [
        InlineKeyboardButton("🔍 Поиск", callback_data=f"{callback_prefix}_search"),
        InlineKeyboardButton("📊 Фильтр", callback_data=f"{callback_prefix}_filter")
    ]
    keyboard.append(admin_row)
    
    # Кнопка назад
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=back_callback)])
    
    return InlineKeyboardMarkup(keyboard)

def get_quick_actions_keyboard() -> InlineKeyboardMarkup:
    """Быстрые действия для админа"""
    keyboard = [
        [
            InlineKeyboardButton("🆕 Новые заявки", callback_data="admin_quick_new_projects"),
            InlineKeyboardButton("💬 Непрочитанные", callback_data="admin_quick_unread")
        ],
        [
            InlineKeyboardButton("🔔 Уведомления", callback_data="admin_quick_notifications"),
            InlineKeyboardButton("📊 Сводка дня", callback_data="admin_quick_daily")
        ],
        [
            InlineKeyboardButton("💰 Финансы", callback_data="admin_quick_finance"),
            InlineKeyboardButton("🚨 Проблемы", callback_data="admin_quick_issues")
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_tools_keyboard() -> InlineKeyboardMarkup:
    """Инструменты администратора"""
    keyboard = [
        [
            InlineKeyboardButton("🔧 Техническое обслуживание", callback_data="admin_tools_maintenance"),
            InlineKeyboardButton("🔄 Перезапуск бота", callback_data="admin_tools_restart")
        ],
        [
            InlineKeyboardButton("📊 Мониторинг", callback_data="admin_tools_monitoring"),
            InlineKeyboardButton("📝 Логи", callback_data="admin_tools_logs")
        ],
        [
            InlineKeyboardButton("🔍 Отладка", callback_data="admin_tools_debug"),
            InlineKeyboardButton("⚡ Производительность", callback_data="admin_tools_performance")
        ],
        [
            InlineKeyboardButton("🛡️ Безопасность", callback_data="admin_tools_security"),
            InlineKeyboardButton("🔐 Права доступа", callback_data="admin_tools_permissions")
        ],
        [InlineKeyboardButton("🔙 Админ меню", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Вспомогательные функции для создания динамических админских клавиатур

def create_admin_list_keyboard(
    items: List[Dict[str, Any]],
    callback_prefix: str,
    title_field: str = "title",
    id_field: str = "id",
    items_per_row: int = 1,
    show_actions: bool = True,
    back_callback: str = "admin_main"
) -> InlineKeyboardMarkup:
    """Создание админской клавиатуры из списка элементов"""
    keyboard = []
    
    # Группируем элементы по строкам
    for i in range(0, len(items), items_per_row):
        row = []
        for j in range(items_per_row):
            if i + j < len(items):
                item = items[i + j]
                title = item.get(title_field, "Без названия")
                item_id = item.get(id_field, 0)
                
                # Добавляем статус к названию если есть
                if 'status' in item:
                    status_emoji = get_status_emoji(item['status'])
                    title = f"{status_emoji} {title}"
                
                row.append(
                    InlineKeyboardButton(
                        title[:25] + "..." if len(title) > 25 else title,
                        callback_data=f"{callback_prefix}_{item_id}"
                    )
                )
        if row:
            keyboard.append(row)
    
    # Админские действия
    if show_actions:
        actions_row = [
            InlineKeyboardButton("➕ Добавить", callback_data=f"{callback_prefix}_add"),
            InlineKeyboardButton("📊 Статистика", callback_data=f"{callback_prefix}_stats")
        ]
        keyboard.append(actions_row)
    
    # Кнопка назад
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=back_callback)])
    
    return InlineKeyboardMarkup(keyboard)

def get_status_emoji(status: str) -> str:
    """Получить эмодзи для статуса"""
    status_emojis = {
        'new': '🆕',
        'review': '👀',
        'accepted': '✅',
        'in_progress': '🔄',
        'testing': '🧪',
        'completed': '🎉',
        'cancelled': '❌',
        'paused': '⏸️',
        'active': '🟢',
        'inactive': '🔴',
        'blocked': '🚫',
        'vip': '⭐',
        'featured': '🌟'
    }
    return status_emojis.get(status, '📋')

def get_priority_keyboard(callback_prefix: str, item_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Клавиатура для установки приоритета"""
    suffix = f"_{item_id}" if item_id else ""
    keyboard = [
        [
            InlineKeyboardButton("🔴 Высокий", callback_data=f"{callback_prefix}_priority_high{suffix}"),
            InlineKeyboardButton("🟡 Средний", callback_data=f"{callback_prefix}_priority_medium{suffix}")
        ],
        [
            InlineKeyboardButton("🟢 Низкий", callback_data=f"{callback_prefix}_priority_low{suffix}"),
            InlineKeyboardButton("⚪ Не задан", callback_data=f"{callback_prefix}_priority_none{suffix}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)