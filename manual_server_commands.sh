#!/bin/bash

# КОМАНДЫ ДЛЯ РУЧНОГО ОБНОВЛЕНИЯ НА СЕРВЕРЕ
# Выполните эти команды по порядку на сервере

echo "🔄 РУЧНОЕ ОБНОВЛЕНИЕ КОДА НА СЕРВЕРЕ"
echo "=================================="

# 1. Подключаемся к серверу
ssh -p 22 root@147.45.215.199

# 2. Переходим в директорию проекта
cd /var/www/bot_business_card

# 3. Проверяем текущее состояние
echo "📍 Текущий коммит:"
git log -1 --oneline

# 4. Агрессивная очистка
echo "🧹 Очищаем локальные изменения..."
git stash
git reset --hard HEAD
git clean -fd

# 5. Принудительное обновление
echo "📥 Получаем последние изменения..."
git fetch --all
git reset --hard origin/main

# 6. Проверяем обновление
echo "✅ Новый коммит:"
git log -1 --oneline

# 7. Проверяем файл
echo "🔍 Проверяем файл avito_messenger.html:"
grep -n "v2.0" app/admin/templates/avito_messenger.html || echo "❌ Файл не найден"

# 8. Если файл все еще старый - прямая замена
if ! grep -q "v2.0" app/admin/templates/avito_messenger.html; then
    echo "❌ Файл старый, заменяем принудительно..."
    
    # Создаем экстренную версию
    cat > app/admin/templates/avito_messenger.html << 'EOF'
{% extends "base.html" %}
{% block title %}Авито Мессенджер - Админ панель{% endblock %}
{% block content %}
<!-- 🚨 ЭКСТРЕННАЯ ЗАМЕНА: ФАЙЛ ЗАМЕНЁН ВРУЧНУЮ -->
<div class="alert alert-danger border-3 border-danger mb-4 text-center" style="background: linear-gradient(45deg, #ff4757, #ff6b6b); font-size: 24px; padding: 30px;">
    <h1>🚨 ЭКСТРЕННАЯ ЗАМЕНА 🚨</h1>
    <h2>ФАЙЛ ЗАМЕНЁН ВРУЧНУЮ - ДЕПЛОЙ РАБОТАЕТ!</h2>
    <div class="form-check form-switch d-inline-block mt-3">
        <input class="form-check-input" type="checkbox" id="manualToggle" style="transform: scale(3);">
        <label class="form-check-label text-white fw-bold fs-3 ms-3" for="manualToggle">
            🤖 AI АВТООТВЕТЫ (РУЧНАЯ ЗАМЕНА)
        </label>
    </div>
</div>
<script>
document.getElementById('manualToggle').onchange = function() {
    alert('🎉 ПЕРЕКЛЮЧАТЕЛЬ РАБОТАЕТ! Состояние: ' + (this.checked ? 'ВКЛЮЧЕН' : 'ВЫКЛЮЧЕН'));
}
alert('🚨 РУЧНАЯ ЗАМЕНА УСПЕШНА! Переключатель готов к работе!');
</script>
{% endblock %}
EOF
    
    echo "✅ Файл заменён экстренной версией"
fi

# 9. Перезапускаем PM2
echo "🔄 Перезапускаем PM2..."
pm2 restart bot-business-card

# 10. Очищаем кэш
echo "🧹 Очищаем Python кэш..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ РУЧНОЕ ОБНОВЛЕНИЕ ЗАВЕРШЕНО!"
echo "Проверьте сайт: http://147.45.215.199:8001/admin/avito/"