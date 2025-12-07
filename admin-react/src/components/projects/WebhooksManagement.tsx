import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Edit2, Check, Zap, AlertCircle, CheckCircle } from 'lucide-react'

interface Webhook {
  id: number
  name: string
  url: string
  events: string[]
  active: boolean
  secret?: string
  headers?: Record<string, string>
  lastTriggered?: string
  failureCount: number
}

interface WebhooksManagementProps {
  isOpen: boolean
  onClose: () => void
  projectId?: number | null
}

const AVAILABLE_EVENTS = [
  { value: 'project.created', label: 'Проект создан' },
  { value: 'project.updated', label: 'Проект обновлен' },
  { value: 'project.deleted', label: 'Проект удален' },
  { value: 'project.status_changed', label: 'Статус изменен' },
  { value: 'task.created', label: 'Задача создана' },
  { value: 'task.completed', label: 'Задача завершена' },
  { value: 'payment.received', label: 'Оплата получена' },
  { value: 'comment.added', label: 'Комментарий добавлен' },
]

export const WebhooksManagement = ({ isOpen, onClose, projectId }: WebhooksManagementProps) => {
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [loading, setLoading] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [testingId, setTestingId] = useState<number | null>(null)

  const [formData, setFormData] = useState({
    name: '',
    url: '',
    events: [] as string[],
    active: true,
    secret: '',
  })

  useEffect(() => {
    if (isOpen) {
      loadWebhooks()

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

  const loadWebhooks = async () => {
    setLoading(true)
    try {
      const url = projectId
        ? `http://localhost:8001/admin/api/projects/${projectId}/webhooks`
        : 'http://localhost:8001/admin/api/webhooks'

      const response = await fetch(url, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setWebhooks(data.webhooks || [])
      } else {
        // Mock data
        setWebhooks(getMockWebhooks())
      }
    } catch (err) {
      console.error('Error loading webhooks:', err)
      setWebhooks(getMockWebhooks())
    } finally {
      setLoading(false)
    }
  }

  const getMockWebhooks = (): Webhook[] => {
    return [
      {
        id: 1,
        name: 'Slack уведомления',
        url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX',
        events: ['project.status_changed', 'task.completed'],
        active: true,
        failureCount: 0,
        lastTriggered: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: 2,
        name: 'Telegram бот',
        url: 'https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
        events: ['payment.received', 'comment.added'],
        active: true,
        failureCount: 2,
        lastTriggered: new Date(Date.now() - 7200000).toISOString(),
      },
    ]
  }

  const handleCreate = async () => {
    if (!formData.name || !formData.url || formData.events.length === 0) {
      alert('Заполните все обязательные поля')
      return
    }

    try {
      const url = projectId
        ? `http://localhost:8001/admin/api/projects/${projectId}/webhooks`
        : 'http://localhost:8001/admin/api/webhooks'

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await loadWebhooks()
        resetForm()
      }
    } catch (err) {
      console.error('Error creating webhook:', err)
    }
  }

  const handleUpdate = async (id: number) => {
    try {
      const url = projectId
        ? `http://localhost:8001/admin/api/projects/${projectId}/webhooks/${id}`
        : `http://localhost:8001/admin/api/webhooks/${id}`

      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await loadWebhooks()
        setEditingId(null)
        resetForm()
      }
    } catch (err) {
      console.error('Error updating webhook:', err)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить webhook?')) return

    try {
      const url = projectId
        ? `http://localhost:8001/admin/api/projects/${projectId}/webhooks/${id}`
        : `http://localhost:8001/admin/api/webhooks/${id}`

      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        await loadWebhooks()
      }
    } catch (err) {
      console.error('Error deleting webhook:', err)
    }
  }

  const handleTest = async (id: number) => {
    setTestingId(id)
    try {
      const url = projectId
        ? `http://localhost:8001/admin/api/projects/${projectId}/webhooks/${id}/test`
        : `http://localhost:8001/admin/api/webhooks/${id}/test`

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        alert('Тестовый webhook отправлен успешно!')
      } else {
        alert('Ошибка отправки webhook')
      }
    } catch (err) {
      console.error('Error testing webhook:', err)
      alert('Ошибка отправки webhook')
    } finally {
      setTestingId(null)
    }
  }

  const handleToggleActive = async (id: number, active: boolean) => {
    try {
      const url = projectId
        ? `http://localhost:8001/admin/api/projects/${projectId}/webhooks/${id}/toggle`
        : `http://localhost:8001/admin/api/webhooks/${id}/toggle`

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({ active: !active }),
      })

      if (response.ok) {
        await loadWebhooks()
      }
    } catch (err) {
      console.error('Error toggling webhook:', err)
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      url: '',
      events: [],
      active: true,
      secret: '',
    })
    setIsCreating(false)
    setEditingId(null)
  }

  const startEdit = (webhook: Webhook) => {
    setFormData({
      name: webhook.name,
      url: webhook.url,
      events: webhook.events,
      active: webhook.active,
      secret: webhook.secret || '',
    })
    setEditingId(webhook.id)
    setIsCreating(true)
  }

  const toggleEvent = (event: string) => {
    if (formData.events.includes(event)) {
      setFormData({ ...formData, events: formData.events.filter((e) => e !== event) })
    } else {
      setFormData({ ...formData, events: [...formData.events, event] })
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-600 to-red-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Zap className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Управление Webhooks</h3>
              <p className="text-orange-100 text-sm mt-1">
                Автоматические уведомления о событиях
              </p>
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

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Create/Edit Form */}
          {isCreating ? (
            <div className="bg-orange-50 border-2 border-orange-200 rounded-xl p-6 mb-6">
              <h4 className="text-lg font-bold text-gray-900 mb-4">
                {editingId ? 'Редактировать webhook' : 'Создать новый webhook'}
              </h4>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Название *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-orange-500 outline-none"
                    placeholder="Например: Slack уведомления"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">URL *</label>
                  <input
                    type="url"
                    value={formData.url}
                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-orange-500 outline-none font-mono text-sm"
                    placeholder="https://hooks.example.com/webhook"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    События *
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {AVAILABLE_EVENTS.map((event) => (
                      <label
                        key={event.value}
                        className="flex items-center gap-2 p-3 border-2 border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={formData.events.includes(event.value)}
                          onChange={() => toggleEvent(event.value)}
                          className="w-4 h-4 rounded"
                        />
                        <span className="text-sm text-gray-700">{event.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Secret (необязательно)
                  </label>
                  <input
                    type="text"
                    value={formData.secret}
                    onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-orange-500 outline-none font-mono text-sm"
                    placeholder="Секретный ключ для подписи запросов"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="active"
                    checked={formData.active}
                    onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                    className="w-4 h-4 rounded"
                  />
                  <label htmlFor="active" className="text-sm font-medium text-gray-700">
                    Активен
                  </label>
                </div>

                <div className="flex gap-2 pt-4">
                  <button
                    onClick={() => (editingId ? handleUpdate(editingId) : handleCreate())}
                    className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-semibold"
                  >
                    {editingId ? 'Сохранить' : 'Создать'}
                  </button>
                  <button
                    onClick={resetForm}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setIsCreating(true)}
              className="w-full px-4 py-3 mb-6 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-xl hover:from-orange-700 hover:to-red-700 transition-all font-semibold flex items-center justify-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Создать webhook
            </button>
          )}

          {/* Webhooks List */}
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка...</div>
          ) : webhooks.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Zap className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Webhooks не настроены</p>
            </div>
          ) : (
            <div className="space-y-4">
              {webhooks.map((webhook) => (
                <div
                  key={webhook.id}
                  className="bg-white border-2 border-gray-200 rounded-xl p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-lg font-bold text-gray-900">{webhook.name}</h4>
                        <div className="flex items-center gap-2">
                          {webhook.active ? (
                            <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-bold flex items-center gap-1">
                              <CheckCircle className="w-3 h-3" />
                              Активен
                            </span>
                          ) : (
                            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-bold">
                              Неактивен
                            </span>
                          )}
                          {webhook.failureCount > 0 && (
                            <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-bold flex items-center gap-1">
                              <AlertCircle className="w-3 h-3" />
                              {webhook.failureCount} ошибок
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-sm text-gray-600 font-mono bg-gray-100 px-3 py-2 rounded mb-2">
                        {webhook.url}
                      </div>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {webhook.events.map((event) => (
                          <span
                            key={event}
                            className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium"
                          >
                            {AVAILABLE_EVENTS.find((e) => e.value === event)?.label || event}
                          </span>
                        ))}
                      </div>
                      {webhook.lastTriggered && (
                        <div className="text-xs text-gray-500">
                          Последний вызов: {formatTimestamp(webhook.lastTriggered)}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleToggleActive(webhook.id, webhook.active)}
                        className={`p-2 rounded-lg transition-colors ${
                          webhook.active
                            ? 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                            : 'bg-green-100 hover:bg-green-200 text-green-700'
                        }`}
                        title={webhook.active ? 'Деактивировать' : 'Активировать'}
                      >
                        <Check className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleTest(webhook.id)}
                        disabled={testingId === webhook.id}
                        className="p-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg transition-colors disabled:opacity-50"
                        title="Тест"
                      >
                        <Zap className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => startEdit(webhook)}
                        className="p-2 bg-yellow-100 hover:bg-yellow-200 text-yellow-700 rounded-lg transition-colors"
                        title="Редактировать"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(webhook.id)}
                        className="p-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
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
