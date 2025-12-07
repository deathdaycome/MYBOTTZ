import { useState, useEffect } from 'react'
import { X, Save, AlertCircle, Zap } from 'lucide-react'

interface QuickEditModalProps {
  isOpen: boolean
  onClose: () => void
  project: any | null
  onSaved: () => void
}

export const QuickEditModal = ({ isOpen, onClose, project, onSaved }: QuickEditModalProps) => {
  const [formData, setFormData] = useState({
    name: '',
    status: '',
    project_cost: 0,
    executor_cost: 0,
    deadline: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen && project) {
      setFormData({
        name: project.name || '',
        status: project.status || '',
        project_cost: project.project_cost || 0,
        executor_cost: project.executor_cost || 0,
        deadline: project.deadline ? project.deadline.split('T')[0] : '',
      })
      setError('')
    }
  }, [isOpen, project])

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

  const handleSubmit = async () => {
    if (!project) return

    if (!formData.name.trim()) {
      setError('Введите название проекта')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${project.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        onSaved()
        onClose()
      } else {
        const data = await response.json()
        setError(data.message || 'Ошибка сохранения')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen || !project) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-yellow-600 to-orange-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Быстрое редактирование</h3>
              <p className="text-yellow-100 text-sm mt-1">Проект #{project.id}</p>
            </div>
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
        <div className="p-6 space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Название <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 outline-none transition-all"
              placeholder="Название проекта"
            />
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Статус</label>
            <input
              type="text"
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 outline-none transition-all"
              placeholder="Статус проекта"
            />
          </div>

          {/* Costs */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Стоимость проекта (₽)
              </label>
              <input
                type="number"
                value={formData.project_cost}
                onChange={(e) =>
                  setFormData({ ...formData, project_cost: Number(e.target.value) || 0 })
                }
                min="0"
                step="100"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Стоимость исполнителю (₽)
              </label>
              <input
                type="number"
                value={formData.executor_cost}
                onChange={(e) =>
                  setFormData({ ...formData, executor_cost: Number(e.target.value) || 0 })
                }
                min="0"
                step="100"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 outline-none transition-all"
              />
            </div>
          </div>

          {/* Deadline */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Дедлайн</label>
            <input
              type="date"
              value={formData.deadline}
              onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-yellow-500 focus:ring-2 focus:ring-yellow-200 outline-none transition-all"
            />
          </div>

          {/* Profit Preview */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-700">Прогнозируемая прибыль:</span>
              <span className="text-2xl font-bold text-green-600">
                {(formData.project_cost - formData.executor_cost).toLocaleString('ru-RU')} ₽
              </span>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-2 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading || !formData.name.trim()}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-lg hover:from-yellow-700 hover:to-orange-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-5 h-5" />
            {loading ? 'Сохранение...' : 'Сохранить'}
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
      </div>
    </div>
  )
}
