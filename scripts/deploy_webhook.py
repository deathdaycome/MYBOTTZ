#!/usr/bin/env python3
"""
Webhook сервер для автоматического деплоя
Сохрани как: /var/www/webhook/deploy_webhook.py
"""

import os
import json
import subprocess
import hmac
import hashlib
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Настройки
WEBHOOK_SECRET = "your-webhook-secret-key-2024"  # Измени на свой секрет
REPO_PATH = "/var/www/bot_business_card"
BRANCH = "main"

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_signature(payload, signature, secret):
    """Проверка подписи GitHub webhook"""
    expected_signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def deploy():
    """Функция деплоя"""
    try:
        logger.info("🚀 Начинаем деплой...")
        
        # Переходим в директорию проекта
        os.chdir(REPO_PATH)
        
        # Останавливаем приложение
        logger.info("Останавливаем приложение...")
        subprocess.run(["pkill", "-f", "python.*run.py"], check=False)
        subprocess.run(["screen", "-S", "bot_app", "-X", "quit"], check=False)
        
        # Обновляем код
        logger.info("Обновляем код...")
        result = subprocess.run([
            "git", "fetch", "origin"
        ], capture_output=True, text=True)
        
        result = subprocess.run([
            "git", "reset", "--hard", f"origin/{BRANCH}"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Git update failed: {result.stderr}")
        
        # Устанавливаем зависимости
        logger.info("Устанавливаем зависимости...")
        subprocess.run([
            "pip3", "install", "--user", "-r", "requirements.txt"
        ], check=True)
        
        # Применяем миграции БД
        logger.info("Применяем миграции...")
        subprocess.run([
            "python3", "-c", 
            "from app.database.database import init_database; init_database(); print('DB OK')"
        ], check=False)
        
        # Запускаем приложение
        logger.info("Запускаем приложение...")
        subprocess.run([
            "screen", "-dmS", "bot_app", 
            "bash", "-c", f"cd {REPO_PATH} && python3 run.py > app.log 2>&1"
        ], check=True)
        
        # Проверяем запуск
        import time
        time.sleep(5)
        
        result = subprocess.run([
            "curl", "-f", "http://localhost:8000/"
        ], capture_output=True, check=False)
        
        if result.returncode == 0:
            logger.info("✅ Деплой успешно завершен!")
            return True
        else:
            logger.warning("⚠️ Приложение запущено, но HTTP проверка не прошла")
            return True
            
    except Exception as e:
        logger.error(f"❌ Ошибка деплоя: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик GitHub webhook"""
    
    # Проверяем подпись
    signature = request.headers.get('X-Hub-Signature-256', '')
    payload = request.get_data()
    
    if not verify_signature(payload, signature, WEBHOOK_SECRET):
        logger.warning("❌ Неверная подпись webhook")
        return jsonify({'error': 'Invalid signature'}), 403
    
    # Парсим данные
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Проверяем что это push в нужную ветку
    if data.get('ref') != f'refs/heads/{BRANCH}':
        logger.info(f"Игнорируем push в ветку: {data.get('ref')}")
        return jsonify({'message': 'Branch ignored'}), 200
    
    # Выполняем деплой
    logger.info(f"📨 Получен webhook от {data.get('pusher', {}).get('name', 'unknown')}")
    
    if deploy():
        return jsonify({'message': 'Deploy successful'}), 200
    else:
        return jsonify({'error': 'Deploy failed'}), 500

@app.route('/status', methods=['GET'])
def status():
    """Проверка статуса"""
    try:
        # Проверяем процесс
        result = subprocess.run(['pgrep', '-f', 'python.*run.py'], 
                              capture_output=True, text=True)
        process_running = result.returncode == 0
        
        # Проверяем HTTP
        result = subprocess.run(['curl', '-f', 'http://localhost:8000/'], 
                              capture_output=True, check=False)
        http_ok = result.returncode == 0
        
        return jsonify({
            'process_running': process_running,
            'http_ok': http_ok,
            'status': 'OK' if process_running and http_ok else 'ERROR'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=False)