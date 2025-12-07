import axiosInstance from '../services/api'

export interface ChatProject {
  id: number
  title: string
  client_name: string | null
  status: string
}

export interface ChatLastMessage {
  sender_type: 'client' | 'executor'
  message_text: string
  created_at: string
}

export interface Chat {
  id: number
  project: ChatProject
  last_message: ChatLastMessage | null
  last_message_at: string | null
  unread_by_executor: number
  unread_by_client: number
  is_pinned_by_owner: boolean
  is_hidden_by_owner: boolean
  created_at: string
}

export interface ChatMessage {
  id: number
  sender_type: 'client' | 'executor'
  message_text: string
  attachments: Array<{
    filename: string
    url: string
    size: number
  }>
  created_at: string
  is_read: boolean
}

const chatsApi = {
  /**
   * Получить список всех чатов
   */
  getChats: async () => {
    const response = await axiosInstance.get('/admin/api/chats')
    return response.data as Chat[]
  },

  /**
   * Получить сообщения чата
   */
  getChatMessages: async (chatId: number) => {
    const response = await axiosInstance.get(`/admin/api/chats/${chatId}/messages`)
    return response.data as {
      messages: ChatMessage[]
    }
  },

  /**
   * Отправить сообщение в чат
   */
  sendMessage: async (chatId: number, formData: FormData) => {
    const response = await axiosInstance.post(
      `/admin/api/chats/${chatId}/messages`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data as ChatMessage
  },

  /**
   * Закрепить/открепить чат
   */
  togglePinChat: async (chatId: number) => {
    const response = await axiosInstance.post(`/admin/api/chats/${chatId}/pin`)
    return response.data as {
      id: number
      is_pinned_by_owner: boolean
      message: string
    }
  },

  /**
   * Скрыть/показать чат
   */
  toggleHideChat: async (chatId: number) => {
    const response = await axiosInstance.post(`/admin/api/chats/${chatId}/hide`)
    return response.data as {
      id: number
      is_hidden_by_owner: boolean
      message: string
    }
  },
}

export default chatsApi
