/**
 * Вкладка "Задачи" проекта
 * Список задач проекта с фильтрацией, созданием и комментариями
 */

import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import {
  CheckSquare, Plus, Loader2, Calendar, User, AlertCircle, Clock,
  CheckCircle2, XCircle, MessageSquare, Trash2, Send, X
} from 'lucide-react'
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
  assigned_to?: {
    id: number
    username: string
    first_name?: string
    last_name?: string
  }
  assigned_to_name?: string
  deadline?: string
  created_at: string
  comments_count?: number
  type?: string
}

interface TaskComment {
  id: number
  task_id: number
  comment: string
  created_at: string
  author?: {
    id: number
    username: string
    first_name?: string
    last_name?: string
  }
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
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [editForm, setEditForm] = useState({
    title: '',
    description: '',
    status: '',
    priority: '',
    deadline: '',
  })
  const [comments, setComments] = useState<TaskComment[]>([])
  const [newComment, setNewComment] = useState('')
  const [loadingComments, setLoadingComments] = useState(false)
  const [submittingComment, setSubmittingComment] = useState(false)

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
        title: createForm.title,
        description: createForm.description,
        priority: createForm.priority,
        deadline: createForm.deadline || null,
        status: 'pending',
      }

      // Автоматически назначаем задачу на исполнителя проекта, если он есть
      if (project.assigned_executor_id) {
        taskData.assigned_to_id = project.assigned_executor_id
      } else {
        // Если нет исполнителя, показываем ошибку
        setError('Невозможно создать задачу: не назначен исполнитель проекта')
        return
      }

      const response = await axiosInstance.post(`/admin/api/projects/${project.id}/tasks`, taskData)

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

  // Открытие модального окна задачи
  const handleOpenTask = async (task: Task) => {
    setSelectedTask(task)
    setEditForm({
      title: task.title,
      description: task.description || '',
      status: task.status,
      priority: task.priority,
      deadline: task.deadline ? task.deadline.split('T')[0] : '',
    })
    setShowTaskModal(true)

    // Загружаем комментарии
    await loadComments(task.id)
  }

  // Загрузка комментариев
  const loadComments = async (taskId: number) => {
    try {
      setLoadingComments(true)
      const response = await axiosInstance.get(`/admin/api/tasks/${taskId}/comments`)

      if (response.data.success) {
        setComments(response.data.comments || [])
      }
    } catch (err: any) {
      console.error('Error loading comments:', err)
    } finally {
      setLoadingComments(false)
    }
  }

  // Добавление комментария
  const handleAddComment = async () => {
    if (!selectedTask || !newComment.trim()) return

    try {
      setSubmittingComment(true)
      const response = await axiosInstance.post(`/admin/api/tasks/${selectedTask.id}/comments`, {
        comment: newComment.trim()
      })

      if (response.data.success) {
        setNewComment('')
        await loadComments(selectedTask.id)
      }
    } catch (err: any) {
      console.error('Error adding comment:', err)
      setError('Ошибка добавления комментария')
    } finally {
      setSubmittingComment(false)
    }
  }

  // Редактирование задачи
  const handleEditTask = async () => {
    if (!selectedTask) return

    try {
      const response = await axiosInstance.put(`/admin/api/tasks/${selectedTask.id}`, {
        title: editForm.title,
        description: editForm.description,
        status: editForm.status,
        priority: editForm.priority,
        deadline: editForm.deadline || null,
      })

      if (response.data.success) {
        loadTasks()
        // Обновляем данные выбранной задачи
        const updatedTask = response.data.task
        setSelectedTask(updatedTask)
      }
    } catch (err: any) {
      console.error('Error updating task:', err)
      setError('Ошибка обновления задачи')
    }
  }

  // Удаление задачи
  const handleDeleteTask = async () => {
    if (!selectedTask) return

    if (!confirm(`Вы уверены, что хотите удалить задачу "${selectedTask.title}"?`)) {
      return
    }

    try {
      const response = await axiosInstance.delete(`/admin/api/tasks/${selectedTask.id}`)

      if (response.data.success) {
        setShowTaskModal(false)
        setSelectedTask(null)
        loadTasks()
      }
    } catch (err: any) {
      console.error('Error deleting task:', err)
      setError('Ошибка удаления задачи')
    }
  }

  // Статусы задач
  const taskStatuses: Record<string, { label: string; color: string; icon: any }> = {
    pending: { label: 'Ожидает', color: 'gray', icon: Clock },
    new: { label: 'Новая', color: 'blue', icon: AlertCircle },
    in_progress: { label: 'В работе', color: 'yellow', icon: Clock },
    review: { label: 'На проверке', color: 'purple', icon: CheckSquare },
    completed: { label: 'Завершена', color: 'green', icon: CheckCircle2 },
    cancelled: { label: 'Отменена', color: 'red', icon: XCircle },
  }

  // Приоритеты
  const priorities: Record<string, { label: string; color: string }> = {
    low: { label: 'Низкий', color: 'gray' },
    normal: { label: 'Обычный', color: 'blue' },
    medium: { label: 'Средний', color: 'blue' },
    high: { label: 'Высокий', color: 'orange' },
    urgent: { label: 'Срочный', color: 'red' },
  }

  const getTaskStatus = (status: string) => {
    return taskStatuses[status] || taskStatuses.pending
  }

  const getPriority = (priority: string) => {
    return priorities[priority] || priorities.normal
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
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center justify-between">
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-red-400 hover:text-red-600"
          >
            <X className="w-4 h-4" />
          </button>
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
                ? 'bg-blue-500 text-white'
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
                onClick={() => handleOpenTask(task)}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`p-2 rounded-lg ${
                      statusInfo.color === 'green' ? 'bg-green-100 dark:bg-green-900/20' :
                      statusInfo.color === 'blue' ? 'bg-blue-100 dark:bg-blue-900/20' :
                      statusInfo.color === 'yellow' ? 'bg-yellow-100 dark:bg-yellow-900/20' :
                      statusInfo.color === 'purple' ? 'bg-purple-100 dark:bg-purple-900/20' :
                      statusInfo.color === 'red' ? 'bg-red-100 dark:bg-red-900/20' :
                      'bg-gray-100 dark:bg-gray-900/20'
                    } mt-1`}>
                      <StatusIcon className={`w-5 h-5 ${
                        statusInfo.color === 'green' ? 'text-green-600 dark:text-green-400' :
                        statusInfo.color === 'blue' ? 'text-blue-600 dark:text-blue-400' :
                        statusInfo.color === 'yellow' ? 'text-yellow-600 dark:text-yellow-400' :
                        statusInfo.color === 'purple' ? 'text-purple-600 dark:text-purple-400' :
                        statusInfo.color === 'red' ? 'text-red-600 dark:text-red-400' :
                        'text-gray-600 dark:text-gray-400'
                      }`} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                          {task.title}
                        </h3>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            priorityInfo.color === 'red' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                            priorityInfo.color === 'orange' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' :
                            priorityInfo.color === 'blue' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                            'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'
                          }`}
                        >
                          {priorityInfo.label}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            statusInfo.color === 'green' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                            statusInfo.color === 'blue' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                            statusInfo.color === 'yellow' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                            statusInfo.color === 'purple' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400' :
                            statusInfo.color === 'red' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                            'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'
                          }`}
                        >
                          {statusInfo.label}
                        </span>
                      </div>

                      {task.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                          {task.description}
                        </p>
                      )}

                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 flex-wrap">
                        {(task.assigned_to?.first_name || task.assigned_to?.username || task.assigned_to_name) && (
                          <div className="flex items-center gap-1">
                            <User className="w-3 h-3" />
                            <span>{task.assigned_to?.first_name || task.assigned_to?.username || task.assigned_to_name}</span>
                          </div>
                        )}
                        {task.deadline && (
                          <div className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            <span>{new Date(task.deadline).toLocaleDateString('ru-RU')}</span>
                          </div>
                        )}
                        {task.comments_count !== undefined && task.comments_count > 0 && (
                          <div className="flex items-center gap-1">
                            <MessageSquare className="w-3 h-3" />
                            <span>{task.comments_count} {task.comments_count === 1 ? 'комментарий' : 'комментария'}</span>
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
                    <option value="normal">Обычный</option>
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

      {/* Модальное окно просмотра/редактирования задачи с комментариями */}
      {showTaskModal && selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Заголовок */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Редактировать задачу</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Проект: {project.title}
                </p>
              </div>
              <button
                onClick={handleDeleteTask}
                className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                title="Удалить задачу"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>

            {/* Контент */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-6 space-y-6">
                {/* Форма редактирования */}
                <div className="space-y-4">
                  {/* Название */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Название задачи *
                    </label>
                    <input
                      type="text"
                      value={editForm.title}
                      onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                      onBlur={handleEditTask}
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
                      onBlur={handleEditTask}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Опишите задачу..."
                    />
                  </div>

                  {/* Статус, Приоритет, Дедлайн */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Статус
                      </label>
                      <select
                        value={editForm.status}
                        onChange={(e) => {
                          setEditForm({ ...editForm, status: e.target.value })
                          handleEditTask()
                        }}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="pending">Ожидает</option>
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
                        onChange={(e) => {
                          setEditForm({ ...editForm, priority: e.target.value })
                          handleEditTask()
                        }}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="low">Низкий</option>
                        <option value="normal">Обычный</option>
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
                        value={editForm.deadline}
                        onChange={(e) => setEditForm({ ...editForm, deadline: e.target.value })}
                        onBlur={handleEditTask}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                {/* Комментарии */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5" />
                    Комментарии ({comments.length})
                  </h4>

                  {/* Список комментариев */}
                  <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                    {loadingComments ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
                      </div>
                    ) : comments.length > 0 ? (
                      comments.map((comment) => (
                        <div
                          key={comment.id}
                          className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                <span className="text-white text-sm font-medium">
                                  {(comment.author?.first_name || comment.author?.username || 'U')[0].toUpperCase()}
                                </span>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-white">
                                  {comment.author?.first_name || comment.author?.username || 'Пользователь'}
                                </p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                  {new Date(comment.created_at).toLocaleString('ru-RU')}
                                </p>
                              </div>
                            </div>
                          </div>
                          <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                            {comment.comment}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                        Комментариев пока нет
                      </p>
                    )}
                  </div>

                  {/* Добавление комментария */}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddComment()}
                      placeholder="Добавить комментарий..."
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                      onClick={handleAddComment}
                      disabled={!newComment.trim() || submittingComment}
                      className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {submittingComment ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Подвал */}
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex items-center justify-end gap-3">
              <button
                onClick={() => {
                  setShowTaskModal(false)
                  setSelectedTask(null)
                  setComments([])
                  setNewComment('')
                }}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectTasks
