import axiosInstance from '../services/api'

// ============= TYPES =============

export enum ClientType {
  INDIVIDUAL = 'individual',
  COMPANY = 'company',
  IP = 'ip',
  SELF_EMPLOYED = 'self_employed'
}

export enum ClientStatus {
  NEW = 'new',
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  VIP = 'vip',
  BLACKLIST = 'blacklist'
}

export interface Client {
  id: number
  name: string
  email?: string
  phone?: string
  telegram?: string
  company_name?: string
  inn?: string
  type: ClientType
  status: ClientStatus
  manager_id?: number
  manager_name?: string
  segment?: string
  source?: string
  notes?: string
  created_at: string
  updated_at?: string
  last_contact?: string
  total_revenue?: number
  projects_count?: number
  deals_count?: number
  tags?: string[]
}

export interface ClientFilters {
  search?: string
  status?: string
  type?: string
  manager_id?: number
  segment?: string
  page?: number
  limit?: number
}

export interface ClientCreateData {
  name: string
  email?: string
  phone?: string
  telegram?: string
  company_name?: string
  inn?: string
  type: ClientType
  status?: ClientStatus
  manager_id?: number
  segment?: string
  source?: string
  notes?: string
  tags?: string[]
}

export interface ClientUpdateData extends Partial<ClientCreateData> {
  id: number
}

export interface Communication {
  id: number
  client_id: number
  type: 'call' | 'email' | 'meeting' | 'message' | 'note'
  direction?: 'incoming' | 'outgoing'
  subject?: string
  content: string
  created_at: string
  created_by: number
  created_by_name?: string
}

export interface TimelineEvent {
  id: number
  type: 'created' | 'updated' | 'communication' | 'deal' | 'project' | 'note'
  title: string
  description?: string
  created_at: string
  created_by_name?: string
  metadata?: Record<string, any>
}

export interface ClientStats {
  total: number
  active: number
  vip: number
  new_month: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  by_segment: Record<string, number>
}

// ============= API FUNCTIONS =============

class ClientsAPI {
  /**
   * Получить список клиентов с фильтрацией
   */
  async getClients(filters?: ClientFilters) {
    try {
      const params = new URLSearchParams()

      if (filters?.search) params.append('search', filters.search)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.type) params.append('type', filters.type)
      if (filters?.manager_id) params.append('manager_id', filters.manager_id.toString())
      if (filters?.segment) params.append('segment', filters.segment)
      if (filters?.page) params.append('page', filters.page.toString())
      if (filters?.limit) params.append('limit', filters.limit.toString())

      const response = await axiosInstance.get(`/admin/clients/?${params.toString()}`)

      return {
        success: true,
        clients: response.data.clients as Client[],
        pagination: response.data.pagination as {
          total: number
          page: number
          limit: number
          pages: number
        },
        stats: response.data.stats
      }
    } catch (error: any) {
      console.error('Error fetching clients:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.message || 'Ошибка загрузки клиентов',
        clients: [],
        pagination: { total: 0, page: 1, limit: 20, pages: 0 }
      }
    }
  }

  /**
   * Получить одного клиента по ID
   */
  async getClient(clientId: number) {
    try {
      const response = await axiosInstance.get(`/admin/clients/api/${clientId}`)

      return {
        success: true,
        client: response.data.client as Client
      }
    } catch (error: any) {
      console.error('Error fetching client:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки клиента'
      }
    }
  }

  /**
   * Создать нового клиента
   */
  async createClient(data: ClientCreateData) {
    try {
      const response = await axiosInstance.post('/admin/clients/api', data)

      return {
        success: true,
        client: response.data.client as Client,
        message: 'Клиент успешно создан'
      }
    } catch (error: any) {
      console.error('Error creating client:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка создания клиента'
      }
    }
  }

  /**
   * Обновить клиента
   */
  async updateClient(clientId: number, data: Partial<ClientCreateData>) {
    try {
      const response = await axiosInstance.put(`/admin/clients/api/${clientId}`, data)

      return {
        success: true,
        client: response.data.client as Client,
        message: 'Клиент успешно обновлен'
      }
    } catch (error: any) {
      console.error('Error updating client:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка обновления клиента'
      }
    }
  }

  /**
   * Удалить клиента
   */
  async deleteClient(clientId: number) {
    try {
      await axiosInstance.delete(`/admin/clients/api/${clientId}`)

      return {
        success: true,
        message: 'Клиент успешно удален'
      }
    } catch (error: any) {
      console.error('Error deleting client:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка удаления клиента'
      }
    }
  }

  /**
   * Добавить коммуникацию с клиентом
   */
  async addCommunication(clientId: number, data: {
    type: Communication['type']
    direction?: Communication['direction']
    subject?: string
    content: string
  }) {
    try {
      const response = await axiosInstance.post(`/admin/clients/api/${clientId}/communication`, data)

      return {
        success: true,
        communication: response.communication as Communication,
        message: 'Коммуникация добавлена'
      }
    } catch (error: any) {
      console.error('Error adding communication:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка добавления коммуникации'
      }
    }
  }

  /**
   * Получить таймлайн клиента
   */
  async getClientTimeline(clientId: number) {
    try {
      const response = await axiosInstance.get(`/admin/clients/api/${clientId}/timeline`)

      return {
        success: true,
        timeline: response.timeline as TimelineEvent[]
      }
    } catch (error: any) {
      console.error('Error fetching timeline:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки истории',
        timeline: []
      }
    }
  }

  /**
   * Получить статистику по сегментам
   */
  async getSegmentStats() {
    try {
      const response = await axiosInstance.get('/admin/clients/api/stats/segments')

      return {
        success: true,
        stats: response.stats
      }
    } catch (error: any) {
      console.error('Error fetching segment stats:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки статистики',
        stats: {}
      }
    }
  }

  /**
   * Простой список клиентов для селектов (совместимость)
   */
  async getClientsSimple() {
    try {
      const response = await axiosInstance.get('/admin/clients/simple')

      return {
        success: true,
        clients: response.data.clients as Array<{
          id: number
          name: string
          telegram_id?: string
          phone?: string
          username?: string
        }>
      }
    } catch (error: any) {
      console.error('Error fetching simple clients:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки списка клиентов',
        clients: []
      }
    }
  }
}

const clientsApi = new ClientsAPI()
export default clientsApi
