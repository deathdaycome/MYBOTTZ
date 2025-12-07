import { useState, useEffect, useCallback } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import tasksArchiveApi from '../api/tasksArchive'
import type { TasksByDate, ArchivedTasksFilters, ArchivedTask, Employee } from '../api/tasksArchive'

interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

export const TasksArchive = () => {
  const { currentTheme } = useTheme()

  // ============= STATE =============
  const [tasksByDate, setTasksByDate] = useState<TasksByDate>({})
  const [totalTasks, setTotalTasks] = useState(0)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<ArchivedTasksFilters>({})
  const [employees, setEmployees] = useState<Employee[]>([])
  const [toasts, setToasts] = useState<Toast[]>([])

  // ============= TOAST NOTIFICATIONS =============
  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 3000)
  }, [])

  // ============= DATA LOADING =============
  const loadArchivedTasks = useCallback(async () => {
    try {
      setLoading(true)
      const response = await tasksArchiveApi.getArchivedTasks(filters)

      if (response.success) {
        setTasksByDate(response.tasks_by_date)
        setTotalTasks(response.total_tasks)
      } else {
        showToast(response.message || 'Ошибка загрузки архивных задач', 'error')
      }
    } catch (error) {
      console.error('Error loading archived tasks:', error)
      showToast('Ошибка загрузки архивных задач', 'error')
    } finally {
      setLoading(false)
    }
  }, [filters, showToast])

  const loadEmployees = useCallback(async () => {
    try {
      const response = await tasksArchiveApi.getEmployees()
      if (response.success) {
        setEmployees(response.employees)
      }
    } catch (error) {
      console.error('Error loading employees:', error)
    }
  }, [])

  useEffect(() => {
    loadArchivedTasks()
  }, [loadArchivedTasks])

  useEffect(() => {
    loadEmployees()
  }, [loadEmployees])

  // ============= HANDLERS =============
  const handleRestoreTask = async (taskId: number) => {
    if (!confirm('Вы уверены, что хотите восстановить эту задачу из архива?')) {
      return
    }

    try {
      const response = await tasksArchiveApi.restoreTask(taskId)

      if (response.success) {
        showToast('Задача успешно восстановлена', 'success')
        // Обновляем список
        await loadArchivedTasks()
      } else {
        showToast(response.message || 'Ошибка восстановления задачи', 'error')
      }
    } catch (error) {
      console.error('Error restoring task:', error)
      showToast('Ошибка восстановления задачи', 'error')
    }
  }

  const handleApplyFilters = () => {
    loadArchivedTasks()
  }

  const handleResetFilters = () => {
    setFilters({})
  }

  // ============= HELPERS =============
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня'
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Вчера'
    } else {
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    }
  }

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'normal': return 'bg-blue-100 text-blue-800'
      case 'low': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityLabel = (priority: string): string => {
    const labels: Record<string, string> = {
      urgent: 'Срочно',
      high: 'Высокий',
      normal: 'Обычный',
      low: 'Низкий'
    }
    return labels[priority] || priority
  }

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      completed: 'Завершена',
      in_progress: 'В работе',
      pending: 'Ожидает'
    }
    return labels[status] || status
  }

  // ============= RENDER =============
  const sortedDates = Object.keys(tasksByDate || {}).sort((a, b) =>
    new Date(b).getTime() - new Date(a).getTime()
  )

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-6`}>
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className={`text-3xl font-bold ${currentTheme.text}`}>Архив задач</h1>
            <p className="text-gray-500 mt-1">Всего в архиве: {totalTasks} задач</p>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className={`block text-sm font-medium ${currentTheme.text} mb-2`}>
              Сотрудник
            </label>
            <select
              value={filters.employee_id || ''}
              onChange={(e) => setFilters({ ...filters, employee_id: e.target.value ? parseInt(e.target.value) : undefined })}
              className={`w-full px-3 py-2 border ${currentTheme.border} rounded-lg ${currentTheme.input} ${currentTheme.text}`}
            >
              <option value="">Все сотрудники</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.first_name} {emp.last_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className={`block text-sm font-medium ${currentTheme.text} mb-2`}>
              Дата от
            </label>
            <input
              type="date"
              value={filters.date_from || ''}
              onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
              className={`w-full px-3 py-2 border ${currentTheme.border} rounded-lg ${currentTheme.input} ${currentTheme.text}`}
            />
          </div>

          <div>
            <label className={`block text-sm font-medium ${currentTheme.text} mb-2`}>
              Дата до
            </label>
            <input
              type="date"
              value={filters.date_to || ''}
              onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
              className={`w-full px-3 py-2 border ${currentTheme.border} rounded-lg ${currentTheme.input} ${currentTheme.text}`}
            />
          </div>

          <div className="flex items-end gap-2">
            <button
              onClick={handleApplyFilters}
              className={`px-4 py-2 rounded-lg ${currentTheme.primary} text-white hover:opacity-90`}
            >
              Применить
            </button>
            <button
              onClick={handleResetFilters}
              className={`px-4 py-2 rounded-lg border ${currentTheme.border} ${currentTheme.text} hover:bg-gray-50`}
            >
              Сбросить
            </button>
          </div>
        </div>
      </div>

      {/* Tasks */}
      {loading ? (
        <div className="text-center py-12">
          <div className={`inline-block animate-spin rounded-full h-12 w-12 border-b-2 ${currentTheme.primary}`}></div>
          <p className={`mt-4 ${currentTheme.text}`}>Загрузка архивных задач...</p>
        </div>
      ) : sortedDates.length === 0 ? (
        <div className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-12 text-center`}>
          <div className="text-gray-400 text-6xl mb-4">📋</div>
          <h3 className={`text-xl font-semibold ${currentTheme.text} mb-2`}>Архив пуст</h3>
          <p className="text-gray-500">Здесь будут отображаться завершенные и архивированные задачи</p>
        </div>
      ) : (
        <div className="space-y-6">
          {sortedDates.map((dateKey) => {
            const employeeGroups = tasksByDate[dateKey] || {}
            const totalTasksForDate = Object.values(employeeGroups).reduce(
              (sum, group) => sum + group.tasks.length,
              0
            )

            return (
              <div
                key={dateKey}
                className={`${currentTheme.card} ${currentTheme.border} border rounded-lg p-6`}
              >
                {/* Date Header */}
                <div className="flex items-center justify-between mb-6 pb-4 border-b">
                  <div className="flex items-center gap-3">
                    <div className="text-2xl">📅</div>
                    <div>
                      <h2 className={`text-xl font-bold ${currentTheme.text}`}>
                        {formatDate(dateKey)}
                      </h2>
                      <p className="text-sm text-gray-500">
                        {new Date(dateKey).toLocaleDateString('ru-RU', { weekday: 'long' })}
                      </p>
                    </div>
                  </div>
                  <div className={`px-4 py-2 rounded-full ${currentTheme.primary} text-white font-semibold`}>
                    {totalTasksForDate} {totalTasksForDate === 1 ? 'задача' : 'задач'}
                  </div>
                </div>

                {/* Employee Groups */}
                <div className="space-y-6">
                  {Object.entries(employeeGroups).map(([employeeKey, group]) => {
                    const employee = group.employee
                    const tasks = group.tasks

                    return (
                      <div key={employeeKey} className="space-y-4">
                        {/* Employee Header */}
                        {employee && (
                          <div className={`flex items-center gap-3 p-3 rounded-lg ${currentTheme.hover}`}>
                            <div className={`w-10 h-10 rounded-full ${currentTheme.primary} text-white flex items-center justify-center font-semibold`}>
                              {employee.first_name?.[0] || employee.username[0].toUpperCase()}
                            </div>
                            <div className="flex-1">
                              <div className={`font-semibold ${currentTheme.text}`}>
                                {employee.first_name} {employee.last_name}
                              </div>
                              <div className="text-sm text-gray-500">@{employee.username}</div>
                            </div>
                            <div className={`px-3 py-1 rounded-full ${currentTheme.primary} text-white text-sm`}>
                              {tasks.length} {tasks.length === 1 ? 'задача' : 'задач'}
                            </div>
                          </div>
                        )}

                        {/* Tasks Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {tasks.map((task: ArchivedTask) => (
                            <div
                              key={task.id}
                              className={`${currentTheme.card} border-l-4 border-green-500 p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow`}
                            >
                              <h3 className={`font-semibold ${currentTheme.text} mb-2`}>
                                {task.title}
                              </h3>

                              {task.description && (
                                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                                  {task.description}
                                </p>
                              )}

                              <div className="flex flex-wrap gap-2 mb-3">
                                <span className={`px-2 py-1 rounded text-xs ${getStatusColor(task.status)}`}>
                                  {getStatusLabel(task.status)}
                                </span>
                                <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(task.priority)}`}>
                                  {getPriorityLabel(task.priority)}
                                </span>
                              </div>

                              {task.completed_at && (
                                <div className="text-xs text-gray-500 mb-3">
                                  Завершена: {new Date(task.completed_at).toLocaleString('ru-RU')}
                                </div>
                              )}

                              <button
                                onClick={() => handleRestoreTask(task.id)}
                                className="w-full px-3 py-2 rounded bg-blue-600 text-white text-sm hover:bg-blue-700"
                              >
                                Восстановить
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Toast Notifications */}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-6 py-3 rounded-lg shadow-lg text-white ${
              toast.type === 'success' ? 'bg-green-600' :
              toast.type === 'error' ? 'bg-red-600' :
              'bg-blue-600'
            }`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  )
}
