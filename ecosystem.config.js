module.exports = {
  apps: [{
    name: 'bot',
    script: 'python',
    args: '-m app.main',
    cwd: '/home/root/bot_business_card',
    interpreter: '/home/root/bot_business_card/venv/bin/python',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_file: './logs/pm2-combined.log',
    time: true,
    merge_logs: true,
    
    // Настройки перезапуска
    min_uptime: '10s',
    max_restarts: 10,
    
    // Автоматический перезапуск при изменении памяти
    monitoring: true,
    
    // Задержка перед перезапуском
    restart_delay: 4000,
    
    // Graceful shutdown
    kill_timeout: 3000,
    wait_ready: true,
    listen_timeout: 3000
  }]
};