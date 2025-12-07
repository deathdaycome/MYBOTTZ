import { useState, useEffect } from 'react'
import {
  X,
  Plug,
  Check,
  AlertCircle,
  RefreshCw,
  Trash2,
  ExternalLink,
  Key,
  Settings,
  Link as LinkIcon,
  Globe,
  MessageSquare,
  Calendar as CalendarIcon,
  Cloud,
  Trello,
  Github,
} from 'lucide-react'

interface Integration {
  id: string
  name: string
  service: string
  description: string
  icon: any
  color: string
  connected: boolean
  apiKey?: string
  webhookUrl?: string
  settings?: Record<string, any>
  lastSync?: string
  status: 'active' | 'inactive' | 'error'
}

interface IntegrationSettingsProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

const AVAILABLE_INTEGRATIONS: Omit<Integration, 'id' | 'connected' | 'lastSync' | 'status'>[] = [
  {
    name: 'Slack',
    service: 'slack',
    description: 'Уведомления о проекте в Slack-канал',
    icon: MessageSquare,
    color: '#4A154B',
  },
  {
    name: 'Trello',
    service: 'trello',
    description: 'Синхронизация задач с Trello-доской',
    icon: Trello,
    color: '#0079BF',
  },
  {
    name: 'GitHub',
    service: 'github',
    description: 'Интеграция с GitHub-репозиторием',
    icon: Github,
    color: '#181717',
  },
  {
    name: 'Google Calendar',
    service: 'google-calendar',
    description: 'Синхронизация дедлайнов с календарем',
    icon: CalendarIcon,
    color: '#4285F4',
  },
  {
    name: 'Dropbox',
    service: 'dropbox',
    description: 'Хранение файлов проекта в Dropbox',
    icon: Cloud,
    color: '#0061FF',
  },
  {
    name: 'Webhook',
    service: 'webhook',
    description: 'Пользовательский webhook для событий',
    icon: LinkIcon,
    color: '#10B981',
  },
]

export const IntegrationSettings = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: IntegrationSettingsProps) => {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null)
  const [isConfiguring, setIsConfiguring] = useState(false)
  const [configForm, setConfigForm] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(false)
  const [testing, setTesting] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen && projectId) {
      loadIntegrations()
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

  const loadIntegrations = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/integrations`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setIntegrations(data.integrations || [])
      } else {
        // Mock data
        setIntegrations([
          {
            id: '1',
            name: 'Slack',
            service: 'slack',
            description: 'Уведомления о проекте в Slack-канал',
            icon: MessageSquare,
            color: '#4A154B',
            connected: true,
            webhookUrl: 'https://hooks.slack.com/services/XXXXX',
            lastSync: new Date().toISOString(),
            status: 'active',
            settings: { channel: '#projects', notifications: ['status_change', 'deadline'] },
          },
          {
            id: '2',
            name: 'GitHub',
            service: 'github',
            description: 'Интеграция с GitHub-репозиторием',
            icon: Github,
            color: '#181717',
            connected: true,
            apiKey: 'ghp_xxxxxxxxxxxxx',
            lastSync: new Date(Date.now() - 3600000).toISOString(),
            status: 'active',
            settings: { repo: 'user/project', branch: 'main' },
          },
        ])
      }
    } catch (err) {
      console.error('Error loading integrations:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = (integrationTemplate: (typeof AVAILABLE_INTEGRATIONS)[0]) => {
    setSelectedIntegration({
      id: Date.now().toString(),
      ...integrationTemplate,
      connected: false,
      status: 'inactive',
    })
    setConfigForm({})
    setIsConfiguring(true)
  }

  const handleSaveIntegration = async () => {
    if (!selectedIntegration || !projectId) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/integrations`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify({
            service: selectedIntegration.service,
            ...configForm,
          }),
        }
      )

      if (response.ok) {
        setIsConfiguring(false)
        setSelectedIntegration(null)
        setConfigForm({})
        await loadIntegrations()
      }
    } catch (err) {
      console.error('Error saving integration:', err)
    }
  }

  const handleDisconnect = async (integrationId: string) => {
    if (!confirm('Отключить эту интеграцию?')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/integrations/${integrationId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadIntegrations()
      }
    } catch (err) {
      console.error('Error disconnecting integration:', err)
    }
  }

  const handleTestIntegration = async (integrationId: string) => {
    setTesting(integrationId)

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/integrations/${integrationId}/test`,
        {
          method: 'POST',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        alert('Интеграция работает корректно!')
      } else {
        alert('Ошибка тестирования интеграции')
      }
    } catch (err) {
      console.error('Error testing integration:', err)
      alert('Ошибка тестирования интеграции')
    } finally {
      setTesting(null)
    }
  }

  const handleSync = async (integrationId: string) => {
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/integrations/${integrationId}/sync`,
        {
          method: 'POST',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadIntegrations()
        alert('Синхронизация выполнена успешно!')
      }
    } catch (err) {
      console.error('Error syncing integration:', err)
    }
  }

  const renderConfigForm = () => {
    if (!selectedIntegration) return null

    switch (selectedIntegration.service) {
      case 'slack':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Webhook URL
              </label>
              <input
                type="text"
                value={configForm.webhookUrl || ''}
                onChange={(e) => setConfigForm({ ...configForm, webhookUrl: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="https://hooks.slack.com/services/..."
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Канал</label>
              <input
                type="text"
                value={configForm.channel || ''}
                onChange={(e) => setConfigForm({ ...configForm, channel: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="#projects"
              />
            </div>
          </div>
        )

      case 'trello':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">API Key</label>
              <input
                type="text"
                value={configForm.apiKey || ''}
                onChange={(e) => setConfigForm({ ...configForm, apiKey: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="Trello API Key"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Token</label>
              <input
                type="text"
                value={configForm.token || ''}
                onChange={(e) => setConfigForm({ ...configForm, token: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="Trello Token"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Board ID</label>
              <input
                type="text"
                value={configForm.boardId || ''}
                onChange={(e) => setConfigForm({ ...configForm, boardId: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="Board ID"
              />
            </div>
          </div>
        )

      case 'github':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Personal Access Token
              </label>
              <input
                type="password"
                value={configForm.token || ''}
                onChange={(e) => setConfigForm({ ...configForm, token: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="ghp_xxxxxxxxxxxx"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Repository (owner/repo)
              </label>
              <input
                type="text"
                value={configForm.repo || ''}
                onChange={(e) => setConfigForm({ ...configForm, repo: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="username/repository"
              />
            </div>
          </div>
        )

      case 'google-calendar':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Client ID
              </label>
              <input
                type="text"
                value={configForm.clientId || ''}
                onChange={(e) => setConfigForm({ ...configForm, clientId: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="Google OAuth Client ID"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Calendar ID
              </label>
              <input
                type="text"
                value={configForm.calendarId || ''}
                onChange={(e) => setConfigForm({ ...configForm, calendarId: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="primary"
              />
            </div>
          </div>
        )

      case 'webhook':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Webhook URL
              </label>
              <input
                type="text"
                value={configForm.url || ''}
                onChange={(e) => setConfigForm({ ...configForm, url: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="https://your-server.com/webhook"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Secret (опционально)
              </label>
              <input
                type="password"
                value={configForm.secret || ''}
                onChange={(e) => setConfigForm({ ...configForm, secret: e.target.value })}
                className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                placeholder="Секретный ключ"
              />
            </div>
          </div>
        )

      default:
        return (
          <div className="text-sm text-gray-600">
            Форма настройки для этого сервиса в разработке
          </div>
        )
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  if (!isOpen) return null

  const connectedIntegrations = integrations.filter((i) => i.connected)
  const availableToConnect = AVAILABLE_INTEGRATIONS.filter(
    (ai) => !integrations.some((i) => i.service === ai.service && i.connected)
  )

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Plug className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Интеграции</h3>
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

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Connected Integrations */}
          {connectedIntegrations.length > 0 && (
            <div>
              <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Check className="w-5 h-5 text-green-600" />
                Подключенные интеграции ({connectedIntegrations.length})
              </h4>

              <div className="space-y-3">
                {connectedIntegrations.map((integration) => {
                  const Icon = integration.icon
                  return (
                    <div
                      key={integration.id}
                      className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-purple-400 transition-all"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4 flex-1">
                          <div
                            className="w-12 h-12 rounded-xl flex items-center justify-center text-white flex-shrink-0"
                            style={{ backgroundColor: integration.color }}
                          >
                            <Icon className="w-6 h-6" />
                          </div>

                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h5 className="font-bold text-gray-900">{integration.name}</h5>
                              <span
                                className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                                  integration.status === 'active'
                                    ? 'bg-green-100 text-green-700'
                                    : integration.status === 'error'
                                      ? 'bg-red-100 text-red-700'
                                      : 'bg-gray-100 text-gray-700'
                                }`}
                              >
                                {integration.status === 'active' ? 'Активна' : integration.status === 'error' ? 'Ошибка' : 'Неактивна'}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{integration.description}</p>

                            {integration.lastSync && (
                              <div className="text-xs text-gray-500">
                                Последняя синхронизация: {formatDate(integration.lastSync)}
                              </div>
                            )}

                            {integration.settings && (
                              <div className="mt-2 flex flex-wrap gap-2">
                                {Object.entries(integration.settings).map(([key, value]) => (
                                  <span
                                    key={key}
                                    className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs font-semibold"
                                  >
                                    {key}: {String(value)}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-2 ml-4">
                          <button
                            onClick={() => handleSync(integration.id)}
                            className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                            title="Синхронизировать"
                          >
                            <RefreshCw className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleTestIntegration(integration.id)}
                            disabled={testing === integration.id}
                            className="p-2 text-green-600 hover:bg-green-100 rounded-lg transition-colors disabled:opacity-50"
                            title="Тестировать"
                          >
                            <Settings className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDisconnect(integration.id)}
                            className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                            title="Отключить"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Available Integrations */}
          {!isConfiguring && availableToConnect.length > 0 && (
            <div>
              <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-gray-600" />
                Доступные интеграции ({availableToConnect.length})
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableToConnect.map((integration) => {
                  const Icon = integration.icon
                  return (
                    <div
                      key={integration.service}
                      className="bg-gray-50 border-2 border-gray-200 rounded-xl p-4 hover:border-purple-400 hover:bg-white transition-all cursor-pointer"
                      onClick={() => handleConnect(integration)}
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className="w-10 h-10 rounded-lg flex items-center justify-center text-white flex-shrink-0"
                          style={{ backgroundColor: integration.color }}
                        >
                          <Icon className="w-5 h-5" />
                        </div>

                        <div className="flex-1">
                          <h5 className="font-bold text-gray-900 mb-1">{integration.name}</h5>
                          <p className="text-sm text-gray-600 mb-3">{integration.description}</p>
                          <button className="text-xs font-semibold text-purple-600 hover:text-purple-700 flex items-center gap-1">
                            <Plug className="w-3.5 h-3.5" />
                            Подключить
                          </button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Configuration Form */}
          {isConfiguring && selectedIntegration && (
            <div className="bg-purple-50 border-2 border-purple-200 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                {selectedIntegration.icon && (
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-white"
                    style={{ backgroundColor: selectedIntegration.color }}
                  >
                    <selectedIntegration.icon className="w-6 h-6" />
                  </div>
                )}
                <div>
                  <h4 className="font-bold text-gray-900">Настройка {selectedIntegration.name}</h4>
                  <p className="text-sm text-gray-600">{selectedIntegration.description}</p>
                </div>
              </div>

              {renderConfigForm()}

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSaveIntegration}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all font-semibold"
                >
                  <Check className="w-5 h-5" />
                  Подключить
                </button>
                <button
                  onClick={() => {
                    setIsConfiguring(false)
                    setSelectedIntegration(null)
                    setConfigForm({})
                  }}
                  className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
                >
                  Отмена
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="text-sm text-gray-600">
            Подключено:{' '}
            <span className="font-bold text-purple-600">{connectedIntegrations.length}</span> из{' '}
            {AVAILABLE_INTEGRATIONS.length}
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
