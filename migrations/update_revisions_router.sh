#!/bin/bash
# Скрипт для обновления revisions.py - замена ProjectRevision на Task с type='REVISION'

FILE="/var/www/bot_business_card/app/admin/routers/revisions.py"

echo "🔄 Обновление revisions.py для использования tasks table..."

# 1. Обновляем импорты - меняем ProjectRevision на Task
sed -i 's/from ...database.models import (/from ...database.models import Task, /g' "$FILE"
sed -i 's/ProjectRevision, //g' "$FILE"

# 2. Обновляем запросы к ProjectRevision на Task с фильтром type
sed -i 's/db\.query(ProjectRevision)/db.query(Task).filter(Task.type == "REVISION")/g' "$FILE"
sed -i 's/ProjectRevision\./Task./g' "$FILE"

# 3. Обновляем поля, которые изменились
sed -i 's/\.revision_number/\.id/g' "$FILE"
sed -i 's/\.estimated_time/\.estimated_hours/g' "$FILE"
sed -i 's/\.actual_time/\.actual_hours/g' "$FILE"

echo "✅ Файл обновлен"
echo "📝 Изменения:"
echo "  • ProjectRevision → Task (с фильтром type='REVISION')"
echo "  • estimated_time → estimated_hours"
echo "  • actual_time → actual_hours"
