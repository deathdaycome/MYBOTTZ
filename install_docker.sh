#!/bin/bash

# 🐳 Установка Docker и Docker Compose

set -e

echo "=========================================="
echo "🐳 УСТАНОВКА DOCKER И DOCKER COMPOSE"
echo "=========================================="

echo ""
echo "📦 Проверка Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker уже установлен"
    docker --version
else
    echo "📥 Установка Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    echo "✅ Docker установлен"
fi

echo ""
echo "📦 Проверка Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose уже установлен"
    docker-compose --version
else
    echo "📥 Установка Docker Compose..."

    # Определяем последнюю версию
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)

    # Скачиваем и устанавливаем
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # Создаём симлинк
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

    echo "✅ Docker Compose установлен"
fi

echo ""
echo "=========================================="
echo "✅ УСТАНОВКА ЗАВЕРШЕНА"
echo "=========================================="
echo ""
docker --version
docker-compose --version
echo ""
echo "Теперь запустите: ./clean_deploy.sh"
echo ""
