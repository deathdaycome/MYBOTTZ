import { useState, useEffect } from 'react'
import { X, Plus, Edit2, Trash2, Check, AlertCircle, Tag } from 'lucide-react'

interface Status {
  id: number
  name: string
  color: string
  icon?: string
}

interface StatusManagementModalProps {
  isOpen: boolean
  onClose: () => void
  onStatusesChanged: () => void
}

const DEFAULT_COLORS = [
  { name: 'Синий', value: '#3B82F6' },
  { name: 'Зеленый', value: '#10B981' },
  { name: 'Желтый', value: '#F59E0B' },
  { name: 'Красный', value: '#EF4444' },
  { name: 'Фиолетовый', value: '#8B5CF6' },
  { name: 'Розовый', value: '#EC4899' },
  { name: 'Индиго', value: '#6366F1' },
  { name: 'Серый', value: '#6B7280' },
]

export const StatusManagementModal = ({
  isOpen,
  onClose,
  onStatusesChanged,
}: StatusManagementModalProps) => {
  const [statuses, setStatuses] = useState<Status[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [newStatus, setNewStatus] = useState({ name: '', color: '#3B82F6' })
  const [isAdding, setIsAdding] = useState(false)

  useEffect(() => {
    if (isOpen) {
      loadStatuses()
      setError('')
      setIsAdding(false)
      setEditingId(null)
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

  const loadStatuses = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8001/admin/api/statuses', {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      const data = await response.json()
      setStatuses(data.statuses || [])
    } catch (err) {
      setError('Ошибка загрузки статусов')
    } finally {
      setLoading(false)
    }
  }

  const handleAddStatus = async () => {
    if (!newStatus.name.trim()) {
      setError('Введите название статуса')
      return
    }

    try {
      const response = await fetch('http://localhost:8001/admin/api/statuses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(newStatus),
      })

      if (response.ok) {
        await loadStatuses()
        setNewStatus({ name: '', color: '#3B82F6' })
        setIsAdding(false)
        onStatusesChanged()
      } else {
        const data = await response.json()
        setError(data.message || 'Ошибка добавления статуса')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    }
  }

  const handleUpdateStatus = async (id: number, updates: Partial<Status>) => {
    try {
      const response = await fetch(`http://localhost:8001/admin/api/statuses/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(updates),
      })

      if (response.ok) {
        await loadStatuses()
        setEditingId(null)
        onStatusesChanged()
      } else {
        const data = await response.json()
        setError(data.message || 'Ошибка обновления статуса')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    }
  }

  const handleDeleteStatus = async (id: number) => {
    if (!confirm('Удалить этот статус? Это действие нельзя отменить.')) {
      return
    }

    try {
      const response = await fetch(`http://localhost:8001/admin/api/statuses/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        await loadStatuses()
        onStatusesChanged()
      } else {
        const data = await response.json()
        setError(data.message || 'Ошибка удаления статуса')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Tag className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Управление статусами</h3>
              <p className="text-purple-100 text-sm mt-1">Создавайте и редактируйте статусы проектов</p>
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
        <div className="p-6 max-h-[600px] overflow-y-auto">
          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-2 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg mb-4">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Add New Status Button */}
          {!isAdding && (
            <button
              type="button"
              onClick={() => setIsAdding(true)}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-semibold mb-4"
            >
              <Plus className="w-5 h-5" />
              Добавить новый статус
            </button>
          )}

          {/* Add New Status Form */}
          {isAdding && (
            <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-4 mb-4">
              <div className="flex items-center gap-2 mb-3">
                <input
                  type="text"
                  value={newStatus.name}
                  onChange={(e) => setNewStatus({ ...newStatus, name: e.target.value })}
                  className="flex-1 px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none"
                  placeholder="Название статуса"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={handleAddStatus}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Check className="w-5 h-5" />
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsAdding(false)
                    setNewStatus({ name: '', color: '#3B82F6' })
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {DEFAULT_COLORS.map((color) => (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => setNewStatus({ ...newStatus, color: color.value })}
                    className={`w-8 h-8 rounded-full border-2 transition-all ${
                      newStatus.color === color.value ? 'border-gray-900 scale-110' : 'border-gray-300'
                    }`}
                    style={{ backgroundColor: color.value }}
                    title={color.name}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Statuses List */}
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка статусов...</div>
          ) : (
            <div className="space-y-2">
              {statuses.map((status) => (
                <div
                  key={status.id}
                  className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div
                    className="w-4 h-4 rounded-full flex-shrink-0"
                    style={{ backgroundColor: status.color }}
                  />
                  {editingId === status.id ? (
                    <>
                      <input
                        type="text"
                        defaultValue={status.name}
                        className="flex-1 px-3 py-1 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                        onBlur={(e) => {
                          if (e.target.value !== status.name) {
                            handleUpdateStatus(status.id, { name: e.target.value })
                          } else {
                            setEditingId(null)
                          }
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.currentTarget.blur()
                          } else if (e.key === 'Escape') {
                            setEditingId(null)
                          }
                        }}
                        autoFocus
                      />
                    </>
                  ) : (
                    <>
                      <span className="flex-1 font-medium text-gray-900">{status.name}</span>
                      <button
                        type="button"
                        onClick={() => setEditingId(status.id)}
                        className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                        title="Редактировать"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteStatus(status.id)}
                        className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {!loading && statuses.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Нет созданных статусов. Добавьте первый статус!
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
