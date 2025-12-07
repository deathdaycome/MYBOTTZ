import axiosInstance from '../services/api'

export interface Lead {
  id: number
  title: string
  status: string
  source?: string
  client_id?: number
  client_name?: string
  client_type?: string
  contact_name?: string
  contact_phone?: string
  contact_email?: string
  contact_telegram?: string
  contact_whatsapp?: string
  company_name?: string
  description?: string
  requirements?: string
  budget?: number
  probability: number
  expected_close_date?: string
  next_action_date?: string
  notes?: string
  manager_id?: number
  manager_name?: string
  created_by_id?: number
  created_by_name?: string
  created_at?: string
  updated_at?: string
  converted_at?: string
  converted_to_deal_id?: number
  lost_reason?: string
  interactions?: any[]
  days_in_funnel?: number
}

export interface LeadStats {
  total: number
  new: number
  in_progress: number
  won_month: number
  lost_month: number
  conversion_rate: number
}

export interface LeadFilters {
  search?: string
  status?: string
  source?: string
  manager_id?: number
  client_id?: number
  page?: number
  limit?: number
}

export interface CreateLeadData {
  title: string
  source?: string
  client_id?: number
  contact_name?: string
  contact_phone?: string
  contact_email?: string
  contact_telegram?: string
  contact_whatsapp?: string
  description?: string
  requirements?: string
  budget?: number
  probability?: number
  expected_close_date?: string
  next_action_date?: string
  notes?: string
  manager_id?: number
}

export interface UpdateLeadData {
  title?: string
  status?: string
  source?: string
  client_id?: number
  contact_name?: string
  contact_phone?: string
  contact_email?: string
  contact_telegram?: string
  contact_whatsapp?: string
  description?: string
  requirements?: string
  budget?: number
  probability?: number
  expected_close_date?: string
  next_action_date?: string
  notes?: string
  manager_id?: number
}

export interface ConvertLeadData {
  title: string
  amount: number
  prepayment_percent?: number
  priority?: string
  start_date?: string
  end_date?: string
  description?: string
}

export interface FunnelStats {
  new: number
  contact_made: number
  qualification: number
  proposal_sent: number
  negotiation: number
  won: number
  lost: number
  postponed: number
}

const leadsApi = {
  // Получение всех лидов с фильтрацией
  getLeads: async (filters?: LeadFilters) => {
    const params = new URLSearchParams()
    if (filters?.search) params.append('search', filters.search)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.source) params.append('source', filters.source)
    if (filters?.manager_id) params.append('manager_id', filters.manager_id.toString())
    if (filters?.client_id) params.append('client_id', filters.client_id.toString())
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())

    const response = await axiosInstance.get(`/admin/leads/api?${params}`)
    return response.data as {
      success: boolean
      leads: Lead[]
      pagination: {
        total: number
        page: number
        limit: number
        pages: number
      }
    }
  },

  // Получение одного лида по ID
  getLead: async (leadId: number) => {
    const response = await axiosInstance.get(`/admin/leads/api/${leadId}`)
    return response.data as {
      success: boolean
      lead: Lead
      message?: string
    }
  },

  // Создание нового лида
  createLead: async (data: CreateLeadData) => {
    const response = await axiosInstance.post('/admin/leads/api', data)
    return response.data as {
      success: boolean
      message: string
      lead: Lead
    }
  },

  // Обновление лида
  updateLead: async (leadId: number, data: UpdateLeadData) => {
    const response = await axiosInstance.put(`/admin/leads/api/${leadId}`, data)
    return response.data as {
      success: boolean
      message: string
      lead: Lead
    }
  },

  // Обновление статуса лида
  updateLeadStatus: async (leadId: number, status: string, lostReason?: string) => {
    const response = await axiosInstance.put(`/admin/leads/api/${leadId}/status`, {
      status,
      lost_reason: lostReason,
    })
    return response.data as {
      success: boolean
      message: string
      lead: Lead
    }
  },

  // Конвертация лида в сделку
  convertLead: async (leadId: number, data: ConvertLeadData) => {
    const response = await axiosInstance.post(`/admin/leads/api/${leadId}/convert`, data)
    return response.data as {
      success: boolean
      message: string
      data?: {
        deal_id: number
        client_id: number
        lead_id: number
      }
    }
  },

  // Получение статистики воронки продаж
  getFunnelStats: async (period: 'day' | 'week' | 'month' | 'quarter' | 'year' = 'month') => {
    const response = await axiosInstance.get(`/admin/leads/api/stats/funnel?period=${period}`)
    return response.data as {
      success: boolean
      period: string
      funnel: FunnelStats
      conversion_rates: { [key: string]: number }
      values: {
        potential: number
        won: number
        lost: number
      }
      metrics: {
        total_leads: number
        avg_budget: number
        avg_probability: number
        avg_days_to_close: number
        win_rate: number
      }
    }
  },
}

export default leadsApi
