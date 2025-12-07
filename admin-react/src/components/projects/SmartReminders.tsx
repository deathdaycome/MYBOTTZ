import { useState, useEffect } from 'react'
import {
  X,
  Bell,
  Plus,
  Trash2,
  Edit2,
  Check,
  Clock,
  Calendar,
  Repeat,
  AlertCircle,
  CheckCircle,
  User,
  ToggleLeft,
  ToggleRight,
} from 'lucide-react'

interface Reminder {
  id: number
  title: string
  description: string
  triggerType: 'date' | 'deadline' | 'status' | 'budget' | 'custom'
  triggerValue: string
  repeatType: 'once' | 'daily' | 'weekly' | 'monthly'
  recipients: string[]
  isActive: boolean
  lastTriggered?: string
  createdAt: string
  createdBy: string
}

interface SmartRemindersProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

const TRIGGER_TYPES = [
  { value: 'date', label: 'Конкретная дата', icon: Calendar },
  { value: 'deadline', label: 'До дедлайна', icon: Clock },
  { value: 'status', label: 'Изменение статуса', icon: CheckCircle },
  { value: 'budget', label: 'Бюджет', icon: AlertCircle },
  { value: 'custom', label: 'Пользовательское', icon: Bell },
]

const REPEAT_OPTIONS = [
  { value: 'once', label: 'Один раз' },
  { value: 'daily', label: 'Ежедневно' },
  { value: 'weekly', label: 'Еженедельно' },
  { value: 'monthly', label: 'Ежемесячно' },
]

const STATUS_OPTIONS = [
  'planned',
  'in_progress',
  'review',
  'testing',
  'completed',
  'on_hold',
  'cancelled',
]

export const SmartReminders = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: SmartRemindersProps) => {
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [isAdding, setIsAdding] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    triggerType: 'date' as const,
    triggerValue: '',
    repeatType: 'once' as const,
    recipients: [] as string[],
  })
  const [newRecipient, setNewRecipient] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && projectId) {
      loadReminders()
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

  const loadReminders = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/reminders`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setReminders(data.reminders || [])
      } else {
        // Mock data
        setReminders([
          {
            id: 1,
            title: 'Напоминание о дедлайне',
            description: 'Уведомить за 3 дня до крайнего срока',
            triggerType: 'deadline',
            triggerValue: '3',
            repeatType: 'once',
            recipients: ['admin@example.com', 'manager@example.com'],
            isActive: true,
            lastTriggered: new Date(Date.now() - 86400000).toISOString(),
            createdAt: new Date(Date.now() - 86400000 * 7).toISOString(),
            createdBy: 'admin',
          },
          {
            id: 2,
            title: 'Проверка бюджета',
            description: 'Оповестить при использовании 80% бюджета',
            triggerType: 'budget',
            triggerValue: '80',
            repeatType: 'once',
            recipients: ['admin@example.com'],
            isActive: true,
            createdAt: new Date(Date.now() - 86400000 * 14).toISOString(),
            createdBy: 'admin',
          },
          {
            id: 3,
            title: 'Еженедельный отчет',
            description: 'Отправлять отчет о прогрессе каждый понедельник',
            triggerType: 'date',
            triggerValue: 'monday',
            repeatType: 'weekly',
            recipients: ['admin@example.com', 'client@example.com'],
            isActive: true,
            lastTriggered: new Date(Date.now() - 86400000 * 2).toISOString(),
            createdAt: new Date(Date.now() - 86400000 * 21).toISOString(),
            createdBy: 'admin',
          },
          {
            id: 4,
            title: 'Смена статуса на "Завершен"',
            description: 'Уведомить всю команду при завершении проекта',
            triggerType: 'status',
            triggerValue: 'completed',
            repeatType: 'once',
            recipients: ['team@example.com'],
            isActive: false,
            createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
            createdBy: 'admin',
          },
        ])
      }
    } catch (err) {
      console.error('Error loading reminders:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddReminder = async () => {
    if (!formData.title.trim()) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/reminders`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify(formData),
        }
      )

      if (response.ok) {
        setFormData({
          title: '',
          description: '',
          triggerType: 'date',
          triggerValue: '',
          repeatType: 'once',
          recipients: [],
        })
        setIsAdding(false)
        await loadReminders()
      }
    } catch (err) {
      console.error('Error adding reminder:', err)
    }
  }

  const handleToggleActive = async (reminderId: number, isActive: boolean) => {
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/reminders/${reminderId}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify({ isActive }),
        }
      )

      if (response.ok) {
        await loadReminders()
      }
    } catch (err) {
      console.error('Error toggling reminder:', err)
    }
  }

  const handleDeleteReminder = async (reminderId: number) => {
    if (!confirm('Удалить это напоминание?')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/reminders/${reminderId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadReminders()
      }
    } catch (err) {
      console.error('Error deleting reminder:', err)
    }
  }

  const handleAddRecipient = () => {
    if (newRecipient.trim() && !formData.recipients.includes(newRecipient.trim())) {
      setFormData({
        ...formData,
        recipients: [...formData.recipients, newRecipient.trim()],
      })
      setNewRecipient('')
    }
  }

  const handleRemoveRecipient = (recipient: string) => {
    setFormData({
      ...formData,
      recipients: formData.recipients.filter((r) => r !== recipient),
    })
  }

  const renderTriggerInput = () => {
    switch (formData.triggerType) {
      case 'date':
        return (
          <input
            type="datetime-local"
            value={formData.triggerValue}
            onChange={(e) => setFormData({ ...formData, triggerValue: e.target.value })}
            className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
          />
        )

      case 'deadline':
        return (
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={formData.triggerValue}
              onChange={(e) => setFormData({ ...formData, triggerValue: e.target.value })}
              className="flex-1 px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
              placeholder="Количество дней"
              min="1"
            />
            <span className="text-sm text-gray-600">дней до дедлайна</span>
          </div>
        )

      case 'status':
        return (
          <select
            value={formData.triggerValue}
            onChange={(e) => setFormData({ ...formData, triggerValue: e.target.value })}
            className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
          >
            <option value="">Выберите статус</option>
            {STATUS_OPTIONS.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        )

      case 'budget':
        return (
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={formData.triggerValue}
              onChange={(e) => setFormData({ ...formData, triggerValue: e.target.value })}
              className="flex-1 px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
              placeholder="Процент бюджета"
              min="1"
              max="100"
            />
            <span className="text-sm text-gray-600">% бюджета использовано</span>
          </div>
        )

      case 'custom':
        return (
          <input
            type="text"
            value={formData.triggerValue}
            onChange={(e) => setFormData({ ...formData, triggerValue: e.target.value })}
            className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
            placeholder="Пользовательское условие"
          />
        )

      default:
        return null
    }
  }

  const getTriggerLabel = (reminder: Reminder): string => {
    switch (reminder.triggerType) {
      case 'date':
        return `Дата: ${new Date(reminder.triggerValue).toLocaleDateString('ru-RU')}`
      case 'deadline':
        return `За ${reminder.triggerValue} дней до дедлайна`
      case 'status':
        return `Статус: ${reminder.triggerValue}`
      case 'budget':
        return `Бюджет: ${reminder.triggerValue}%`
      case 'custom':
        return reminder.triggerValue
      default:
        return 'Неизвестно'
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

  const activeReminders = reminders.filter((r) => r.isActive).length

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Bell className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Умные напоминания</h3>
              <p className="text-blue-100 text-sm mt-1">{projectName}</p>
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

        {/* Stats */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-gray-600" />
              <span className="text-gray-600">Всего:</span>
              <span className="font-bold text-blue-600">{reminders.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-gray-600">Активных:</span>
              <span className="font-bold text-green-600">{activeReminders}</span>
            </div>
          </div>

          {!isAdding && (
            <button
              onClick={() => setIsAdding(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold text-sm"
            >
              <Plus className="w-4 h-4" />
              Добавить напоминание
            </button>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Add Reminder Form */}
          {isAdding && (
            <div className="mb-6 bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
              <h4 className="font-bold text-gray-900 mb-4">Новое напоминание</h4>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Название
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
                    placeholder="Краткое название напоминания"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Описание
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none resize-none"
                    rows={2}
                    placeholder="Подробное описание"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Тип триггера
                    </label>
                    <select
                      value={formData.triggerType}
                      onChange={(e) =>
                        setFormData({ ...formData, triggerType: e.target.value as any })
                      }
                      className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
                    >
                      {TRIGGER_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">
                      Повторение
                    </label>
                    <select
                      value={formData.repeatType}
                      onChange={(e) =>
                        setFormData({ ...formData, repeatType: e.target.value as any })
                      }
                      className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
                    >
                      {REPEAT_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Условие срабатывания
                  </label>
                  {renderTriggerInput()}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Получатели
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="email"
                      value={newRecipient}
                      onChange={(e) => setNewRecipient(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddRecipient()}
                      className="flex-1 px-4 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 outline-none"
                      placeholder="Email получателя"
                    />
                    <button
                      onClick={handleAddRecipient}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                  {formData.recipients.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {formData.recipients.map((recipient) => (
                        <span
                          key={recipient}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold flex items-center gap-2"
                        >
                          <User className="w-3.5 h-3.5" />
                          {recipient}
                          <button
                            onClick={() => handleRemoveRecipient(recipient)}
                            className="hover:text-blue-900"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleAddReminder}
                    disabled={!formData.title.trim() || formData.recipients.length === 0}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-semibold"
                  >
                    <Check className="w-4 h-4" />
                    Создать
                  </button>
                  <button
                    onClick={() => {
                      setIsAdding(false)
                      setFormData({
                        title: '',
                        description: '',
                        triggerType: 'date',
                        triggerValue: '',
                        repeatType: 'once',
                        recipients: [],
                      })
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Reminders List */}
          {loading ? (
            <div className="text-center py-12 text-gray-500">Загрузка напоминаний...</div>
          ) : reminders.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg font-semibold">Нет напоминаний</p>
              <p className="text-sm mt-2">Создайте первое умное напоминание</p>
            </div>
          ) : (
            <div className="space-y-3">
              {reminders.map((reminder) => {
                const TriggerIcon =
                  TRIGGER_TYPES.find((t) => t.value === reminder.triggerType)?.icon || Bell

                return (
                  <div
                    key={reminder.id}
                    className={`bg-white border-2 rounded-xl p-4 transition-all ${
                      reminder.isActive
                        ? 'border-blue-400 hover:border-blue-500'
                        : 'border-gray-200 opacity-60'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3 flex-1">
                        <div
                          className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                            reminder.isActive ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
                          }`}
                        >
                          <TriggerIcon className="w-5 h-5" />
                        </div>

                        <div className="flex-1">
                          <h5 className="font-bold text-gray-900 text-lg mb-1">
                            {reminder.title}
                          </h5>
                          {reminder.description && (
                            <p className="text-sm text-gray-700 mb-2">{reminder.description}</p>
                          )}

                          <div className="flex flex-wrap gap-2 mb-2">
                            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold">
                              {getTriggerLabel(reminder)}
                            </span>
                            <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold flex items-center gap-1">
                              <Repeat className="w-3 h-3" />
                              {REPEAT_OPTIONS.find((o) => o.value === reminder.repeatType)?.label}
                            </span>
                            <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold flex items-center gap-1">
                              <User className="w-3 h-3" />
                              {reminder.recipients.length} получателей
                            </span>
                          </div>

                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <div className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5" />
                              <span>Создано: {formatDate(reminder.createdAt)}</span>
                            </div>
                            {reminder.lastTriggered && (
                              <div className="flex items-center gap-1">
                                <Bell className="w-3.5 h-3.5" />
                                <span>Сработало: {formatDate(reminder.lastTriggered)}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => handleToggleActive(reminder.id, !reminder.isActive)}
                          className={`p-2 rounded-lg transition-colors ${
                            reminder.isActive
                              ? 'text-green-600 hover:bg-green-100'
                              : 'text-gray-400 hover:bg-gray-100'
                          }`}
                          title={reminder.isActive ? 'Деактивировать' : 'Активировать'}
                        >
                          {reminder.isActive ? (
                            <ToggleRight className="w-5 h-5" />
                          ) : (
                            <ToggleLeft className="w-5 h-5" />
                          )}
                        </button>
                        <button
                          onClick={() => handleDeleteReminder(reminder.id)}
                          className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <AlertCircle className="w-4 h-4" />
            <span>Напоминания отправляются автоматически при срабатывании условий</span>
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
