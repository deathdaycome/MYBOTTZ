# 🔑 Настройка SSH ключа для GitHub Actions

## Вариант 1: Использовать существующий ключ (если у вас уже есть доступ к серверу)

### На вашем Mac:

1. **Проверьте, есть ли у вас SSH ключ:**
```bash
ls ~/.ssh/
```

Ищите файлы:
- `id_rsa` (приватный ключ) и `id_rsa.pub` (публичный ключ)
- или `id_ed25519` и `id_ed25519.pub`

2. **Если ключ есть, скопируйте его содержимое:**
```bash
cat ~/.ssh/id_rsa
# или
cat ~/.ssh/id_ed25519
```

Вы увидите что-то вроде:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA... (много символов)
...
-----END RSA PRIVATE KEY-----
```

3. **Скопируйте ВСЁ содержимое (включая BEGIN и END строки)**

## Вариант 2: Создать новый SSH ключ специально для деплоя

### На вашем Mac:

1. **Создайте новый SSH ключ:**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/github_actions_deploy -C "github-actions-deploy"
```

Когда спросит пароль (passphrase), просто нажмите Enter дважды (без пароля).

2. **Скопируйте публичный ключ на сервер:**
```bash
# Покажите публичный ключ
cat ~/.ssh/github_actions_deploy.pub
```

3. **Подключитесь к серверу и добавьте ключ:**
```bash
ssh user@your-server.com
```

На сервере выполните:
```bash
# Добавьте публичный ключ в authorized_keys
echo "ВСТАВЬТЕ_СЮДА_СОДЕРЖИМОЕ_ПУБЛИЧНОГО_КЛЮЧА" >> ~/.ssh/authorized_keys

# Установите правильные права
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

4. **Теперь скопируйте ПРИВАТНЫЙ ключ для GitHub:**
```bash
cat ~/.ssh/github_actions_deploy
```

## Вариант 3: Использовать пароль вместо ключа (НЕ рекомендуется)

Если не хотите использовать SSH ключи, можно изменить GitHub Actions workflow для использования пароля:

1. Добавьте в GitHub Secrets:
   - `SERVER_PASSWORD` - ваш пароль от сервера

2. Измените `.github/workflows/deploy.yml`:
```yaml
- name: Deploy to server via SSH
  uses: appleboy/ssh-action@v1.0.0
  with:
    host: ${{ secrets.SERVER_HOST }}
    username: ${{ secrets.SERVER_USER }}
    password: ${{ secrets.SERVER_PASSWORD }}  # Используем пароль вместо ключа
    port: ${{ secrets.SERVER_PORT }}
```

## 📝 Добавление ключа в GitHub

1. **Перейдите в ваш репозиторий на GitHub**
2. **Settings → Secrets and variables → Actions**
3. **Нажмите "New repository secret"**
4. **Название:** `SERVER_SSH_KEY`
5. **Значение:** Вставьте ПРИВАТНЫЙ ключ целиком:
   ```
   -----BEGIN OPENSSH PRIVATE KEY-----
   b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAA...
   ...много строк...
   -----END OPENSSH PRIVATE KEY-----
   ```

## ⚠️ Важные моменты:

1. **НИКОГДА не публикуйте приватный ключ!** Он должен храниться только в GitHub Secrets.

2. **Убедитесь, что копируете ПРИВАТНЫЙ ключ** (без .pub в названии).

3. **Копируйте ключ полностью**, включая строки BEGIN и END.

4. **Проверьте доступ:**
   ```bash
   # Проверьте, что можете подключиться с этим ключом
   ssh -i ~/.ssh/github_actions_deploy user@your-server.com "echo 'Работает!'"
   ```

## 🔧 Решение проблем

### Если GitHub Actions не может подключиться:

1. **Проверьте формат ключа:**
   - Должны быть сохранены все переносы строк
   - Включены BEGIN и END строки

2. **Проверьте права на сервере:**
   ```bash
   ls -la ~/.ssh/
   # Должно быть: drwx------ для папки .ssh
   # Должно быть: -rw------- для authorized_keys
   ```

3. **Проверьте SSH конфигурацию сервера:**
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```
   Убедитесь, что включено:
   ```
   PubkeyAuthentication yes
   AuthorizedKeysFile .ssh/authorized_keys
   ```

4. **Перезапустите SSH сервис:**
   ```bash
   sudo systemctl restart sshd
   # или
   sudo service ssh restart
   ```

## ✅ Готово!

После добавления SSH ключа в GitHub Secrets, автоматический деплой будет работать!