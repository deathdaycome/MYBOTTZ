import { useState, useEffect } from 'react'
import { X, History, User, Calendar, ChevronDown, ChevronRight } from 'lucide-react'

interface Change {
  field: string
  oldValue: string | null
  newValue: string | null
  type: 'added' | 'removed' | 'modified'
}

interface HistoryEntry {
  id: number
  userId: number
  userName: string
  action: string
  changes: Change[]
  timestamp: string
  ipAddress?: string
}

interface ChangeHistoryModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

export const ChangeHistoryModal = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: ChangeHistoryModalProps) => {
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set())
  const [filter, setFilter] = useState<'all' | 'created' | 'updated' | 'deleted'>('all')

  useEffect(() => {
    if (isOpen && projectId) {
      loadHistory()
    }
  }, [isOpen, projectId])

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

  const loadHistory = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/history`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setHistory(data.history || [])
      } else {
        // Mock data for demonstration
        setHistory(getMockHistory())
      }
    } catch (err) {
      console.error('Error loading history:', err)
      setHistory(getMockHistory())
    } finally {
      setLoading(false)
    }
  }

  const getMockHistory = (): HistoryEntry[] => {
    return [
      {
        id: 1,
        userId: 1,
        userName: 'Администратор',
        action: 'updated',
        changes: [
          {
            field: 'status',
            oldValue: 'new',
            newValue: 'in_progress',
            type: 'modified',
          },
          {
            field: 'assigned_to',
            oldValue: null,
            newValue: 'Иван Иванов',
            type: 'added',
          },
        ],
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        ipAddress: '192.168.1.1',
      },
      {
        id: 2,
        userId: 1,
        userName: 'Администратор',
        action: 'updated',
        changes: [
          {
            field: 'estimated_cost',
            oldValue: '100000',
            newValue: '150000',
            type: 'modified',
          },
          {
            field: 'description',
            oldValue: 'Старое описание проекта',
            newValue: 'Новое описание проекта с дополнительными деталями',
            type: 'modified',
          },
        ],
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        ipAddress: '192.168.1.1',
      },
      {
        id: 3,
        userId: 1,
        userName: 'Администратор',
        action: 'created',
        changes: [
          {
            field: 'title',
            oldValue: null,
            newValue: projectName,
            type: 'added',
          },
          {
            field: 'status',
            oldValue: null,
            newValue: 'new',
            type: 'added',
          },
        ],
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        ipAddress: '192.168.1.1',
      },
    ]
  }

  const toggleExpand = (id: number) => {
    const newExpanded = new Set(expandedIds)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedIds(newExpanded)
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date)
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'created':
        return 'bg-green-100 text-green-700'
      case 'updated':
        return 'bg-blue-100 text-blue-700'
      case 'deleted':
        return 'bg-red-100 text-red-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getActionLabel = (action: string) => {
    const labels: Record<string, string> = {
      created: 'Создано',
      updated: 'Обновлено',
      deleted: 'Удалено',
    }
    return labels[action] || action
  }

  const getFieldLabel = (field: string) => {
    const labels: Record<string, string> = {
      title: 'Название',
      description: 'Описание',
      status: 'Статус',
      assigned_to: 'Исполнитель',
      estimated_cost: 'Стоимость',
      deadline: 'Дедлайн',
      priority: 'Приоритет',
      complexity: 'Сложность',
    }
    return labels[field] || field
  }

  const renderDiff = (change: Change) => {
    if (change.type === 'added') {
      return (
        <div className="bg-green-50 border-l-4 border-green-500 p-3 rounded">
          <div className="text-sm font-semibold text-green-700 mb-1">Добавлено:</div>
          <div className="text-sm text-green-900 font-mono bg-green-100 p-2 rounded">
            {change.newValue}
          </div>
        </div>
      )
    }

    if (change.type === 'removed') {
      return (
        <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded">
          <div className="text-sm font-semibold text-red-700 mb-1">Удалено:</div>
          <div className="text-sm text-red-900 font-mono bg-red-100 p-2 rounded line-through">
            {change.oldValue}
          </div>
        </div>
      )
    }

    if (change.type === 'modified') {
      return (
        <div className="bg-yellow-50 border-l-4 border-yellow-500 p-3 rounded">
          <div className="text-sm font-semibold text-yellow-700 mb-2">Изменено:</div>
          <div className="space-y-2">
            <div>
              <div className="text-xs text-gray-500 mb-1">Было:</div>
              <div className="text-sm text-gray-900 font-mono bg-red-100 p-2 rounded">
                {change.oldValue || '(пусто)'}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">Стало:</div>
              <div className="text-sm text-gray-900 font-mono bg-green-100 p-2 rounded">
                {change.newValue || '(пусто)'}
              </div>
            </div>
          </div>
        </div>
      )
    }

    return null
  }

  const filteredHistory =
    filter === 'all' ? history : history.filter((entry) => entry.action === filter)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <History className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">История изменений</h3>
              <p className="text-purple-100 text-sm mt-1">{projectName}</p>
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

        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-700">Фильтр:</span>
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Все
            </button>
            <button
              onClick={() => setFilter('created')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                filter === 'created'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Создание
            </button>
            <button
              onClick={() => setFilter('updated')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                filter === 'updated'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Обновления
            </button>
            <button
              onClick={() => setFilter('deleted')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                filter === 'deleted'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Удаления
            </button>
          </div>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка истории...</div>
          ) : filteredHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-500">История изменений пуста</div>
          ) : (
            <div className="space-y-4">
              {filteredHistory.map((entry) => {
                const isExpanded = expandedIds.has(entry.id)

                return (
                  <div
                    key={entry.id}
                    className="bg-white border-2 border-gray-200 rounded-xl overflow-hidden"
                  >
                    {/* Entry Header */}
                    <button
                      onClick={() => toggleExpand(entry.id)}
                      className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        {isExpanded ? (
                          <ChevronDown className="w-5 h-5 text-gray-400" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-gray-400" />
                        )}

                        <span
                          className={`px-3 py-1 rounded-lg text-xs font-bold ${getActionColor(
                            entry.action
                          )}`}
                        >
                          {getActionLabel(entry.action)}
                        </span>

                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <User className="w-4 h-4" />
                          <span className="font-medium">{entry.userName}</span>
                        </div>

                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <Calendar className="w-4 h-4" />
                          <span>{formatTimestamp(entry.timestamp)}</span>
                        </div>
                      </div>

                      <div className="text-xs text-gray-500">
                        {entry.changes.length} изменений
                      </div>
                    </button>

                    {/* Entry Details */}
                    {isExpanded && (
                      <div className="px-4 pb-4 pt-2 bg-gray-50 border-t border-gray-200">
                        <div className="space-y-3">
                          {entry.changes.map((change, index) => (
                            <div key={index}>
                              <div className="text-sm font-semibold text-gray-700 mb-2">
                                {getFieldLabel(change.field)}
                              </div>
                              {renderDiff(change)}
                            </div>
                          ))}
                        </div>

                        {entry.ipAddress && (
                          <div className="mt-4 pt-3 border-t border-gray-300 text-xs text-gray-500">
                            IP адрес: {entry.ipAddress}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Всего записей: <strong>{filteredHistory.length}</strong>
          </div>
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
