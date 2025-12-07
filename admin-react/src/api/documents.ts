import axiosInstance from '../services/api'

export interface Document {
  id: number
  name: string
  type: 'contract' | 'invoice' | 'act' | 'other'
  number: string | null
  description: string | null
  file_path: string
  file_type: string
  file_size: number
  project_id: number | null
  project_name: string | null
  created_at: string | null
  created_by: string | null
}

export interface DocumentStats {
  total: number
  contracts: number
  invoices: number
  acts: number
  other: number
}

export interface Project {
  id: number
  title: string
  client_name: string | null
}

const documentsApi = {
  /**
   * Получить статистику документов
   */
  getStats: async (): Promise<DocumentStats> => {
    const response = await axiosInstance.get('/admin/documents/api/list')
    const data = response.data

    if (!data.success) {
      throw new Error(data.message || 'Failed to load statistics')
    }

    const documents = data.documents as Document[]

    return {
      total: documents.length,
      contracts: documents.filter((d) => d.type === 'contract').length,
      invoices: documents.filter((d) => d.type === 'invoice').length,
      acts: documents.filter((d) => d.type === 'act').length,
      other: documents.filter((d) => d.type === 'other').length,
    }
  },

  /**
   * Получить список документов с фильтрацией
   */
  getDocuments: async (params?: {
    type?: string
    search?: string
    project_id?: number
  }): Promise<Document[]> => {
    const queryParams = new URLSearchParams()

    if (params?.type) queryParams.append('type', params.type)
    if (params?.search) queryParams.append('search', params.search)
    if (params?.project_id) queryParams.append('project_id', params.project_id.toString())

    const url = `/admin/documents/api/list${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    const response = await axiosInstance.get(url)

    if (!response.data.success) {
      throw new Error(response.data.message || 'Failed to load documents')
    }

    return response.data.documents as Document[]
  },

  /**
   * Загрузить новый документ
   */
  uploadDocument: async (data: {
    file: File
    name: string
    type: 'contract' | 'invoice' | 'act' | 'other'
    description?: string
    number?: string
    project_id?: number
  }): Promise<{ success: boolean; message: string; document?: Document }> => {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('name', data.name)
    formData.append('type', data.type)

    if (data.description) formData.append('description', data.description)
    if (data.number) formData.append('number', data.number)
    if (data.project_id) formData.append('project_id', data.project_id.toString())

    const response = await axiosInstance.post('/admin/documents/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  },

  /**
   * Скачать документ
   */
  downloadDocument: async (documentId: number): Promise<Blob> => {
    const response = await axiosInstance.get(`/admin/documents/api/download/${documentId}`, {
      responseType: 'blob',
    })

    return response.data
  },

  /**
   * Удалить документ
   */
  deleteDocument: async (documentId: number): Promise<{ success: boolean; message: string }> => {
    const response = await axiosInstance.delete(`/admin/documents/api/${documentId}`)
    return response.data
  },

  /**
   * Получить список проектов для привязки
   */
  getProjects: async (): Promise<Project[]> => {
    const response = await axiosInstance.get('/admin/documents/api/projects')

    if (!response.data.success) {
      throw new Error(response.data.message || 'Failed to load projects')
    }

    return response.data.projects as Project[]
  },
}

export default documentsApi
