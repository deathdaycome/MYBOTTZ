/**
 * ADMIN.JS - Общие JavaScript функции для админ-панели
 * =====================================================
 */

// ===============================
// ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
// ===============================

window.AdminApp = {
    config: {
        apiUrl: '/api',
        refreshInterval: 30000, // 30 секунд
        maxRetries: 3,
        timeout: 10000
    },
    cache: new Map(),
    timers: new Map(),
    charts: new Map(),
    modals: new Map()
};

// ===============================
// УТИЛИТАРНЫЕ ФУНКЦИИ
// ===============================

/**
 * Безопасное логирование с уровнями
 */
const Logger = {
    debug: (message, data = null) => {
        if (window.location.hostname === 'localhost') {
            console.log(`[DEBUG] ${message}`, data);
        }
    },
    
    info: (message, data = null) => {
        console.info(`[INFO] ${message}`, data);
    },
    
    warn: (message, data = null) => {
        console.warn(`[WARN] ${message}`, data);
    },
    
    error: (message, error = null) => {
        console.error(`[ERROR] ${message}`, error);
        // Отправляем ошибки на сервер в продакшене
        if (window.location.hostname !== 'localhost') {
            AdminApp.api.post('/log-error', {
                message,
                error: error?.toString(),
                stack: error?.stack,
                url: window.location.href,
                timestamp: new Date().toISOString()
            }).catch(() => {}); // Игнорируем ошибки логирования
        }
    }
};

/**
 * Улучшенное форматирование данных
 */
const Formatter = {
    // Форматирование чисел
    number: (num, options = {}) => {
        const defaults = {
            locale: 'ru-RU',
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        };
        return new Intl.NumberFormat(options.locale || defaults.locale, {
            ...defaults,
            ...options
        }).format(num);
    },
    
    // Форматирование валюты
    currency: (amount, currency = 'RUB') => {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    },
    
    // Форматирование даты
    date: (date, options = {}) => {
        const defaults = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        return new Intl.DateTimeFormat('ru-RU', {
            ...defaults,
            ...options
        }).format(new Date(date));
    },
    
    // Форматирование времени
    time: (date, options = {}) => {
        const defaults = {
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Intl.DateTimeFormat('ru-RU', {
            ...defaults,
            ...options
        }).format(new Date(date));
    },
    
    // Относительное время (например, "2 часа назад")
    relativeTime: (date) => {
        const rtf = new Intl.RelativeTimeFormat('ru', { numeric: 'auto' });
        const now = new Date();
        const diff = new Date(date) - now;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (Math.abs(days) > 0) return rtf.format(days, 'day');
        if (Math.abs(hours) > 0) return rtf.format(hours, 'hour');
        if (Math.abs(minutes) > 0) return rtf.format(minutes, 'minute');
        return rtf.format(seconds, 'second');
    },
    
    // Размер файла
    fileSize: (bytes) => {
        const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
        if (bytes === 0) return '0 Б';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    },
    
    // Процент
    percent: (value, total) => {
        const percent = (value / total) * 100;
        return `${percent.toFixed(1)}%`;
    }
};

/**
 * Валидация данных
 */
const Validator = {
    email: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    phone: (phone) => {
        const re = /^[\+]?[1-9][\d]{0,15}$/;
        return re.test(phone.replace(/\s+/g, ''));
    },
    
    url: (url) => {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },
    
    required: (value) => {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    },
    
    minLength: (value, min) => {
        return value && value.length >= min;
    },
    
    maxLength: (value, max) => {
        return value && value.length <= max;
    },
    
    numeric: (value) => {
        return !isNaN(value) && !isNaN(parseFloat(value));
    },
    
    integer: (value) => {
        return Number.isInteger(Number(value));
    },
    
    positive: (value) => {
        return Number(value) > 0;
    }
};

// ===============================
// API УПРАВЛЕНИЕ
// ===============================

/**
 * Улучшенный API клиент
 */
AdminApp.api = {
    // Базовый запрос с retry логикой
    request: async (url, options = {}) => {
        const { timeout = AdminApp.config.timeout, retries = AdminApp.config.maxRetries } = options;
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        const requestOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            signal: controller.signal,
            ...options
        };

        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                const response = await fetch(`${AdminApp.config.apiUrl}${url}`, requestOptions);
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                }
                return await response.text();
                
            } catch (error) {
                if (attempt === retries) {
                    Logger.error(`API request failed after ${retries + 1} attempts`, error);
                    throw error;
                }
                
                // Экспоненциальная задержка между попытками
                const delay = Math.pow(2, attempt) * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    },

    // GET запрос
    get: (url, params = {}) => {
        const query = new URLSearchParams(params).toString();
        const fullUrl = query ? `${url}?${query}` : url;
        return AdminApp.api.request(fullUrl, { method: 'GET' });
    },

    // POST запрос
    post: (url, data = {}) => {
        return AdminApp.api.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // PUT запрос
    put: (url, data = {}) => {
        return AdminApp.api.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // DELETE запрос
    delete: (url) => {
        return AdminApp.api.request(url, { method: 'DELETE' });
    },

    // Загрузка файлов
    upload: (url, formData) => {
        return AdminApp.api.request(url, {
            method: 'POST',
            body: formData,
            headers: {} // Убираем Content-Type для FormData
        });
    }
};

// ===============================
// КЭШИРОВАНИЕ
// ===============================

/**
 * Система кэширования с TTL
 */
AdminApp.cache = {
    data: new Map(),

    set: (key, value, ttl = 300000) => { // 5 минут по умолчанию
        const expiry = Date.now() + ttl;
        AdminApp.cache.data.set(key, { value, expiry });
    },

    get: (key) => {
        const item = AdminApp.cache.data.get(key);
        if (!item) return null;
        
        if (Date.now() > item.expiry) {
            AdminApp.cache.data.delete(key);
            return null;
        }
        
        return item.value;
    },

    has: (key) => {
        return AdminApp.cache.get(key) !== null;
    },

    delete: (key) => {
        return AdminApp.cache.data.delete(key);
    },

    clear: () => {
        AdminApp.cache.data.clear();
    },

    // Кэшированный API запрос
    fetch: async (key, fetcher, ttl = 300000) => {
        let data = AdminApp.cache.get(key);
        if (data === null) {
            data = await fetcher();
            AdminApp.cache.set(key, data, ttl);
        }
        return data;
    }
};

// ===============================
// УВЕДОМЛЕНИЯ
// ===============================

/**
 * Расширенная система уведомлений
 */
const Notifications = {
    container: null,
    queue: [],
    maxVisible: 5,

    init: () => {
        if (!Notifications.container) {
            Notifications.container = document.getElementById('notification-container') || 
                document.createElement('div');
            Notifications.container.id = 'notification-container';
            Notifications.container.className = 'notification-container';
            document.body.appendChild(Notifications.container);
        }
    },

    show: (message, type = 'info', options = {}) => {
        Notifications.init();
        
        const defaults = {
            duration: 5000,
            closable: true,
            persistent: false,
            actions: []
        };
        
        const config = { ...defaults, ...options };
        const id = 'notification-' + Date.now() + Math.random().toString(36).substr(2, 9);
        
        const notification = {
            id,
            message,
            type,
            ...config
        };

        // Добавляем в очередь
        Notifications.queue.push(notification);
        Notifications.processQueue();
        
        return id;
    },

    processQueue: () => {
        const visible = Notifications.container.children.length;
        if (visible >= Notifications.maxVisible || Notifications.queue.length === 0) {
            return;
        }

        const notification = Notifications.queue.shift();
        Notifications.render(notification);
        
        // Рекурсивно обрабатываем очередь
        setTimeout(Notifications.processQueue, 100);
    },

    render: (notification) => {
        const element = document.createElement('div');
        element.id = notification.id;
        element.className = `alert alert-${notification.type} notification-item fade-in`;
        
        let actionsHtml = '';
        if (notification.actions && notification.actions.length > 0) {
            actionsHtml = '<div class="notification-actions">' +
                notification.actions.map(action => 
                    `<button class="btn btn-sm btn-outline-${notification.type}" onclick="${action.handler}">${action.text}</button>`
                ).join('') +
                '</div>';
        }

        element.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div class="notification-content">
                    <div class="notification-message">${notification.message}</div>
                    ${actionsHtml}
                </div>
                ${notification.closable ? '<button type="button" class="btn-close" onclick="Notifications.hide(\'' + notification.id + '\')"></button>' : ''}
            </div>
            ${!notification.persistent ? '<div class="notification-progress"></div>' : ''}
        `;

        Notifications.container.appendChild(element);

        // Автоскрытие
        if (!notification.persistent && notification.duration > 0) {
            const progressBar = element.querySelector('.notification-progress');
            if (progressBar) {
                progressBar.style.animation = `notificationProgress ${notification.duration}ms linear`;
            }
            
            setTimeout(() => {
                Notifications.hide(notification.id);
            }, notification.duration);
        }
    },

    hide: (id) => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('fade-out');
            setTimeout(() => {
                element.remove();
                Notifications.processQueue();
            }, 300);
        }
    },

    hideAll: () => {
        const notifications = Notifications.container.querySelectorAll('.notification-item');
        notifications.forEach(notification => {
            Notifications.hide(notification.id);
        });
        Notifications.queue = [];
    },

    // Специализированные методы
    success: (message, options = {}) => Notifications.show(message, 'success', options),
    error: (message, options = {}) => Notifications.show(message, 'danger', { duration: 8000, ...options }),
    warning: (message, options = {}) => Notifications.show(message, 'warning', options),
    info: (message, options = {}) => Notifications.show(message, 'info', options),

    // Уведомление с подтверждением
    confirm: (message, onConfirm, onCancel = null) => {
        return Notifications.show(message, 'warning', {
            persistent: true,
            actions: [
                { text: 'Подтвердить', handler: `Notifications.hide('${message}'); (${onConfirm.toString()})();` },
                { text: 'Отмена', handler: `Notifications.hide('${message}'); ${onCancel ? `(${onCancel.toString()})();` : ''}` }
            ]
        });
    }
};

// Добавляем стили для уведомлений
const notificationStyles = `
.notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
}

.notification-item {
    margin-bottom: 10px;
    border-radius: 10px;
    border: none;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    position: relative;
    overflow: hidden;
}

.notification-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 3px;
    background: rgba(255,255,255,0.3);
    width: 100%;
}

@keyframes notificationProgress {
    from { width: 100%; }
    to { width: 0%; }
}

.fade-out {
    animation: fadeOut 0.3s ease-out forwards;
}

@keyframes fadeOut {
    to { opacity: 0; transform: translateX(100%); }
}

.notification-actions {
    margin-top: 10px;
    display: flex;
    gap: 8px;
}
`;

// Добавляем стили в документ
if (!document.getElementById('notification-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'notification-styles';
    styleSheet.textContent = notificationStyles;
    document.head.appendChild(styleSheet);
}

// ===============================
// УПРАВЛЕНИЕ ФОРМАМИ
// ===============================

/**
 * Расширенная работа с формами
 */
const FormManager = {
    // Сериализация формы в объект
    serialize: (form) => {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            // Поддержка массивов (checkbox, multiple select)
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    },

    // Заполнение формы данными
    populate: (form, data) => {
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox' || field.type === 'radio') {
                    field.checked = Boolean(data[key]);
                } else if (field.tagName === 'SELECT' && field.multiple) {
                    const values = Array.isArray(data[key]) ? data[key] : [data[key]];
                    Array.from(field.options).forEach(option => {
                        option.selected = values.includes(option.value);
                    });
                } else {
                    field.value = data[key] || '';
                }
            }
        });
    },

    // Валидация формы
    validate: (form, rules = {}) => {
        const errors = {};
        const data = FormManager.serialize(form);
        
        Object.keys(rules).forEach(field => {
            const value = data[field];
            const fieldRules = rules[field];
            
            fieldRules.forEach(rule => {
                if (typeof rule === 'function') {
                    const result = rule(value, data);
                    if (result !== true) {
                        errors[field] = errors[field] || [];
                        errors[field].push(result);
                    }
                } else if (typeof rule === 'object') {
                    const { validator, message } = rule;
                    if (!validator(value, data)) {
                        errors[field] = errors[field] || [];
                        errors[field].push(message);
                    }
                }
            });
        });
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    // Отображение ошибок валидации
    showErrors: (form, errors) => {
        // Очищаем предыдущие ошибки
        form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(feedback => {
            feedback.remove();
        });

        // Показываем новые ошибки
        Object.keys(errors).forEach(field => {
            const fieldElement = form.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                fieldElement.classList.add('is-invalid');
                
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = errors[field][0]; // Показываем первую ошибку
                
                fieldElement.parentNode.appendChild(feedback);
            }
        });
    },

    // Автосохранение формы
    enableAutoSave: (form, key, interval = 30000) => {
        const save = () => {
            const data = FormManager.serialize(form);
            localStorage.setItem(`autosave_${key}`, JSON.stringify({
                data,
                timestamp: Date.now()
            }));
        };

        // Сохраняем при изменениях
        form.addEventListener('input', save);
        form.addEventListener('change', save);

        // Периодическое сохранение
        const timerId = setInterval(save, interval);
        AdminApp.timers.set(`autosave_${key}`, timerId);

        return timerId;
    },

    // Восстановление данных автосохранения
    restoreAutoSave: (form, key, maxAge = 86400000) => { // 24 часа
        const saved = localStorage.getItem(`autosave_${key}`);
        if (saved) {
            try {
                const { data, timestamp } = JSON.parse(saved);
                if (Date.now() - timestamp < maxAge) {
                    FormManager.populate(form, data);
                    return true;
                }
            } catch (error) {
                Logger.error('Error restoring autosave data', error);
            }
        }
        return false;
    }
};

// ===============================
// УПРАВЛЕНИЕ МОДАЛЬНЫМИ ОКНАМИ
// ===============================

/**
 * Расширенное управление модальными окнами
 */
const ModalManager = {
    // Создание динамического модального окна
    create: (options = {}) => {
        const defaults = {
            id: 'modal-' + Date.now(),
            title: 'Модальное окно',
            body: '',
            footer: '',
            size: '', // 'sm', 'lg', 'xl'
            backdrop: true,
            keyboard: true,
            focus: true,
            show: true
        };

        const config = { ...defaults, ...options };
        
        const modalHtml = `
            <div class="modal fade" id="${config.id}" tabindex="-1" data-bs-backdrop="${config.backdrop}" data-bs-keyboard="${config.keyboard}">
                <div class="modal-dialog ${config.size ? `modal-${config.size}` : ''} modal-modern">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${config.title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${config.body}
                        </div>
                        ${config.footer ? `<div class="modal-footer">${config.footer}</div>` : ''}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modalElement = document.getElementById(config.id);
        const modal = new bootstrap.Modal(modalElement, {
            backdrop: config.backdrop,
            keyboard: config.keyboard,
            focus: config.focus
        });

        AdminApp.modals.set(config.id, modal);

        // Автоудаление после скрытия
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
            AdminApp.modals.delete(config.id);
        });

        if (config.show) {
            modal.show();
        }

        return { modal, element: modalElement, id: config.id };
    },

    // Модальное окно подтверждения
    confirm: (message, onConfirm, onCancel = null, options = {}) => {
        const footer = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="button" class="btn btn-primary" id="confirm-btn">Подтвердить</button>
        `;

        const { modal, element } = ModalManager.create({
            title: options.title || 'Подтверждение',
            body: message,
            footer,
            size: options.size || 'sm',
            ...options
        });

        element.querySelector('#confirm-btn').addEventListener('click', () => {
            modal.hide();
            if (onConfirm) onConfirm();
        });

        if (onCancel) {
            element.addEventListener('hidden.bs.modal', onCancel);
        }

        return modal;
    },

    // Модальное окно с формой
    form: (formHtml, onSubmit, options = {}) => {
        const footer = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button type="submit" class="btn btn-primary" form="modal-form">Сохранить</button>
        `;

        const body = `<form id="modal-form">${formHtml}</form>`;

        const { modal, element } = ModalManager.create({
            title: options.title || 'Форма',
            body,
            footer,
            ...options
        });

        const form = element.querySelector('#modal-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const data = FormManager.serialize(form);
            
            if (options.validate) {
                const validation = FormManager.validate(form, options.validate);
                if (!validation.isValid) {
                    FormManager.showErrors(form, validation.errors);
                    return;
                }
            }

            if (onSubmit) {
                const result = onSubmit(data, form, modal);
                // Если onSubmit возвращает Promise, ждем его выполнения
                if (result instanceof Promise) {
                    result.then(() => modal.hide()).catch(() => {});
                } else if (result !== false) {
                    modal.hide();
                }
            }
        });

        return { modal, element, form };
    },

    // Загрузка содержимого модального окна по AJAX
    loadRemote: async (url, options = {}) => {
        try {
            const content = await AdminApp.api.get(url);
            return ModalManager.create({
                body: content,
                ...options
            });
        } catch (error) {
            Logger.error('Failed to load modal content', error);
            Notifications.error('Не удалось загрузить содержимое');
            return null;
        }
    }
};

// ===============================
// УПРАВЛЕНИЕ ТАБЛИЦАМИ
// ===============================

/**
 * Расширенное управление таблицами
 */
const TableManager = {
    // Инициализация таблицы с сортировкой и фильтрацией
    init: (tableSelector, options = {}) => {
        const table = document.querySelector(tableSelector);
        if (!table) return null;

        const defaults = {
            sortable: true,
            searchable: true,
            pageable: true,
            pageSize: 10,
            responsive: true
        };

        const config = { ...defaults, ...options };
        
        if (config.sortable) {
            TableManager.enableSorting(table);
        }
        
        if (config.searchable) {
            TableManager.enableSearch(table);
        }
        
        if (config.pageable) {
            TableManager.enablePagination(table, config.pageSize);
        }
        
        if (config.responsive) {
            TableManager.makeResponsive(table);
        }

        return table;
    },

    // Включение сортировки
    enableSorting: (table) => {
        const headers = table.querySelectorAll('th[data-sortable]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
            
            header.addEventListener('click', () => {
                const column = header.dataset.sortable;
                const currentSort = table.dataset.sort;
                const currentDirection = table.dataset.sortDirection || 'asc';
                
                let newDirection = 'asc';
                if (currentSort === column && currentDirection === 'asc') {
                    newDirection = 'desc';
                }
                
                TableManager.sortTable(table, column, newDirection);
                
                // Обновляем иконки
                headers.forEach(h => {
                    const icon = h.querySelector('i');
                    icon.className = 'fas fa-sort text-muted';
                });
                
                const icon = header.querySelector('i');
                icon.className = `fas fa-sort-${newDirection === 'asc' ? 'up' : 'down'} text-primary`;
                
                table.dataset.sort = column;
                table.dataset.sortDirection = newDirection;
            });
        });
    },

    // Сортировка таблицы
    sortTable: (table, column, direction) => {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.querySelector(`[data-value="${column}"]`)?.dataset.value || 
                          a.querySelector(`td:nth-child(${TableManager.getColumnIndex(table, column)})`)?.textContent || '';
            const bValue = b.querySelector(`[data-value="${column}"]`)?.dataset.value || 
                          b.querySelector(`td:nth-child(${TableManager.getColumnIndex(table, column)})`)?.textContent || '';
            
            let comparison = 0;
            if (TableManager.isNumeric(aValue) && TableManager.isNumeric(bValue)) {
                comparison = parseFloat(aValue) - parseFloat(bValue);
            } else {
                comparison = aValue.localeCompare(bValue, 'ru');
            }
            
            return direction === 'asc' ? comparison : -comparison;
        });
        
        rows.forEach(row => tbody.appendChild(row));
    },

    // Получение индекса колонки
    getColumnIndex: (table, column) => {
        const headers = table.querySelectorAll('th');
        for (let i = 0; i < headers.length; i++) {
            if (headers[i].dataset.sortable === column) {
                return i + 1;
            }
        }
        return 1;
    },

    // Проверка на число
    isNumeric: (str) => {
        return !isNaN(str) && !isNaN(parseFloat(str));
    },

    // Поиск по таблице
    enableSearch: (table) => {
        let searchInput = document.querySelector(`[data-table-search="${table.id}"]`);
        
        if (!searchInput) {
            searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.className = 'form-control search-input';
            searchInput.placeholder = 'Поиск...';
            searchInput.dataset.tableSearch = table.id;
            
            const container = document.createElement('div');
            container.className = 'search-container mb-3';
            container.innerHTML = '<i class="fas fa-search search-icon"></i>';
            container.appendChild(searchInput);
            
            table.parentNode.insertBefore(container, table);
        }
        
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                TableManager.filterTable(table, e.target.value);
            }, 300);
        });
    },

    // Фильтрация таблицы
    filterTable: (table, query) => {
        const rows = table.querySelectorAll('tbody tr');
        const normalizedQuery = query.toLowerCase().trim();
        
        rows.forEach(row => {
            if (!normalizedQuery) {
                row.style.display = '';
                return;
            }
            
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(normalizedQuery) ? '' : 'none';
        });
        
        // Обновляем пагинацию если она включена
        if (table.dataset.paginated === 'true') {
            TableManager.updatePagination(table);
        }
    },

    // Пагинация
    enablePagination: (table, pageSize) => {
        table.dataset.paginated = 'true';
        table.dataset.pageSize = pageSize;
        table.dataset.currentPage = '1';
        
        TableManager.updatePagination(table);
    },

    updatePagination: (table) => {
        const pageSize = parseInt(table.dataset.pageSize);
        const currentPage = parseInt(table.dataset.currentPage);
        const rows = Array.from(table.querySelectorAll('tbody tr')).filter(row => 
            row.style.display !== 'none'
        );
        
        const totalPages = Math.ceil(rows.length / pageSize);
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        
        // Скрываем все строки
        rows.forEach(row => row.style.display = 'none');
        
        // Показываем строки текущей страницы
        rows.slice(startIndex, endIndex).forEach(row => row.style.display = '');
        
        // Создаем/обновляем пагинацию
        TableManager.renderPagination(table, currentPage, totalPages);
    },

    renderPagination: (table, currentPage, totalPages) => {
        let pagination = table.parentNode.querySelector('.pagination-container');
        
        if (!pagination) {
            pagination = document.createElement('div');
            pagination.className = 'pagination-container mt-3';
            table.parentNode.appendChild(pagination);
        }
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let paginationHtml = '<nav><ul class="pagination pagination-modern justify-content-center">';
        
        // Предыдущая страница
        paginationHtml += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Номера страниц
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
            if (startPage > 2) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }
        
        // Следующая страница
        paginationHtml += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        paginationHtml += '</ul></nav>';
        pagination.innerHTML = paginationHtml;
        
        // Обработчики событий для пагинации
        pagination.querySelectorAll('a[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.closest('a').dataset.page);
                if (page >= 1 && page <= totalPages) {
                    table.dataset.currentPage = page;
                    TableManager.updatePagination(table);
                }
            });
        });
    },

    // Адаптивность таблицы
    makeResponsive: (table) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    }
};

// ===============================
// ГРАФИКИ И ДИАГРАММЫ
// ===============================

/**
 * Менеджер графиков
 */
const ChartManager = {
    // Создание графика
    create: (canvasId, config) => {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const chart = new Chart(ctx, config);
        AdminApp.charts.set(canvasId, chart);
        return chart;
    }
};