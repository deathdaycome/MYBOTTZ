import axiosInstance from '../services/api'

// ============= TYPES =============

export interface DailyRegistration {
  date: string
  registrations: number
}

export interface UserAnalytics {
  total_users: number
  new_users: number
  active_users: number
  conversion_rate: number
  daily_registrations: DailyRegistration[]
}

export interface DailyProject {
  date: string
  projects: number
}

export interface ProjectAnalytics {
  total_projects: number
  new_projects: number
  completed_projects: number
  completion_rate: number
  status_distribution: {
    new: number
    review: number
    accepted: number
    in_progress: number
    testing: number
    completed: number
    cancelled: number
  }
  daily_projects: DailyProject[]
}

export interface FinanceAnalytics {
  total_revenue: number
  potential_revenue: number
  avg_check: number
  client_payments: number
  executor_payments: number
  profit: number
}

export interface DashboardAnalytics {
  user_statistics: UserAnalytics
  project_statistics: ProjectAnalytics
  financial_report: FinanceAnalytics
  conversion_funnel: {
    total_users: number
    users_with_projects: number
    users_with_accepted_projects: number
    users_with_completed_projects: number
    overall_conversion: number
    project_creation_rate: number
    project_acceptance_rate: number
    project_completion_rate: number
  }
  consultant_statistics: {
    new_sessions: number
    avg_rating: number
    popular_topics: Record<string, number>
  }
  engagement_metrics: {
    daily_active_users: number
    retention_rate: number
  }
  performance_metrics: {
    avg_response_time: number
    avg_acceptance_time: number
    avg_development_time: number
    time_estimation_accuracy: number
  }
}

export interface ExportAnalyticsData {
  success: boolean
  data: DashboardAnalytics
  exported_at: string
  period_days: number
}

// ============= API CLIENT =============

const analyticsApi = {
  /**
   * Получить данные дашборда аналитики
   */
  getDashboard: async (days: number = 30) => {
    const response = await axiosInstance.get('/admin/api/analytics/dashboard', {
      params: { days },
    })
    return response.data as {
      success: boolean
      data: DashboardAnalytics
    }
  },

  /**
   * Получить аналитику пользователей
   */
  getUserAnalytics: async (days: number = 30) => {
    const response = await axiosInstance.get('/admin/api/analytics/users', {
      params: { days },
    })
    return response.data as {
      success: boolean
      data: UserAnalytics
    }
  },

  /**
   * Получить аналитику проектов
   */
  getProjectAnalytics: async (days: number = 30) => {
    const response = await axiosInstance.get('/admin/api/analytics/projects', {
      params: { days },
    })
    return response.data as {
      success: boolean
      data: ProjectAnalytics
    }
  },

  /**
   * Получить финансовую аналитику
   */
  getFinanceAnalytics: async (days: number = 30) => {
    const response = await axiosInstance.get('/admin/api/analytics/finance', {
      params: { days },
    })
    return response.data as {
      success: boolean
      data: FinanceAnalytics
    }
  },

  /**
   * Экспорт данных аналитики
   */
  exportAnalytics: async (format: string = 'json', days: number = 30) => {
    const response = await axiosInstance.get('/admin/api/analytics/export', {
      params: { format, days },
    })
    return response.data as ExportAnalyticsData
  },
}

export default analyticsApi
