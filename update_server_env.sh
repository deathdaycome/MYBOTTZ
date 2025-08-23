#!/bin/bash

# Скрипт для обновления переменных окружения на сервере
echo "🔄 Принудительно обновляем переменные окружения на сервере..."

# SSH данные
SERVER_HOST="147.45.215.199"
SERVER_USER="root"
SERVER_PORT="22"

# Подключаемся к серверу и принудительно обновляем переменные
ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST << 'EOF'
cd /var/www/bot_business_card

echo "📍 Текущая директория: $(pwd)"

# Проверяем текущие переменные PM2
echo "🔍 Проверяем текущие переменные PM2..."
pm2 env 0 | grep -E "(OPENROUTER|DEFAULT_MODEL)" || echo "❌ OpenRouter переменные не найдены"

# Принудительно останавливаем и удаляем процесс
echo "🛑 Останавливаем PM2 процесс..."
pm2 stop bot-business-card || true
pm2 delete bot-business-card || true

# Пересоздаем ecosystem.config.js с новыми переменными
echo "📝 Создаем новый ecosystem.config.js с актуальным OpenRouter ключом..."
cat > ecosystem.config.js << 'INNER_EOF'
module.exports = {
  apps: [{
    name: 'bot-business-card',
    script: '/var/www/bot_business_card/venv/bin/python',
    args: '-m app.main',
    cwd: '/var/www/bot_business_card',
    interpreter: 'none',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      BOT_TOKEN: '7881909419:AAEeAZIRYxQZxkVfKKUV5WYCemBk7qxkFP8',
      TELEGRAM_BOT_TOKEN: '7881909419:AAEeAZIRYxQZxkVfKKUV5WYCemBk7qxkFP8',
      BOT_USERNAME: 'ivan_dev_bot',
      OPENROUTER_API_KEY: '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',
      OPENROUTER_BASE_URL: 'https://openrouter.ai/api/v1',
      DEFAULT_MODEL: 'openai/gpt-4o-mini',
      DATABASE_URL: 'sqlite:///./data/bot.db',
      DATABASE_ECHO: 'False',
      ADMIN_SECRET_KEY: 'your_super_secret_key_here_make_it_long_and_random',
      ADMIN_USERNAME: 'admin',
      ADMIN_PASSWORD: 'qwerty123',
      ADMIN_PORT: '8001',
      MAX_FILE_SIZE: '10485760',
      UPLOAD_PATH: './uploads',
      LOG_LEVEL: 'INFO',
      LOG_FILE: './logs/bot.log',
      NOTIFICATION_CHAT_ID: '501613334',
      ADMIN_CHAT_ID: '501613334',
      ADMIN_IDS: '501613334',
      BASE_HOURLY_RATE: '1000',
      URGENT_MULTIPLIER: '1.3',
      REDIS_URL: 'redis://localhost:6379/0',
      CONSULTANT_SYSTEM_PROMPT: 'Ты - эксперт-консультант по разработке Telegram-ботов и чат-ботов.',
      CONSULTANT_MAX_TOKENS: '1000',
      CONSULTANT_TEMPERATURE: '0.7'
    }
  }]
};
INNER_EOF

echo "✅ ecosystem.config.js обновлен с новым OpenRouter ключом"

# Запускаем с новой конфигурацией
echo "🚀 Запускаем PM2 процесс с новыми переменными..."
pm2 start ecosystem.config.js

# Сохраняем конфигурацию
pm2 save

echo "⏳ Ждем запуска (5 секунд)..."
sleep 5

# Проверяем статус
echo "📊 Статус PM2:"
pm2 status

# Проверяем переменные окружения
echo "🔍 Проверяем OpenRouter переменные в PM2:"
pm2 env 0 | grep -E "(OPENROUTER|DEFAULT_MODEL)"

# Показываем последние логи
echo "📋 Последние логи (20 строк):"
pm2 logs bot-business-card --lines 20 --nostream

echo "✅ Принудительное обновление завершено!"
EOF

echo "🎉 Переменные окружения принудительно обновлены на сервере!"