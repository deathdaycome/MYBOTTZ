import axiosInstance from '../services/api'

export interface Task {
  id: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  type: 'TASK' | 'REVISION'  // Тип: задача или правка
  project_id?: number  // ID проекта (для задач из проектов)
  project?: {
    id: number
    title: string
    status?: string
  }
  created_from_chat?: boolean  // Создано из чата
  color?: 'normal' | 'red' | 'yellow' | 'green'
  tags?: string[]
  assigned_to_id: number
  assigned_to?: {
    id: number
    username: string
    first_name: string
    last_name: string
    role: string
  }
  created_by_id: number
  created_by?: {
    id: number
    username: string
    first_name: string
    last_name: string
    role: string
  }
  deadline?: string
  estimated_hours?: number
  actual_hours?: number
  progress?: number
  timer_started_at?: string
  time_spent_seconds?: number
  deploy_url?: string
  is_overdue?: boolean
  days_until_deadline?: number
  can_delete?: boolean
  created_by_admin?: boolean
  created_at: string
  updated_at: string
  completed_at?: string
  task_metadata?: Record<string, any>
}

export interface TaskComment {
  id: number
  task_id: number
  author_id: number
  author?: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  comment: string
  comment_type?: 'comment' | 'status_change' | 'reassignment'
  is_internal?: boolean
  attachments?: Array<{
    filename: string
    original_filename: string
    path: string
    type: string
    size: number
  }>
  is_read?: boolean
  read_by?: number[]
  is_read_by_me?: boolean
  created_at: string
}

export interface TaskStats {
  total_tasks: number
  pending_tasks: number
  in_progress_tasks: number
  completed_tasks: number
  overdue_tasks: number
  today_tasks: number
  priority_stats: {
    urgent: number
    high: number
    normal: number
    low: number
  }
  recent_tasks: Task[]
  employee_stats?: Array<{
    employee: any
    total_tasks: number
    pending_tasks: number
    completed_tasks: number
    overdue_tasks: number
  }>
}

export interface CreateTaskData {
  title: string
  description?: string
  assigned_to_id: number
  priority?: 'low' | 'normal' | 'high' | 'urgent'
  deadline?: string
  estimated_hours?: number
  color?: 'normal' | 'red' | 'yellow' | 'green'
  tags?: string[]
  created_by_admin?: boolean
  project_id?: number  // ID проекта (опционально, для задач из проектов)
}

export interface UpdateTaskData {
  title?: string
  description?: string
  status?: 'pending' | 'in_progress' | 'completed'
  priority?: 'low' | 'normal' | 'high' | 'urgent'
  deadline?: string
  estimated_hours?: number
  actual_hours?: number
  assigned_to_id?: number
  color?: 'normal' | 'red' | 'yellow' | 'green'
  tags?: string[]
  deploy_url?: string
}

const tasksApi = {
  // Получение всех задач
  getTasks: async (filters?: {
    status?: string
    assigned_to_id?: number
    created_by_id?: number
    priority?: string
    type?: string  // TASK или REVISION
    project_id?: number  // Фильтр по проекту
  }) => {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.assigned_to_id) params.append('assigned_to_id', filters.assigned_to_id.toString())
    if (filters?.created_by_id) params.append('created_by_id', filters.created_by_id.toString())
    if (filters?.priority) params.append('priority', filters.priority)
    if (filters?.type) params.append('type', filters.type)
    if (filters?.project_id) params.append('project_id', filters.project_id.toString())

    const queryString = params.toString()
    const url = queryString ? `/admin/api/tasks/?${queryString}` : '/admin/api/tasks/'
    const response = await axiosInstance.get(url)
    return response.data as { success: boolean; tasks: Task[] }
  },

  // Получение моих задач
  getMyTasks: async () => {
    const response = await axiosInstance.get('/admin/api/tasks/my-tasks')
    return response.data as { success: boolean; tasks: Task[] }
  },

  // Получение задач сотрудника
  getEmployeeTasks: async (employeeId: string | number) => {
    const response = await axiosInstance.get(`/admin/api/tasks/employee/${employeeId}`)
    return response.data as { success: boolean; tasks: Task[] }
  },

  // Получение одной задачи
  getTask: async (taskId: number) => {
    const response = await axiosInstance.get(`/admin/api/tasks/${taskId}`)
    return response.data as { success: boolean; task: Task }
  },

  // Создание задачи
  createTask: async (data: CreateTaskData) => {
    const response = await axiosInstance.post('/admin/api/tasks/', data)
    return response.data as { success: boolean; message: string; task: Task }
  },

  // Обновление задачи
  updateTask: async (taskId: number, data: UpdateTaskData) => {
    const response = await axiosInstance.put(`/admin/api/tasks/${taskId}`, data)
    return response.data as { success: boolean; message: string; task: Task }
  },

  // Обновление статуса задачи (для drag-and-drop)
  updateTaskStatus: async (taskId: number, status: string) => {
    const response = await axiosInstance.put(`/admin/api/tasks/${taskId}/status`, { status })
    return response.data as { success: boolean; message: string }
  },

  // Переназначение задачи
  reassignTask: async (taskId: number, assigned_to_id: number) => {
    const response = await axiosInstance.put(`/admin/api/tasks/${taskId}/reassign`, { assigned_to_id })
    return response.data as { success: boolean; message: string }
  },

  // Удаление задачи
  deleteTask: async (taskId: number) => {
    const response = await axiosInstance.delete(`/admin/api/tasks/${taskId}`)
    return response.data as { success: boolean; message: string }
  },

  // Получение комментариев
  getComments: async (taskId: number) => {
    const response = await axiosInstance.get(`/admin/api/tasks/${taskId}/comments`)
    return response.data as {
      success: boolean
      comments: TaskComment[]
      total_count: number
      unread_count: number
    }
  },

  // Добавление комментария
  addComment: async (taskId: number, comment: string, is_internal: boolean = false, files?: File[]) => {
    const formData = new FormData()
    formData.append('comment', comment)
    formData.append('is_internal', is_internal.toString())

    if (files) {
      files.forEach((file) => {
        formData.append('files', file)
      })
    }

    const response = await axiosInstance.post(`/admin/api/tasks/${taskId}/comments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000, // 60 секунд для загрузки файлов
    })
    return response.data as { success: boolean; message: string; comment: TaskComment }
  },

  // Отметить комментарий как прочитанный
  markCommentRead: async (taskId: number, commentId: number) => {
    const response = await axiosInstance.post(
      `/admin/api/tasks/${taskId}/comments/${commentId}/mark_read`
    )
    return response.data as { success: boolean; message: string }
  },

  // Отметить все комментарии как прочитанные
  markAllCommentsRead: async (taskId: number) => {
    const response = await axiosInstance.post(`/admin/api/tasks/${taskId}/mark_all_comments_read`)
    return response.data as { success: boolean; marked_count: number }
  },

  // Получение количества непрочитанных комментариев
  getUnreadCommentsCount: async (taskId: number) => {
    const response = await axiosInstance.get(`/admin/api/tasks/${taskId}/unread_comments_count`)
    return response.data as { success: boolean; task_id: number; unread_count: number }
  },

  // Получение статистики
  getStats: async () => {
    const response = await axiosInstance.get('/admin/api/tasks/stats/dashboard')
    return response.data as { success: boolean; stats: TaskStats }
  },

  // Получение списка исполнителей
  getExecutors: async () => {
    const response = await axiosInstance.get('/admin/api/users/executors')
    return response.data.executors || []
  },

  // Получение списка проектов для фильтров
  getProjects: async () => {
    const response = await axiosInstance.get('/admin/api/projects/')
    return response.data.projects || []
  },

  // Получение задач конкретного проекта
  getProjectTasks: async (projectId: number) => {
    const response = await axiosInstance.get(`/admin/api/projects/${projectId}/tasks`)
    return response.data as { success: boolean; tasks: Task[]; total_count: number }
  },

  // Обновление прогресса
  updateProgress: async (taskId: number, progress: number) => {
    const response = await axiosInstance.post(`/admin/api/tasks/${taskId}/progress`, { progress })
    return response.data as { success: boolean; progress: number; message: string }
  },

  // Запуск таймера
  startTimer: async (taskId: number) => {
    const response = await axiosInstance.post(`/admin/tasks/${taskId}/timer/start`)
    return response.data as { success: boolean; message: string; data: Task }
  },

  // Остановка таймера
  stopTimer: async (taskId: number) => {
    const response = await axiosInstance.post(`/admin/tasks/${taskId}/timer/stop`)
    return response.data as {
      success: boolean
      message: string
      data: Task
      time_formatted: string
    }
  },

  // Отметить задачу как выполненную (для сотрудника)
  markCompleted: async (taskId: number) => {
    const response = await axiosInstance.post(`/admin/api/tasks/${taskId}/mark-completed`)
    return response.data as { success: boolean; message: string; task: Task }
  },

  // Архивация задачи
  archiveTask: async (taskId: number) => {
    const response = await axiosInstance.post(`/admin/api/tasks/${taskId}/archive`)
    return response.data as { success: boolean; message: string; task: Task }
  },

  // Получение архивных задач
  getArchivedTasks: async (filters?: {
    employee_id?: number
    date_from?: string
    date_to?: string
  }) => {
    const params = new URLSearchParams()
    if (filters?.employee_id) params.append('employee_id', filters.employee_id.toString())
    if (filters?.date_from) params.append('date_from', filters.date_from)
    if (filters?.date_to) params.append('date_to', filters.date_to)

    const response = await axiosInstance.get(`/admin/api/tasks/archive/list?${params}`)
    return response.data as {
      success: boolean
      tasks_by_date: Record<
        string,
        Record<string, { employee: any; tasks: Task[] }>
      >
      total_tasks: number
    }
  },

  // Загрузка файлов к задаче
  uploadFiles: async (taskId: number, files: File[]) => {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await axiosInstance.post(`/admin/api/tasks/${taskId}/upload-image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data as {
      success: boolean
      message: string
      files: Array<{
        filename: string
        path: string
        uploaded_at: string
        uploaded_by: number
      }>
    }
  },
}

export default tasksApi
