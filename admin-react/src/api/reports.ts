import axiosInstance from '../services/api'

// ============= TYPES =============

export interface DashboardMetrics {
  current_month: {
    income: number
    expense: number
    profit: number
    profit_margin: number
  }
  last_month: {
    income: number
    expense: number
    profit: number
    profit_margin: number
  }
  changes: {
    income_change: number
    expense_change: number
    profit_change: number
  }
}

export interface ProjectReportItem {
  id: number
  title: string
  client: string
  executor: string | null
  status: string
  estimated_cost: number
  completion_percentage: number
  deadline: string | null
}

export interface ProjectsReport {
  summary: {
    total_projects: number
    completion_rate: number
    total_revenue: number
    total_cost: number
  }
  projects: ProjectReportItem[]
  top_clients?: Array<[string, number]>
  top_executors?: Array<{ name: string; completed_count: number }>
}

export interface FinancialReportItem {
  month: string
  income: number
  expense: number
  profit: number
}

export interface FinancialReport {
  summary: {
    total_income: number
    total_expense: number
    profit: number
    profit_margin: number
    transactions_count: number
  }
  monthly_data?: FinancialReportItem[]
  expense_categories?: Record<string, number>
  by_category?: Record<string, Array<{ amount: number; type: string }>>
}

export interface ExecutorReport {
  executor: {
    id: number
    username: string
    email: string
  }
  statistics: {
    total_projects: number
    completed_projects: number
    in_progress_projects: number
    total_earnings: number
    average_rating: number
  }
  projects: Array<{
    id: number
    title: string
    status: string
    estimated_cost: number
    completion_percentage: number
  }>
}

export interface QuickStats {
  period: string
  stats: {
    projects: {
      total: number
      completed: number
      in_progress: number
      completion_rate: number
    }
    financial: {
      income: number
      expense: number
      profit: number
      transactions: number
    }
    top_clients: Array<{ name: string; total_revenue: number }>
    top_executors: Array<{ name: string; completed_count: number }>
  }
}

export interface PnLReport {
  period: {
    start: string
    end: string
  }
  total_revenue: number
  total_expenses: number
  net_profit: number
  profit_margin: number
  revenue_by_category: Array<{ name: string; amount: number }>
  expenses_by_category: Array<{ name: string; amount: number }>
  trend_data: {
    labels: string[]
    revenue: number[]
    expenses: number[]
  }
  comparison: {
    previous_revenue: number
    previous_expenses: number
    previous_profit: number
  }
  transactions_count: number
}

export interface ProjectsReportFilters {
  start_date?: string
  end_date?: string
  status?: string
  executor_id?: number
}

export interface FinancialReportFilters {
  start_date?: string
  end_date?: string
}

// ============= API CLIENT =============

const reportsApi = {
  /**
   * Получить метрики для дашборда
   */
  getDashboardMetrics: async () => {
    const response = await axiosInstance.get('/admin/api/reports/dashboard-metrics')
    return response.data as {
      success: boolean
      metrics: DashboardMetrics
    }
  },

  /**
   * Получить отчет по проектам
   */
  getProjectsReport: async (filters?: ProjectsReportFilters) => {
    const params: any = {}
    if (filters?.start_date) params.start_date = filters.start_date
    if (filters?.end_date) params.end_date = filters.end_date
    if (filters?.status) params.status = filters.status
    if (filters?.executor_id) params.executor_id = filters.executor_id

    const response = await axiosInstance.get('/admin/api/reports/projects', { params })
    return response.data as {
      success: boolean
      report: ProjectsReport
    }
  },

  /**
   * Получить финансовый отчет
   */
  getFinancialReport: async (filters?: FinancialReportFilters) => {
    const params: any = {}
    if (filters?.start_date) params.start_date = filters.start_date
    if (filters?.end_date) params.end_date = filters.end_date

    const response = await axiosInstance.get('/admin/api/reports/financial', { params })
    return response.data as {
      success: boolean
      report: FinancialReport
    }
  },

  /**
   * Получить отчет по исполнителю
   */
  getExecutorReport: async (executorId: number) => {
    const response = await axiosInstance.get(`/admin/api/reports/executor/${executorId}`)
    return response.data as {
      success: boolean
      report: ExecutorReport
    }
  },

  /**
   * Получить быструю статистику
   */
  getQuickStats: async (period: 'today' | 'week' | 'month' | 'year' = 'month') => {
    const response = await axiosInstance.get('/admin/api/reports/quick-stats', {
      params: { period },
    })
    return response.data as {
      success: boolean
      period: string
      stats: QuickStats['stats']
    }
  },

  /**
   * Получить отчет P&L (прибыли и убытки)
   */
  getPnLReport: async (
    period: 'month' | 'quarter' | 'year' = 'month',
    startDate?: string,
    endDate?: string
  ) => {
    const params: any = { period }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    const response = await axiosInstance.get('/admin/api/reports/pnl', { params })
    return response.data as {
      success: boolean
      data: PnLReport
    }
  },

  /**
   * Экспорт отчета в Excel
   */
  exportToExcel: async (
    reportType: 'projects' | 'financial' | 'executor',
    filters?: {
      start_date?: string
      end_date?: string
      status?: string
      executor_id?: number
    }
  ) => {
    const params: any = { report_type: reportType }
    if (filters?.start_date) params.start_date = filters.start_date
    if (filters?.end_date) params.end_date = filters.end_date
    if (filters?.status) params.status = filters.status
    if (filters?.executor_id) params.executor_id = filters.executor_id

    const response = await axiosInstance.get('/admin/api/reports/export/excel', {
      params,
      responseType: 'blob',
    })

    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute(
      'download',
      `${reportType}_report_${new Date().toISOString().split('T')[0]}.xlsx`
    )
    document.body.appendChild(link)
    link.click()
    link.remove()

    return { success: true }
  },
}

export default reportsApi
