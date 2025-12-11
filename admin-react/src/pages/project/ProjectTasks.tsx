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
  assigned_executor_id?: number
  assigned_executor?: {
    id: number
    username: string
    first_name?: string
    last_name?: string
  }
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
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    priority: 'medium',
    deadline: '',
  })
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [editForm, setEditForm] = useState({
    title: '',
    description: '',
    status: '',
    priority: '',
    deadline: '',
  })

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

  // Создание задачи
  const handleCreateTask = async () => {
    try {
      const taskData: any = {
        project_id: project.id,
        title: createForm.title,
        description: createForm.description,
        priority: createForm.priority,
        deadline: createForm.deadline || null,
        status: 'new',
        type: 'TASK',
      }

      // Автоматически назначаем задачу на исполнителя проекта, если он есть
      if (project.assigned_executor_id) {
        taskData.assigned_to_id = project.assigned_executor_id
      }

      const response = await axiosInstance.post('/admin/api/tasks', taskData)

      if (response.data.success) {
        setShowCreateModal(false)
        setCreateForm({ title: '', description: '', priority: 'medium', deadline: '' })
        loadTasks()
      }
    } catch (err: any) {
      console.error('Error creating task:', err)
      setError('Ошибка создания задачи')
    }
  }

  // Открытие модального окна редактирования
  const handleOpenEdit = (task: Task) => {
    setEditingTask(task)
    setEditForm({
      title: task.title,
      description: task.description || '',
      status: task.status,
      priority: task.priority,
      deadline: task.deadline || '',
    })
    setShowEditModal(true)
  }

  // Редактирование задачи
  const handleEditTask = async () => {
    if (!editingTask) return

    try {
      const response = await axiosInstance.put(`/admin/api/tasks/${editingTask.id}`, {
        title: editForm.title,
        description: editForm.description,
        status: editForm.status,
        priority: editForm.priority,
        deadline: editForm.deadline || null,
      })

      if (response.data.success) {
        setShowEditModal(false)
        setEditingTask(null)
        setEditForm({ title: '', description: '', status: '', priority: '', deadline: '' })
        loadTasks()
      }
    } catch (err: any) {
      console.error('Error updating task:', err)
      setError('Ошибка обновления задачи')
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
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
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
                onClick={() => handleOpenEdit(task)}
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
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Создать задачу</span>
            </button>
          )}
        </div>
      )}

      {/* Модальное окно создания задачи */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">Создать задачу</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Проект: {project.title}
              </p>
            </div>

            <div className="p-6 space-y-4">
              {/* Название */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Название задачи *
                </label>
                <input
                  type="text"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Введите название задачи"
                />
              </div>

              {/* Описание */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Описание
                </label>
                <textarea
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Опишите задачу..."
                />
              </div>

              {/* Приоритет и Дедлайн */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Приоритет
                  </label>
                  <select
                    value={createForm.priority}
                    onChange={(e) => setCreateForm({ ...createForm, priority: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Низкий</option>
                    <option value="medium">Средний</option>
                    <option value="high">Высокий</option>
                    <option value="urgent">Срочный</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Дедлайн
                  </label>
                  <input
                    type="date"
                    value={createForm.deadline}
                    onChange={(e) => setCreateForm({ ...createForm, deadline: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex items-center justify-end gap-3">
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setCreateForm({ title: '', description: '', priority: 'medium', deadline: '' })
                }}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateTask}
                disabled={!createForm.title.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Создать задачу
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно редактирования задачи */}
      {showEditModal && editingTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">Редактировать задачу</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Проект: {project.title}
              </p>
            </div>

            <div className="p-6 space-y-4">
              {/* Название */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Название задачи *
                </label>
                <input
                  type="text"
                  value={editForm.title}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Введите название задачи"
                />
              </div>

              {/* Описание */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Описание
                </label>
                <textarea
                  value={editForm.description}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Опишите задачу..."
                />
              </div>

              {/* Статус и Приоритет */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Статус
                  </label>
                  <select
                    value={editForm.status}
                    onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="new">Новая</option>
                    <option value="in_progress">В работе</option>
                    <option value="review">На проверке</option>
                    <option value="completed">Завершена</option>
                    <option value="cancelled">Отменена</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Приоритет
                  </label>
                  <select
                    value={editForm.priority}
                    onChange={(e) => setEditForm({ ...editForm, priority: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Низкий</option>
                    <option value="medium">Средний</option>
                    <option value="high">Высокий</option>
                    <option value="urgent">Срочный</option>
                  </select>
                </div>
              </div>

              {/* Дедлайн */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Дедлайн
                </label>
                <input
                  type="date"
                  value={editForm.deadline}
                  onChange={(e) => setEditForm({ ...editForm, deadline: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex items-center justify-end gap-3">
              <button
                onClick={() => {
                  setShowEditModal(false)
                  setEditingTask(null)
                  setEditForm({ title: '', description: '', status: '', priority: '', deadline: '' })
                }}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleEditTask}
                disabled={!editForm.title.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Сохранить изменения
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectTasks
