import axios from 'axios'

// API Configuration
const API_CONFIG = {
  // Используем пустую baseURL для относительных путей
  // В development Vite проксирует запросы на localhost:8001 (см. vite.config.ts)
  // В production nginx проксирует /admin/api/* на backend
  baseURL: '',  // Относительные URL - запросы идут на тот же домен
  timeout: 10000, // Увеличил timeout до 10 секунд для создания задач
}

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
  // withCredentials removed - we use Basic auth (Authorization header), not cookies
})

// Request interceptor - добавляем auth из localStorage
axiosInstance.interceptors.request.use(
  (config) => {
    // Берем auth из localStorage
    const authString = localStorage.getItem('auth')

    if (authString) {
      try {
        const { username, password } = JSON.parse(authString)
        const authHeader = `Basic ${btoa(`${username}:${password}`)}`
        config.headers.Authorization = authHeader

        console.log('🔑 Auth added for:', username)
      } catch (e) {
        console.error('❌ Error parsing auth from localStorage:', e)
      }
    } else {
      console.log('⚠️ No auth in localStorage - request will be unauthorized')
    }

    return config
  },
  (error) => {
    console.error('❌ Axios interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - редирект на login при 401
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('❌ 401 Unauthorized - redirecting to login')

      // Очищаем localStorage
      localStorage.removeItem('auth')

      // Редирект на страницу входа (только если мы не на /login)
      if (!window.location.pathname.includes('/login')) {
        // В продакшене базовый путь /admin
        const loginPath = import.meta.env.MODE === 'production' ? '/admin/login' : '/login'
        window.location.href = loginPath
      }
    }

    return Promise.reject(error)
  }
)

// API Service
export const apiService = {
  // Dashboard Metrics
  async getDashboardMetrics() {
    const response = await axiosInstance.get('/admin/reports/dashboard-metrics')
    return response.data
  },

  // Finance
  async getFinanceCategories(type: 'income' | 'expense') {
    const response = await axiosInstance.get(`/admin/finance/categories?type=${type}`)
    return response.data
  },

  async createTransaction(data: {
    type: 'income' | 'expense'
    amount: number
    category_id: number
    account: string
    description: string
    date: string
  }) {
    const response = await axiosInstance.post('/admin/finance/transactions', data)
    return response.data
  },

  // Reports
  async sendDailyReport() {
    const response = await axiosInstance.post('/admin/api/reports/daily')
    return response.data
  },

  // Cache
  async clearCache() {
    const response = await axiosInstance.post('/admin/api/cache/clear')
    return response.data
  },

  // Projects
  async getProjects(showArchived = false) {
    const response = await axiosInstance.get(
      `/admin/api/projects/?show_archived=${showArchived}`
    )
    return response.data
  },

  async getProject(projectId: number) {
    const response = await axiosInstance.get(`/admin/api/projects/${projectId}`)
    return response.data
  },

  async createProject(data: any) {
    const response = await axiosInstance.post('/admin/api/projects/create', data)
    return response.data
  },

  async updateProject(projectId: number, data: any) {
    const response = await axiosInstance.put(`/admin/api/projects/${projectId}`, data)
    return response.data
  },

  async deleteProject(projectId: number) {
    const response = await axiosInstance.delete(`/admin/api/projects/${projectId}`)
    return response.data
  },

  async archiveProject(projectId: number) {
    const response = await axiosInstance.post(`/admin/api/projects/${projectId}/archive`)
    return response.data
  },

  // restoreProject удален - используйте archiveProject для восстановления тоже (backend toggle)

  async completeProject(projectId: number) {
    const response = await axiosInstance.post(`/admin/api/projects/${projectId}/complete`)
    return response.data
  },

  async updateProjectStatus(projectId: number, status: string, comment?: string) {
    const response = await axiosInstance.put(`/admin/api/projects/${projectId}/status`, {
      status,
      comment,
    })
    return response.data
  },

  async getProjectFiles(projectId: number) {
    const response = await axiosInstance.get(`/admin/api/projects/${projectId}/files`)
    return response.data
  },

  async uploadProjectFile(projectId: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axiosInstance.post(
      `/admin/api/projects/${projectId}/files`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  async downloadProjectFile(projectId: number, fileId: number) {
    const response = await axiosInstance.get(
      `/admin/api/projects/${projectId}/files/${fileId}`,
      {
        responseType: 'blob',
      }
    )
    return response.data
  },

  async deleteProjectFile(projectId: number, fileId: number) {
    const response = await axiosInstance.delete(
      `/admin/api/projects/${projectId}/files/${fileId}`
    )
    return response.data
  },

  async exportProjects() {
    const response = await axiosInstance.get('/admin/api/export/projects')
    return response.data
  },

  async getRecentProjects() {
    const response = await axiosInstance.get('/admin/projects/recent')
    return response.data
  },

  // Users & Executors
  async getExecutors() {
    const response = await axiosInstance.get('/admin/api/users/executors')
    return response.data
  },

  async getClients() {
    const response = await axiosInstance.get('/admin/api/clients/simple')
    return response.data
  },

  async getRecentUsers() {
    const response = await axiosInstance.get('/admin/users/recent')
    return response.data
  },

  // Messaging
  async sendMessageToClient(telegramId: number, message: string) {
    const response = await axiosInstance.post('/admin/api/send-message', {
      telegram_id: telegramId,
      message,
    })
    return response.data
  },

  // Statistics
  async getStatistics() {
    const response = await axiosInstance.get('/admin/reports/statistics')
    return response.data
  },

  async getProjectsChartData() {
    const response = await axiosInstance.get('/admin/reports/projects-chart')
    return response.data
  },

  async getStatusChartData() {
    const response = await axiosInstance.get('/admin/reports/status-chart')
    return response.data
  },
}

export default axiosInstance
