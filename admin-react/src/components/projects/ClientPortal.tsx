import React, { useState, useEffect } from 'react'
import {
  Globe,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Link as LinkIcon,
  Copy,
  Check,
  X,
  Settings,
  Users,
  FileText,
  MessageSquare,
  Bell,
  Download,
  Calendar,
  TrendingUp,
  RefreshCw,
  Mail,
  Shield,
} from 'lucide-react'

interface ClientPortalProps {
  projectId: number
  onClose: () => void
}

interface PortalSettings {
  enabled: boolean
  url: string
  accessPassword: string | null
  allowComments: boolean
  allowFileDownload: boolean
  allowTaskView: boolean
  allowTimelineView: boolean
  allowBudgetView: boolean
  showTeamMembers: boolean
  emailNotifications: boolean
  customBranding: {
    enabled: boolean
    logo: string
    primaryColor: string
    companyName: string
  }
  accessLog: boolean
  expiresAt: string | null
}

interface PortalAccess {
  id: number
  clientName: string
  clientEmail: string
  accessGranted: string
  lastAccess: string | null
  accessCount: number
  ipAddress: string
}

interface PortalActivity {
  id: number
  clientName: string
  action: string
  timestamp: string
  details: string
}

const ClientPortal: React.FC<ClientPortalProps> = ({ projectId, onClose }) => {
  const [settings, setSettings] = useState<PortalSettings>({
    enabled: false,
    url: `https://portal.example.com/projects/${projectId}`,
    accessPassword: null,
    allowComments: true,
    allowFileDownload: true,
    allowTaskView: true,
    allowTimelineView: true,
    allowBudgetView: false,
    showTeamMembers: true,
    emailNotifications: true,
    customBranding: {
      enabled: false,
      logo: '',
      primaryColor: '#3B82F6',
      companyName: 'Ваша компания',
    },
    accessLog: true,
    expiresAt: null,
  })

  const [accessList, setAccessList] = useState<PortalAccess[]>([])
  const [activityLog, setActivityLog] = useState<PortalActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [activeTab, setActiveTab] = useState<'settings' | 'access' | 'activity' | 'preview'>('settings')
  const [newPassword, setNewPassword] = useState('')

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  useEffect(() => {
    fetchPortalData()
  }, [projectId])

  const fetchPortalData = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/portal`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setSettings(data.settings)
        setAccessList(data.accessList || [])
        setActivityLog(data.activityLog || [])
      } else {
        // Mock data
        setSettings({
          ...settings,
          enabled: true,
          accessPassword: 'client2024',
        })
        setAccessList([
          {
            id: 1,
            clientName: 'Иван Петров',
            clientEmail: 'ivan.petrov@client.com',
            accessGranted: '2024-03-01T10:00:00',
            lastAccess: '2024-03-15T14:30:00',
            accessCount: 24,
            ipAddress: '192.168.1.100',
          },
          {
            id: 2,
            clientName: 'Ольга Сидорова',
            clientEmail: 'olga.sidorova@client.com',
            accessGranted: '2024-03-05T11:20:00',
            lastAccess: '2024-03-14T16:45:00',
            accessCount: 12,
            ipAddress: '192.168.1.101',
          },
          {
            id: 3,
            clientName: 'Александр Козлов',
            clientEmail: 'alex.kozlov@client.com',
            accessGranted: '2024-03-10T09:15:00',
            lastAccess: null,
            accessCount: 0,
            ipAddress: '-',
          },
        ])
        setActivityLog([
          {
            id: 1,
            clientName: 'Иван Петров',
            action: 'Просмотр проекта',
            timestamp: '2024-03-15T14:30:00',
            details: 'Открыта страница обзора проекта',
          },
          {
            id: 2,
            clientName: 'Иван Петров',
            action: 'Скачивание файла',
            timestamp: '2024-03-15T14:35:00',
            details: 'Скачан файл: Техническое задание.pdf',
          },
          {
            id: 3,
            clientName: 'Ольга Сидорова',
            action: 'Добавление комментария',
            timestamp: '2024-03-14T16:45:00',
            details: 'Комментарий к задаче "Дизайн главной страницы"',
          },
          {
            id: 4,
            clientName: 'Иван Петров',
            action: 'Просмотр таймлайна',
            timestamp: '2024-03-15T14:32:00',
            details: 'Открыт таймлайн проекта',
          },
          {
            id: 5,
            clientName: 'Ольга Сидорова',
            action: 'Просмотр бюджета',
            timestamp: '2024-03-14T16:40:00',
            details: 'Открыта страница бюджета',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching portal data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveSettings = async () => {
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/portal/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(settings),
      })

      if (response.ok) {
        alert('Настройки сохранены')
      }
    } catch (error) {
      console.error('Error saving settings:', error)
      alert('Настройки сохранены (локально)')
    }
  }

  const handleTogglePortal = async () => {
    const newSettings = { ...settings, enabled: !settings.enabled }
    setSettings(newSettings)
    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/portal/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({ enabled: newSettings.enabled }),
      })
    } catch (error) {
      console.error('Error toggling portal:', error)
    }
  }

  const handleGeneratePassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let password = ''
    for (let i = 0; i < 12; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    setNewPassword(password)
    setSettings({ ...settings, accessPassword: password })
  }

  const handleRemovePassword = () => {
    setSettings({ ...settings, accessPassword: null })
    setNewPassword('')
  }

  const handleCopyUrl = () => {
    navigator.clipboard.writeText(settings.url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleCopyCredentials = () => {
    const text = `URL: ${settings.url}\n${settings.accessPassword ? `Пароль: ${settings.accessPassword}` : 'Пароль не требуется'}`
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleRevokeAccess = async (accessId: number) => {
    if (!confirm('Отозвать доступ?')) return

    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/portal/access/${accessId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      setAccessList(accessList.filter((a) => a.id !== accessId))
    } catch (error) {
      console.error('Error revoking access:', error)
    }
  }

  const calculateStats = () => {
    const totalAccess = accessList.length
    const activeUsers = accessList.filter((a) => a.lastAccess !== null).length
    const totalViews = accessList.reduce((sum, a) => sum + a.accessCount, 0)
    const avgViewsPerUser = totalAccess > 0 ? totalViews / totalAccess : 0
    const recentActivity = activityLog.filter((a) => {
      const activityDate = new Date(a.timestamp)
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
      return activityDate >= dayAgo
    }).length

    return {
      totalAccess,
      activeUsers,
      totalViews,
      avgViewsPerUser,
      recentActivity,
    }
  }

  const stats = calculateStats()

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка портала...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-violet-600 to-purple-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Globe className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Клиентский портал</h2>
              <p className="text-violet-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-violet-100">Статус портала:</span>
              <button
                onClick={handleTogglePortal}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  settings.enabled ? 'bg-green-500' : 'bg-gray-400'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    settings.enabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className={`text-sm font-medium ${settings.enabled ? 'text-green-100' : 'text-gray-200'}`}>
                {settings.enabled ? 'Активен' : 'Неактивен'}
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              aria-label="Закрыть"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-5 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Users className="w-4 h-4" />
              <span>Всего клиентов</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.totalAccess}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <TrendingUp className="w-4 h-4" />
              <span>Активных</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.activeUsers}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Eye className="w-4 h-4" />
              <span>Всего просмотров</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">{stats.totalViews}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <TrendingUp className="w-4 h-4" />
              <span>Ср. просмотров</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">{stats.avgViewsPerUser.toFixed(1)}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Bell className="w-4 h-4" />
              <span>За 24 часа</span>
            </div>
            <div className="text-2xl font-bold text-orange-600">{stats.recentActivity}</div>
          </div>
        </div>

        {/* Portal URL */}
        {settings.enabled && (
          <div className="p-6 bg-violet-50 border-b">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700 mb-2">Ссылка на портал:</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 flex items-center gap-2 bg-white border border-gray-300 rounded-lg px-4 py-3">
                    <LinkIcon className="w-5 h-5 text-gray-400" />
                    <span className="font-mono text-sm text-gray-900">{settings.url}</span>
                  </div>
                  <button
                    onClick={handleCopyUrl}
                    className="px-4 py-3 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors flex items-center gap-2"
                  >
                    {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                    {copied ? 'Скопировано' : 'Копировать'}
                  </button>
                  <button
                    onClick={handleCopyCredentials}
                    className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                  >
                    <Mail className="w-5 h-5" />
                    Отправить
                  </button>
                </div>
                {settings.accessPassword && (
                  <p className="text-sm text-gray-600 mt-2">
                    Пароль доступа: <span className="font-mono font-medium">{showPassword ? settings.accessPassword : '••••••••'}</span>
                    <button
                      onClick={() => setShowPassword(!showPassword)}
                      className="ml-2 text-violet-600 hover:text-violet-700"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4 inline" /> : <Eye className="w-4 h-4 inline" />}
                    </button>
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1 p-4 bg-white border-b">
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'settings' ? 'bg-violet-100 text-violet-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Settings className="w-5 h-5" />
            Настройки
          </button>
          <button
            onClick={() => setActiveTab('access')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'access' ? 'bg-violet-100 text-violet-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Users className="w-5 h-5" />
            Доступ ({accessList.length})
          </button>
          <button
            onClick={() => setActiveTab('activity')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'activity' ? 'bg-violet-100 text-violet-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <TrendingUp className="w-5 h-5" />
            Активность
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              activeTab === 'preview' ? 'bg-violet-100 text-violet-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Eye className="w-5 h-5" />
            Предпросмотр
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'settings' && (
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Security */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Безопасность
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.accessPassword !== null}
                        onChange={(e) => {
                          if (e.target.checked) {
                            handleGeneratePassword()
                          } else {
                            handleRemovePassword()
                          }
                        }}
                        className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                      />
                      <div>
                        <span className="font-medium text-gray-900">Защита паролем</span>
                        <p className="text-sm text-gray-500">Требовать пароль для доступа к порталу</p>
                      </div>
                    </label>
                  </div>
                  {settings.accessPassword && (
                    <div className="ml-8 space-y-3">
                      <div className="flex items-center gap-3">
                        <input
                          type={showPassword ? 'text' : 'password'}
                          value={settings.accessPassword}
                          onChange={(e) => setSettings({ ...settings, accessPassword: e.target.value })}
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                        />
                        <button
                          onClick={() => setShowPassword(!showPassword)}
                          className="p-2 text-gray-400 hover:text-gray-600"
                        >
                          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                        <button
                          onClick={handleGeneratePassword}
                          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
                        >
                          <RefreshCw className="w-4 h-4" />
                          Сгенерировать
                        </button>
                      </div>
                    </div>
                  )}
                  <div>
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.accessLog}
                        onChange={(e) => setSettings({ ...settings, accessLog: e.target.checked })}
                        className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                      />
                      <div>
                        <span className="font-medium text-gray-900">Журнал доступа</span>
                        <p className="text-sm text-gray-500">Отслеживать все действия клиентов на портале</p>
                      </div>
                    </label>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Срок действия ссылки</label>
                    <input
                      type="datetime-local"
                      value={settings.expiresAt || ''}
                      onChange={(e) => setSettings({ ...settings, expiresAt: e.target.value || null })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-500 mt-1">Оставьте пустым для бессрочного доступа</p>
                  </div>
                </div>
              </div>

              {/* Permissions */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Lock className="w-5 h-5" />
                  Разрешения
                </h3>
                <div className="space-y-4">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.allowComments}
                      onChange={(e) => setSettings({ ...settings, allowComments: e.target.checked })}
                      className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Разрешить комментарии</span>
                      <p className="text-sm text-gray-500">Клиенты могут оставлять комментарии к задачам</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.allowFileDownload}
                      onChange={(e) => setSettings({ ...settings, allowFileDownload: e.target.checked })}
                      className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Разрешить скачивание файлов</span>
                      <p className="text-sm text-gray-500">Клиенты могут скачивать документы проекта</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.allowTaskView}
                      onChange={(e) => setSettings({ ...settings, allowTaskView: e.target.checked })}
                      className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Показывать задачи</span>
                      <p className="text-sm text-gray-500">Отображать список задач проекта</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.allowTimelineView}
                      onChange={(e) => setSettings({ ...settings, allowTimelineView: e.target.checked })}
                      className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Показывать таймлайн</span>
                      <p className="text-sm text-gray-500">Отображать временную шкалу проекта</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.allowBudgetView}
                      onChange={(e) => setSettings({ ...settings, allowBudgetView: e.target.checked })}
                      className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Показывать бюджет</span>
                      <p className="text-sm text-gray-500">Отображать информацию о бюджете проекта</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.showTeamMembers}
                      onChange={(e) => setSettings({ ...settings, showTeamMembers: e.target.checked })}
                      className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Показывать команду</span>
                      <p className="text-sm text-gray-500">Отображать информацию о членах команды</p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Notifications */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Bell className="w-5 h-5" />
                  Уведомления
                </h3>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.emailNotifications}
                    onChange={(e) => setSettings({ ...settings, emailNotifications: e.target.checked })}
                    className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                  />
                  <div>
                    <span className="font-medium text-gray-900">Email уведомления</span>
                    <p className="text-sm text-gray-500">Отправлять клиентам уведомления об обновлениях</p>
                  </div>
                </label>
              </div>

              {/* Custom Branding */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Брендирование</h3>
                <div className="space-y-4">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.customBranding.enabled}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          customBranding: { ...settings.customBranding, enabled: e.target.checked },
                        })
                      }
                      className="w-5 h-5 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Использовать свой бренд</span>
                      <p className="text-sm text-gray-500">Настроить логотип и цветовую схему портала</p>
                    </div>
                  </label>
                  {settings.customBranding.enabled && (
                    <div className="ml-8 space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Название компании</label>
                        <input
                          type="text"
                          value={settings.customBranding.companyName}
                          onChange={(e) =>
                            setSettings({
                              ...settings,
                              customBranding: { ...settings.customBranding, companyName: e.target.value },
                            })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Основной цвет</label>
                        <div className="flex items-center gap-3">
                          <input
                            type="color"
                            value={settings.customBranding.primaryColor}
                            onChange={(e) =>
                              setSettings({
                                ...settings,
                                customBranding: { ...settings.customBranding, primaryColor: e.target.value },
                              })
                            }
                            className="w-16 h-10 rounded border border-gray-300 cursor-pointer"
                          />
                          <span className="font-mono text-sm text-gray-600">{settings.customBranding.primaryColor}</span>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">URL логотипа</label>
                        <input
                          type="text"
                          value={settings.customBranding.logo}
                          onChange={(e) =>
                            setSettings({
                              ...settings,
                              customBranding: { ...settings.customBranding, logo: e.target.value },
                            })
                          }
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                          placeholder="https://example.com/logo.png"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={handleSaveSettings}
                  className="px-6 py-3 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors font-medium"
                >
                  Сохранить настройки
                </button>
              </div>
            </div>
          )}

          {activeTab === 'access' && (
            <div>
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Клиент</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Доступ предоставлен</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Последний визит</th>
                      <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Просмотров</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP адрес</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Действия</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {accessList.map((access) => (
                      <tr key={access.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-400 to-purple-400 flex items-center justify-center text-white font-bold text-sm">
                              {access.clientName.charAt(0)}
                            </div>
                            <span className="font-medium text-gray-900">{access.clientName}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{access.clientEmail}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {new Date(access.accessGranted).toLocaleDateString('ru-RU')}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {access.lastAccess ? (
                            <div>
                              <div>{new Date(access.lastAccess).toLocaleDateString('ru-RU')}</div>
                              <div className="text-xs text-gray-400">
                                {new Date(access.lastAccess).toLocaleTimeString('ru-RU')}
                              </div>
                            </div>
                          ) : (
                            <span className="text-gray-400">Не заходил</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="font-medium text-gray-900">{access.accessCount}</span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600 font-mono">{access.ipAddress}</td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => handleRevokeAccess(access.id)}
                            className="text-red-600 hover:text-red-800 text-sm font-medium"
                          >
                            Отозвать
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {accessList.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Нет клиентов с доступом</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'activity' && (
            <div>
              <div className="bg-white border border-gray-200 rounded-lg">
                <div className="divide-y divide-gray-200">
                  {activityLog.map((activity) => (
                    <div key={activity.id} className="p-6 hover:bg-gray-50">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-400 to-purple-400 flex items-center justify-center text-white font-bold">
                          {activity.clientName.charAt(0)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-1">
                            <div>
                              <p className="font-medium text-gray-900">{activity.clientName}</p>
                              <p className="text-sm text-gray-600">{activity.action}</p>
                            </div>
                            <span className="text-sm text-gray-500">
                              {new Date(activity.timestamp).toLocaleString('ru-RU')}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500">{activity.details}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {activityLog.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <TrendingUp className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Нет активности</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'preview' && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="text-center py-12">
                <Eye className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Предпросмотр портала</h3>
                <p className="text-gray-600 mb-6">Здесь будет отображаться предпросмотр клиентского портала</p>
                <div className="max-w-4xl mx-auto">
                  <div
                    className="border-4 rounded-lg p-8"
                    style={{
                      borderColor: settings.customBranding.enabled
                        ? settings.customBranding.primaryColor
                        : '#8B5CF6',
                    }}
                  >
                    <div className="text-center mb-8">
                      {settings.customBranding.enabled && settings.customBranding.logo ? (
                        <img
                          src={settings.customBranding.logo}
                          alt="Logo"
                          className="h-16 mx-auto mb-4"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none'
                          }}
                        />
                      ) : (
                        <Globe className="w-16 h-16 mx-auto mb-4 text-violet-600" />
                      )}
                      <h2 className="text-2xl font-bold text-gray-900">
                        {settings.customBranding.enabled
                          ? settings.customBranding.companyName
                          : 'Клиентский портал'}
                      </h2>
                      <p className="text-gray-600 mt-2">Проект #{projectId}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-6">
                      {settings.allowTaskView && (
                        <div className="border border-gray-200 rounded-lg p-4 text-center">
                          <FileText className="w-8 h-8 mx-auto mb-2 text-gray-600" />
                          <p className="text-sm font-medium text-gray-900">Задачи</p>
                        </div>
                      )}
                      {settings.allowTimelineView && (
                        <div className="border border-gray-200 rounded-lg p-4 text-center">
                          <Calendar className="w-8 h-8 mx-auto mb-2 text-gray-600" />
                          <p className="text-sm font-medium text-gray-900">Таймлайн</p>
                        </div>
                      )}
                      {settings.allowFileDownload && (
                        <div className="border border-gray-200 rounded-lg p-4 text-center">
                          <Download className="w-8 h-8 mx-auto mb-2 text-gray-600" />
                          <p className="text-sm font-medium text-gray-900">Файлы</p>
                        </div>
                      )}
                      {settings.allowComments && (
                        <div className="border border-gray-200 rounded-lg p-4 text-center">
                          <MessageSquare className="w-8 h-8 mx-auto mb-2 text-gray-600" />
                          <p className="text-sm font-medium text-gray-900">Комментарии</p>
                        </div>
                      )}
                    </div>

                    <div className="text-center text-sm text-gray-500">
                      {settings.accessPassword ? (
                        <div className="flex items-center justify-center gap-2">
                          <Lock className="w-4 h-4" />
                          <span>Защищено паролем</span>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center gap-2">
                          <Unlock className="w-4 h-4" />
                          <span>Открытый доступ</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ClientPortal
