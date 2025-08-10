#!/bin/bash

# Скрипт для настройки systemd сервиса на сервере
# Запускать с sudo правами на сервере

SERVICE_NAME="botdev"
PROJECT_DIR="/home/$USER/bot_business_card"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
USER_NAME=$USER

# Создаем файл сервиса
cat > /tmp/${SERVICE_NAME}.service << EOF
[Unit]
Description=BotDev Business Card Bot
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="PYTHONPATH=$PROJECT_DIR"
ExecStart=$PYTHON_PATH -m app.main
Restart=always
RestartSec=10
StandardOutput=append:/var/log/${SERVICE_NAME}/output.log
StandardError=append:/var/log/${SERVICE_NAME}/error.log

# Защита
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

# Создаем директорию для логов
sudo mkdir -p /var/log/${SERVICE_NAME}
sudo chown $USER_NAME:$USER_NAME /var/log/${SERVICE_NAME}

# Копируем файл сервиса
sudo mv /tmp/${SERVICE_NAME}.service /etc/systemd/system/

# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable ${SERVICE_NAME}

# Запускаем сервис
sudo systemctl start ${SERVICE_NAME}

# Проверяем статус
sudo systemctl status ${SERVICE_NAME}

echo "✅ Сервис ${SERVICE_NAME} успешно настроен!"
echo ""
echo "Полезные команды:"
echo "  sudo systemctl status ${SERVICE_NAME}  - проверить статус"
echo "  sudo systemctl start ${SERVICE_NAME}   - запустить"
echo "  sudo systemctl stop ${SERVICE_NAME}    - остановить"
echo "  sudo systemctl restart ${SERVICE_NAME} - перезапустить"
echo "  sudo journalctl -u ${SERVICE_NAME} -f  - смотреть логи в реальном времени"
echo "  tail -f /var/log/${SERVICE_NAME}/output.log - смотреть логи приложения"