#!/bin/bash

# Скрипт для локального деплоя на сервер
# Использование: ./scripts/deploy.sh

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Начинаем деплой на сервер...${NC}"

# Проверяем, есть ли незакоммиченные изменения
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠️  Обнаружены незакоммиченные изменения:${NC}"
    git status -s
    echo ""
    read -p "Хотите закоммитить их? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Введите сообщение коммита: " commit_msg
        git add -A
        git commit -m "$commit_msg"
    else
        echo -e "${RED}❌ Деплой отменен. Сначала закоммитьте изменения.${NC}"
        exit 1
    fi
fi

# Пушим изменения на GitHub
echo -e "${YELLOW}📤 Отправляем изменения на GitHub...${NC}"
git push origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Изменения успешно отправлены на GitHub${NC}"
    echo -e "${YELLOW}⏳ GitHub Actions начнет автоматический деплой...${NC}"
    echo ""
    echo "Вы можете отслеживать процесс деплоя здесь:"
    echo "https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
    echo ""
    echo -e "${GREEN}🎉 Готово! Бот скоро будет обновлен на сервере.${NC}"
else
    echo -e "${RED}❌ Ошибка при отправке на GitHub${NC}"
    exit 1
fi