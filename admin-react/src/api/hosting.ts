import axiosInstance from '../services/api'

// ============= TYPES =============

export interface HostingServer {
  id: number
  project_id: number | null
  client_id: number | null
  client_name: string
  client_company: string | null
  client_telegram_id: number | null
  server_name: string
  configuration: string | null
  ip_address: string | null
  cost_price: number
  client_price: number
  service_fee: number
  total_price: number
  profit_amount: number
  profit_percent: number
  start_date: string
  next_payment_date: string
  payment_period: 'monthly' | 'quarterly' | 'yearly'
  status: 'active' | 'overdue' | 'suspended' | 'closed'
  notes: string | null
  created_at: string
  updated_at: string
}

export interface HostingPayment {
  id: number
  server_id: number
  amount: number
  payment_date: string | null
  expected_date: string
  period_start: string
  period_end: string
  status: 'pending' | 'paid' | 'cancelled'
  payment_method: string | null
  notes: string | null
  created_at: string
}

export interface HostingStats {
  active_servers: number
  profit_month: number
  profit_all_time: number
  overdue_count: number
  overdue_sum: number
}

export interface HostingProject {
  id: number
  title: string
  status: string
  user_id: number
  client_telegram_id: number | null
}

export interface HostingProjectData {
  id: number
  title: string
  user_id: number
  client_name: string
  client_telegram_id: number | null
  estimated_cost: number | null
}

export interface HostingClient {
  id: number
  name: string
  company: string | null
  telegram_id: number | null
}

export interface CalendarEvent {
  id: number
  title: string
  date: string
  amount: number
  status: string
  color: string
  server_id: number
}

export interface CalendarData {
  calendar: CalendarEvent[]
  month: number
  year: number
}

export interface ServerCreateData {
  project_id?: number | null
  client_id?: number | null
  client_name: string
  client_company?: string | null
  client_telegram_id?: number | null
  server_name: string
  configuration?: string | null
  ip_address?: string | null
  cost_price: number
  client_price: number
  service_fee?: number
  start_date: string
  next_payment_date: string
  payment_period: 'monthly' | 'quarterly' | 'yearly'
  notes?: string | null
}

export interface PaymentCreateData {
  server_id: number
  amount: number
  payment_date?: string | null
  expected_date: string
  period_start: string
  period_end: string
  status?: 'pending' | 'paid' | 'cancelled'
  payment_method?: string | null
  notes?: string | null
}

// ============= API CLIENT =============

const hostingApi = {
  // ========== STATISTICS ==========

  /**
   * Получить статистику по хостингу
   */
  getStats: async () => {
    const response = await axiosInstance.get('/admin/hosting/api/stats')
    return response.data as {
      success: boolean
      stats: HostingStats
    }
  },

  // ========== SERVERS ==========

  /**
   * Получить список серверов
   */
  getServers: async (status?: string) => {
    const params = status ? { status } : {}
    const response = await axiosInstance.get('/admin/hosting/api/servers', { params })
    return response.data as {
      success: boolean
      servers: HostingServer[]
      total: number
    }
  },

  /**
   * Получить информацию о сервере
   */
  getServer: async (serverId: number) => {
    const response = await axiosInstance.get(`/admin/hosting/api/server/${serverId}`)
    return response.data as {
      success: boolean
      server: HostingServer
      payments: HostingPayment[]
    }
  },

  /**
   * Создать новый сервер
   */
  createServer: async (data: ServerCreateData) => {
    const response = await axiosInstance.post('/admin/hosting/api/server', data)
    return response.data as {
      success: boolean
      server: HostingServer
      message: string
    }
  },

  /**
   * Обновить сервер
   */
  updateServer: async (serverId: number, data: ServerCreateData) => {
    const response = await axiosInstance.put(`/admin/hosting/api/server/${serverId}`, data)
    return response.data as {
      success: boolean
      server: HostingServer
      message: string
    }
  },

  /**
   * Удалить сервер
   */
  deleteServer: async (serverId: number) => {
    const response = await axiosInstance.delete(`/admin/hosting/api/server/${serverId}`)
    return response.data as {
      success: boolean
      message: string
    }
  },

  // ========== PAYMENTS ==========

  /**
   * Зарегистрировать платеж
   */
  createPayment: async (data: PaymentCreateData) => {
    const response = await axiosInstance.post('/admin/hosting/api/payment', data)
    return response.data as {
      success: boolean
      payment: HostingPayment
      message: string
    }
  },

  // ========== CALENDAR ==========

  /**
   * Получить календарь платежей
   */
  getCalendar: async (month?: number, year?: number) => {
    const params: any = {}
    if (month) params.month = month
    if (year) params.year = year

    const response = await axiosInstance.get('/admin/hosting/api/calendar', { params })
    return response.data as {
      success: boolean
      calendar: CalendarEvent[]
      month: number
      year: number
    }
  },

  // ========== HELPERS ==========

  /**
   * Поиск клиентов
   */
  searchClients: async (query: string) => {
    const response = await axiosInstance.get('/admin/hosting/api/clients/search', {
      params: { q: query },
    })
    return response.data as {
      success: boolean
      clients: HostingClient[]
    }
  },

  /**
   * Получить список активных проектов
   */
  getProjects: async () => {
    const response = await axiosInstance.get('/admin/hosting/api/projects')
    return response.data as {
      success: boolean
      projects: HostingProject[]
    }
  },

  /**
   * Получить данные проекта для автозаполнения
   */
  getProjectData: async (projectId: number) => {
    const response = await axiosInstance.get(`/admin/hosting/api/project/${projectId}`)
    return response.data as {
      success: boolean
      project: HostingProjectData
      error?: string
    }
  },

  // ========== TIMEWEB INTEGRATION ==========

  /**
   * Автоматическая синхронизация всех серверов из Timeweb Cloud
   */
  syncWithTimeweb: async () => {
    const response = await axiosInstance.post('/admin/hosting/api/timeweb/sync-all')
    return response.data as {
      success: boolean
      message: string
      created: Array<{ timeweb_id: number; crm_id: number; name: string }>
      updated: Array<{ timeweb_id: number; crm_id: number; name: string }>
      errors: Array<{ server_id: number; server_name: string; error: string }>
      created_count: number
      updated_count: number
      error_count: number
      total_processed: number
    }
  },

  // ========== BALANCE MANAGEMENT ==========

  /**
   * Получить баланс клиента
   */
  getClientBalance: async (clientId: number) => {
    const response = await axiosInstance.get(`/admin/hosting/api/balance/${clientId}`)
    return response.data as {
      success: boolean
      balance: {
        id: number
        client_id: number
        client_name: string
        balance: number
        total_monthly_cost: number
        days_remaining: number
        low_balance_notified: boolean
        created_at: string
        updated_at: string
      }
    }
  },

  /**
   * Пополнить баланс клиента
   */
  addClientBalance: async (clientId: number, amount: number, description?: string) => {
    const response = await axiosInstance.post(
      `/admin/hosting/api/balance/${clientId}/add?amount=${amount}${description ? `&description=${encodeURIComponent(description)}` : ''}`
    )
    return response.data as {
      success: boolean
      message: string
      balance: any
      transaction: any
    }
  },

  /**
   * Получить историю транзакций клиента
   */
  getClientTransactions: async (clientId: number, limit = 50) => {
    const response = await axiosInstance.get(`/admin/hosting/api/balance/${clientId}/transactions?limit=${limit}`)
    return response.data as {
      success: boolean
      transactions: Array<{
        id: number
        type: string
        amount: number
        balance_before: number
        balance_after: number
        description: string
        created_at: string
      }>
      total: number
    }
  },

  /**
   * Получить клиентов с низким балансом
   */
  getLowBalanceClients: async (daysThreshold = 5) => {
    const response = await axiosInstance.get(`/admin/hosting/api/balance/low?days_threshold=${daysThreshold}`)
    return response.data as {
      success: boolean
      clients: Array<any>
      total: number
      threshold_days: number
    }
  },

  /**
   * Получить общую статистику по балансам
   */
  getBalanceSummary: async () => {
    const response = await axiosInstance.get('/admin/hosting/api/balance/summary')
    return response.data as {
      success: boolean
      total_clients: number
      total_balance: number
      total_monthly_revenue: number
      low_balance_count: number
      negative_balance_count: number
      low_balance_clients: Array<any>
    }
  },
}

export default hostingApi
