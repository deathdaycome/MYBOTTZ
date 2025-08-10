#!/bin/bash

# Скрипт для настройки PM2 на сервере
# Запускать на сервере в директории проекта

echo "🚀 Настройка PM2 для бота..."

# Активируем виртуальное окружение
source venv/bin/activate

# Останавливаем бота если он запущен
pm2 stop bot 2>/dev/null || true
pm2 delete bot 2>/dev/null || true

# Запускаем бота через PM2
pm2 start "python -m app.main" \
  --name "bot" \
  --interpreter python \
  --cwd ~/bot_business_card \
  --max-memory-restart 500M \
  --log ~/bot_business_card/logs/pm2.log \
  --error ~/bot_business_card/logs/pm2-error.log \
  --time

# Настраиваем автозапуск при перезагрузке сервера
pm2 startup systemd -u $USER --hp /home/$USER
pm2 save

# Показываем статус
pm2 status

echo ""
echo "✅ PM2 настроен успешно!"
echo ""
echo "📋 Полезные команды PM2:"
echo "  pm2 status          - статус процессов"
echo "  pm2 logs bot        - смотреть логи"
echo "  pm2 restart bot     - перезапустить бота"
echo "  pm2 stop bot        - остановить бота"
echo "  pm2 start bot       - запустить бота"
echo "  pm2 monit           - мониторинг в реальном времени"
echo "  pm2 info bot        - детальная информация"
echo ""
echo "📊 Мониторинг:"
echo "  pm2 web             - веб-интерфейс на порту 9615"