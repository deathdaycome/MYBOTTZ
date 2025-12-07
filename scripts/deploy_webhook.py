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
        
        # Полная остановка всех процессов приложения (кроме webhook)
        logger.info("Останавливаем все процессы приложения...")
        
        # Останавливаем только процессы run.py (НЕ webhook!)
        subprocess.run(["pkill", "-f", "python.*run.py"], check=False)
        subprocess.run(["pkill", "-f", "python3.*run.py"], check=False)
        
        # Безопасная остановка только screen сессии с ботом
        # НЕ используем pgrep для поиска webhook процессов
        result = subprocess.run(['pgrep', '-f', 'python.*run.py'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.isdigit():
                    subprocess.run(['kill', pid], check=False)
        
        # Закрываем screen сессии
        subprocess.run(["screen", "-S", "bot_app", "-X", "quit"], check=False)
        subprocess.run(["pkill", "-f", "SCREEN.*bot_app"], check=False)
        
        # Освобождаем только порт 8000 (НЕ трогаем 9999 - webhook!)
        logger.info("Освобождаем порт 8000...")
        subprocess.run(["fuser", "-k", "8000/tcp"], check=False)
        
        # Ждем полного завершения процессов
        import time
        time.sleep(3)
        
        # Проверяем что процессы остановлены
        result = subprocess.run(['pgrep', '-f', 'python.*run.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.warning("⚠️ Процессы все еще запущены, принудительно завершаем...")
            subprocess.run(["pkill", "-9", "-f", "python.*run.py"], check=False)
            time.sleep(2)
        
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
        
        # Проверяем что порт 8000 свободен (НЕ трогаем 9999 - webhook!)
        result = subprocess.run(['lsof', '-ti', ':8000'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            logger.info("Освобождаем порт 8000...")
            subprocess.run(['kill', '-9'] + result.stdout.strip().split('\n'), 
                         check=False)
        
        # Запускаем в screen сессии с детальным логированием
        logger.info("Запускаем приложение в screen сессии...")
        
        # Убедимся что директория существует
        if not os.path.exists(REPO_PATH):
            raise Exception(f"Директория {REPO_PATH} не существует")
        
        # Проверим что run.py существует
        run_py_path = os.path.join(REPO_PATH, "run.py")
        if not os.path.exists(run_py_path):
            raise Exception(f"Файл {run_py_path} не найден")
        
        # Убиваем существующие screen сессии с таким именем
        subprocess.run(["screen", "-S", "bot_app", "-X", "quit"], check=False)
        time.sleep(1)
        
        # Запускаем новую screen сессию
        cmd = [
            "screen", "-dmS", "bot_app", 
            "bash", "-c", f"cd {REPO_PATH} && python3 run.py > app.log 2>&1"
        ]
        
        logger.info(f"Выполняем команду: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Ошибка запуска screen: {result.stderr}")
            raise Exception(f"Не удалось запустить screen сессию: {result.stderr}")
        
        logger.info("Screen сессия создана успешно")
        
        # Проверяем запуск с несколькими попытками
        for attempt in range(5):  # Увеличиваем количество попыток
            time.sleep(3)  # Меньше ждем между попытками
            logger.info(f"Проверка запуска (попытка {attempt + 1}/5)...")
            
            # Проверяем screen сессию
            screen_result = subprocess.run(['screen', '-list'], 
                                         capture_output=True, text=True)
            screen_exists = 'bot_app' in screen_result.stdout
            logger.info(f"Screen сессия bot_app: {'найдена' if screen_exists else 'НЕ найдена'}")
            
            # Проверяем процесс Python
            process_result = subprocess.run(['pgrep', '-f', 'python.*run.py'], 
                                          capture_output=True, text=True)
            process_running = process_result.returncode == 0
            logger.info(f"Python процесс run.py: {'запущен' if process_running else 'НЕ запущен'}")
            
            # Если процесс не запущен, показываем ошибки
            if not process_running:
                # Проверяем логи приложения
                log_path = os.path.join(REPO_PATH, "app.log")
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            logger.error("Последние строки app.log:")
                            for line in lines[-5:]:
                                logger.error(f"  {line.strip()}")
            
            # Проверяем HTTP (только если процесс запущен)
            http_ok = False
            if process_running:
                http_result = subprocess.run([
                    "curl", "-f", "--connect-timeout", "5", "http://localhost:8000/"
                ], capture_output=True, check=False)
                http_ok = http_result.returncode == 0
                logger.info(f"HTTP проверка: {'OK' if http_ok else 'FAILED'}")
            
            if process_running and screen_exists:
                if http_ok:
                    logger.info("✅ Деплой успешно завершен! Приложение работает полностью.")
                    return True
                else:
                    logger.info("✅ Процесс и screen запущены, HTTP инициализируется...")
                    if attempt >= 2:  # После 3-й попытки считаем успешным
                        logger.info("✅ Деплой завершен, приложение запускается...")
                        return True
            else:
                logger.warning(f"❌ Попытка {attempt + 1}: process={process_running}, screen={screen_exists}")
                
                # Если это не последняя попытка, пробуем перезапустить
                if attempt < 4:
                    logger.info("Пробуем перезапустить...")
                    subprocess.run(["screen", "-S", "bot_app", "-X", "quit"], check=False)
                    time.sleep(1)
                    
                    restart_cmd = [
                        "screen", "-dmS", "bot_app", 
                        "bash", "-c", f"cd {REPO_PATH} && python3 run.py > app.log 2>&1"
                    ]
                    subprocess.run(restart_cmd, check=False)
                else:
                    logger.error("❌ Не удалось запустить приложение после всех попыток")
                    return False
        
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