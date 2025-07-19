"""
Навигационные клавиатуры и breadcrumbs для бота
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional, Dict, Any, Tuple

class NavigationBreadcrumbs:
    """Класс для работы с хлебными крошками навигации"""
    
    def __init__(self):
        self.breadcrumbs_map = {
            # Основные разделы
            'main_menu': {'title': '🏠 Главная', 'parent': None},
            'create_tz': {'title': '🚀 Создать ТЗ', 'parent': 'main_menu'},
            'portfolio': {'title': '💼 Портфолио', 'parent': 'main_menu'},
            'my_projects': {'title': '📊 Мои проекты', 'parent': 'main_menu'},
            'calculator': {'title': '🧮 Калькулятор', 'parent': 'main_menu'},
            'consultant': {'title': '🤖 AI Консультант', 'parent': 'main_menu'},
            'faq': {'title': '❓ FAQ', 'parent': 'main_menu'},
            'consultation': {'title': '💬 Консультация', 'parent': 'main_menu'},
            'contacts': {'title': '📞 Контакты', 'parent': 'main_menu'},
            
            # Подразделы создания ТЗ
            'tz_text': {'title': '📝 Текстом', 'parent': 'create_tz'},
            'tz_voice': {'title': '🎤 Голосом', 'parent': 'create_tz'},
            'tz_step_by_step': {'title': '📋 Пошагово', 'parent': 'create_tz'},
            'tz_upload': {'title': '📄 Документ', 'parent': 'create_tz'},
            
            # Подразделы портфолио
            'portfolio_telegram': {'title': '🤖 Telegram боты', 'parent': 'portfolio'},
            'portfolio_whatsapp': {'title': '💬 WhatsApp боты', 'parent': 'portfolio'},
            'portfolio_web': {'title': '🌐 Веб-боты', 'parent': 'portfolio'},
            'portfolio_integration': {'title': '🔗 Интеграции', 'parent': 'portfolio'},
            'portfolio_featured': {'title': '⭐ Рекомендуемые', 'parent': 'portfolio'},
            'portfolio_all': {'title': '📊 Все проекты', 'parent': 'portfolio'},
            
            # Подразделы FAQ
            'faq_pricing': {'title': '💰 Ценообразование', 'parent': 'faq'},
            'faq_timeline': {'title': '⏰ Сроки', 'parent': 'faq'},
            'faq_support': {'title': '🛠 Поддержка', 'parent': 'faq'},
            'faq_integration': {'title': '🔗 Интеграции', 'parent': 'faq'},
            'faq_platforms': {'title': '📱 Платформы', 'parent': 'faq'},
            'faq_all': {'title': '📊 Все вопросы', 'parent': 'faq'},
            
            # Калькулятор
            'calc_simple': {'title': '🟢 Простой', 'parent': 'calculator'},
            'calc_medium': {'title': '🟡 Средний', 'parent': 'calculator'},
            'calc_complex': {'title': '🟠 Сложный', 'parent': 'calculator'},
            'calc_premium': {'title': '🔴 Премиум', 'parent': 'calculator'},
            'calc_detailed': {'title': '⚙️ Детально', 'parent': 'calculator'},
            
            # Консультации
            'book_consultation': {'title': '📅 Записаться', 'parent': 'consultation'},
            'contact_now': {'title': '📞 Связаться', 'parent': 'consultation'},
            'leave_request': {'title': '📋 Заявка', 'parent': 'consultation'},
            
            # Админка
            'admin_main': {'title': '⚙️ Админка', 'parent': 'main_menu'},
            'admin_users': {'title': '👥 Пользователи', 'parent': 'admin_main'},
            'admin_projects': {'title': '📊 Проекты', 'parent': 'admin_main'},
            'admin_analytics': {'title': '📈 Аналитика', 'parent': 'admin_main'},
            'admin_settings': {'title': '⚙️ Настройки', 'parent': 'admin_main'},
            'admin_broadcast': {'title': '📢 Рассылка', 'parent': 'admin_main'},
            'admin_portfolio': {'title': '💼 Портфолио', 'parent': 'admin_main'},
        }
    
    def get_breadcrumb_path(self, current_section: str) -> List[Dict[str, str]]:
        """Получить путь хлебных крошек до текущего раздела"""
        path = []
        section = current_section
        
        while section and section in self.breadcrumbs_map:
            section_info = self.breadcrumbs_map[section]
            path.insert(0, {
                'callback': section,
                'title': section_info['title']
            })
            section = section_info['parent']
        
        return path
    
    def get_parent_section(self, current_section: str) -> Optional[str]:
        """Получить родительский раздел"""
        if current_section in self.breadcrumbs_map:
            return self.breadcrumbs_map[current_section]['parent']
        return None

# Глобальный экземпляр для использования в модуле
navigation = NavigationBreadcrumbs()

def get_breadcrumb_keyboard(current_section: str, max_buttons: int = 3) -> List[List[InlineKeyboardButton]]:
    """Создать клавиатуру с хлебными крошками"""
    path = navigation.get_breadcrumb_path(current_section)
    
    if len(path) <= 1:
        return []
    
    # Ограничиваем количество кнопок
    if len(path) > max_buttons:
        # Показываем главную, ... и последние кнопки
        breadcrumb_buttons = [
            InlineKeyboardButton(path[0]['title'], callback_data=path[0]['callback'])
        ]
        
        if len(path) > max_buttons:
            breadcrumb_buttons.append(InlineKeyboardButton("...", callback_data="breadcrumb_info"))
        
        # Добавляем последние кнопки
        for item in path[-(max_buttons-2):]:
            if item != path[0]:  # Избегаем дублирования
                breadcrumb_buttons.append(
                    InlineKeyboardButton(item['title'], callback_data=item['callback'])
                )
    else:
        # Показываем все кнопки
        breadcrumb_buttons = [
            InlineKeyboardButton(item['title'], callback_data=item['callback'])
            for item in path[:-1]  # Исключаем текущий раздел
        ]
    
    return [breadcrumb_buttons] if breadcrumb_buttons else []

def get_back_button(current_section: str) -> Optional[InlineKeyboardButton]:
    """Получить кнопку 'Назад' для текущего раздела"""
    parent = navigation.get_parent_section(current_section)
    if parent:
        parent_info = navigation.breadcrumbs_map.get(parent, {})
        title = parent_info.get('title', '🔙 Назад')
        return InlineKeyboardButton(f"🔙 {title.replace('🏠 ', '').replace('⚙️ ', '')}", 
                                   callback_data=parent)
    return None

def get_navigation_keyboard(
    current_section: str,
    additional_buttons: List[List[InlineKeyboardButton]] = None,
    show_breadcrumbs: bool = True,
    show_back_button: bool = True,
    show_home_button: bool = True
) -> InlineKeyboardMarkup:
    """Создать полную навигационную клавиатуру"""
    keyboard = []
    
    # Добавляем хлебные крошки
    if show_breadcrumbs:
        breadcrumbs = get_breadcrumb_keyboard(current_section)
        keyboard.extend(breadcrumbs)
    
    # Добавляем дополнительные кнопки
    if additional_buttons:
        keyboard.extend(additional_buttons)
    
    # Навигационные кнопки
    nav_buttons = []
    
    if show_back_button:
        back_btn = get_back_button(current_section)
        if back_btn:
            nav_buttons.append(back_btn)
    
    if show_home_button and current_section != 'main_menu':
        nav_buttons.append(InlineKeyboardButton("🏠 Главная", callback_data="main_menu"))
    
    if nav_buttons:
        # Разбиваем навигационные кнопки по 2 в ряд
        for i in range(0, len(nav_buttons), 2):
            row = nav_buttons[i:i+2]
            keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

def get_section_menu_keyboard(section: str) -> InlineKeyboardMarkup:
    """Получить меню для конкретного раздела"""
    keyboards = {
        'create_tz': get_create_tz_navigation(),
        'portfolio': get_portfolio_navigation(),
        'my_projects': get_my_projects_navigation(),
        'calculator': get_calculator_navigation(),
        'consultant': get_consultant_navigation(),
        'faq': get_faq_navigation(),
        'consultation': get_consultation_navigation(),
        'admin_main': get_admin_navigation(),
    }
    
    return keyboards.get(section, get_navigation_keyboard(section))

def get_create_tz_navigation() -> InlineKeyboardMarkup:
    """Навигация для создания ТЗ"""
    keyboard = [
        [InlineKeyboardButton("📝 Описать текстом", callback_data="tz_text")],
        [InlineKeyboardButton("🎤 Голосовое сообщение", callback_data="tz_voice")],
        [InlineKeyboardButton("📋 Пошаговое создание", callback_data="tz_step_by_step")],
        [InlineKeyboardButton("📄 Загрузить документ", callback_data="tz_upload")],
    ]
    
    return get_navigation_keyboard('create_tz', keyboard, show_breadcrumbs=False)

def get_portfolio_navigation() -> InlineKeyboardMarkup:
    """Навигация по портфолио"""
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
    ]
    
    return get_navigation_keyboard('portfolio', keyboard, show_breadcrumbs=False)

def get_my_projects_navigation() -> InlineKeyboardMarkup:
    """Навигация по проектам пользователя"""
    keyboard = [
        [
            InlineKeyboardButton("🆕 Новые", callback_data="projects_new"),
            InlineKeyboardButton("🔄 В работе", callback_data="projects_active")
        ],
        [
            InlineKeyboardButton("✅ Завершенные", callback_data="projects_completed"),
            InlineKeyboardButton("📊 Все проекты", callback_data="projects_all")
        ],
        [InlineKeyboardButton("📈 Статистика", callback_data="projects_stats")],
    ]
    
    return get_navigation_keyboard('my_projects', keyboard, show_breadcrumbs=False)

def get_calculator_navigation() -> InlineKeyboardMarkup:
    """Навигация калькулятора"""
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
    ]
    
    return get_navigation_keyboard('calculator', keyboard, show_breadcrumbs=False)

def get_consultant_navigation() -> InlineKeyboardMarkup:
    """Навигация AI консультанта"""
    keyboard = [
        [
            InlineKeyboardButton("💬 Новая консультация", callback_data="consultant_new"),
            InlineKeyboardButton("📋 Мои вопросы", callback_data="consultant_history")
        ],
        [
            InlineKeyboardButton("🎯 Быстрые вопросы", callback_data="consultant_quick"),
            InlineKeyboardButton("💡 Рекомендации", callback_data="consultant_tips")
        ],
        [InlineKeyboardButton("⭐ Оценить консультанта", callback_data="consultant_rate")],
    ]
    
    return get_navigation_keyboard('consultant', keyboard, show_breadcrumbs=False)

def get_faq_navigation() -> InlineKeyboardMarkup:
    """Навигация FAQ"""
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
        [InlineKeyboardButton("❓ Задать вопрос", callback_data="faq_ask")],
    ]
    
    return get_navigation_keyboard('faq', keyboard, show_breadcrumbs=False)

def get_consultation_navigation() -> InlineKeyboardMarkup:
    """Навигация консультаций"""
    keyboard = [
        [InlineKeyboardButton("📅 Записаться на консультацию", callback_data="book_consultation")],
        [InlineKeyboardButton("📞 Связаться сейчас", callback_data="contact_now")],
        [InlineKeyboardButton("📋 Оставить заявку", callback_data="leave_request")],
        [InlineKeyboardButton("💬 Чат с поддержкой", callback_data="support_chat")],
    ]
    
    return get_navigation_keyboard('consultation', keyboard, show_breadcrumbs=False)

def get_admin_navigation() -> InlineKeyboardMarkup:
    """Навигация админки"""
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
            InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton("⚡ Быстрые действия", callback_data="admin_quick"),
            InlineKeyboardButton("🔧 Инструменты", callback_data="admin_tools")
        ],
    ]
    
    return get_navigation_keyboard('admin_main', keyboard, show_breadcrumbs=False, show_home_button=False)

def get_quick_navigation_keyboard() -> InlineKeyboardMarkup:
    """Быстрая навигация по основным разделам"""
    keyboard = [
        [
            InlineKeyboardButton("🚀 ТЗ", callback_data="create_tz"),
            InlineKeyboardButton("💼 Портфолио", callback_data="portfolio"),
            InlineKeyboardButton("📊 Проекты", callback_data="my_projects")
        ],
        [
            InlineKeyboardButton("🤖 AI", callback_data="consultant"),
            InlineKeyboardButton("🧮 Калькулятор", callback_data="calculator"),
            InlineKeyboardButton("❓ FAQ", callback_data="faq")
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_contextual_keyboard(
    current_section: str,
    context_data: Optional[Dict[str, Any]] = None
) -> InlineKeyboardMarkup:
    """Получить контекстную клавиатуру в зависимости от раздела и данных"""
    
    # Базовая навигация
    keyboard = []
    
    # Контекстные кнопки в зависимости от раздела
    if current_section.startswith('tz_'):
        keyboard = [
            [InlineKeyboardButton("💾 Сохранить черновик", callback_data="tz_save_draft")],
            [InlineKeyboardButton("👀 Предпросмотр", callback_data="tz_preview")],
        ]
    
    elif current_section.startswith('portfolio_'):
        keyboard = [
            [InlineKeyboardButton("🔍 Фильтры", callback_data="portfolio_filters")],
            [InlineKeyboardButton("💡 Получить предложение", callback_data="portfolio_suggest")],
        ]
    
    elif current_section.startswith('project_'):
        if context_data and context_data.get('project_id'):
            project_id = context_data['project_id']
            keyboard = [
                [
                    InlineKeyboardButton("💬 Чат", callback_data=f"project_chat_{project_id}"),
                    InlineKeyboardButton("📄 ТЗ", callback_data=f"project_tz_{project_id}")
                ],
                [InlineKeyboardButton("📊 Статус", callback_data=f"project_status_{project_id}")],
            ]
    
    elif current_section.startswith('calc_'):
        keyboard = [
            [InlineKeyboardButton("💾 Сохранить расчет", callback_data="calc_save")],
            [InlineKeyboardButton("📧 Отправить на email", callback_data="calc_email")],
            [InlineKeyboardButton("🚀 Создать ТЗ", callback_data="calc_to_tz")],
        ]
    
    elif current_section.startswith('consultant'):
        keyboard = [
            [InlineKeyboardButton("🔄 Новый вопрос", callback_data="consultant_new")],
            [InlineKeyboardButton("⭐ Оценить ответ", callback_data="consultant_rate")],
        ]
    
    # Добавляем навигацию
    return get_navigation_keyboard(current_section, keyboard)

def get_step_navigation_keyboard(
    current_step: int,
    total_steps: int,
    step_prefix: str,
    can_skip: bool = False,
    show_progress: bool = True
) -> InlineKeyboardMarkup:
    """Навигация по шагам (пошаговые процессы)"""
    keyboard = []
    
    # Прогресс
    if show_progress:
        progress_text = f"Шаг {current_step} из {total_steps}"
        keyboard.append([InlineKeyboardButton(progress_text, callback_data="step_info")])
    
    # Навигация по шагам
    step_row = []
    
    if current_step > 1:
        step_row.append(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"{step_prefix}_step_{current_step - 1}")
        )
    
    if can_skip:
        step_row.append(
            InlineKeyboardButton("⏭️ Пропустить", callback_data=f"{step_prefix}_skip_{current_step}")
        )
    
    if current_step < total_steps:
        step_row.append(
            InlineKeyboardButton("➡️ Далее", callback_data=f"{step_prefix}_step_{current_step + 1}")
        )
    else:
        step_row.append(
            InlineKeyboardButton("✅ Завершить", callback_data=f"{step_prefix}_finish")
        )
    
    if step_row:
        keyboard.append(step_row)
    
    # Дополнительные действия
    action_row = []
    action_row.append(InlineKeyboardButton("💾 Сохранить", callback_data=f"{step_prefix}_save"))
    action_row.append(InlineKeyboardButton("❌ Отмена", callback_data="main_menu"))
    
    keyboard.append(action_row)
    
    return InlineKeyboardMarkup(keyboard)

def get_search_navigation_keyboard(
    search_query: str,
    results_count: int,
    current_page: int = 1,
    total_pages: int = 1,
    search_context: str = "general"
) -> InlineKeyboardMarkup:
    """Навигация для результатов поиска"""
    keyboard = []
    
    # Информация о результатах
    if results_count > 0:
        info_text = f"Найдено: {results_count}"
        keyboard.append([InlineKeyboardButton(info_text, callback_data="search_info")])
    
    # Пагинация для результатов
    if total_pages > 1:
        pagination_row = []
        
        if current_page > 1:
            pagination_row.append(
                InlineKeyboardButton("⬅️", callback_data=f"search_page_{current_page - 1}_{search_context}")
            )
        
        pagination_row.append(
            InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="page_info")
        )
        
        if current_page < total_pages:
            pagination_row.append(
                InlineKeyboardButton("➡️", callback_data=f"search_page_{current_page + 1}_{search_context}")
            )
        
        keyboard.append(pagination_row)
    
    # Действия с поиском
    search_actions = [
        InlineKeyboardButton("🔍 Новый поиск", callback_data=f"search_new_{search_context}"),
        InlineKeyboardButton("🗑️ Очистить", callback_data=f"search_clear_{search_context}")
    ]
    keyboard.append(search_actions)
    
    # Навигация назад
    back_section = {
        'portfolio': 'portfolio',
        'projects': 'my_projects',
        'faq': 'faq',
        'admin': 'admin_main'
    }.get(search_context, 'main_menu')
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=back_section)])
    
    return InlineKeyboardMarkup(keyboard)

def get_multi_select_keyboard(
    options: List[Dict[str, Any]],
    selected_options: List[Any],
    callback_prefix: str,
    id_field: str = 'id',
    title_field: str = 'title',
    max_per_row: int = 2
) -> InlineKeyboardMarkup:
    """Клавиатура множественного выбора"""
    keyboard = []
    
    # Опции выбора
    for i in range(0, len(options), max_per_row):
        row = []
        for j in range(max_per_row):
            if i + j < len(options):
                option = options[i + j]
                option_id = option[id_field]
                option_title = option[title_field]
                
                is_selected = option_id in selected_options
                button_text = f"{'✅' if is_selected else '⚪'} {option_title}"
                
                row.append(
                    InlineKeyboardButton(
                        button_text,
                        callback_data=f"{callback_prefix}_toggle_{option_id}"
                    )
                )
        
        if row:
            keyboard.append(row)
    
    # Управляющие кнопки
    control_row = [
        InlineKeyboardButton("✅ Выбрать все", callback_data=f"{callback_prefix}_select_all"),
        InlineKeyboardButton("❌ Снять все", callback_data=f"{callback_prefix}_deselect_all")
    ]
    keyboard.append(control_row)
    
    # Кнопки действий
    action_row = [
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"{callback_prefix}_confirm"),
        InlineKeyboardButton("❌ Отмена", callback_data=f"{callback_prefix}_cancel")
    ]
    keyboard.append(action_row)
    
    return InlineKeyboardMarkup(keyboard)

def get_smart_navigation_keyboard(
    current_section: str,
    user_context: Optional[Dict[str, Any]] = None,
    show_shortcuts: bool = True
) -> InlineKeyboardMarkup:
    """Умная навигация на основе контекста пользователя"""
    keyboard = []
    
    # Анализируем контекст пользователя
    if user_context:
        # Если у пользователя есть активные проекты
        if user_context.get('active_projects_count', 0) > 0:
            keyboard.append([
                InlineKeyboardButton("📊 Мои проекты", callback_data="my_projects")
            ])
        
        # Если пользователь часто использует консультанта
        if user_context.get('consultant_sessions', 0) > 5:
            keyboard.append([
                InlineKeyboardButton("🤖 AI Консультант", callback_data="consultant")
            ])
        
        # Если пользователь новый
        if user_context.get('is_new_user', False):
            keyboard.append([
                InlineKeyboardButton("🎯 Быстрый старт", callback_data="quick_start")
            ])
    
    # Быстрые действия в зависимости от раздела
    if show_shortcuts:
        shortcuts = get_section_shortcuts(current_section)
        if shortcuts:
            keyboard.extend(shortcuts)
    
    # Основная навигация
    main_nav = [
        InlineKeyboardButton("🏠 Главная", callback_data="main_menu"),
        InlineKeyboardButton("🚀 Создать ТЗ", callback_data="create_tz")
    ]
    keyboard.append(main_nav)
    
    return InlineKeyboardMarkup(keyboard)

def get_section_shortcuts(section: str) -> List[List[InlineKeyboardButton]]:
    """Получить быстрые действия для раздела"""
    shortcuts = {
        'portfolio': [
            [InlineKeyboardButton("⭐ Рекомендуемые", callback_data="portfolio_featured")]
        ],
        'my_projects': [
            [InlineKeyboardButton("🆕 Новый проект", callback_data="create_tz")]
        ],
        'consultant': [
            [InlineKeyboardButton("💬 Быстрый вопрос", callback_data="consultant_quick")]
        ],
        'calculator': [
            [InlineKeyboardButton("🚀 Создать ТЗ", callback_data="calc_to_tz")]
        ]
    }
    
    return shortcuts.get(section, [])

def create_items_keyboard(
    items: List[Dict[str, Any]],
    callback_prefix: str,
    title_field: str = "title",
    id_field: str = "id",
    items_per_row: int = 2,
    show_back_button: bool = True,
    back_callback: str = "main_menu",
    max_title_length: int = 20
) -> InlineKeyboardMarkup:
    """Создание клавиатуры из списка элементов с улучшенными опциями"""
    keyboard = []
    
    # Группируем элементы по строкам
    for i in range(0, len(items), items_per_row):
        row = []
        for j in range(items_per_row):
            if i + j < len(items):
                item = items[i + j]
                title = item.get(title_field, "Без названия")
                item_id = item.get(id_field, 0)
                
                # Обрезаем название если оно слишком длинное
                if len(title) > max_title_length:
                    title = title[:max_title_length-3] + "..."
                
                # Добавляем эмодзи статуса если есть
                if 'status' in item:
                    status_emoji = get_status_emoji(item['status'])
                    title = f"{status_emoji} {title}"
                
                row.append(
                    InlineKeyboardButton(
                        title,
                        callback_data=f"{callback_prefix}_{item_id}"
                    )
                )
        if row:
            keyboard.append(row)
    
    # Кнопка назад
    if show_back_button:
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=back_callback)])
    
    return InlineKeyboardMarkup(keyboard)

def get_status_emoji(status: str) -> str:
    """Получить эмодзи для статуса"""
    status_emojis = {
        'new': '🆕',
        'review': '👀', 
        'accepted': '✅',
        'rejected': '❌',
        'in_progress': '🔄',
        'testing': '🧪',
        'completed': '🎉',
        'cancelled': '❌',
        'paused': '⏸️',
        'active': '🟢',
        'inactive': '🔴',
        'blocked': '🚫',
        'vip': '⭐',
        'featured': '🌟',
        'draft': '📝',
        'published': '📢',
        'archived': '📁',
        'pending': '⏳',
        'approved': '✅',
        'declined': '❌',
        'processing': '⚙️'
    }
    return status_emojis.get(status.lower(), '📋')

def get_breadcrumb_string(current_section: str, separator: str = " › ") -> str:
    """Получить строку хлебных крошек"""
    path = navigation.get_breadcrumb_path(current_section)
    titles = [item['title'].replace('🏠 ', '').replace('⚙️ ', '') for item in path]
    return separator.join(titles)

def get_navigation_summary(current_section: str) -> Dict[str, Any]:
    """Получить сводку навигации для текущего раздела"""
    return {
        'current_section': current_section,
        'breadcrumbs': navigation.get_breadcrumb_path(current_section),
        'parent_section': navigation.get_parent_section(current_section),
        'breadcrumb_string': get_breadcrumb_string(current_section),
        'section_title': navigation.breadcrumbs_map.get(current_section, {}).get('title', current_section)
    }

def extract_navigation_context(callback_data: str) -> Dict[str, Any]:
    """Извлечь контекст навигации из callback_data"""
    parts = callback_data.split('_')
    
    context = {
        'action': parts[0] if parts else '',
        'section': parts[1] if len(parts) > 1 else '',
        'subsection': parts[2] if len(parts) > 2 else '',
        'id': parts[3] if len(parts) > 3 else None,
        'extra': '_'.join(parts[4:]) if len(parts) > 4 else None
    }
    
    return context

def build_navigation_callback(
    action: str,
    section: str,
    subsection: Optional[str] = None,
    item_id: Optional[int] = None,
    extra: Optional[str] = None
) -> str:
    """Построить callback_data для навигации"""
    parts = [action, section]
    
    if subsection:
        parts.append(subsection)
    if item_id is not None:
        parts.append(str(item_id))
    if extra:
        parts.append(extra)
    
    result = '_'.join(parts)
    
    # Ограничиваем длину для Telegram
    if len(result) > 64:
        result = result[:64]
    
    return result

# Глобальные константы для навигации
NAVIGATION_LIMITS = {
    'MAX_BREADCRUMBS': 3,
    'MAX_BUTTONS_PER_ROW': 3,
    'MAX_TITLE_LENGTH': 25,
    'MAX_CALLBACK_LENGTH': 64,
    'MAX_RECENT_ITEMS': 10,
    'MAX_FAVORITES': 20
}

# Экспорт основных функций для удобного импорта
__all__ = [
    'NavigationBreadcrumbs',
    'navigation',
    'get_navigation_keyboard',
    'get_breadcrumb_keyboard',
    'get_section_menu_keyboard',
    'get_contextual_keyboard',
    'get_step_navigation_keyboard',
    'get_search_navigation_keyboard',
    'get_multi_select_keyboard',
    'get_quick_navigation_keyboard',
    'get_smart_navigation_keyboard',
    'create_items_keyboard',
    'get_navigation_summary'
]