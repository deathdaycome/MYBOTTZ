from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional

def get_consultant_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню AI консультанта"""
    keyboard = [
        [InlineKeyboardButton("🤖 Начать новую консультацию", callback_data="consultant_new_session")],
        [InlineKeyboardButton("📋 Продолжить сессию", callback_data="consultant_continue_session")],
        [InlineKeyboardButton("📚 Популярные вопросы", callback_data="consultant_popular_questions")],
        [InlineKeyboardButton("📊 История консультаций", callback_data="consultant_history")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_consultant_topics_keyboard() -> InlineKeyboardMarkup:
    """Выбор темы консультации"""
    keyboard = [
        [
            InlineKeyboardButton("🤖 Telegram боты", callback_data="topic_telegram_bots"),
            InlineKeyboardButton("💬 WhatsApp боты", callback_data="topic_whatsapp_bots")
        ],
        [
            InlineKeyboardButton("🌐 Веб-боты", callback_data="topic_web_bots"),
            InlineKeyboardButton("🔗 Интеграции", callback_data="topic_integrations")
        ],
        [
            InlineKeyboardButton("🏗 Архитектура", callback_data="topic_architecture"),
            InlineKeyboardButton("💾 Базы данных", callback_data="topic_databases")
        ],
        [
            InlineKeyboardButton("🚀 Деплой", callback_data="topic_deployment"),
            InlineKeyboardButton("🔐 Безопасность", callback_data="topic_security")
        ],
        [
            InlineKeyboardButton("💰 Ценообразование", callback_data="topic_pricing"),
            InlineKeyboardButton("📈 Маркетинг", callback_data="topic_marketing")
        ],
        [InlineKeyboardButton("🎯 Другая тема", callback_data="topic_other")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_consultant_session_keyboard(session_id: str) -> InlineKeyboardMarkup:
    """Клавиатура активной сессии консультанта"""
    keyboard = [
        [InlineKeyboardButton("❓ Задать вопрос", callback_data=f"consultant_ask_{session_id}")],
        [
            InlineKeyboardButton("📚 Примеры кода", callback_data=f"consultant_examples_{session_id}"),
            InlineKeyboardButton("🔧 Инструменты", callback_data=f"consultant_tools_{session_id}")
        ],
        [
            InlineKeyboardButton("📝 Сохранить чат", callback_data=f"consultant_save_{session_id}"),
            InlineKeyboardButton("⭐ Оценить ответ", callback_data=f"consultant_rate_{session_id}")
        ],
        [InlineKeyboardButton("🏁 Завершить сессию", callback_data=f"consultant_end_{session_id}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_popular_questions_keyboard() -> InlineKeyboardMarkup:
    """Популярные вопросы консультанту"""
    keyboard = [
        [InlineKeyboardButton("🚀 Как начать разрабатывать ботов?", callback_data="q_how_to_start")],
        [InlineKeyboardButton("💰 Сколько стоит разработка бота?", callback_data="q_bot_cost")],
        [InlineKeyboardButton("⏱ Сколько времени нужно на разработку?", callback_data="q_development_time")],
        [InlineKeyboardButton("🔧 Какие технологии использовать?", callback_data="q_technologies")],
        [InlineKeyboardButton("🤝 Как найти первых клиентов?", callback_data="q_find_clients")],
        [InlineKeyboardButton("📊 Как оценивать сложность проекта?", callback_data="q_project_complexity")],
        [InlineKeyboardButton("🔒 Как обеспечить безопасность?", callback_data="q_security")],
        [InlineKeyboardButton("📈 Как масштабировать бота?", callback_data="q_scaling")],
        [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_consultant_examples_keyboard(topic: str) -> InlineKeyboardMarkup:
    """Примеры кода по теме"""
    if topic == "telegram_bots":
        keyboard = [
            [InlineKeyboardButton("📝 Простой эхо-бот", callback_data="example_echo_bot")],
            [InlineKeyboardButton("📊 Бот с меню", callback_data="example_menu_bot")],
            [InlineKeyboardButton("💾 Бот с базой данных", callback_data="example_db_bot")],
            [InlineKeyboardButton("💳 Бот с платежами", callback_data="example_payment_bot")]
        ]
    elif topic == "web_bots":
        keyboard = [
            [InlineKeyboardButton("🌐 Веб-чат виджет", callback_data="example_web_widget")],
            [InlineKeyboardButton("🔗 REST API бот", callback_data="example_rest_bot")],
            [InlineKeyboardButton("📱 PWA чат", callback_data="example_pwa_chat")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📝 Базовые примеры", callback_data="example_basic")],
            [InlineKeyboardButton("🔧 Продвинутые примеры", callback_data="example_advanced")]
        ]
    
    keyboard.extend([
        [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_consultant_tools_keyboard() -> InlineKeyboardMarkup:
    """Инструменты разработчика"""
    keyboard = [
        [
            InlineKeyboardButton("🐍 Python библиотеки", callback_data="tools_python"),
            InlineKeyboardButton("📚 Документация", callback_data="tools_docs")
        ],
        [
            InlineKeyboardButton("🛠 IDE и редакторы", callback_data="tools_ide"),
            InlineKeyboardButton("☁️ Хостинг сервисы", callback_data="tools_hosting")
        ],
        [
            InlineKeyboardButton("📊 Мониторинг", callback_data="tools_monitoring"),
            InlineKeyboardButton("🔒 Безопасность", callback_data="tools_security")
        ],
        [
            InlineKeyboardButton("💳 Платежи", callback_data="tools_payments"),
            InlineKeyboardButton("📈 Аналитика", callback_data="tools_analytics")
        ],
        [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_consultant_rating_keyboard(session_id: str, query_id: int) -> InlineKeyboardMarkup:
    """Оценка ответа консультанта"""
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data=f"rate_1_{session_id}_{query_id}"),
            InlineKeyboardButton("⭐⭐", callback_data=f"rate_2_{session_id}_{query_id}"),
            InlineKeyboardButton("⭐⭐⭐", callback_data=f"rate_3_{session_id}_{query_id}"),
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data=f"rate_4_{session_id}_{query_id}"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"rate_5_{session_id}_{query_id}")
        ],
        [InlineKeyboardButton("💬 Оставить комментарий", callback_data=f"comment_{session_id}_{query_id}")],
        [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_consultant_history_keyboard(sessions: List[dict], page: int = 1, items_per_page: int = 5) -> InlineKeyboardMarkup:
    """История консультаций с пагинацией"""
    keyboard = []
    
    # Сессии на текущей странице
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_sessions = sessions[start_idx:end_idx]
    
    for session in page_sessions:
        session_id = session.get('session_id', '')
        topic = session.get('topic', 'Общие вопросы')
        created_at = session.get('created_at', '')
        
        # Форматируем дату
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_str = date_obj.strftime('%d.%m %H:%M')
        except:
            date_str = created_at[:16] if created_at else ''
        
        button_text = f"{topic} • {date_str}"
        if len(button_text) > 35:
            button_text = button_text[:32] + "..."
        
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"history_session_{session_id}")
        ])
    
    # Пагинация
    total_pages = (len(sessions) + items_per_page - 1) // items_per_page
    if total_pages > 1:
        pagination_row = []
        
        if page > 1:
            pagination_row.append(
                InlineKeyboardButton("⬅️", callback_data=f"history_page_{page - 1}")
            )
        
        pagination_row.append(
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data="page_info")
        )
        
        if page < total_pages:
            pagination_row.append(
                InlineKeyboardButton("➡️", callback_data=f"history_page_{page + 1}")
            )
        
        keyboard.append(pagination_row)
    
    # Основные кнопки
    keyboard.extend([
        [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_session_actions_keyboard(session_id: str) -> InlineKeyboardMarkup:
    """Действия с сессией консультации"""
    keyboard = [
        [InlineKeyboardButton("📖 Просмотреть полностью", callback_data=f"session_view_{session_id}")],
        [
            InlineKeyboardButton("📝 Экспорт в PDF", callback_data=f"session_export_pdf_{session_id}"),
            InlineKeyboardButton("📄 Экспорт в TXT", callback_data=f"session_export_txt_{session_id}")
        ],
        [InlineKeyboardButton("🔄 Продолжить сессию", callback_data=f"session_continue_{session_id}")],
        [InlineKeyboardButton("🗑 Удалить сессию", callback_data=f"session_delete_{session_id}")],
        [InlineKeyboardButton("📊 История", callback_data="consultant_history")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_quick_questions_keyboard() -> InlineKeyboardMarkup:
    """Быстрые вопросы в активной сессии"""
    keyboard = [
        [InlineKeyboardButton("💡 Покажи пример кода", callback_data="quick_show_example")],
        [InlineKeyboardButton("🔧 Какие инструменты использовать?", callback_data="quick_tools_recommend")],
        [InlineKeyboardButton("💰 Сколько это будет стоить?", callback_data="quick_estimate_cost")],
        [InlineKeyboardButton("⏱ Сколько времени займет?", callback_data="quick_estimate_time")],
        [InlineKeyboardButton("🚀 Как лучше реализовать?", callback_data="quick_best_approach")],
        [InlineKeyboardButton("🔒 Вопросы безопасности?", callback_data="quick_security_tips")],
        [InlineKeyboardButton("📈 Как масштабировать?", callback_data="quick_scaling_tips")],
        [InlineKeyboardButton("❓ Задать свой вопрос", callback_data="ask_custom_question")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_consultant_feedback_keyboard(session_id: str) -> InlineKeyboardMarkup:
    """Обратная связь по сессии"""
    keyboard = [
        [InlineKeyboardButton("👍 Полезно", callback_data=f"feedback_helpful_{session_id}")],
        [InlineKeyboardButton("👎 Не помогло", callback_data=f"feedback_not_helpful_{session_id}")],
        [InlineKeyboardButton("💡 Предложить улучшение", callback_data=f"feedback_suggest_{session_id}")],
        [InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")]
    ]
    return InlineKeyboardMarkup(keyboard)