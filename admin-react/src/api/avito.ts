import axiosInstance from '../services/api'

interface AvitoChat {
  id: string
  users: Array<{
    id: number
    name: string
  }>
  context?: {
    type: string
    value: {
      title?: string
      price?: number
    }
  }
  last_message?: {
    content: {
      text: string
    }
    created: number
  }
  unread_count: number
}

interface AvitoMessage {
  id: string
  chat_id: string
  author_id: number
  type: string
  direction: string
  content: {
    text?: string
    image?: {
      '640x480'?: string
      '1280x960'?: string
    }
  }
  created: number
}

interface AvitoMessageResponse {
  messages: AvitoMessage[]
  total: number
}

interface AvitoChatsResponse {
  chats: AvitoChat[]
  total: number
  current_user_id: number
}

interface AvitoSettings {
  user_id: string
}

interface AiSalesResponse {
  status: string
  action: string
  offer?: string
  variants?: Array<{
    title: string
    text: string
  }>
  context_analysis?: string
  recommended_variant?: number
  success?: boolean
}

interface PollingStatusResponse {
  polling_active: boolean
  auto_response_enabled: boolean
}

const avitoApi = {
  // Get list of chats
  getChats: async (unreadOnly: boolean = false, limit: number = 50, offset: number = 0): Promise<AvitoChatsResponse> => {
    const response = await axiosInstance.get('/admin/avito/chats', {
      params: { unread_only: unreadOnly, limit, offset }
    })
    return response.data
  },

  // Get chat info
  getChatInfo: async (chatId: string): Promise<AvitoChat> => {
    const response = await axiosInstance.get(`/admin/avito/chats/${chatId}`)
    return response.data
  },

  // Get chat messages
  getChatMessages: async (chatId: string, limit: number = 100, offset: number = 0): Promise<AvitoMessageResponse> => {
    const response = await axiosInstance.get(`/admin/avito/chats/${chatId}/messages`, {
      params: { limit, offset }
    })
    return response.data
  },

  // Send message
  sendMessage: async (chatId: string, text: string): Promise<AvitoMessage> => {
    const response = await axiosInstance.post(`/admin/avito/chats/${chatId}/messages`, { text })
    return response.data
  },

  // Delete message
  deleteMessage: async (chatId: string, messageId: string): Promise<{ status: string; deleted: boolean }> => {
    const response = await axiosInstance.post(`/admin/avito/chats/${chatId}/messages/${messageId}/delete`)
    return response.data
  },

  // Upload and send image
  uploadImage: async (chatId: string, file: File): Promise<AvitoMessage> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axiosInstance.post(`/admin/avito/chats/${chatId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Mark chat as read
  markChatAsRead: async (chatId: string): Promise<{ status: string; marked_as_read: boolean }> => {
    const response = await axiosInstance.post(`/admin/avito/chats/${chatId}/read`)
    return response.data
  },

  // Generate AI response
  generateAiResponse: async (chatId: string): Promise<{ suggestion: string; reasoning: string; confidence: number }> => {
    const response = await axiosInstance.post(`/admin/avito/chats/${chatId}/ai-suggest`)
    return response.data
  },

  // Create lead from chat
  createLead: async (chatId: string): Promise<any> => {
    const response = await axiosInstance.post(`/admin/avito/chats/${chatId}/create-lead`)
    return response.data
  },

  // AI Sales - get suggestions
  getAiSalesSuggestions: async (
    chatId: string,
    industry: string,
    actionType: 'suggest_response' | 'startup_offer'
  ): Promise<AiSalesResponse> => {
    const response = await axiosInstance.post(`/admin/avito/chats/${chatId}/ai-sales`, {
      industry,
      action_type: actionType
    })
    return response.data
  },

  // Get industry suggestions
  getIndustries: async (partial: string = ''): Promise<{ suggestions: string[] }> => {
    const response = await axiosInstance.get('/admin/avito/ai-sales/industries', {
      params: { partial }
    })
    return response.data
  },

  // Configure Avito
  configure: async (userId: string): Promise<{ status: string; message: string }> => {
    const response = await axiosInstance.post('/admin/avito/configure', { user_id: userId })
    return response.data
  },

  // Setup webhook
  setupWebhook: async (): Promise<{ success: boolean; message: string; webhook_url?: string }> => {
    const response = await axiosInstance.post('/admin/avito/setup-webhook')
    return response.data
  },

  // Update client status
  updateClientStatus: async (
    chatId: string,
    status: string,
    notes?: string
  ): Promise<{ status: string; message: string }> => {
    const response = await axiosInstance.post(`/admin/avito/chats/${chatId}/status`, {
      status,
      notes
    })
    return response.data
  },

  // Export chat dialog
  exportChat: async (chatId: string): Promise<Blob> => {
    const response = await axiosInstance.get(`/admin/avito/chats/${chatId}/export`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Polling controls
  startPolling: async (): Promise<{ status: string; message: string }> => {
    const response = await axiosInstance.post('/admin/avito/polling/start')
    return response.data
  },

  stopPolling: async (): Promise<{ status: string; message: string }> => {
    const response = await axiosInstance.post('/admin/avito/polling/stop')
    return response.data
  },

  getPollingStatus: async (): Promise<PollingStatusResponse> => {
    const response = await axiosInstance.get('/admin/avito/polling/status')
    return response.data
  },

  toggleAutoResponse: async (enabled: boolean): Promise<{ status: string; message: string; enabled: boolean }> => {
    const response = await axiosInstance.post('/admin/avito/auto-response/toggle', { enabled })
    return response.data
  },

  // Debug
  getDebugStatus: async (): Promise<any> => {
    const response = await axiosInstance.get('/admin/avito/debug')
    return response.data
  }
}

export default avitoApi
