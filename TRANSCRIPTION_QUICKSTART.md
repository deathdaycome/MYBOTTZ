# Быстрый старт: Функционал транскрибации

## Что было добавлено

### Frontend
- ✅ `admin-react/src/pages/Transcription.tsx` - React компонент с UI
- ✅ Роут `/transcription` в App.tsx

### Backend
- ✅ `app/api/transcription.py` - API endpoints
- ✅ `app/services/transcription_service.py` - Бизнес-логика
- ✅ Интеграция с app/main.py

### Документация
- ✅ `requirements-transcription.txt` - Зависимости
- ✅ `TRANSCRIPTION_SETUP.md` - Полная инструкция
- ✅ `TRANSCRIPTION_QUICKSTART.md` - Этот файл

## Установка за 5 минут

### 1. Установить FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Проверка
ffmpeg -version
```

### 2. Установить Python зависимости

```bash
cd "/Users/ivan/Desktop/СРМ РЕАКТ"
source venv/bin/activate
pip install -r requirements-transcription.txt
```

### 3. Создать директории

```bash
mkdir -p uploads/transcriptions/chunks
```

### 4. Запустить сервисы

```bash
# Terminal 1: Backend
cd "/Users/ivan/Desktop/СРМ РЕАКТ"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Frontend
cd "/Users/ivan/Desktop/СРМ РЕАКТ/admin-react"
npm run dev
```

### 5. Открыть в браузере

```
http://localhost:5173/transcription
```

## Проверка работоспособности

```bash
# Health check
curl http://localhost:8001/api/v1/transcription/health
```

Ожидаемый результат:
```json
{
  "status": "healthy",
  "ffmpeg_available": true,
  "whisper_available": true,
  "openrouter_configured": true,
  "active_tasks": 0
}
```

## Основные команды

### Проверка зависимостей

```bash
python3 << EOF
import shutil
from importlib import import_module

checks = {
    "FFmpeg": shutil.which("ffmpeg") is not None,
    "faster-whisper": False,
    "ffmpeg-python": False,
    "python-docx": False,
}

try:
    import_module("faster_whisper")
    checks["faster-whisper"] = True
except ImportError:
    pass

try:
    import_module("ffmpeg")
    checks["ffmpeg-python"] = True
except ImportError:
    pass

try:
    import_module("docx")
    checks["python-docx"] = True
except ImportError:
    pass

for name, status in checks.items():
    print(f"{'✅' if status else '❌'} {name}")
EOF
```

### Тестирование API

```bash
# 1. Проверить доступность
curl -X GET http://localhost:8001/api/v1/transcription/health

# 2. Загрузить тестовый файл (замените YOUR_TOKEN на ваш токен)
curl -X POST http://localhost:8001/api/v1/transcription/upload-video \
  -H "Authorization: Basic YOUR_TOKEN" \
  -F "video=@/path/to/test.mp4"

# 3. Проверить статус (замените TASK_ID на полученный ID)
curl -X GET http://localhost:8001/api/v1/transcription/status/TASK_ID \
  -H "Authorization: Basic YOUR_TOKEN"
```

## Возможности

### Запись с микрофона
- ✅ Запись в реальном времени
- ✅ Аудио визуализация
- ✅ Автосохранение каждые 30 сек
- ✅ Неограниченное время записи

### Загрузка файлов
- ✅ Drag & Drop интерфейс
- ✅ Видео форматы: MP4, AVI, MOV, MKV
- ✅ Аудио форматы: MP3, WAV, M4A, FLAC
- ✅ До 2GB размер файла

### Обработка
- ✅ Извлечение аудио из видео (FFmpeg)
- ✅ Транскрибация речи (faster-whisper)
- ✅ Анализ с GPT (OpenRouter)
- ✅ Создание DOCX документа

### Результаты
- ✅ DOCX с транскрипцией и анализом
- ✅ MP3 аудио файл
- ✅ Предпросмотр текста

## Быстрые исправления

### Если FFmpeg не найден:
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Проверка
which ffmpeg
```

### Если faster-whisper не установлен:
```bash
pip install faster-whisper
```

### Если не работает микрофон:
1. Проверьте разрешения браузера
2. Используйте Chrome или Firefox
3. Работает только на localhost или HTTPS

### Если медленно обрабатывается:
В файле `app/services/transcription_service.py` (строка 102) измените модель:
```python
# Было
model = WhisperModel("small", device="cpu", compute_type="int8")

# Станет (быстрее, но менее точно)
model = WhisperModel("tiny", device="cpu", compute_type="int8")
```

## Структура проекта

```
СРМ РЕАКТ/
├── admin-react/
│   └── src/
│       ├── pages/
│       │   └── Transcription.tsx          # React компонент
│       └── App.tsx                        # Роутинг
├── app/
│   ├── api/
│   │   └── transcription.py              # API endpoints
│   ├── services/
│   │   └── transcription_service.py      # Логика обработки
│   └── main.py                           # Интеграция
├── uploads/
│   └── transcriptions/                   # Хранилище файлов
│       ├── chunks/                       # Чанки для автосохранения
│       ├── {task_id}_transcript.docx    # Результаты DOCX
│       └── {task_id}_audio.mp3          # Результаты MP3
├── requirements-transcription.txt        # Зависимости
├── TRANSCRIPTION_SETUP.md               # Полная инструкция
└── TRANSCRIPTION_QUICKSTART.md          # Этот файл
```

## API Endpoints

```
POST   /api/v1/transcription/upload-chunk      # Автосохранение
POST   /api/v1/transcription/finalize          # Финализация записи
POST   /api/v1/transcription/upload-video      # Загрузка видео
GET    /api/v1/transcription/status/{task_id}  # Проверка статуса
GET    /api/v1/transcription/download/{file}   # Скачивание
DELETE /api/v1/transcription/task/{task_id}    # Удаление задачи
GET    /api/v1/transcription/health            # Health check
```

## Конфигурация

### OpenRouter (уже настроен)
```env
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=openai/gpt-4o-mini
```

### Whisper модели (изменить в коде)
- `tiny` - Самая быстрая (~1x скорость)
- `base` - Баланс
- `small` - **По умолчанию** (2-3x скорость)
- `medium` - Высокая точность (4-5x скорость)
- `large` - Максимальная точность (10x+ скорость)

### Размер файлов (изменить в коде)
```python
# app/api/transcription.py, строка 124
if len(content) > 2 * 1024 * 1024 * 1024:  # 2GB
    raise HTTPException(status_code=400, detail="File too large")
```

## Мониторинг

### Логи
```bash
# Backend логи
tail -f logs/bot.log

# Или системные логи
sudo journalctl -u crm-transcription -f
```

### Метрики
```bash
# Health check
curl http://localhost:8001/api/v1/transcription/health

# Системные ресурсы
htop
df -h
```

### Активные задачи
```bash
# Посмотреть активные задачи через Python
python3 << EOF
import requests
response = requests.get('http://localhost:8001/api/v1/transcription/health')
print(f"Active tasks: {response.json()['active_tasks']}")
EOF
```

## Production checklist

- [ ] FFmpeg установлен и в PATH
- [ ] faster-whisper установлен
- [ ] OpenRouter API ключ настроен
- [ ] Директория uploads создана с правами 755
- [ ] NGINX настроен (client_max_body_size 2G)
- [ ] Systemd сервис создан и запущен
- [ ] HTTPS настроен (для микрофона)
- [ ] Backup скрипт настроен
- [ ] Мониторинг настроен
- [ ] Логи ротируются

## Следующие шаги

1. **Протестировать**: Откройте /transcription и попробуйте записать аудио
2. **Настроить**: Измените модель Whisper если нужно
3. **Интегрировать**: Добавьте ссылку в навигацию
4. **Мониторить**: Следите за логами и производительностью
5. **Оптимизировать**: Настройте под ваши требования

## Поддержка

Полная документация: `TRANSCRIPTION_SETUP.md`

Если проблемы:
1. Проверьте health endpoint
2. Проверьте логи
3. Проверьте системные ресурсы
4. Перезапустите сервисы

## Готово!

Функционал транскрибации полностью интегрирован и готов к использованию.

Откройте http://localhost:5173/transcription и начните использовать!
