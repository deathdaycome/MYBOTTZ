import axios from 'axios';

// Используем относительный URL для API запросов
// Vite proxy перенаправит /api/* на http://localhost:8000/api/*
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export { apiClient };
export default apiClient;

// Добавляем interceptor для автоматической отправки Telegram initData
apiClient.interceptors.request.use((config) => {
  // Получаем initData из Telegram WebApp
  const initData = window.Telegram?.WebApp?.initData;

  if (initData) {
    config.headers['X-Telegram-Init-Data'] = initData;
  }

  return config;
});

// Interceptor для обработки ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Неавторизован - возможно, невалидные данные Telegram
      console.error('Unauthorized access');
    }
    return Promise.reject(error);
  }
);
