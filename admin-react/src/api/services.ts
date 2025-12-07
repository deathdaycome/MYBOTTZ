import axiosInstance from '../services/api'

export interface Service {
  id: number
  name: string
  description?: string
  provider_type: 'ai' | 'hosting' | 'payment' | 'analytics' | 'storage' | 'email' | 'sms' | 'cdn' | 'monitoring' | 'other'
  website?: string
  contact_info?: Record<string, any>
  pricing_model?: 'monthly' | 'yearly' | 'usage' | 'per_request' | 'one_time' | 'custom'
  status: 'active' | 'inactive'
  monthly_cost?: number
  yearly_cost?: number
  last_expense?: string
  created_at: string
  updated_at: string
  statistics?: {
    monthly_cost: number
    total_cost: number
    expense_count: number
  }
}

export interface ServiceExpense {
  id: number
  service_provider_id: number
  project_id?: number
  amount: number
  expense_type: 'subscription' | 'usage' | 'one_time'
  description?: string
  expense_date: string
  usage_details?: Record<string, any>
  invoice_url?: string
  is_recurring?: boolean
  recurring_period?: 'monthly' | 'yearly'
  created_at: string
}

export interface ServiceStats {
  period: string
  total_services: number
  active_services: number
  total_cost: number
  projected_month_cost: number
  month_cost_so_far: number
  service_types: Array<{
    type: string
    count: number
    total_cost: number
  }>
  top_services: Array<{
    name: string
    type: string
    total_cost: number
    expense_count: number
  }>
}

const servicesApi = {
  // Get all services
  getServices: async (filters?: { service_type?: string; status?: string }) => {
    const params = new URLSearchParams()
    if (filters?.service_type) params.append('service_type', filters.service_type)
    if (filters?.status) params.append('status', filters.status)

    const response = await axiosInstance.get(`/admin/api/services?${params}`)
    return response.data as { success: boolean; services: Service[] }
  },

  // Get single service
  getService: async (serviceId: number) => {
    const response = await axiosInstance.get(`/admin/api/services/${serviceId}`)
    return response.data as { success: boolean; service: Service; recent_expenses: ServiceExpense[] }
  },

  // Create service
  createService: async (data: {
    name: string
    description?: string
    provider_type: string
    website?: string
    contact_info?: Record<string, any>
    pricing_model?: string
    status?: string
  }) => {
    const response = await axiosInstance.post('/admin/api/services', data)
    return response.data as { success: boolean; message: string; service: Service }
  },

  // Update service
  updateService: async (serviceId: number, data: Partial<Service>) => {
    const response = await axiosInstance.put(`/admin/api/services/${serviceId}`, data)
    return response.data as { success: boolean; message: string; service: Service }
  },

  // Delete service
  deleteService: async (serviceId: number) => {
    const response = await axiosInstance.delete(`/admin/api/services/${serviceId}`)
    return response.data as { success: boolean; message: string }
  },

  // Create expense for service
  createExpense: async (
    serviceId: number,
    data: {
      amount: number
      expense_type: 'subscription' | 'usage' | 'one_time'
      description?: string
      expense_date?: string
      project_id?: number
      invoice_url?: string
      is_recurring?: boolean
      recurring_period?: 'monthly' | 'yearly'
    }
  ) => {
    const response = await axiosInstance.post(`/admin/api/services/${serviceId}/expense`, data)
    return response.data as { success: boolean; message: string; expense: ServiceExpense }
  },

  // Get statistics
  getStats: async (period: 'week' | 'month' | 'quarter' | 'year' = 'month') => {
    const response = await axiosInstance.get(`/admin/api/services/stats?period=${period}`)
    return response.data as { success: boolean; statistics: ServiceStats }
  },

  // Get upcoming billing
  getUpcomingBilling: async (daysAhead: number = 30) => {
    const response = await axiosInstance.get(
      `/admin/api/services/billing/upcoming?days_ahead=${daysAhead}`
    )
    return response.data as {
      success: boolean
      upcoming_billing: ServiceExpense[]
      total_upcoming_cost: number
      days_ahead: number
    }
  },

  // Reset service usage
  resetUsage: async (serviceId: number) => {
    const response = await axiosInstance.post(`/admin/api/services/${serviceId}/reset-usage`)
    return response.data as { success: boolean; message: string; service: Service }
  },
}

export default servicesApi
