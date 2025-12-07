import axiosInstance from '../services/api'

// ============= TYPES =============

export interface MyTask {
  id: number
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'urgent' | 'high' | 'normal' | 'low'
  assigned_to_id?: number
  assigned_to_name?: string
  created_by_id: number
  created_by_name?: string
  created_by_admin?: boolean
  project_id?: number
  project_name?: string
  created_at: string
  deadline?: string
  completed_at?: string
  task_metadata?: Record<string, any>
}

export interface Executor {
  id: number
  username: string
  first_name?: string
  last_name?: string
  role: string
  is_active: boolean
}

export interface TasksByStatus {
  pending: MyTask[]
  in_progress: MyTask[]
  completed: MyTask[]
}

// ============= API FUNCTIONS =============

class MyTasksAPI {
  /**
   * Получить задачи текущего пользователя или конкретного сотрудника (для owner)
   */
  async getUserTasks(userId?: number) {
    try {
      const params = new URLSearchParams()

      if (userId) {
        params.append('assigned_to_id', userId.toString())
      }

      // Exclude archived tasks
      params.append('per_page', '1000')

      const response = await axiosInstance.get(`/admin/api/tasks/?${params.toString()}`)

      // Group tasks by status
      const tasksByStatus: TasksByStatus = {
        pending: [],
        in_progress: [],
        completed: []
      }

      const tasks = response.data.tasks || []
      tasks.forEach((task: MyTask) => {
        if (task.status === 'pending') {
          tasksByStatus.pending.push(task)
        } else if (task.status === 'in_progress') {
          tasksByStatus.in_progress.push(task)
        } else if (task.status === 'completed') {
          tasksByStatus.completed.push(task)
        }
      })

      return {
        success: true,
        tasksByStatus,
        total: tasks.length
      }
    } catch (error: any) {
      console.error('Error fetching user tasks:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки задач',
        tasksByStatus: {
          pending: [],
          in_progress: [],
          completed: []
        },
        total: 0
      }
    }
  }

  /**
   * Обновить статус задачи (для drag & drop)
   */
  async updateTaskStatus(taskId: number, newStatus: 'pending' | 'in_progress' | 'completed') {
    try {
      const response = await axiosInstance.put(`/admin/api/tasks/${taskId}`, {
        status: newStatus
      })

      return {
        success: response.data.success,
        message: response.data.success ? 'Статус задачи обновлен' : response.data.error
      }
    } catch (error: any) {
      console.error('Error updating task status:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.response?.data?.error || 'Ошибка обновления статуса'
      }
    }
  }

  /**
   * Получить список исполнителей (для owner)
   */
  async getExecutors() {
    try {
      const response = await axiosInstance.get('/admin/api/users/executors')

      const executors = (response.data.executors || []).filter((admin: Executor) =>
        ['executor', 'owner'].includes(admin.role) && admin.is_active
      )

      return {
        success: true,
        executors
      }
    } catch (error: any) {
      console.error('Error fetching executors:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки исполнителей',
        executors: []
      }
    }
  }

  /**
   * Создать новую задачу
   */
  async createTask(taskData: {
    title: string
    description?: string
    priority: string
    deadline?: string
    assigned_to_id?: number | null
    created_by_admin?: boolean
  }) {
    try {
      const response = await axiosInstance.post('/admin/api/tasks', taskData)

      return {
        success: true,
        message: 'Задача создана успешно',
        task: response.data
      }
    } catch (error: any) {
      console.error('Error creating task:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка создания задачи'
      }
    }
  }

  /**
   * Получить детали задачи
   */
  async getTask(taskId: number) {
    try {
      const response = await axiosInstance.get(`/admin/api/tasks/${taskId}`)

      return {
        success: true,
        task: response.data as MyTask
      }
    } catch (error: any) {
      console.error('Error fetching task:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки задачи',
        task: null
      }
    }
  }

  /**
   * Удалить задачу
   */
  async deleteTask(taskId: number) {
    try {
      const response = await axiosInstance.delete(`/admin/api/tasks/${taskId}`)

      return {
        success: true,
        message: 'Задача удалена'
      }
    } catch (error: any) {
      console.error('Error deleting task:', error)
      return {
        success: false,
        message: error.response?.data?.detail || error.response?.data?.message || 'Ошибка удаления задачи'
      }
    }
  }
}

const myTasksApi = new MyTasksAPI()
export default myTasksApi
