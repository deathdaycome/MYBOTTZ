import { useState, useEffect } from 'react'
import { X, AlertCircle, Users } from 'lucide-react'
import { apiService } from '../../services/api'

interface AssignExecutorModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  currentExecutor?: { id: number; first_name: string } | null
  currentCost?: number
  onAssigned: () => void
}

interface Executor {
  id: number
  first_name?: string
  full_name?: string
  username?: string
  role?: string
}

export const AssignExecutorModal = ({
  isOpen,
  onClose,
  projectId,
  currentExecutor,
  currentCost = 0,
  onAssigned,
}: AssignExecutorModalProps) => {
  const [executors, setExecutors] = useState<Executor[]>([])
  const [selectedExecutorId, setSelectedExecutorId] = useState<number | null>(null)
  const [executorCost, setExecutorCost] = useState<number>(0)
  const [loading, setLoading] = useState(false)
  const [loadingExecutors, setLoadingExecutors] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      setSelectedExecutorId(currentExecutor?.id || null)
      setExecutorCost(currentCost || 0)
      setError('')
      loadExecutors()
    }
  }, [isOpen, currentExecutor, currentCost])

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

  const loadExecutors = async () => {
    setLoadingExecutors(true)
    try {
      const data = await apiService.getExecutors()
      const executorsList = data.executors || data.users || []
      setExecutors(executorsList)
    } catch (err) {
      setError('Ошибка загрузки исполнителей')
    } finally {
      setLoadingExecutors(false)
    }
  }

  const handleSubmit = async () => {
    if (!selectedExecutorId) {
      setError('Пожалуйста, выберите исполнителя')
      return
    }

    if (!projectId) {
      setError('Не указан ID проекта')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(`/admin/api/projects/${projectId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:admin123'),
        },
        body: JSON.stringify({
          assigned_executor_id: selectedExecutorId,
          executor_cost: executorCost || 0,
        }),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        onAssigned()
        onClose()
      } else {
        setError(data.message || 'Ошибка назначения исполнителя')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen || !projectId) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Назначение исполнителя</h3>
              <p className="text-indigo-100 text-sm mt-1">Проект #{projectId}</p>
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
        <div className="p-6 space-y-6">
          {/* Current Executor Info */}
          {currentExecutor && (
            <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
              <p className="text-sm text-blue-900">
                <span className="font-semibold">Текущий исполнитель:</span>{' '}
                {currentExecutor.first_name}
              </p>
              {currentCost > 0 && (
                <p className="text-sm text-blue-900 mt-1">
                  <span className="font-semibold">Текущая стоимость:</span>{' '}
                  {currentCost.toLocaleString('ru-RU')} ₽
                </p>
              )}
            </div>
          )}

          {/* Executor Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Выберите исполнителя <span className="text-red-500">*</span>
            </label>
            {loadingExecutors ? (
              <div className="px-4 py-3 border-2 border-gray-200 rounded-lg text-gray-500 text-sm">
                Загрузка исполнителей...
              </div>
            ) : (
              <select
                value={selectedExecutorId || ''}
                onChange={(e) => setSelectedExecutorId(Number(e.target.value) || null)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              >
                <option value="">Выберите исполнителя...</option>
                {executors.map((executor) => {
                  const name =
                    executor.first_name || executor.full_name || executor.username || 'Без имени'
                  const role = executor.role || 'исполнитель'
                  return (
                    <option key={executor.id} value={executor.id}>
                      {name} ({role})
                    </option>
                  )
                })}
              </select>
            )}
          </div>

          {/* Executor Cost */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Стоимость работы исполнителя (₽)
            </label>
            <input
              type="number"
              value={executorCost}
              onChange={(e) => setExecutorCost(Number(e.target.value) || 0)}
              min="0"
              step="100"
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="Введите стоимость работы"
            />
            <p className="text-xs text-gray-500 mt-2">
              Укажите стоимость работы для расчета прибыли проекта
            </p>
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
            disabled={loading || !selectedExecutorId}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Назначение...' : 'Назначить исполнителя'}
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
