import axiosInstance from '../services/api'

export interface Contractor {
  id: number
  username: string
  first_name?: string
  last_name?: string
  email: string
  role: string
  is_active: boolean
  telegram_id?: number
  created_at?: string
  last_login?: string
  total_payments?: number
}

export interface ContractorDetails extends Contractor {
  assignments: ContractorAssignment[]
  payments: ContractorPayment[]
}

export interface ContractorAssignment {
  id: number
  project_name: string
  status: string
  start_date?: string
  end_date?: string
}

export interface ContractorPayment {
  id: number
  amount: number
  description: string
  payment_date?: string
  status: string
  created_at: string
}

export interface CreateContractorData {
  username: string
  email: string
  first_name?: string
  last_name?: string
  role: string
  is_active: boolean
  admin_login?: string
  admin_password: string
  force_password_change?: boolean
}

export interface UpdateContractorData {
  username?: string
  email?: string
  first_name?: string
  last_name?: string
  is_active?: boolean
  telegram_id?: number
}

export interface CreatePaymentData {
  amount: number
  description: string
}

const contractorsApi = {
  // Получение всех исполнителей
  getContractors: async (filters?: {
    search?: string
    specialization?: string
    status?: string
    page?: number
    limit?: number
  }) => {
    const params = new URLSearchParams()
    if (filters?.search) params.append('search', filters.search)
    if (filters?.specialization) params.append('specialization', filters.specialization)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())

    const response = await axiosInstance.get(`/admin/api/contractors/?${params}`)
    return response.data as {
      success: boolean
      data: Contractor[]
      total: number
    }
  },

  // Получение одного исполнителя
  getContractor: async (contractorId: number) => {
    const response = await axiosInstance.get(`/admin/api/contractors/${contractorId}`)
    return response.data as {
      success: boolean
      contractor: ContractorDetails
      assignments: ContractorAssignment[]
      payments: ContractorPayment[]
    }
  },

  // Создание исполнителя
  createContractor: async (data: CreateContractorData) => {
    const response = await axiosInstance.post('/admin/api/contractors/', data)
    return response.data as {
      success: boolean
      message: string
      data: Contractor
    }
  },

  // Обновление исполнителя
  updateContractor: async (contractorId: number, data: UpdateContractorData) => {
    const response = await axiosInstance.put(`/admin/api/contractors/${contractorId}`, data)
    return response.data as {
      success: boolean
      message: string
      data: Contractor
    }
  },

  // Удаление исполнителя
  deleteContractor: async (contractorId: number) => {
    const response = await axiosInstance.delete(`/admin/api/contractors/${contractorId}`)
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Смена пароля исполнителя
  changePassword: async (contractorId: number, newPassword: string) => {
    const response = await axiosInstance.post(`/admin/api/contractors/${contractorId}/change-password`, {
      new_password: newPassword,
    })
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Создание выплаты
  createPayment: async (contractorId: number, data: CreatePaymentData) => {
    const response = await axiosInstance.post(`/admin/api/contractors/${contractorId}/payments`, data)
    return response.data as {
      success: boolean
      message: string
      payment: ContractorPayment
    }
  },
}

export default contractorsApi
