# Инструкция по установке и настройке функционала транскрибации

## Обзор

Функционал транскрибации позволяет:
- Записывать аудио с микрофона с визуализацией в реальном времени
- Загружать видео и аудио файлы (до 2GB)
- Автоматически транскрибировать речь в текст (русский язык)
- Анализировать транскрипцию с помощью GPT (OpenRouter)
- Создавать DOCX документы с транскрипцией и анализом
- Извлекать аудио из видео файлов

## Архитектура

### Frontend (React + TypeScript)
- **Компонент**: `admin-react/src/pages/Transcription.tsx`
- **Функционал**:
  - Два таба: "Запись с микрофона" и "Загрузка видео"
  - Запись с микрофона (WebRTC MediaRecorder API)
  - Аудио визуализация (Canvas + Web Audio API)
  - Drag & Drop для загрузки файлов
  - Progress bar с отслеживанием статуса
  - Скачивание результатов (DOCX и MP3)

### Backend (FastAPI + Python)
- **API Роуты**: `app/api/transcription.py`
- **Сервис**: `app/services/transcription_service.py`
- **Endpoints**:
  - `POST /api/v1/transcription/upload-chunk` - Загрузка чанков аудио (автосохранение)
  - `POST /api/v1/transcription/finalize` - Финализация записи и запуск обработки
  - `POST /api/v1/transcription/upload-video` - Загрузка видео/аудио файла
  - `GET /api/v1/transcription/status/{task_id}` - Проверка статуса обработки
  - `GET /api/v1/transcription/download/{filename}` - Скачивание файлов
  - `GET /api/v1/transcription/health` - Health check

## Установка

### 1. Системные зависимости

#### macOS
```bash
# Установка FFmpeg
brew install ffmpeg

# Проверка установки
ffmpeg -version
```

#### Ubuntu/Debian
```bash
# Установка FFmpeg
sudo apt-get update
sudo apt-get install ffmpeg

# Проверка установки
ffmpeg -version
```

#### Windows
1. Скачать FFmpeg с https://ffmpeg.org/download.html
2. Извлечь в `C:\ffmpeg`
3. Добавить `C:\ffmpeg\bin` в PATH
4. Перезапустить терминал
5. Проверить: `ffmpeg -version`

### 2. Python зависимости

```bash
# Перейти в корневую директорию проекта
cd "/Users/ivan/Desktop/СРМ РЕАКТ"

# Активировать виртуальное окружение
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate  # Windows

# Установить зависимости для транскрибации
pip install -r requirements-transcription.txt

# Или установить вручную
pip install faster-whisper>=1.0.0
pip install ffmpeg-python>=0.2.0
```

### 3. Проверка установки

```bash
# Запустить Python и проверить импорты
python3 << EOF
try:
    from faster_whisper import WhisperModel
    print("✅ faster-whisper установлен")
except ImportError:
    print("❌ faster-whisper не найден")

try:
    import ffmpeg
    print("✅ ffmpeg-python установлен")
except ImportError:
    print("❌ ffmpeg-python не найден")

import shutil
if shutil.which("ffmpeg"):
    print("✅ FFmpeg доступен в системе")
else:
    print("❌ FFmpeg не найден в PATH")
EOF
```

### 4. Настройка .env

OpenRouter API ключ уже настроен в `.env`:
```env
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=openai/gpt-4o-mini
```

Если нужно изменить модель для анализа, доступные варианты:
- `openai/gpt-4o-mini` (быстрая, дешевая)
- `openai/gpt-4o` (лучшее качество)
- `anthropic/claude-3.5-sonnet` (отличный анализ)

### 5. Создание директории для загрузок

```bash
# Создать директорию для транскрибаций
mkdir -p uploads/transcriptions
mkdir -p uploads/transcriptions/chunks

# Установить права доступа
chmod 755 uploads/transcriptions
```

## Запуск

### 1. Запуск Backend

```bash
# Убедитесь что вы в корневой директории проекта
cd "/Users/ivan/Desktop/СРМ РЕАКТ"

# Активировать venv
source venv/bin/activate

# Запустить FastAPI сервер
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Сервер будет доступен на: http://localhost:8001

### 2. Запуск Frontend (React)

```bash
# Перейти в директорию React приложения
cd admin-react

# Установить зависимости (если еще не установлены)
npm install

# Запустить dev сервер
npm run dev
```

Frontend будет доступен на: http://localhost:5173

### 3. Проверка работоспособности

1. Откройте браузер: http://localhost:5173/transcription
2. Проверьте health endpoint: http://localhost:8001/api/v1/transcription/health

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "ffmpeg_available": true,
  "whisper_available": true,
  "openrouter_configured": true,
  "active_tasks": 0
}
```

## Использование

### Запись с микрофона

1. Перейдите на вкладку "Запись с микрофона"
2. Нажмите "Начать запись" (браузер запросит доступ к микрофону)
3. Говорите в микрофон (аудио визуализация покажет уровень звука)
4. Нажмите "Остановить" когда закончите
5. Прослушайте запись
6. Нажмите "Обработать запись"
7. Дождитесь завершения обработки (прогресс показывается в реальном времени)
8. Скачайте DOCX с транскрипцией или MP3 файл

### Загрузка видео/аудио

1. Перейдите на вкладку "Загрузка видео"
2. Перетащите файл в зону загрузки или нажмите для выбора
3. Дождитесь завершения обработки
4. Скачайте результаты

### Поддерживаемые форматы

**Аудио**: MP3, WAV, M4A, FLAC, WEBM, OGG
**Видео**: MP4, AVI, MOV, MKV, WEBM (аудио будет извлечено)
**Максимальный размер**: 2GB

## Процесс обработки

1. **Загрузка файла** (0-10%)
   - Сохранение файла на диск

2. **Извлечение аудио** (10-20%)
   - Если загружено видео, извлекается аудио дорожка
   - Конвертация в MP3 формат

3. **Транскрибация** (20-70%)
   - Использование faster-whisper для распознавания речи
   - Модель: small (можно изменить в коде)
   - Язык: русский (автоопределение)

4. **Анализ с GPT** (70-80%)
   - Отправка транскрипции в OpenRouter
   - Получение резюме, ключевых моментов и действий

5. **Создание DOCX** (80-90%)
   - Генерация документа с форматированием
   - Включает: резюме, ключевые моменты, полную транскрипцию

6. **Подготовка файлов** (90-100%)
   - Конвертация аудио в MP3
   - Подготовка ссылок для скачивания

## Настройка производительности

### Выбор модели Whisper

В файле `app/services/transcription_service.py` можно изменить модель:

```python
# Строка 102
model = WhisperModel("small", device="cpu", compute_type="int8")

# Доступные модели (от быстрой к точной):
# - "tiny" - самая быстрая, низкая точность
# - "base" - баланс
# - "small" - рекомендуется (по умолчанию)
# - "medium" - высокая точность, требует больше RAM
# - "large-v2" или "large-v3" - максимальная точность, медленная
```

### GPU ускорение (опционально)

Если есть NVIDIA GPU с CUDA:

```bash
# Установить CUDA версию faster-whisper
pip uninstall faster-whisper
pip install faster-whisper[gpu]

# В коде изменить:
model = WhisperModel("small", device="cuda", compute_type="float16")
```

### Оптимизация для Apple Silicon (M1/M2/M3)

```python
# Apple Silicon хорошо работает с CPU
model = WhisperModel("small", device="cpu", compute_type="int8")

# Для лучшей производительности можно использовать medium модель
model = WhisperModel("medium", device="cpu", compute_type="int8")
```

## Troubleshooting

### Ошибка: "FFmpeg not found"

**Решение**:
```bash
# Проверить FFmpeg в системе
which ffmpeg

# Если не найден, установить (см. раздел Установка)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### Ошибка: "faster-whisper not installed"

**Решение**:
```bash
pip install faster-whisper>=1.0.0
```

### Ошибка: "Не удалось получить доступ к микрофону"

**Решение**:
1. Проверьте разрешения браузера (Settings → Privacy → Microphone)
2. Используйте HTTPS (или localhost для разработки)
3. Попробуйте другой браузер (Chrome/Firefox рекомендуются)

### Низкое качество транскрибации

**Решение**:
1. Используйте более крупную модель (medium или large)
2. Проверьте качество аудио
3. Уменьшите фоновый шум
4. Говорите четко и не слишком быстро

### Медленная обработка

**Решение**:
1. Используйте меньшую модель (tiny или base)
2. Включите GPU ускорение (если доступно)
3. Уменьшите длительность аудио
4. Увеличьте ресурсы сервера (CPU/RAM)

### Ошибка OpenRouter API

**Решение**:
1. Проверьте API ключ в `.env`
2. Проверьте баланс на OpenRouter
3. Проверьте интернет соединение
4. Если ключ истек, получите новый на https://openrouter.ai

### CORS ошибки

**Решение**:
Убедитесь что в `app/main.py` настроены правильные CORS origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://nikolaevcodev.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Продакшн развертывание

### 1. Настройка NGINX

```nginx
# /etc/nginx/sites-available/crm

location /api/v1/transcription/ {
    proxy_pass http://localhost:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;

    # Увеличить таймауты для длинных обработок
    proxy_read_timeout 600s;
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;

    # Увеличить размер загружаемых файлов
    client_max_body_size 2G;
}
```

### 2. Systemd сервис

```ini
# /etc/systemd/system/crm-transcription.service

[Unit]
Description=CRM Transcription Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/crm
Environment="PATH=/var/www/crm/venv/bin"
ExecStart=/var/www/crm/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl daemon-reload
sudo systemctl enable crm-transcription
sudo systemctl start crm-transcription
sudo systemctl status crm-transcription
```

### 3. Мониторинг

```bash
# Проверка логов
sudo journalctl -u crm-transcription -f

# Проверка health endpoint
curl http://localhost:8001/api/v1/transcription/health

# Проверка используемых ресурсов
htop
df -h
```

### 4. Резервное копирование

```bash
# Создать backup директории с транскрибациями
tar -czf transcriptions-backup-$(date +%Y%m%d).tar.gz uploads/transcriptions/

# Автоматический backup (добавить в crontab)
0 3 * * * cd /var/www/crm && tar -czf /backups/transcriptions-$(date +\%Y\%m\%d).tar.gz uploads/transcriptions/
```

## Безопасность

1. **Аутентификация**: Все endpoints требуют авторизации (Basic Auth)
2. **Размер файлов**: Ограничение 2GB (настраивается в коде)
3. **Валидация**: Проверка типов файлов
4. **Изоляция**: Файлы сохраняются с уникальными ID
5. **Очистка**: Рекомендуется регулярно удалять старые файлы

```bash
# Автоматическая очистка файлов старше 7 дней (добавить в crontab)
0 2 * * * find /var/www/crm/uploads/transcriptions -type f -mtime +7 -delete
```

## API документация

### Swagger UI
http://localhost:8001/docs

### Health Check
```bash
curl http://localhost:8001/api/v1/transcription/health
```

### Пример использования API

```python
import requests

# Загрузка видео файла
files = {'video': open('video.mp4', 'rb')}
response = requests.post(
    'http://localhost:8001/api/v1/transcription/upload-video',
    files=files,
    headers={'Authorization': 'Basic YOUR_TOKEN'}
)
task_id = response.json()['task_id']

# Проверка статуса
import time
while True:
    status = requests.get(
        f'http://localhost:8001/api/v1/transcription/status/{task_id}',
        headers={'Authorization': 'Basic YOUR_TOKEN'}
    ).json()

    print(f"Status: {status['status']}, Progress: {status['progress']}%")

    if status['status'] == 'completed':
        # Скачать DOCX
        docx = requests.get(
            f"http://localhost:8001{status['result']['docx_url']}",
            headers={'Authorization': 'Basic YOUR_TOKEN'}
        )
        with open('transcript.docx', 'wb') as f:
            f.write(docx.content)
        break

    time.sleep(2)
```

## Дополнительные возможности

### Пакетная обработка

Можно обрабатывать несколько файлов одновременно. Сервис использует background tasks FastAPI.

### Webhook уведомления (TODO)

Можно добавить отправку webhook при завершении обработки:

```python
# В transcription_service.py
async def process_audio(self, audio_file: Path, task_id: str, webhook_url: Optional[str] = None):
    # ... обработка ...

    if webhook_url and status == "completed":
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json={"task_id": task_id, "status": "completed"})
```

### Интеграция с хранилищем S3 (TODO)

Для продакшена можно хранить файлы в S3:

```python
import boto3

s3_client = boto3.client('s3')
s3_client.upload_file(file_path, 'bucket-name', f'transcriptions/{task_id}.docx')
```

## Контакты и поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f logs/bot.log`
2. Проверьте health endpoint
3. Проверьте системные ресурсы (CPU, RAM, Disk)
4. Создайте issue в репозитории

## Лицензии

- faster-whisper: MIT License
- FFmpeg: LGPL/GPL
- OpenRouter: Commercial (требуется API ключ)
- python-docx: MIT License
