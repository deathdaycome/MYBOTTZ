import axiosInstance from '../services/api'

// ============= TYPES =============

export interface PortfolioProject {
  id: number
  title: string
  subtitle?: string
  description: string
  category: string
  main_image?: string
  image_paths?: string[]
  technologies?: string
  complexity: string
  complexity_level: number
  development_time?: number
  cost?: number
  cost_range?: string
  show_cost: boolean
  demo_link?: string
  repository_link?: string
  external_links?: Array<{ name: string; url: string }>
  is_featured: boolean
  is_visible: boolean
  is_published: boolean
  sort_order: number
  tags?: string
  client_name?: string
  project_status: string
  views_count: number
  likes_count: number
  created_at: string
  updated_at?: string
  completed_at?: string
  created_by?: number
}

export interface PortfolioStats {
  total: number
  visible: number
  featured: number
  total_views: number
  categories: Record<string, number>
}

export interface Category {
  id: string
  name: string
  count: number
}

export interface PaginationData {
  page: number
  per_page: number
  total: number
  pages: number
}

export interface PortfolioListResponse {
  success: boolean
  data: PortfolioProject[]
  pagination: PaginationData
}

export interface PortfolioItemResponse {
  success: boolean
  data: PortfolioProject
}

export interface PortfolioStatsResponse {
  success: boolean
  stats: PortfolioStats
}

export interface CategoriesResponse {
  success: boolean
  categories: Category[]
}

export interface MessageResponse {
  success: boolean
  message: string
  item?: PortfolioProject
  data?: PortfolioProject
}

export interface UploadImageResponse {
  success: boolean
  message: string
  data: {
    filename: string
    original_path: string
    thumb_path: string
    size: number
    content_type: string
  }
}

export interface PortfolioCreateData {
  title: string
  subtitle?: string
  description: string
  category: string
  technologies?: string
  complexity?: string
  complexity_level?: number
  development_time?: number
  cost?: number
  cost_range?: string
  show_cost?: boolean
  demo_link?: string
  repository_link?: string
  external_links?: string
  is_featured?: boolean
  is_visible?: boolean
  sort_order?: number
  tags?: string
  client_name?: string
  project_status?: string
  main_image?: File
  completed_at?: string
}

// ============= API CLIENT =============

const portfolioApi = {
  // Get portfolio list with filters and pagination
  getList: async (params?: {
    page?: number
    per_page?: number
    category?: string
    search?: string
    featured_only?: boolean
    visible_only?: boolean
    sort_by?: string
  }): Promise<PortfolioListResponse> => {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.per_page) queryParams.append('per_page', params.per_page.toString())
    if (params?.category) queryParams.append('category', params.category)
    if (params?.search) queryParams.append('search', params.search)
    if (params?.featured_only !== undefined)
      queryParams.append('featured_only', params.featured_only.toString())
    if (params?.visible_only !== undefined)
      queryParams.append('visible_only', params.visible_only.toString())
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by)

    const response = await axiosInstance.get(`/api/portfolio/?${queryParams.toString()}`)
    return response.data
  },

  // Get categories list
  getCategories: async (): Promise<CategoriesResponse> => {
    const response = await axiosInstance.get('/api/portfolio/categories')
    return response.data
  },

  // Get single portfolio item
  getItem: async (projectId: number): Promise<PortfolioItemResponse> => {
    const response = await axiosInstance.get(`/api/portfolio/${projectId}`)
    return response.data
  },

  // Create new portfolio item
  create: async (data: PortfolioCreateData): Promise<MessageResponse> => {
    const formData = new FormData()

    // Append all fields
    formData.append('title', data.title)
    if (data.subtitle) formData.append('subtitle', data.subtitle)
    formData.append('description', data.description)
    formData.append('category', data.category)
    if (data.technologies) formData.append('technologies', data.technologies)
    formData.append('complexity', data.complexity || 'medium')
    formData.append('complexity_level', (data.complexity_level || 5).toString())
    if (data.development_time)
      formData.append('development_time', data.development_time.toString())
    if (data.cost) formData.append('cost', data.cost.toString())
    if (data.cost_range) formData.append('cost_range', data.cost_range)
    formData.append('show_cost', (data.show_cost || false).toString())
    if (data.demo_link) formData.append('demo_link', data.demo_link)
    if (data.repository_link) formData.append('repository_link', data.repository_link)
    formData.append('external_links', data.external_links || '[]')
    formData.append('is_featured', (data.is_featured || false).toString())
    formData.append('is_visible', (data.is_visible !== false).toString())
    formData.append('sort_order', (data.sort_order || 0).toString())
    if (data.tags) formData.append('tags', data.tags)
    if (data.client_name) formData.append('client_name', data.client_name)
    formData.append('project_status', data.project_status || 'completed')
    if (data.completed_at) formData.append('completed_at', data.completed_at)

    // Append main image if exists
    if (data.main_image) {
      formData.append('main_image', data.main_image)
    }

    const response = await axiosInstance.post('/api/portfolio/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Update portfolio item
  update: async (
    projectId: number,
    data: PortfolioCreateData & { remove_main_image?: boolean }
  ): Promise<MessageResponse> => {
    const formData = new FormData()

    // Append all fields
    formData.append('title', data.title)
    formData.append('subtitle', data.subtitle || '')
    formData.append('description', data.description)
    formData.append('category', data.category)
    formData.append('technologies', data.technologies || '')
    formData.append('complexity', data.complexity || 'medium')
    formData.append('complexity_level', (data.complexity_level || 5).toString())
    formData.append('development_time', (data.development_time || 0).toString())
    formData.append('cost', (data.cost || 0).toString())
    formData.append('cost_range', data.cost_range || '')
    formData.append('show_cost', (data.show_cost || false).toString())
    formData.append('demo_link', data.demo_link || '')
    formData.append('repository_link', data.repository_link || '')
    formData.append('external_links', data.external_links || '[]')
    formData.append('is_featured', (data.is_featured || false).toString())
    formData.append('is_visible', (data.is_visible !== false).toString())
    formData.append('sort_order', (data.sort_order || 0).toString())
    formData.append('tags', data.tags || '')
    formData.append('client_name', data.client_name || '')
    formData.append('project_status', data.project_status || 'completed')
    formData.append('remove_main_image', (data.remove_main_image || false).toString())

    // Append main image if exists
    if (data.main_image) {
      formData.append('main_image', data.main_image)
    }

    const response = await axiosInstance.put(`/api/portfolio/${projectId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Delete portfolio item
  delete: async (projectId: number): Promise<MessageResponse> => {
    const response = await axiosInstance.delete(`/api/portfolio/${projectId}`)
    return response.data
  },

  // Upload image
  uploadImage: async (file: File, subfolder?: string): Promise<UploadImageResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    if (subfolder) formData.append('subfolder', subfolder)

    const response = await axiosInstance.post('/api/portfolio/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Reorder portfolio items
  reorder: async (orderData: Array<{ id: number; order: number }>): Promise<MessageResponse> => {
    const response = await axiosInstance.post('/api/portfolio/reorder', {
      projects: orderData,
    })
    return response.data
  },

  // Get portfolio statistics
  getStats: async (): Promise<PortfolioStatsResponse> => {
    const response = await axiosInstance.get('/api/portfolio/stats/overview')
    return response.data
  },

  // Publish to Telegram
  publishToTelegram: async (portfolioId: number): Promise<MessageResponse> => {
    const response = await axiosInstance.post(`/api/portfolio/${portfolioId}/publish`)
    return response.data
  },

  // Update published item in Telegram
  updatePublished: async (portfolioId: number): Promise<MessageResponse> => {
    const response = await axiosInstance.put(`/api/portfolio/${portfolioId}/update-published`)
    return response.data
  },

  // Unpublish from Telegram
  unpublish: async (portfolioId: number): Promise<MessageResponse> => {
    const response = await axiosInstance.delete(`/api/portfolio/${portfolioId}/unpublish`)
    return response.data
  },
}

export default portfolioApi
