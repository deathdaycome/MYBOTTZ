"""
Единая навигация для всей админ панели
"""

def get_navigation_items(role_or_path=None, db=None) -> list:
    """Возвращает полный список элементов навигации с активным элементом
    
    Args:
        role_or_path: может быть или ролью пользователя (для обратной совместимости) 
                      или путем текущей страницы (новый формат)
        db: сессия базы данных (для обратной совместимости)
    """
    
    navigation = [
        {"name": "Дашборд", "url": "/admin/dashboard", "icon": "fas fa-chart-line"},
        {"name": "Клиенты", "url": "/admin/clients", "icon": "fas fa-address-book"},
        {"name": "Лиды", "url": "/admin/leads", "icon": "fas fa-user-check"},
        {"name": "Сделки", "url": "/admin/deals", "icon": "fas fa-handshake"},
        {"name": "Проекты", "url": "/admin/projects", "icon": "fas fa-project-diagram"},
        {"name": "База проектов", "url": "/admin/project-database", "icon": "fas fa-database"},
        {"name": "Портфолио", "url": "/admin/portfolio", "icon": "fas fa-briefcase"},
        {"name": "Правки", "url": "/admin/edits", "icon": "fas fa-edit"},
        {"name": "Планировщик задач", "url": "/admin/task-scheduler", "icon": "fas fa-tasks"},
        {"name": "Мои задачи", "url": "/admin/my-tasks", "icon": "fas fa-clipboard-list"},
        {"name": "Документы", "url": "/admin/documents", "icon": "fas fa-file-alt"},
        {"name": "Финансы", "url": "/admin/finance", "icon": "fas fa-chart-bar"},
        {"name": "Пользователи", "url": "/admin/users", "icon": "fas fa-users"},
        {"name": "Исполнители", "url": "/admin/executors", "icon": "fas fa-user-tie"},
        {"name": "Сервисы", "url": "/admin/services", "icon": "fas fa-server"},
        {"name": "Аналитика", "url": "/admin/analytics", "icon": "fas fa-chart-area"},
        {"name": "Отчеты", "url": "/admin/reports", "icon": "fas fa-file-invoice"},
        {"name": "Автоматизация", "url": "/admin/automation", "icon": "fas fa-robot"},
        {"name": "Уведомления", "url": "/admin/notifications", "icon": "fas fa-bell"},
        {"name": "Настройки", "url": "/admin/settings", "icon": "fas fa-cog"},
    ]
    
    # Устанавливаем активный элемент если передан путь страницы (новый формат)
    if role_or_path and isinstance(role_or_path, str) and role_or_path.startswith('/'):
        for item in navigation:
            item["active"] = item["url"] == role_or_path
    
    return navigation