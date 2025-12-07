import axiosInstance from '../services/api'

export interface Deal {
  id: number
  title: string
  status: string
  client_id?: number
  client_name?: string
  client_phone?: string
  description?: string
  technical_requirements?: string
  amount: number
  cost?: number
  discount: number
  prepayment_percent: number
  prepayment_amount?: number
  paid_amount?: number
  margin?: number
  payment_progress?: number
  payment_status?: string
  payment_schedule?: any[]
  contract_number?: string
  start_date?: string
  end_date?: string
  actual_start_date?: string
  actual_end_date?: string
  manager_id?: number
  manager_name?: string
  executor_id?: number
  executor_name?: string
  priority: string
  tags?: string[]
  project_id?: number
  created_by_id?: number
  created_at?: string
  updated_at?: string
  closed_at?: string
}

export interface DealStats {
  total: number
  active: number
  completed_month: number
  total_amount: number
  paid_amount: number
  payment_progress: number
}

export interface DealFilters {
  search?: string
  status?: string
  client_id?: number
  manager_id?: number
  executor_id?: number
  priority?: string
  page?: number
  limit?: number
}

export interface CreateDealData {
  title: string
  client_id: number
  description?: string
  technical_requirements?: string
  amount: number
  cost?: number
  discount?: number
  prepayment_percent?: number
  start_date?: string
  end_date?: string
  manager_id?: number
  executor_id?: number
  priority?: string
  tags?: string[]
}

export interface UpdateDealData {
  title?: string
  description?: string
  technical_requirements?: string
  amount?: number
  cost?: number
  discount?: number
  prepayment_percent?: number
  start_date?: string
  end_date?: string
  manager_id?: number
  executor_id?: number
  priority?: string
  tags?: string[]
}

export interface PipelineData {
  new: Deal[]
  discussion: Deal[]
  contract_prep: Deal[]
  contract_signed: Deal[]
  prepayment: Deal[]
  in_work: Deal[]
  testing: Deal[]
  acceptance: Deal[]
  payment: Deal[]
}

export interface PipelineStats {
  [key: string]: {
    count: number
    total_amount: number
  }
}

const dealsApi = {
  // Получение всех сделок с фильтрацией
  getDeals: async (filters?: DealFilters) => {
    const params = new URLSearchParams()
    if (filters?.search) params.append('search', filters.search)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.client_id) params.append('client_id', filters.client_id.toString())
    if (filters?.manager_id) params.append('manager_id', filters.manager_id.toString())
    if (filters?.executor_id) params.append('executor_id', filters.executor_id.toString())
    if (filters?.priority) params.append('priority', filters.priority)
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())

    const response = await axiosInstance.get(`/admin/deals/api?${params}`)
    return response.data as {
      success: boolean
      deals: Deal[]
      pagination: {
        total: number
        page: number
        limit: number
        pages: number
      }
    }
  },

  // Создание новой сделки
  createDeal: async (data: CreateDealData) => {
    const response = await axiosInstance.post('/admin/deals/api', data)
    return response.data as {
      success: boolean
      message: string
      deal: Deal
    }
  },

  // Обновление статуса сделки
  updateDealStatus: async (dealId: number, status: string) => {
    const response = await axiosInstance.put(`/admin/deals/api/${dealId}/status`, { status })
    return response.data as {
      success: boolean
      message: string
      deal: Deal
    }
  },

  // Добавление платежа к сделке
  addPayment: async (dealId: number, amount: number, type: string, description?: string) => {
    const response = await axiosInstance.post(`/admin/deals/api/${dealId}/payment`, {
      amount,
      type,
      description,
    })
    return response.data as {
      success: boolean
      message: string
      deal: Deal
    }
  },

  // Конвертация сделки в проект
  convertToProject: async (dealId: number, projectData: any) => {
    const response = await axiosInstance.post(
      `/admin/deals/api/${dealId}/convert-to-project`,
      projectData
    )
    return response.data as {
      success: boolean
      message: string
      data?: any
    }
  },

  // Получение данных для канбан-доски
  getPipeline: async () => {
    const response = await axiosInstance.get('/admin/deals/api/pipeline')
    return response.data as {
      success: boolean
      pipeline: PipelineData
      stats: PipelineStats
    }
  },
}

export default dealsApi
