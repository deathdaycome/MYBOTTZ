/**
 * Вкладка "Задачи" проекта
 * Список задач проекта с фильтрацией и созданием
 */

import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { CheckSquare, Plus, Loader2, Calendar, User, AlertCircle, Clock, CheckCircle2, XCircle } from 'lucide-react'
import axiosInstance from '../../services/api'

interface Project {
  id: number
  title: string
}

interface Task {
  id: number
  title: string
  description?: string
  status: string
  priority: string
  assigned_to?: number
  assigned_to_name?: string
  deadline?: string
  created_at: string
  type: string
}

interface OutletContext {
  project: Project
}

export const ProjectTasks = () => {
  const { project } = useOutletContext<OutletContext>()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')

  // Загрузка задач
  useEffect(() => {
    loadTasks()
  }, [project.id])

  const loadTasks = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get(`/admin/api/projects/${project.id}/tasks`)

      if (response.data.success) {
        // Фильтруем только задачи (не правки)
        const projectTasks = (response.data.tasks || []).filter((task: Task) => task.type !== 'REVISION')
        setTasks(projectTasks)
      }
      setError(null)
    } catch (err: any) {
      console.error('Error loading tasks:', err)
      setError('Ошибка загрузки задач')
    } finally {
      setLoading(false)
    }
  }

  // Статусы задач
  const taskStatuses: Record<string, { label: string; color: string; icon: any }> = {
    new: { label: 'Новая', color: 'blue', icon: AlertCircle },
    in_progress: { label: 'В работе', color: 'yellow', icon: Clock },
    review: { label: 'На проверке', color: 'purple', icon: CheckSquare },
    completed: { label: 'Завершена', color: 'green', icon: CheckCircle2 },
    cancelled: { label: 'Отменена', color: 'red', icon: XCircle },
  }

  // Приоритеты
  const priorities: Record<string, { label: string; color: string }> = {
    low: { label: 'Низкий', color: 'gray' },
    medium: { label: 'Средний', color: 'blue' },
    high: { label: 'Высокий', color: 'orange' },
    urgent: { label: 'Срочный', color: 'red' },
  }

  const getTaskStatus = (status: string) => {
    return taskStatuses[status] || taskStatuses.new
  }

  const getPriority = (priority: string) => {
    return priorities[priority] || priorities.medium
  }

  // Фильтрация задач
  const filteredTasks = tasks.filter((task) => {
    if (statusFilter === 'all') return true
    return task.status === statusFilter
  })

  // Подсчет задач по статусам
  const statusCounts = tasks.reduce((acc, task) => {
    acc[task.status] = (acc[task.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Задачи проекта</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
          <Plus className="w-4 h-4" />
          <span>Создать задачу</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Фильтры по статусам */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => setStatusFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
            statusFilter === 'all'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          }`}
        >
          Все ({tasks.length})
        </button>

        {Object.entries(taskStatuses).map(([status, info]) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              statusFilter === status
                ? `bg-${info.color}-500 text-white`
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {info.label} ({statusCounts[status] || 0})
          </button>
        ))}
      </div>

      {/* Список задач */}
      {filteredTasks.length > 0 ? (
        <div className="space-y-3">
          {filteredTasks.map((task) => {
            const statusInfo = getTaskStatus(task.status)
            const priorityInfo = getPriority(task.priority)
            const StatusIcon = statusInfo.icon

            return (
              <div
                key={task.id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`p-2 bg-${statusInfo.color}-100 dark:bg-${statusInfo.color}-900/20 rounded-lg mt-1`}>
                      <StatusIcon className={`w-5 h-5 text-${statusInfo.color}-600 dark:text-${statusInfo.color}-400`} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-base font-semibold text-gray-900 dark:text-white truncate">
                          {task.title}
                        </h3>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium bg-${priorityInfo.color}-100 text-${priorityInfo.color}-700 dark:bg-${priorityInfo.color}-900/30 dark:text-${priorityInfo.color}-400`}
                        >
                          {priorityInfo.label}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium bg-${statusInfo.color}-100 text-${statusInfo.color}-700 dark:bg-${statusInfo.color}-900/30 dark:text-${statusInfo.color}-400`}
                        >
                          {statusInfo.label}
                        </span>
                      </div>

                      {task.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                          {task.description}
                        </p>
                      )}

                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                        {task.assigned_to_name && (
                          <div className="flex items-center gap-1">
                            <User className="w-3 h-3" />
                            <span>{task.assigned_to_name}</span>
                          </div>
                        )}
                        {task.deadline && (
                          <div className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            <span>{new Date(task.deadline).toLocaleDateString('ru-RU')}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>Создана: {new Date(task.created_at).toLocaleDateString('ru-RU')}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <CheckSquare className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {statusFilter === 'all' ? 'Задачи не найдены' : 'Нет задач с таким статусом'}
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            {statusFilter === 'all'
              ? `Создайте первую задачу для проекта "${project.title}"`
              : 'Попробуйте изменить фильтр'}
          </p>
          {statusFilter === 'all' && (
            <button className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
              <Plus className="w-4 h-4" />
              <span>Создать задачу</span>
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default ProjectTasks
