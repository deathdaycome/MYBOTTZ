import axiosInstance from '../services/api'

// ============= TYPES =============

export interface ArchivedTask {
  id: number
  title: string
  description?: string
  status: string
  priority: string
  assigned_to_id?: number
  assigned_to_name?: string
  created_by_id: number
  created_by_name?: string
  project_id?: number
  project_name?: string
  created_at: string
  completed_at?: string
  deadline?: string
  task_metadata?: Record<string, any>
}

export interface Employee {
  id: number
  username: string
  first_name?: string
  last_name?: string
  role: string
  is_active: boolean
}

export interface TasksByEmployee {
  employee: Employee | null
  tasks: ArchivedTask[]
}

export interface TasksByDate {
  [dateKey: string]: {
    [employeeKey: string]: TasksByEmployee
  }
}

export interface ArchivedTasksFilters {
  employee_id?: number
  date_from?: string
  date_to?: string
}

// ============= API FUNCTIONS =============

class TasksArchiveAPI {
  /**
   * Получить архивные задачи с фильтрацией
   */
  async getArchivedTasks(filters?: ArchivedTasksFilters) {
    try {
      const params = new URLSearchParams()

      if (filters?.employee_id) params.append('employee_id', filters.employee_id.toString())
      if (filters?.date_from) params.append('date_from', filters.date_from)
      if (filters?.date_to) params.append('date_to', filters.date_to)

      const response = await axiosInstance.get(`/admin/api/tasks/archive/list?${params.toString()}`)

      return {
        success: true,
        tasks_by_date: response.data.tasks_by_date as TasksByDate,
        total_tasks: response.data.total_tasks as number
      }
    } catch (error: any) {
      console.error('Error fetching archived tasks:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.response?.data?.error || 'Ошибка загрузки архивных задач',
        tasks_by_date: {},
        total_tasks: 0
      }
    }
  }

  /**
   * Архивировать задачу
   */
  async archiveTask(taskId: number) {
    try {
      const response = await axiosInstance.post(`/admin/api/tasks/${taskId}/archive`)

      return {
        success: response.data.success,
        message: response.data.success ? 'Задача успешно архивирована' : response.data.error
      }
    } catch (error: any) {
      console.error('Error archiving task:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.response?.data?.error || 'Ошибка архивации задачи'
      }
    }
  }

  /**
   * Восстановить задачу из архива (удалить флаг архивации)
   */
  async restoreTask(taskId: number) {
    try {
      // Используем тот же endpoint для обновления, но убираем флаг archived
      const response = await axiosInstance.put(`/admin/api/tasks/${taskId}`, {
        task_metadata: {
          archived: false
        }
      })

      return {
        success: response.data.success,
        message: response.data.success ? 'Задача успешно восстановлена' : response.data.error
      }
    } catch (error: any) {
      console.error('Error restoring task:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.response?.data?.error || 'Ошибка восстановления задачи'
      }
    }
  }

  /**
   * Получить список сотрудников для фильтра
   */
  async getEmployees() {
    try {
      const response = await axiosInstance.get('/admin/api/users/executors')

      const employees = (response.data.executors || []).filter((admin: Employee) =>
        ['executor', 'owner'].includes(admin.role) && admin.is_active
      )

      return {
        success: true,
        employees
      }
    } catch (error: any) {
      console.error('Error fetching employees:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Ошибка загрузки сотрудников',
        employees: []
      }
    }
  }
}

const tasksArchiveApi = new TasksArchiveAPI()
export default tasksArchiveApi
