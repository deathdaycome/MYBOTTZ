#!/bin/bash
# Скрипт для очистки сервера от мусора

echo "========================================="
echo "ДИАГНОСТИКА ДИСКА"
echo "========================================="

echo -e "\n1. Общее использование диска:"
df -h /

echo -e "\n2. Топ-10 самых больших директорий:"
du -h / 2>/dev/null | sort -rh | head -10

echo -e "\n3. Использование Docker:"
docker system df

echo -e "\n========================================="
echo "ОЧИСТКА"
echo "========================================="

echo -e "\n1. Удаление неиспользуемых Docker образов..."
docker image prune -af

echo -e "\n2. Удаление остановленных контейнеров..."
docker container prune -f

echo -e "\n3. Удаление неиспользуемых volumes..."
docker volume prune -f

echo -e "\n4. Удаление build cache..."
docker builder prune -af

echo -e "\n5. Очистка логов journald старше 7 дней..."
journalctl --vacuum-time=7d

echo -e "\n6. Очистка apt cache..."
apt-get clean
apt-get autoclean
apt-get autoremove -y

echo -e "\n7. Очистка временных файлов..."
find /tmp -type f -atime +7 -delete 2>/dev/null
find /var/tmp -type f -atime +7 -delete 2>/dev/null

echo -e "\n========================================="
echo "РЕЗУЛЬТАТ"
echo "========================================="

echo -e "\nИспользование диска после очистки:"
df -h /

echo -e "\nDocker после очистки:"
docker system df
