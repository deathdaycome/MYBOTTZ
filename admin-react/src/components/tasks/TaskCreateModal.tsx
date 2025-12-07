import { useState, useEffect } from 'react'
import { X, Plus } from 'lucide-react'
import tasksApi from '../../api/tasks'
import type { CreateTaskData } from '../../api/tasks'
import { TagInput } from './TaskTags'

interface Employee {
  id: number
  name: string
  username: string
  role: string
}

interface TaskCreateModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  employees: Employee[]
}

export const TaskCreateModal = ({ isOpen, onClose, onSuccess, employees }: TaskCreateModalProps) => {
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<{ title?: string; assigned_to?: string }>({})

  const [formData, setFormData] = useState<CreateTaskData>({
    title: '',
    description: '',
    assigned_to_id: 0,
    priority: 'normal',
    deadline: '',
    estimated_hours: undefined,
    color: 'normal',
    tags: [],
    created_by_admin: true,
  })

  // Suggested tags
  const suggestedTags = [
    'bug', 'feature', 'urgent', 'design', 'backend', 'frontend',
    'mobile', 'security', 'testing', 'devops', 'api', 'database'
  ]

  useEffect(() => {
    if (isOpen) {
      // Выбираем первого исполнителя, если есть
      const firstExecutorId = employees.length > 0 ? employees[0].id : 0

      // Reset form on open
      setFormData({
        title: '',
        description: '',
        assigned_to_id: firstExecutorId,
        priority: 'normal',
        deadline: '',
        estimated_hours: undefined,
        color: 'normal',
        tags: [],
        created_by_admin: true,
      })
      setErrors({})

      // Если нет исполнителей, показываем предупреждение
      if (employees.length === 0) {
        setErrors({ assigned_to: 'Нет доступных исполнителей. Добавьте исполнителей в системе.' })
      }
    }
  }, [isOpen, employees])

  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'

      // Scroll modal to top when opened
      setTimeout(() => {
        const modalContent = document.querySelector('.task-create-modal-content')
        if (modalContent) {
          modalContent.scrollTop = 0
        }
      }, 0)
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

    // Валидация
    const newErrors: { title?: string; assigned_to?: string } = {}

    if (!formData.title.trim()) {
      newErrors.title = 'Введите название задачи'
    }

    if (!formData.assigned_to_id || formData.assigned_to_id === 0) {
      newErrors.assigned_to = 'Выберите исполнителя'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      // Прокрутить форму к верху, чтобы показать ошибки
      const modalContent = document.querySelector('.task-create-modal-content')
      if (modalContent) {
        modalContent.scrollTo({ top: 0, behavior: 'smooth' })
      }
      return
    }

    try {
      setLoading(true)
      setErrors({})
      const response = await tasksApi.createTask(formData)

      if (response.success) {
        onSuccess()
        onClose()
      } else {
        alert(`Ошибка: ${response.message || 'Неизвестная ошибка'}`)
      }
    } catch (error: any) {
      console.error('Ошибка при создании задачи:', error)
      alert(`Ошибка создания задачи: ${error.response?.data?.error || error.message || 'Неизвестная ошибка'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof CreateTaskData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="task-create-modal-content bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Plus className="w-6 h-6" />
            <h3 className="text-xl font-bold">Создать задачу</h3>
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
          {/* Error Banner */}
          {Object.keys(errors).length > 0 && (
            <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4">
              <p className="text-sm font-semibold text-red-800">
                Пожалуйста, исправьте ошибки в форме:
              </p>
              <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
                {errors.title && <li>{errors.title}</li>}
                {errors.assigned_to && <li>{errors.assigned_to}</li>}
              </ul>
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Название задачи <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => {
                handleChange('title', e.target.value)
                if (errors.title) setErrors({ ...errors, title: undefined })
              }}
              className={`w-full px-4 py-3 border-2 rounded-lg outline-none transition-all ${
                errors.title
                  ? 'border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                  : 'border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200'
              }`}
              placeholder="Введите название задачи"
              required
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600 font-medium">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Описание</label>
            <textarea
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all resize-none"
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

          {/* Assigned to */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Исполнитель <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.assigned_to_id}
              onChange={(e) => {
                handleChange('assigned_to_id', parseInt(e.target.value))
                if (errors.assigned_to) setErrors({ ...errors, assigned_to: undefined })
              }}
              className={`w-full px-4 py-3 border-2 rounded-lg outline-none transition-all ${
                errors.assigned_to
                  ? 'border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                  : 'border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200'
              }`}
              required
            >
              <option value={0}>Выберите исполнителя</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.name} (@{emp.username})
                </option>
              ))}
            </select>
            {errors.assigned_to && (
              <p className="mt-1 text-sm text-red-600 font-medium">{errors.assigned_to}</p>
            )}
          </div>

          {/* Priority and Color */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Приоритет</label>
              <select
                value={formData.priority}
                onChange={(e) => handleChange('priority', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
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
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
              >
                <option value="normal">Без метки</option>
                <option value="red">🔴 Красная</option>
                <option value="yellow">🟡 Желтая</option>
                <option value="green">🟢 Зеленая</option>
              </select>
            </div>
          </div>

          {/* Deadline and Estimated Hours */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Дедлайн</label>
              <input
                type="datetime-local"
                value={formData.deadline}
                onChange={(e) => handleChange('deadline', e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
              />
            </div>

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
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                placeholder="0"
              />
            </div>
          </div>

          {/* Info */}
          <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              <span className="font-semibold">ℹ️ Информация:</span> После создания задачи исполнитель получит уведомление.
            </p>
          </div>

          {/* Footer */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              ) : (
                <>
                  <Plus className="w-5 h-5" />
                  Создать задачу
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
