# Настройка постоянного Cloudflare Tunnel

## Шаг 1: Регистрация в Cloudflare

1. Перейдите на https://dash.cloudflare.com/sign-up
2. Зарегистрируйтесь (бесплатно, email + пароль)
3. Подтвердите email

## Шаг 2: Установка cloudflared и авторизация

### 2.1 Проверка установки
```bash
cloudflared --version
```

### 2.2 Авторизация
```bash
cloudflared tunnel login
```

**Что произойдет:**
- Откроется браузер с Cloudflare
- Нужно войти в свой аккаунт
- Нажать "Authorize" (Авторизовать)
- Сертификат сохранится автоматически

## Шаг 3: Создание постоянного туннеля

### 3.1 Создать туннель с именем
```bash
cloudflared tunnel create miniapp
```

**Результат:**
```
Created tunnel miniapp with id: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

**ВАЖНО:** Сохраните этот ID! Он понадобится.

### 3.2 Список туннелей (для проверки)
```bash
cloudflared tunnel list
```

## Шаг 4: Создание конфигурационного файла

Создайте файл `~/.cloudflared/config.yml`:

```yaml
tunnel: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
credentials-file: /Users/ivan/.cloudflared/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.json

ingress:
  - hostname: miniapp-ваше-имя.trycloudflare.com
    service: http://localhost:5173
  - service: http_status:404
```

**ЗАМЕНИТЕ:**
- `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX` - на ваш tunnel ID
- `miniapp-ваше-имя` - на желаемое имя поддомена

## Шаг 5: Создание DNS записи

```bash
cloudflared tunnel route dns miniapp miniapp-ваше-имя.trycloudflare.com
```

## Шаг 6: Запуск туннеля

### Один раз (для теста):
```bash
cloudflared tunnel run miniapp
```

### Постоянный запуск (в фоне):
```bash
cloudflared tunnel run miniapp > /tmp/cloudflare_tunnel.log 2>&1 &
```

## Шаг 7: Проверка работы

```bash
curl https://miniapp-ваше-имя.trycloudflare.com
```

Должна вернуться HTML страница вашего Mini App.

## Шаг 8: Автозапуск при старте системы (опционально)

### Для macOS:
```bash
cloudflared service install
```

## Ваш постоянный URL

После настройки ваш URL будет:
```
https://miniapp-ваше-имя.trycloudflare.com
```

Этот URL **НЕ ИЗМЕНИТСЯ** и будет работать постоянно!

Вставьте его в BotFather **ОДИН РАЗ** и больше не трогайте.

---

## Альтернатива: С собственным доменом (если есть)

Если у вас есть свой домен, можно настроить так:

1. Добавьте домен в Cloudflare
2. Создайте туннель с вашим доменом:
   ```bash
   cloudflared tunnel route dns miniapp app.ваш-домен.ru
   ```
3. URL будет: `https://app.ваш-домен.ru`

---

## Устранение проблем

### Туннель не запускается
```bash
# Проверить логи
tail -f /tmp/cloudflare_tunnel.log

# Проверить статус
cloudflared tunnel info miniapp
```

### Забыли tunnel ID
```bash
cloudflared tunnel list
```

### Удалить туннель (если нужно начать заново)
```bash
cloudflared tunnel delete miniapp
```

---

## Следующий шаг после настройки

После того как туннель создан и работает:

1. Скопируйте ваш постоянный URL
2. Откройте @BotFather в Telegram
3. `/mybots` → ваш бот → "Bot Settings" → "Menu Button"
4. Вставьте URL **ОДИН РАЗ**
5. Готово! Больше не нужно будет менять URL!
