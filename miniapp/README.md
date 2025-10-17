# Telegram Mini App - BotDev Studio

Красивый и современный Mini App для управления проектами в Telegram.

## 🚀 Быстрый старт

```bash
cd miniapp
npm install
npm run dev
```

Откройте http://localhost:5173

## 📦 Что создано

### ✅ Frontend (React + TypeScript)
- Dashboard с анимациями
- Страница "Мои проекты"
- UI компоненты (Button, Card, Badge, Input)
- Интеграция с Telegram WebApp SDK
- Красивый дизайн с Tailwind CSS
- Плавные анимации Framer Motion

### ✅ Backend API
- `/api/miniapp/projects` - работа с проектами
- `/api/miniapp/revisions` - система правок
- Проверка Telegram initData для безопасности

## 🎨 Дизайн

- Современный Material Design
- Градиенты и тени
- Адаптивный дизайн
- Темная/светлая тема (авто из Telegram)
- Плавные анимации

## 📱 Запуск в Telegram

1. Установите ngrok:
```bash
brew install ngrok
ngrok http 5173
```

2. Создайте Mini App в @BotFather

3. Используйте ngrok URL

## 🔧 Что доделать

- Остальные страницы (создание проекта, детали, правки, AI)
- Подключить реальные данные из API
- Добавить загрузку файлов
- WebSocket для чата

Запускайте и смотрите результат! 🚀
