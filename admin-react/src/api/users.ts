import axiosInstance from '../services/api'

export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  role: 'owner' | 'admin' | 'executor' | 'salesperson' | 'timlead'
  is_active: boolean
  telegram_id?: number
  created_at?: string
  last_login?: string
  tasks_count?: number
  active_tasks?: number
}

export interface CreateUserData {
  username: string
  password: string
  email?: string
  first_name?: string
  last_name?: string
  role: 'admin' | 'executor' | 'salesperson' | 'owner' | 'timlead'
}

export interface UpdateUserData {
  first_name?: string
  last_name?: string
  email?: string
  password?: string
  is_active?: boolean
}

export interface UserNotificationSettings {
  new_tasks: boolean
  deadlines: boolean
  comments: boolean
  reports: boolean
}

const usersApi = {
  // Получить всех пользователей
  getUsers: async () => {
    const response = await axiosInstance.get('/admin/api/users/api')
    return response.data as {
      success: boolean
      users: User[]
    }
  },

  // Получить одного пользователя
  getUser: async (userId: number) => {
    const response = await axiosInstance.get(`/admin/api/users/${userId}`)
    return response.data as {
      success: boolean
      user: User
      message?: string
    }
  },

  // Создать пользователя
  createUser: async (data: CreateUserData) => {
    const response = await axiosInstance.post('/admin/api/users/create', data)
    return response.data as {
      success: boolean
      message: string
      user?: User
      detail?: string
    }
  },

  // Обновить пользователя
  updateUser: async (userId: number, data: UpdateUserData) => {
    const response = await axiosInstance.put(`/admin/api/users/${userId}`, data)
    return response.data as {
      success: boolean
      message: string
      user?: User
    }
  },

  // Изменить пароль пользователя
  changePassword: async (userId: number, newPassword: string) => {
    const response = await axiosInstance.put(`/admin/api/users/${userId}/password`, {
      password: newPassword,
      new_password: newPassword
    })
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Просмотреть пароль пользователя (только для owner)
  viewPassword: async (userId: number) => {
    const response = await axiosInstance.get(`/admin/api/users/${userId}/password/view`)
    return response.data as {
      success: boolean
      password: string
      message: string
    }
  },

  // Деактивировать пользователя
  deactivateUser: async (userId: number) => {
    const response = await axiosInstance.delete(`/admin/api/users/${userId}`)
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Обновить настройки уведомлений
  updateNotifications: async (userId: number, settings: UserNotificationSettings) => {
    const response = await axiosInstance.put(`/admin/api/users/${userId}/notifications`, settings)
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Переключить статус пользователя
  toggleUserStatus: async (userId: number, isActive: boolean) => {
    const response = await axiosInstance.put(`/admin/api/users/${userId}`, {
      is_active: isActive
    })
    return response.data as {
      success: boolean
      message: string
    }
  },

  // Получить исполнителей
  getExecutors: async () => {
    const response = await axiosInstance.get('/admin/api/users/executors')
    return response.data as {
      success: boolean
      executors: User[]
    }
  }
}

export default usersApi
