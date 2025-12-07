#!/bin/bash
# Автоматический деплой с проверкой и исправлением БД
# Запускается через GitHub Actions или вручную

echo "🚀 Начинаем автоматический деплой..."
echo "========================================"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Путь к проекту
PROJECT_PATH="/var/www/bot_business_card"
DB_PATH="$PROJECT_PATH/data/bot.db"

# Переходим в директорию проекта
cd $PROJECT_PATH || exit 1

# 1. Обновляем код из репозитория
echo -e "${YELLOW}📥 Обновляем код из репозитория...${NC}"
git pull origin main || {
    echo -e "${RED}❌ Ошибка при обновлении кода${NC}"
    exit 1
}

# 2. Устанавливаем зависимости
echo -e "${YELLOW}📦 Проверяем зависимости...${NC}"
if [ -f "requirements.txt" ]; then
    source venv/bin/activate 2>/dev/null || {
        echo "  Создаем виртуальное окружение..."
        python3 -m venv venv
        source venv/bin/activate
    }
    pip install -r requirements.txt --quiet || {
        echo -e "${RED}❌ Ошибка при установке зависимостей${NC}"
        exit 1
    }
fi

# 3. Проверяем и создаем директорию для БД если нужно
echo -e "${YELLOW}🗂️  Проверяем структуру директорий...${NC}"
mkdir -p $PROJECT_PATH/data
mkdir -p $PROJECT_PATH/logs
mkdir -p $PROJECT_PATH/uploads

# 4. Проверяем и исправляем БД
echo -e "${YELLOW}🔧 Проверяем и исправляем БД...${NC}"
if [ -f "$DB_PATH" ]; then
    echo -e "  ${GREEN}✓ БД найдена: $DB_PATH${NC}"
    
    # Добавляем недостающие колонки в projects
    sqlite3 "$DB_PATH" "ALTER TABLE projects ADD COLUMN source_deal_id INTEGER;" 2>/dev/null && \
        echo -e "  ${GREEN}+ Добавлена колонка source_deal_id${NC}" || \
        echo "  ℹ source_deal_id уже существует"
    
    sqlite3 "$DB_PATH" "ALTER TABLE projects ADD COLUMN paid_amount REAL DEFAULT 0.0;" 2>/dev/null && \
        echo -e "  ${GREEN}+ Добавлена колонка paid_amount${NC}" || \
        echo "  ℹ paid_amount уже существует"
    
    # Добавляем колонки в finance_transactions
    sqlite3 "$DB_PATH" "ALTER TABLE finance_transactions ADD COLUMN account VARCHAR(50) DEFAULT 'card';" 2>/dev/null && \
        echo -e "  ${GREEN}+ Добавлена колонка account в finance_transactions${NC}"
    
    # Добавляем колонки в deals
    sqlite3 "$DB_PATH" "ALTER TABLE deals ADD COLUMN converted_to_project_id INTEGER;" 2>/dev/null && \
        echo -e "  ${GREEN}+ Добавлена колонка converted_to_project_id в deals${NC}"
    
    # Добавляем колонки в leads
    for column in "source VARCHAR(100)" "utm_source VARCHAR(255)" "utm_medium VARCHAR(255)" \
                 "utm_campaign VARCHAR(255)" "assigned_to INTEGER" "last_contact_date DATETIME" \
                 "conversion_date DATETIME" "rejection_reason TEXT" "budget REAL" \
                 "priority VARCHAR(20) DEFAULT 'normal'" "tags JSON" "notes TEXT"; do
        col_name=$(echo $column | cut -d' ' -f1)
        sqlite3 "$DB_PATH" "ALTER TABLE leads ADD COLUMN $column;" 2>/dev/null && \
            echo -e "  ${GREEN}+ Добавлена колонка $col_name в leads${NC}"
    done
    
    echo -e "  ${GREEN}✓ Проверка БД завершена${NC}"
else
    echo -e "  ${YELLOW}⚠ БД не найдена, будет создана при первом запуске${NC}"
fi

# 5. Запускаем миграции если есть
if [ -d "$PROJECT_PATH/app/database/migrations" ]; then
    echo -e "${YELLOW}🔄 Запускаем миграции БД...${NC}"
    for migration in $PROJECT_PATH/app/database/migrations/*.py; do
        if [ -f "$migration" ]; then
            python3 "$migration" 2>/dev/null && \
                echo -e "  ${GREEN}✓ $(basename $migration)${NC}" || \
                echo "  ℹ $(basename $migration) - уже применена или не требуется"
        fi
    done
fi

# 6. Перезапускаем приложение через PM2
echo -e "${YELLOW}🔄 Перезапускаем приложение...${NC}"
pm2 restart bot-business-card || {
    echo "  PM2 процесс не найден, запускаем новый..."
    pm2 start "$PROJECT_PATH/app/main.py" --name bot-business-card --interpreter python3
}

# 7. Проверяем статус
echo -e "${YELLOW}📊 Проверяем статус приложения...${NC}"
sleep 3
pm2_status=$(pm2 list | grep bot-business-card | grep online)
if [ -n "$pm2_status" ]; then
    echo -e "${GREEN}✅ Приложение успешно запущено!${NC}"
    pm2 list | grep bot-business-card
else
    echo -e "${RED}❌ Приложение не запустилось, проверьте логи:${NC}"
    echo "   pm2 logs bot-business-card --lines 50"
    exit 1
fi

# 8. Очистка старых логов (опционально)
echo -e "${YELLOW}🧹 Очистка старых логов...${NC}"
find $PROJECT_PATH/logs -name "*.log" -mtime +7 -delete 2>/dev/null
echo -e "  ${GREEN}✓ Старые логи удалены${NC}"

echo "========================================"
echo -e "${GREEN}✅ Деплой завершен успешно!${NC}"
echo ""
echo "Полезные команды:"
echo "  pm2 logs bot-business-card    - просмотр логов"
echo "  pm2 status                    - статус процессов"
echo "  pm2 restart bot-business-card - перезапуск"
echo ""