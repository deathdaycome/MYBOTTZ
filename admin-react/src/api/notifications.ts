import axiosInstance from '../services/api'

export interface Employee {
  id: number
  username: string
  full_name: string
  email: string
  role: string
  telegram_id?: string
}

export interface NotificationSettings {
  id: number
  admin_user_id: number
  telegram_user_id: string
  notifications_enabled: boolean
  notification_language: string

  // Project notifications
  project_assigned: boolean
  project_status_changed: boolean
  project_deadline_reminder: boolean
  project_overdue: boolean
  project_new_task: boolean

  // Task notifications
  task_assigned: boolean
  task_status_changed: boolean
  task_deadline_reminder: boolean
  task_comment_added: boolean

  // Revision notifications
  revision_new: boolean
  revision_status_changed: boolean
  revision_message_new: boolean

  // Chat notifications
  project_chat_new_message: boolean

  // Sales notifications (Avito/CRM)
  avito_new_message: boolean
  avito_unread_reminder: boolean
  avito_urgent_message: boolean
  lead_assigned: boolean
  lead_status_changed: boolean
  deal_assigned: boolean
  deal_status_changed: boolean

  // Time settings
  work_hours_start: string
  work_hours_end: string
  weekend_notifications: boolean
  urgent_notifications_always: boolean

  // Intervals
  avito_reminder_interval: number
  project_reminder_interval: number

  // Timestamps
  created_at?: string
  updated_at?: string
}

export interface QueueStats {
  pending: number
  sent: number
  failed: number
  cancelled?: number
}

export interface NotificationQueue {
  id: number
  admin_user_id: number
  notification_type: string
  title: string
  message: string
  status: string
  priority: string
  scheduled_at: string
  sent_at?: string
  error_message?: string
}

export interface NotificationLog {
  id: number
  admin_user_id: number
  notification_type: string
  title: string
  message: string
  status: string
  sent_at: string
  error_message?: string
}

export interface Project {
  id: number
  title: string
  status: string
}

export interface TestNotificationResponse {
  success: boolean
  message?: string
  error?: string
}

export interface NotificationTypeGroup {
  label: string
  types: NotificationType[]
}

export interface NotificationType {
  key: string
  label: string
  description: string
}

export interface NotificationTypes {
  [category: string]: NotificationTypeGroup
}

export interface EmployeeWithSettings extends Employee {
  settings: NotificationSettings | null
}

const notificationsApi = {
  // Get all employees with their notification settings (новый JSON API)
  getEmployeesWithSettings: async (): Promise<EmployeeWithSettings[]> => {
    const response = await axiosInstance.get('/admin/notifications/api/employees')
    return response.data.employees || []
  },

  // Get all employees (executors and sales) - старый метод
  getEmployees: async (): Promise<Employee[]> => {
    const response = await axiosInstance.get('/admin/api/users/api')
    return response.data.users || []
  },

  // Get employee notification settings (новый JSON API)
  getEmployeeSettings: async (employeeId: number): Promise<NotificationSettings | null> => {
    const response = await axiosInstance.get(`/admin/notifications/api/settings/${employeeId}`)
    return response.data.settings
  },

  // Update employee notification settings (новый JSON API)
  updateEmployeeSettings: async (
    employeeId: number,
    settings: Partial<NotificationSettings>
  ): Promise<{ success: boolean; message?: string; settings?: NotificationSettings }> => {
    const response = await axiosInstance.put(
      `/admin/notifications/api/settings/${employeeId}`,
      settings,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )
    return response.data
  },

  // Get notification types with descriptions (новый JSON API)
  getNotificationTypes: async (): Promise<NotificationTypes> => {
    const response = await axiosInstance.get('/admin/notifications/api/types')
    return response.data.types
  },

  // Get queue statistics
  getQueueStats: async (): Promise<QueueStats> => {
    const response = await axiosInstance.get('/admin/notifications/stats/queue')
    return response.data
  },

  // Get notification queue
  getQueue: async (params?: {
    status?: string
    notification_type?: string
    page?: number
    limit?: number
  }): Promise<{
    notifications: NotificationQueue[]
    total: number
    pages: number
  }> => {
    const response = await axiosInstance.get('/admin/notifications/queue', { params })
    return response.data
  },

  // Get notification logs
  getLogs: async (params?: {
    employee_id?: number
    notification_type?: string
    status?: string
    page?: number
    limit?: number
  }): Promise<{
    logs: NotificationLog[]
    total: number
    pages: number
  }> => {
    const response = await axiosInstance.get('/admin/notifications/log', { params })
    return response.data
  },

  // Send test notification
  sendTestNotification: async (employeeId: number): Promise<TestNotificationResponse> => {
    const response = await axiosInstance.post(`/admin/notifications/test/${employeeId}`)
    return response.data
  },

  // Process queue manually
  processQueue: async (): Promise<{ success: boolean; message?: string }> => {
    const response = await axiosInstance.post('/admin/notifications/process-queue')
    return response.data
  },

  // Get notification statistics
  getStats: async (days: number = 7): Promise<{
    by_type: Array<{ type: string; count: number; unique_users: number }>
    by_day: Array<{ date: string; count: number }>
    period_days: number
  }> => {
    const response = await axiosInstance.get('/admin/notifications/stats', {
      params: { days }
    })
    return response.data.data
  },

  // Test functions for different notification types
  testAdminNotification: async (): Promise<TestNotificationResponse> => {
    const response = await axiosInstance.post('/admin/api/notifications/test-admin', {
      message: 'Тестовое уведомление из React админ-панели'
    })
    return response.data
  },

  testErrorNotification: async (): Promise<TestNotificationResponse> => {
    const response = await axiosInstance.post('/admin/api/notifications/test-error', {
      error: 'Тестовая ошибка из React админ-панели',
      context: {
        source: 'react-admin-panel',
        timestamp: new Date().toISOString()
      }
    })
    return response.data
  },

  testDailyReport: async (): Promise<TestNotificationResponse> => {
    const response = await axiosInstance.post('/admin/api/notifications/daily-report')
    return response.data
  },

  testAvitoNotification: async (): Promise<TestNotificationResponse> => {
    const response = await axiosInstance.post('/admin/api/notifications/test-avito')
    return response.data
  },

  // Get projects for testing status notifications
  getProjects: async (): Promise<Project[]> => {
    const response = await axiosInstance.get('/admin/api/projects/')
    return response.data.projects || []
  },

  // Update project status (for testing status notifications)
  updateProjectStatus: async (
    projectId: number,
    status: string,
    comment?: string
  ): Promise<{ success: boolean; message?: string }> => {
    const response = await axiosInstance.put(`/admin/api/projects/${projectId}/status`, {
      status,
      comment: comment || 'Тестовое изменение статуса из React админ-панели'
    })
    return response.data
  },

  // Get bot status
  getBotStatus: async (): Promise<{
    success: boolean
    bot_info?: {
      username: string
      first_name: string
    }
  }> => {
    const response = await axiosInstance.get('/admin/api/notifications/bot-status')
    return response.data
  }
}

export default notificationsApi
