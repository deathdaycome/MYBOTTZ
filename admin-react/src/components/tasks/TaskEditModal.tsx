import { useState, useEffect } from 'react'
import { X, Save, ExternalLink } from 'lucide-react'
import tasksApi from '../../api/tasks'
import type { Task, UpdateTaskData } from '../../api/tasks'
import { TagInput } from './TaskTags'

interface Employee {
  id: number
  name: string
  username: string
  role: string
}

interface TaskEditModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  task: Task
  employees: Employee[]
}

export const TaskEditModal = ({ isOpen, onClose, onSuccess, task, employees }: TaskEditModalProps) => {
  const [loading, setLoading] = useState(false)

  const [formData, setFormData] = useState<UpdateTaskData>({
    title: task.title,
    description: task.description,
    status: task.status,
    priority: task.priority,
    deadline: task.deadline || '',
    estimated_hours: task.estimated_hours,
    actual_hours: task.actual_hours,
    assigned_to_id: task.assigned_to_id,
    color: task.color || 'normal',
    tags: task.tags || [],
  })
  const [deployUrl, setDeployUrl] = useState(task.deploy_url || '')

  // Suggested tags
  const suggestedTags = [
    'bug', 'feature', 'urgent', 'design', 'backend', 'frontend',
    'mobile', 'security', 'testing', 'devops', 'api', 'database'
  ]

  useEffect(() => {
    if (isOpen) {
      // Update form data when task changes
      setFormData({
        title: task.title,
        description: task.description,
        status: task.status,
        priority: task.priority,
        deadline: task.deadline ? task.deadline.split('.')[0] : '',
        estimated_hours: task.estimated_hours,
        actual_hours: task.actual_hours,
        assigned_to_id: task.assigned_to_id,
        color: task.color || 'normal',
        tags: task.tags || [],
      })
      setDeployUrl(task.deploy_url || '')
    }
  }, [isOpen, task])

  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }, [isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title?.trim()) {
      alert('Введите название задачи')
      return
    }

    try {
      setLoading(true)
      const updateData = {
        ...formData,
        deploy_url: deployUrl || undefined,
      }
      const response = await tasksApi.updateTask(task.id, updateData)

      if (response.success) {
        onSuccess()
      }
    } catch (error) {
      console.error('Error updating task:', error)
      alert('Ошибка обновления задачи')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof UpdateTaskData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <Save className="w-6 h-6" />
            <h3 className="text-xl font-bold">Редактировать задачу</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Название задачи <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="Введите название задачи"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Описание</label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all resize-none"
              placeholder="Введите описание задачи"
            />
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Теги</label>
            <TagInput
              value={formData.tags || []}
              onChange={(tags) => handleChange('tags', tags)}
              suggestions={suggestedTags}
            />
          </div>

          {/* Status and Assigned to */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Статус</label>
              <select
                value={formData.status}
                onChange={(e) => handleChange('status', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              >
                <option value="pending">Новая</option>
                <option value="in_progress">В работе</option>
                <option value="completed">Завершена</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Исполнитель</label>
              <select
                value={formData.assigned_to_id}
                onChange={(e) => handleChange('assigned_to_id', parseInt(e.target.value))}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              >
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name} (@{emp.username})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Priority and Color */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Приоритет</label>
              <select
                value={formData.priority}
                onChange={(e) => handleChange('priority', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              >
                <option value="low">Низкий</option>
                <option value="normal">Обычный</option>
                <option value="high">Высокий</option>
                <option value="urgent">Срочный</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Цветовая метка</label>
              <select
                value={formData.color}
                onChange={(e) => handleChange('color', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              >
                <option value="normal">Без метки</option>
                <option value="red">🔴 Красная</option>
                <option value="yellow">🟡 Желтая</option>
                <option value="green">🟢 Зеленая</option>
              </select>
            </div>
          </div>

          {/* Deadline */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Дедлайн</label>
            <input
              type="datetime-local"
              value={formData.deadline}
              onChange={(e) => handleChange('deadline', e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
            />
          </div>

          {/* Deploy URL */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <ExternalLink className="w-4 h-4 text-blue-500" />
              Ссылка на деплой
            </label>
            <input
              type="url"
              value={deployUrl}
              onChange={(e) => setDeployUrl(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="https://example.com/app"
            />
            <p className="text-xs text-gray-500 mt-1">
              Добавьте ссылку на задеплоенное приложение для отслеживания прогресса
            </p>
          </div>

          {/* Estimated and Actual Hours */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Оценка времени (часы)
              </label>
              <input
                type="number"
                value={formData.estimated_hours || ''}
                onChange={(e) =>
                  handleChange('estimated_hours', e.target.value ? parseFloat(e.target.value) : undefined)
                }
                min="0"
                step="0.5"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                placeholder="0"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Фактическое время (часы)
              </label>
              <input
                type="number"
                value={formData.actual_hours || ''}
                onChange={(e) =>
                  handleChange('actual_hours', e.target.value ? parseFloat(e.target.value) : undefined)
                }
                min="0"
                step="0.5"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                placeholder="0"
              />
            </div>
          </div>

          {/* Footer */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Сохранить изменения
                </>
              )}
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold disabled:opacity-50"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
