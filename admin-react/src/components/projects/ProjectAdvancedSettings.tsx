import { useState, useEffect } from 'react'
import { X, Settings, Save, AlertCircle, CheckCircle, Globe, Lock, Bell, Users } from 'lucide-react'

interface ProjectSettings {
  // Privacy
  visibility: 'private' | 'team' | 'organization' | 'public'
  allowGuestView: boolean
  requireApproval: boolean

  // Notifications
  notifyOnStatusChange: boolean
  notifyOnDeadline: boolean
  notifyOnBudgetAlert: boolean
  emailDigest: 'none' | 'daily' | 'weekly'

  // Permissions
  allowTaskCreation: 'owner' | 'team' | 'all'
  allowComments: 'owner' | 'team' | 'all'
  allowFileUpload: 'owner' | 'team' | 'all'

  // Automation
  autoArchiveCompleted: boolean
  autoArchiveDays: number
  autoStatusChange: boolean
  autoAssignTasks: boolean

  // Integration
  slackNotifications: boolean
  slackWebhook: string
  githubIntegration: boolean
  githubRepo: string

  // Custom fields
  customFields: Array<{
    id: number
    name: string
    type: 'text' | 'number' | 'date' | 'select'
    required: boolean
    options?: string[]
  }>
}

interface ProjectAdvancedSettingsProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

export const ProjectAdvancedSettings = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: ProjectAdvancedSettingsProps) => {
  const [settings, setSettings] = useState<ProjectSettings>({
    visibility: 'team',
    allowGuestView: false,
    requireApproval: true,
    notifyOnStatusChange: true,
    notifyOnDeadline: true,
    notifyOnBudgetAlert: true,
    emailDigest: 'daily',
    allowTaskCreation: 'team',
    allowComments: 'all',
    allowFileUpload: 'team',
    autoArchiveCompleted: false,
    autoArchiveDays: 30,
    autoStatusChange: false,
    autoAssignTasks: false,
    slackNotifications: false,
    slackWebhook: '',
    githubIntegration: false,
    githubRepo: '',
    customFields: [],
  })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState<'privacy' | 'notifications' | 'permissions' | 'automation' | 'integration'>('privacy')

  useEffect(() => {
    if (isOpen && projectId) {
      loadSettings()
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

  const loadSettings = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/settings`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setSettings(data.settings || settings)
      }
    } catch (err) {
      console.error('Error loading settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/settings`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify(settings),
        }
      )

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

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-gray-700 to-gray-900 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Расширенные настройки</h3>
              <p className="text-gray-300 text-sm mt-1">{projectName}</p>
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

        {/* Tabs */}
        <div className="flex border-b border-gray-200 bg-gray-50 flex-shrink-0 overflow-x-auto">
          {[
            { key: 'privacy', label: 'Приватность', icon: Lock },
            { key: 'notifications', label: 'Уведомления', icon: Bell },
            { key: 'permissions', label: 'Доступы', icon: Users },
            { key: 'automation', label: 'Автоматизация', icon: Settings },
            { key: 'integration', label: 'Интеграции', icon: Globe },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-6 py-3 font-semibold whitespace-nowrap transition-colors ${
                activeTab === tab.key
                  ? 'bg-white border-b-2 border-gray-700 text-gray-900'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Загрузка настроек...</div>
          ) : (
            <>
              {/* Privacy Settings */}
              {activeTab === 'privacy' && (
                <div className="space-y-6">
                  <div>
                    <h4 className="font-bold text-gray-900 mb-4">Видимость проекта</h4>
                    <div className="space-y-3">
                      {[
                        { value: 'private', label: 'Приватный', desc: 'Доступ только владельцу' },
                        { value: 'team', label: 'Команда', desc: 'Доступ членам команды' },
                        { value: 'organization', label: 'Организация', desc: 'Доступ всей организации' },
                        { value: 'public', label: 'Публичный', desc: 'Доступ всем' },
                      ].map((option) => (
                        <label
                          key={option.value}
                          className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                        >
                          <input
                            type="radio"
                            name="visibility"
                            value={option.value}
                            checked={settings.visibility === option.value}
                            onChange={(e) =>
                              setSettings({ ...settings, visibility: e.target.value as any })
                            }
                            className="w-5 h-5"
                          />
                          <div>
                            <div className="font-semibold text-gray-900">{option.label}</div>
                            <div className="text-sm text-gray-600">{option.desc}</div>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.allowGuestView}
                        onChange={(e) =>
                          setSettings({ ...settings, allowGuestView: e.target.checked })
                        }
                        className="w-5 h-5"
                      />
                      <div>
                        <div className="font-semibold text-gray-900">Разрешить гостевой просмотр</div>
                        <div className="text-sm text-gray-600">Гости могут просматривать без авторизации</div>
                      </div>
                    </label>

                    <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.requireApproval}
                        onChange={(e) =>
                          setSettings({ ...settings, requireApproval: e.target.checked })
                        }
                        className="w-5 h-5"
                      />
                      <div>
                        <div className="font-semibold text-gray-900">Требовать одобрение доступа</div>
                        <div className="text-sm text-gray-600">Новые участники требуют одобрения</div>
                      </div>
                    </label>
                  </div>
                </div>
              )}

              {/* Notifications Settings */}
              {activeTab === 'notifications' && (
                <div className="space-y-6">
                  <div className="space-y-3">
                    <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifyOnStatusChange}
                        onChange={(e) =>
                          setSettings({ ...settings, notifyOnStatusChange: e.target.checked })
                        }
                        className="w-5 h-5"
                      />
                      <div>
                        <div className="font-semibold text-gray-900">Уведомлять об изменении статуса</div>
                        <div className="text-sm text-gray-600">Отправлять уведомления при смене статуса</div>
                      </div>
                    </label>

                    <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifyOnDeadline}
                        onChange={(e) =>
                          setSettings({ ...settings, notifyOnDeadline: e.target.checked })
                        }
                        className="w-5 h-5"
                      />
                      <div>
                        <div className="font-semibold text-gray-900">Уведомлять о приближении дедлайна</div>
                        <div className="text-sm text-gray-600">Напоминание за 3 дня до дедлайна</div>
                      </div>
                    </label>

                    <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifyOnBudgetAlert}
                        onChange={(e) =>
                          setSettings({ ...settings, notifyOnBudgetAlert: e.target.checked })
                        }
                        className="w-5 h-5"
                      />
                      <div>
                        <div className="font-semibold text-gray-900">Уведомлять о превышении бюджета</div>
                        <div className="text-sm text-gray-600">Предупреждение при 80% использования</div>
                      </div>
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Email-дайджест
                    </label>
                    <select
                      value={settings.emailDigest}
                      onChange={(e) => setSettings({ ...settings, emailDigest: e.target.value as any })}
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-gray-500 outline-none"
                    >
                      <option value="none">Отключен</option>
                      <option value="daily">Ежедневно</option>
                      <option value="weekly">Еженедельно</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Permissions Settings */}
              {activeTab === 'permissions' && (
                <div className="space-y-6">
                  {[
                    { key: 'allowTaskCreation', label: 'Создание задач' },
                    { key: 'allowComments', label: 'Комментарии' },
                    { key: 'allowFileUpload', label: 'Загрузка файлов' },
                  ].map((perm) => (
                    <div key={perm.key}>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        {perm.label}
                      </label>
                      <select
                        value={settings[perm.key as keyof typeof settings] as string}
                        onChange={(e) =>
                          setSettings({ ...settings, [perm.key]: e.target.value as any })
                        }
                        className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-gray-500 outline-none"
                      >
                        <option value="owner">Только владелец</option>
                        <option value="team">Команда проекта</option>
                        <option value="all">Все пользователи</option>
                      </select>
                    </div>
                  ))}
                </div>
              )}

              {/* Automation Settings */}
              {activeTab === 'automation' && (
                <div className="space-y-3">
                  <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.autoArchiveCompleted}
                      onChange={(e) =>
                        setSettings({ ...settings, autoArchiveCompleted: e.target.checked })
                      }
                      className="w-5 h-5"
                    />
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">Автоархивация завершенных проектов</div>
                      <div className="text-sm text-gray-600">Архивировать через:</div>
                      {settings.autoArchiveCompleted && (
                        <input
                          type="number"
                          value={settings.autoArchiveDays}
                          onChange={(e) =>
                            setSettings({ ...settings, autoArchiveDays: Number(e.target.value) })
                          }
                          className="mt-2 w-32 px-3 py-1 border-2 border-gray-300 rounded-lg"
                          min="1"
                        />
                      )}
                      {settings.autoArchiveCompleted && <span className="ml-2 text-sm">дней</span>}
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.autoStatusChange}
                      onChange={(e) =>
                        setSettings({ ...settings, autoStatusChange: e.target.checked })
                      }
                      className="w-5 h-5"
                    />
                    <div>
                      <div className="font-semibold text-gray-900">Автоматическая смена статуса</div>
                      <div className="text-sm text-gray-600">Менять статус при выполнении условий</div>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.autoAssignTasks}
                      onChange={(e) =>
                        setSettings({ ...settings, autoAssignTasks: e.target.checked })
                      }
                      className="w-5 h-5"
                    />
                    <div>
                      <div className="font-semibold text-gray-900">Автоназначение задач</div>
                      <div className="text-sm text-gray-600">Распределять задачи автоматически</div>
                    </div>
                  </label>
                </div>
              )}

              {/* Integration Settings */}
              {activeTab === 'integration' && (
                <div className="space-y-6">
                  <div>
                    <label className="flex items-center gap-3 mb-3">
                      <input
                        type="checkbox"
                        checked={settings.slackNotifications}
                        onChange={(e) =>
                          setSettings({ ...settings, slackNotifications: e.target.checked })
                        }
                        className="w-5 h-5"
                      />
                      <span className="font-semibold text-gray-900">Slack уведомления</span>
                    </label>
                    {settings.slackNotifications && (
                      <input
                        type="text"
                        value={settings.slackWebhook}
                        onChange={(e) => setSettings({ ...settings, slackWebhook: e.target.value })}
                        className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-gray-500 outline-none"
                        placeholder="https://hooks.slack.com/services/..."
                      />
                    )}
                  </div>

                  <div>
                    <label className="flex items-center gap-3 mb-3">
                      <input
                        type="checkbox"
                        checked={settings.githubIntegration}
                        onChange={(e) =>
                          setSettings({ ...settings, githubIntegration: e.target.checked })
                        }
                        className="w-5 h-5"
                      />
                      <span className="font-semibold text-gray-900">GitHub интеграция</span>
                    </label>
                    {settings.githubIntegration && (
                      <input
                        type="text"
                        value={settings.githubRepo}
                        onChange={(e) => setSettings({ ...settings, githubRepo: e.target.value })}
                        className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-gray-500 outline-none"
                        placeholder="owner/repository"
                      />
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <AlertCircle className="w-4 h-4" />
            <span>Изменения вступят в силу сразу после сохранения</span>
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
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-all font-semibold disabled:opacity-50"
            >
              {saving ? (
                <>
                  <Settings className="w-5 h-5 animate-spin" />
                  Сохранение...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Сохранить
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
