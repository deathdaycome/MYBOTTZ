#!/bin/bash
# Скрипт автоматической настройки Avito Webhook
# Упрощает развертывание webhook для real-time обновлений

set -e  # Выходим при первой ошибке

echo "🔧 Настройка Avito Webhook для real-time обновлений"
echo "=" * 50

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для цветного вывода
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверяем что мы в правильной директории
if [ ! -f "setup_avito_webhook.py" ]; then
    print_error "Файл setup_avito_webhook.py не найден!"
    print_error "Убедитесь, что вы находитесь в корневой директории проекта"
    exit 1
fi

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 не найден! Установите Python 3.7+"
    exit 1
fi

print_success "Python3 найден: $(python3 --version)"

# Функция для показа меню
show_menu() {
    echo
    echo "Выберите действие:"
    echo "1) Настроить webhook (подключить real-time обновления)"
    echo "2) Отключить webhook" 
    echo "3) Тестировать доступность webhook endpoint"
    echo "4) Выход"
    echo
}

# Основной цикл
while true; do
    show_menu
    read -p "Введите номер действия (1-4): " choice
    
    case $choice in
        1)
            print_status "Настраиваем webhook для real-time обновлений..."
            if python3 setup_avito_webhook.py setup; then
                print_success "✅ Webhook успешно настроен!"
                print_status "Теперь сообщения в чатах будут обновляться в реальном времени"
                print_status "Обновите страницу админ-панели для применения изменений"
            else
                print_error "❌ Ошибка настройки webhook"
                print_status "Проверьте логи выше и настройки переменных окружения"
            fi
            ;;
        2)
            print_status "Отключаем webhook..."
            if python3 setup_avito_webhook.py unsubscribe; then
                print_success "✅ Webhook отключен"
                print_status "Система вернется к обновлениям по расписанию"
            else
                print_error "❌ Ошибка отключения webhook"
            fi
            ;;
        3)
            print_status "Тестируем доступность webhook endpoint..."
            if python3 setup_avito_webhook.py test; then
                print_success "✅ Webhook endpoint доступен и работает"
            else
                print_error "❌ Webhook endpoint недоступен"
                print_status "Проверьте что сервер запущен и доступен извне"
            fi
            ;;
        4)
            print_status "Выход..."
            exit 0
            ;;
        *)
            print_warning "Неверный выбор. Попробуйте снова."
            ;;
    esac
    
    echo
    read -p "Нажмите Enter для продолжения..."
done