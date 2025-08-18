#!/usr/bin/env python3
"""
Webhook сервер для автоматического деплоя с PM2
Сохрани как: /root/webhook/deploy_webhook.py
"""

import os
import json
import subprocess
import hmac
import hashlib
from flask import Flask, request, jsonify
import logging
import time

app = Flask(__name__)

# Настройки
WEBHOOK_SECRET = "your-webhook-secret-key-2024"  # Измени на свой секрет
REPO_PATH = "/var/www/bot_business_card"
BRANCH = "main"

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/webhook/deploy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def verify_signature(payload, signature, secret):
    """Проверка подписи GitHub webhook"""
    expected_signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def clear_python_cache():
    """Очистка кеша Python"""
    logger.info("🧹 Очищаем кеш Python...")
    try:
        # Удаляем __pycache__ директории
        subprocess.run([
            "find", REPO_PATH, "-type", "d", "-name", "__pycache__", 
            "-exec", "rm", "-rf", "{}", "+"
        ], check=False, stderr=subprocess.DEVNULL)
        
        # Удаляем .pyc файлы
        subprocess.run([
            "find", REPO_PATH, "-name", "*.pyc", "-delete"
        ], check=False, stderr=subprocess.DEVNULL)
        
        # Удаляем .pyo файлы
        subprocess.run([
            "find", REPO_PATH, "-name", "*.pyo", "-delete"
        ], check=False, stderr=subprocess.DEVNULL)
        
        logger.info("✅ Кеш Python очищен")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка при очистке кеша: {e}")

def deploy():
    """Функция деплоя с PM2"""
    try:
        logger.info("🚀 Начинаем деплой...")
        
        # Переходим в директорию проекта
        os.chdir(REPO_PATH)
        
        # Обновляем код
        logger.info("📥 Получаем последние изменения...")
        result = subprocess.run([
            "git", "fetch", "origin"
        ], capture_output=True, text=True)
        
        result = subprocess.run([
            "git", "reset", "--hard", f"origin/{BRANCH}"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Git update failed: {result.stderr}")
        
        # ВАЖНО: Очищаем кеш Python
        clear_python_cache()
        
        # Очищаем кеш pip
        logger.info("🧹 Очищаем кеш pip...")
        subprocess.run(["pip", "cache", "purge"], check=False, stderr=subprocess.DEVNULL)
        
        # Активируем виртуальное окружение и обновляем зависимости
        logger.info("📦 Обновляем зависимости...")
        venv_python = os.path.join(REPO_PATH, "venv", "bin", "python3")
        venv_pip = os.path.join(REPO_PATH, "venv", "bin", "pip")
        
        result = subprocess.run([
            venv_pip, "install", "-r", "requirements.txt", "--no-cache-dir"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"⚠️ Предупреждение при установке зависимостей: {result.stderr}")
        
        # Применяем миграции БД
        logger.info("🗄️ Проверяем базу данных...")
        subprocess.run([
            venv_python, "-c", 
            "from app.database.database import init_database; init_database(); print('DB OK')"
        ], check=False, stderr=subprocess.DEVNULL)
        
        # Останавливаем старый процесс
        logger.info("🛑 Останавливаем старое приложение...")
        subprocess.run(["pm2", "stop", "bot-business-card"], 
                      check=False, stderr=subprocess.DEVNULL)
        time.sleep(2)
        
        # Удаляем из PM2
        subprocess.run(["pm2", "delete", "bot-business-card"], 
                      check=False, stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        # Запускаем приложение через PM2
        logger.info("🔄 Запускаем приложение через PM2...")
        result = subprocess.run([
            "pm2", "start", "ecosystem.config.js"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"PM2 start failed: {result.stderr}")
        
        # Сохраняем конфигурацию PM2
        subprocess.run(["pm2", "save"], check=False)
        
        # Ждем запуска
        logger.info("⏳ Ждем запуска приложения...")
        time.sleep(5)
        
        # Проверяем статус
        result = subprocess.run([
            "pm2", "status", "bot-business-card"
        ], capture_output=True, text=True)
        
        if "online" in result.stdout.lower():
            logger.info("✅ Приложение успешно запущено!")
            
            # Показываем последние логи
            result = subprocess.run([
                "pm2", "logs", "bot-business-card", "--lines", "10", "--nostream"
            ], capture_output=True, text=True, timeout=5)
            
            if result.stdout:
                logger.info("📋 Последние логи:")
                for line in result.stdout.split('\n')[-10:]:
                    if line.strip():
                        logger.info(f"  {line}")
            
            return True
        else:
            logger.error("❌ Приложение не запустилось")
            
            # Показываем ошибки
            result = subprocess.run([
                "pm2", "logs", "bot-business-card", "--err", "--lines", "20", "--nostream"
            ], capture_output=True, text=True, timeout=5)
            
            if result.stdout:
                logger.error("❌ Ошибки:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        logger.error(f"  {line}")
            
            return False
            
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
        # Проверяем PM2 статус
        result = subprocess.run([
            'pm2', 'jlist'
        ], capture_output=True, text=True)
        
        pm2_data = json.loads(result.stdout) if result.stdout else []
        app_status = None
        
        for app in pm2_data:
            if app.get('name') == 'bot-business-card':
                app_status = {
                    'status': app.get('pm2_env', {}).get('status'),
                    'uptime': app.get('pm2_env', {}).get('pm_uptime'),
                    'restarts': app.get('pm2_env', {}).get('restart_time'),
                    'cpu': app.get('monit', {}).get('cpu'),
                    'memory': app.get('monit', {}).get('memory')
                }
                break
        
        # Проверяем HTTP
        http_ok = False
        try:
            result = subprocess.run([
                'curl', '-f', '--connect-timeout', '3', 
                'http://localhost:8001/admin/'
            ], capture_output=True, check=False)
            http_ok = result.returncode == 0
        except:
            pass
        
        return jsonify({
            'pm2_status': app_status,
            'http_ok': http_ok,
            'overall_status': 'OK' if app_status and app_status.get('status') == 'online' else 'ERROR'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def logs():
    """Получение логов"""
    try:
        lines = request.args.get('lines', 50, type=int)
        
        result = subprocess.run([
            'pm2', 'logs', 'bot-business-card', 
            '--lines', str(lines), '--nostream'
        ], capture_output=True, text=True, timeout=10)
        
        return jsonify({
            'logs': result.stdout,
            'errors': result.stderr
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Запускаем webhook сервер на порту 9999...")
    app.run(host='0.0.0.0', port=9999, debug=False)