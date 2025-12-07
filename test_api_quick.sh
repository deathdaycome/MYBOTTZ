#!/bin/bash
# Быстрый тест API проектов

# Логинимся и сохраняем cookies
curl -s -c /tmp/cookies.txt -X POST "http://localhost:8001/admin/auth/login" \
  -d "username=admin&password=qwerty123" > /dev/null

echo "=== Тест /admin/api/projects/?show_archived=false ==="
curl -s -b /tmp/cookies.txt "http://localhost:8001/admin/api/projects/?show_archived=false" | python3 -m json.tool | head -50

echo ""
echo "=== Тест /admin/projects/?page=1&per_page=20 ==="
curl -s -b /tmp/cookies.txt "http://localhost:8001/admin/projects/?page=1&per_page=20" | python3 -m json.tool | head -50

rm /tmp/cookies.txt
