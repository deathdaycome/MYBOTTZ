import { useState, useEffect } from 'react'
import { X, CheckCircle, AlertCircle } from 'lucide-react'
import { apiService } from '../../services/api'

interface ProjectStatusModalProps {
  projectId: number | null
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export const ProjectStatusModal = ({
  projectId,
  isOpen,
  onClose,
  onSuccess,
}: ProjectStatusModalProps) => {
  const [status, setStatus] = useState('new')
  const [loading, setLoading] = useState(false)
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const statusOptions = [
    { value: 'new', label: 'Новый' },
    { value: 'review', label: 'На рассмотрении' },
    { value: 'accepted', label: 'Принят' },
    { value: 'in_progress', label: 'В работе' },
    { value: 'testing', label: 'Тестирование' },
    { value: 'completed', label: 'Завершен' },
    { value: 'cancelled', label: 'Отменен' },
  ]

  useEffect(() => {
    if (!isOpen) {
      setStatus('new')
      setAlert(null)
    }
  }, [isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!projectId) return

    setLoading(true)
    setAlert(null)

    try {
      const response = await apiService.updateProjectStatus(projectId, status)

      if (response.success) {
        setAlert({ type: 'success', message: 'Статус обновлен!' })

        setTimeout(() => {
          onClose()
          if (onSuccess) {
            onSuccess()
          }
        }, 1000)
      } else {
        setAlert({ type: 'error', message: 'Ошибка обновления статуса' })
      }
    } catch (error: any) {
      setAlert({ type: 'error', message: error.message || 'Ошибка обновления статуса' })
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4 flex items-center justify-between">
          <h3 className="text-xl font-bold text-white">Изменить статус проекта</h3>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Новый статус:
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              required
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Alert */}
          {alert && (
            <div
              className={`flex items-center gap-2 px-4 py-3 rounded-xl ${
                alert.type === 'success'
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}
            >
              {alert.type === 'success' ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <AlertCircle className="w-5 h-5" />
              )}
              <span className="font-medium text-sm">{alert.message}</span>
            </div>
          )}

          {/* Footer */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Сохранение...
                </>
              ) : (
                'Сохранить'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
