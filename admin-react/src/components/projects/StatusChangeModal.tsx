import { useState, useEffect } from 'react'
import { X, AlertCircle } from 'lucide-react'

interface StatusChangeModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  currentStatus: string
  onStatusChanged: () => void
}

const STATUS_OPTIONS = [
  { value: 'new', label: '🆕 Новый', color: 'bg-blue-100 text-blue-800' },
  { value: 'review', label: '👀 На рассмотрении', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'accepted', label: '✅ Принят', color: 'bg-green-100 text-green-800' },
  { value: 'in_progress', label: '🔄 В работе', color: 'bg-purple-100 text-purple-800' },
  { value: 'testing', label: '🧪 Тестирование', color: 'bg-orange-100 text-orange-800' },
  { value: 'completed', label: '🎉 Завершен', color: 'bg-emerald-100 text-emerald-800' },
  { value: 'cancelled', label: '❌ Отменен', color: 'bg-red-100 text-red-800' },
  { value: 'on_hold', label: '⏸️ Приостановлен', color: 'bg-gray-100 text-gray-800' },
]

export const StatusChangeModal = ({
  isOpen,
  onClose,
  projectId,
  currentStatus,
  onStatusChanged,
}: StatusChangeModalProps) => {
  const [selectedStatus, setSelectedStatus] = useState('')
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      setSelectedStatus('')
      setComment('')
      setError('')
    }
  }, [isOpen])

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

  if (!isOpen || !projectId) return null

  const currentStatusData = STATUS_OPTIONS.find((s) => s.value === currentStatus)
  const availableStatuses = STATUS_OPTIONS.filter((s) => s.value !== currentStatus)

  const handleSubmit = async () => {
    if (!selectedStatus) {
      setError('Пожалуйста, выберите новый статус')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          status: selectedStatus,
          comment: comment || undefined,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        onStatusChanged()
        onClose()
      } else {
        setError(data.message || 'Ошибка изменения статуса')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold">Изменение статуса проекта</h3>
            <p className="text-purple-100 text-sm mt-1">Проект #{projectId}</p>
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
        <div className="p-6 space-y-6">
          {/* Current Status */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Текущий статус
            </label>
            <div className="flex items-center gap-2">
              {currentStatusData && (
                <span
                  className={`px-4 py-2 rounded-lg font-semibold text-sm ${currentStatusData.color}`}
                >
                  {currentStatusData.label}
                </span>
              )}
            </div>
          </div>

          {/* New Status Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Новый статус <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              {availableStatuses.map((status) => (
                <button
                  key={status.value}
                  type="button"
                  onClick={() => setSelectedStatus(status.value)}
                  className={`px-4 py-3 rounded-lg font-semibold text-sm transition-all border-2 ${
                    selectedStatus === status.value
                      ? 'border-purple-500 ring-2 ring-purple-200 ' + status.color
                      : 'border-gray-200 hover:border-purple-300 ' + status.color
                  }`}
                >
                  {status.label}
                </button>
              ))}
            </div>
          </div>

          {/* Comment */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Комментарий
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all resize-none"
              rows={4}
              placeholder="Добавьте комментарий к изменению статуса (необязательно)"
            />
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
            disabled={loading || !selectedStatus}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Сохранение...' : 'Изменить статус'}
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
