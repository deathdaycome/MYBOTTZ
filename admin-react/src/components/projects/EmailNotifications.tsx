import { useState, useEffect } from 'react'
import { X, Mail, Bell, CheckCircle, Clock, AlertTriangle, Users, FileText } from 'lucide-react'

interface NotificationSetting {
  id: string
  name: string
  description: string
  enabled: boolean
  icon: any
  category: 'projects' | 'tasks' | 'payments' | 'team'
}

interface EmailNotificationsProps {
  isOpen: boolean
  onClose: () => void
}

const DEFAULT_SETTINGS: NotificationSetting[] = [
  // Projects
  {
    id: 'project_created',
    name: 'Создание проекта',
    description: 'Уведомление при создании нового проекта',
    enabled: true,
    icon: FileText,
    category: 'projects',
  },
  {
    id: 'project_status_changed',
    name: 'Изменение статуса проекта',
    description: 'Уведомление при изменении статуса проекта',
    enabled: true,
    icon: AlertTriangle,
    category: 'projects',
  },
  {
    id: 'project_deadline_approaching',
    name: 'Приближение дедлайна',
    description: 'Уведомление за 3 дня до дедлайна проекта',
    enabled: true,
    icon: Clock,
    category: 'projects',
  },
  {
    id: 'project_completed',
    name: 'Завершение проекта',
    description: 'Уведомление при завершении проекта',
    enabled: true,
    icon: CheckCircle,
    category: 'projects',
  },
  {
    id: 'project_assigned',
    name: 'Назначение проекта',
    description: 'Уведомление при назначении вам проекта',
    enabled: true,
    icon: Users,
    category: 'projects',
  },

  // Tasks
  {
    id: 'task_created',
    name: 'Создание задачи',
    description: 'Уведомление при создании новой задачи в проекте',
    enabled: true,
    icon: FileText,
    category: 'tasks',
  },
  {
    id: 'task_assigned',
    name: 'Назначение задачи',
    description: 'Уведомление при назначении вам задачи',
    enabled: true,
    icon: Users,
    category: 'tasks',
  },
  {
    id: 'task_deadline_approaching',
    name: 'Приближение дедлайна задачи',
    description: 'Уведомление за 1 день до дедлайна задачи',
    enabled: true,
    icon: Clock,
    category: 'tasks',
  },
  {
    id: 'task_completed',
    name: 'Завершение задачи',
    description: 'Уведомление при завершении задачи',
    enabled: false,
    icon: CheckCircle,
    category: 'tasks',
  },
  {
    id: 'task_comment_added',
    name: 'Новый комментарий к задаче',
    description: 'Уведомление при добавлении комментария к задаче',
    enabled: false,
    icon: Mail,
    category: 'tasks',
  },

  // Payments
  {
    id: 'payment_received',
    name: 'Получение оплаты',
    description: 'Уведомление при получении оплаты по проекту',
    enabled: true,
    icon: CheckCircle,
    category: 'payments',
  },
  {
    id: 'payment_due',
    name: 'Ожидание оплаты',
    description: 'Напоминание об ожидаемой оплате',
    enabled: true,
    icon: Clock,
    category: 'payments',
  },
  {
    id: 'payment_overdue',
    name: 'Просроченная оплата',
    description: 'Уведомление о просроченной оплате',
    enabled: true,
    icon: AlertTriangle,
    category: 'payments',
  },

  // Team
  {
    id: 'team_member_added',
    name: 'Добавление участника',
    description: 'Уведомление при добавлении нового участника в проект',
    enabled: false,
    icon: Users,
    category: 'team',
  },
  {
    id: 'team_member_removed',
    name: 'Удаление участника',
    description: 'Уведомление при удалении участника из проекта',
    enabled: false,
    icon: Users,
    category: 'team',
  },
  {
    id: 'team_mention',
    name: 'Упоминание в комментарии',
    description: 'Уведомление при упоминании вас в комментарии',
    enabled: true,
    icon: Bell,
    category: 'team',
  },
]

export const EmailNotifications = ({ isOpen, onClose }: EmailNotificationsProps) => {
  const [settings, setSettings] = useState<NotificationSetting[]>(DEFAULT_SETTINGS)
  const [emailAddress, setEmailAddress] = useState('admin@example.com')
  const [emailFrequency, setEmailFrequency] = useState<'instant' | 'daily' | 'weekly'>('instant')
  const [quietHoursEnabled, setQuietHoursEnabled] = useState(false)
  const [quietHoursStart, setQuietHoursStart] = useState('22:00')
  const [quietHoursEnd, setQuietHoursEnd] = useState('08:00')
  const [saving, setSaving] = useState(false)
  const [testEmailSending, setTestEmailSending] = useState(false)

  useEffect(() => {
    if (isOpen) {
      loadSettings()
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

  const loadSettings = async () => {
    try {
      const response = await fetch('http://localhost:8001/admin/api/notification-settings', {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        if (data.settings) {
          setSettings(data.settings)
        }
        if (data.email) setEmailAddress(data.email)
        if (data.frequency) setEmailFrequency(data.frequency)
        if (data.quietHours) {
          setQuietHoursEnabled(data.quietHours.enabled)
          setQuietHoursStart(data.quietHours.start)
          setQuietHoursEnd(data.quietHours.end)
        }
      }
    } catch (err) {
      console.error('Error loading settings:', err)
    }
  }

  const handleToggleSetting = (id: string) => {
    setSettings((prev) =>
      prev.map((s) => (s.id === id ? { ...s, enabled: !s.enabled } : s))
    )
  }

  const handleSaveSettings = async () => {
    setSaving(true)
    try {
      const response = await fetch('http://localhost:8001/admin/api/notification-settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({
          settings,
          email: emailAddress,
          frequency: emailFrequency,
          quietHours: {
            enabled: quietHoursEnabled,
            start: quietHoursStart,
            end: quietHoursEnd,
          },
        }),
      })

      if (response.ok) {
        alert('Настройки сохранены успешно!')
      } else {
        alert('Ошибка сохранения настроек')
      }
    } catch (err) {
      console.error('Error saving settings:', err)
      alert('Ошибка сохранения настроек')
    } finally {
      setSaving(false)
    }
  }

  const handleSendTestEmail = async () => {
    setTestEmailSending(true)
    try {
      const response = await fetch('http://localhost:8001/admin/api/test-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify({ email: emailAddress }),
      })

      if (response.ok) {
        alert('Тестовое письмо отправлено на ' + emailAddress)
      } else {
        alert('Ошибка отправки тестового письма')
      }
    } catch (err) {
      console.error('Error sending test email:', err)
      alert('Ошибка отправки тестового письма')
    } finally {
      setTestEmailSending(false)
    }
  }

  const handleEnableAll = (category: string) => {
    setSettings((prev) =>
      prev.map((s) => (s.category === category ? { ...s, enabled: true } : s))
    )
  }

  const handleDisableAll = (category: string) => {
    setSettings((prev) =>
      prev.map((s) => (s.category === category ? { ...s, enabled: false } : s))
    )
  }

  if (!isOpen) return null

  const categories = {
    projects: { name: 'Проекты', icon: FileText },
    tasks: { name: 'Задачи', icon: CheckCircle },
    payments: { name: 'Оплаты', icon: AlertTriangle },
    team: { name: 'Команда', icon: Users },
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Mail className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Email-уведомления</h3>
              <p className="text-blue-100 text-sm mt-1">
                Настройте, какие события будут отправляться на почту
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
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Email Settings */}
          <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
            <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Mail className="w-5 h-5 text-blue-600" />
              Настройки почты
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Email-адрес
                </label>
                <input
                  type="email"
                  value={emailAddress}
                  onChange={(e) => setEmailAddress(e.target.value)}
                  className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                  placeholder="your@email.com"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Частота отправки
                </label>
                <select
                  value={emailFrequency}
                  onChange={(e) => setEmailFrequency(e.target.value as any)}
                  className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                >
                  <option value="instant">Мгновенно</option>
                  <option value="daily">Ежедневная сводка</option>
                  <option value="weekly">Еженедельная сводка</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={quietHoursEnabled}
                  onChange={(e) => setQuietHoursEnabled(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-semibold text-gray-700">
                  Тихие часы (не отправлять уведомления)
                </span>
              </label>

              {quietHoursEnabled && (
                <div className="mt-3 grid grid-cols-2 gap-4 pl-7">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">С</label>
                    <input
                      type="time"
                      value={quietHoursStart}
                      onChange={(e) => setQuietHoursStart(e.target.value)}
                      className="w-full px-3 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">До</label>
                    <input
                      type="time"
                      value={quietHoursEnd}
                      onChange={(e) => setQuietHoursEnd(e.target.value)}
                      className="w-full px-3 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none text-sm"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={handleSendTestEmail}
                disabled={testEmailSending}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold text-sm disabled:opacity-50"
              >
                <Bell className="w-4 h-4" />
                {testEmailSending ? 'Отправка...' : 'Отправить тестовое письмо'}
              </button>
            </div>
          </div>

          {/* Notification Categories */}
          {Object.entries(categories).map(([categoryKey, categoryData]) => {
            const categorySettings = settings.filter((s) => s.category === categoryKey)
            const enabledCount = categorySettings.filter((s) => s.enabled).length

            return (
              <div key={categoryKey} className="bg-gray-50 border-2 border-gray-200 rounded-xl p-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-bold text-gray-900 flex items-center gap-2">
                    <categoryData.icon className="w-5 h-5 text-gray-600" />
                    {categoryData.name}
                    <span className="text-sm font-normal text-gray-500">
                      ({enabledCount}/{categorySettings.length})
                    </span>
                  </h4>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEnableAll(categoryKey)}
                      className="text-xs px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold"
                    >
                      Включить все
                    </button>
                    <button
                      onClick={() => handleDisableAll(categoryKey)}
                      className="text-xs px-3 py-1 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                    >
                      Выключить все
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  {categorySettings.map((setting) => (
                    <label
                      key={setting.id}
                      className="flex items-start gap-3 p-3 bg-white rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={setting.enabled}
                        onChange={() => handleToggleSetting(setting.id)}
                        className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <setting.icon className="w-4 h-4 text-gray-500" />
                          <span className="font-semibold text-gray-900 text-sm">
                            {setting.name}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">{setting.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )
          })}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="text-sm text-gray-600">
            Включено:{' '}
            <span className="font-bold text-blue-600">
              {settings.filter((s) => s.enabled).length}/{settings.length}
            </span>{' '}
            уведомлений
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
            >
              Отмена
            </button>
            <button
              onClick={handleSaveSettings}
              disabled={saving}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-semibold disabled:opacity-50"
            >
              {saving ? 'Сохранение...' : 'Сохранить настройки'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
