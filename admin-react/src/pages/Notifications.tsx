import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Bell,
  Send,
  AlertTriangle,
  BarChart3,
  MessageCircle,
  Users,
  RefreshCw,
  Settings,
  Activity,
  CheckCircle,
  XCircle,
  Loader,
  User,
  Clock,
  Zap
} from 'lucide-react'
import notificationsApi from '../api/notifications'

interface Employee {
  id: number
  username: string
  full_name: string
  email: string
  role: string
  telegram_id?: string
}

interface NotificationSettings {
  notifications_enabled: boolean
  telegram_user_id: string
  project_assigned: boolean
  project_status_changed: boolean
  project_deadline_reminder: boolean
  project_overdue: boolean
  avito_new_message: boolean
  avito_unread_reminder: boolean
  avito_urgent_message: boolean
  lead_assigned: boolean
  lead_status_changed: boolean
  deal_assigned: boolean
  deal_status_changed: boolean
  work_hours_start: string
  work_hours_end: string
  weekend_notifications: boolean
  urgent_notifications_always: boolean
  avito_reminder_interval: number
  project_reminder_interval: number
}

interface Project {
  id: number
  title: string
  status: string
}

interface LogEntry {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
  timestamp: string
}

export const Notifications = () => {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<number | null>(null)
  const [selectedStatus, setSelectedStatus] = useState('in_progress')
  const [loading, setLoading] = useState(true)
  const [botStatus, setBotStatus] = useState<{
    online: boolean
    username?: string
    checking: boolean
  }>({ online: false, checking: true })
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [employeeSettings, setEmployeeSettings] = useState<Record<number, Partial<NotificationSettings>>>({})

  // Toast notifications
  const [toasts, setToasts] = useState<Array<{ id: number; message: string; type: 'success' | 'error' | 'info' }>>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 3000)
  }, [])

  const addLog = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const newLog: LogEntry = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toLocaleString('ru-RU')
    }
    setLogs(prev => [newLog, ...prev.slice(0, 9)])
  }, [])

  // Load initial data
  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      const [employeesData, projectsData] = await Promise.all([
        notificationsApi.getEmployees(),
        notificationsApi.getProjects()
      ])
      setEmployees(employeesData)
      setProjects(projectsData)

      // Load settings for all employees
      const settingsPromises = employeesData.map(async (emp) => {
        try {
          const settings = await notificationsApi.getEmployeeSettings(emp.id)
          return { id: emp.id, settings }
        } catch (error) {
          return { id: emp.id, settings: null }
        }
      })

      const settingsResults = await Promise.all(settingsPromises)
      const settingsMap: Record<number, Partial<NotificationSettings>> = {}
      settingsResults.forEach(({ id, settings }) => {
        if (settings) {
          settingsMap[id] = settings
        }
      })
      setEmployeeSettings(settingsMap)
    } catch (error: any) {
      console.error('Error loading data:', error)
      addLog('Ошибка загрузки данных', 'error')
    } finally {
      setLoading(false)
    }
  }, [addLog])

  // Check bot status
  const checkBotStatus = useCallback(async () => {
    try {
      setBotStatus(prev => ({ ...prev, checking: true }))
      const data = await notificationsApi.getBotStatus()
      setBotStatus({
        online: data.success,
        username: data.bot_info?.username,
        checking: false
      })
    } catch (error) {
      setBotStatus({ online: false, checking: false })
    }
  }, [])

  // Test admin notification
  const testAdminNotification = useCallback(async () => {
    try {
      addLog('Отправка тестового уведомления администратору...', 'info')
      const data = await notificationsApi.testAdminNotification()
      if (data.success) {
        addLog('Тестовое уведомление отправлено', 'success')
        showToast('Уведомление отправлено', 'success')
      } else {
        addLog(`Ошибка: ${data.message}`, 'error')
        showToast('Ошибка отправки', 'error')
      }
    } catch (error: any) {
      console.error('Error:', error)
      addLog('Ошибка отправки уведомления', 'error')
      showToast('Ошибка отправки', 'error')
    }
  }, [addLog, showToast])

  // Test error notification
  const testErrorNotification = useCallback(async () => {
    try {
      addLog('Отправка тестового уведомления об ошибке...', 'info')
      const data = await notificationsApi.testErrorNotification()
      if (data.success) {
        addLog('Уведомление об ошибке отправлено', 'success')
        showToast('Уведомление отправлено', 'success')
      } else {
        addLog(`Ошибка: ${data.message}`, 'error')
        showToast('Ошибка отправки', 'error')
      }
    } catch (error: any) {
      console.error('Error:', error)
      addLog('Ошибка отправки уведомления', 'error')
      showToast('Ошибка отправки', 'error')
    }
  }, [addLog, showToast])

  // Test daily report
  const testDailyReport = useCallback(async () => {
    try {
      addLog('Отправка ежедневного отчета...', 'info')
      const data = await notificationsApi.testDailyReport()
      if (data.success) {
        addLog('Ежедневный отчет отправлен', 'success')
        showToast('Отчет отправлен', 'success')
      } else {
        addLog(`Ошибка: ${data.message}`, 'error')
        showToast('Ошибка отправки', 'error')
      }
    } catch (error: any) {
      console.error('Error:', error)
      addLog('Ошибка отправки отчета', 'error')
      showToast('Ошибка отправки', 'error')
    }
  }, [addLog, showToast])

  // Test Avito notification
  const testAvitoNotification = useCallback(async () => {
    try {
      addLog('Отправка тестового Avito уведомления...', 'info')
      const data = await notificationsApi.testAvitoNotification()
      if (data.success) {
        addLog('Avito уведомление отправлено', 'success')
        showToast('Уведомление отправлено', 'success')
      } else {
        addLog(`Ошибка: ${data.message}`, 'error')
        showToast('Ошибка отправки', 'error')
      }
    } catch (error: any) {
      console.error('Error:', error)
      addLog('Ошибка отправки Avito уведомления', 'error')
      showToast('Ошибка отправки', 'error')
    }
  }, [addLog, showToast])

  // Test status notification
  const testStatusNotification = useCallback(async () => {
    if (!selectedProject) {
      showToast('Выберите проект', 'error')
      addLog('Выберите проект', 'error')
      return
    }

    const project = projects.find(p => p.id === selectedProject)
    if (!project) {
      showToast('Проект не найден', 'error')
      return
    }

    try {
      addLog(`Тестирование смены статуса проекта #${selectedProject}...`, 'info')
      const data = await notificationsApi.updateProjectStatus(
        selectedProject,
        selectedStatus,
        'Тестовое изменение статуса из React админ-панели'
      )

      if (data.success) {
        addLog(`Статус проекта #${selectedProject} изменен`, 'success')
        showToast('Уведомление клиенту отправлено', 'success')
      } else {
        addLog(`Ошибка: ${data.message}`, 'error')
        showToast('Ошибка изменения статуса', 'error')
      }
    } catch (error: any) {
      console.error('Error:', error)
      addLog('Ошибка изменения статуса', 'error')
      showToast('Ошибка изменения статуса', 'error')
    }
  }, [selectedProject, selectedStatus, projects, addLog, showToast])

  // Update employee notification setting
  const updateEmployeeSetting = useCallback(async (
    employeeId: number,
    settingKey: string,
    value: boolean | string | number
  ) => {
    try {
      setEmployeeSettings(prev => ({
        ...prev,
        [employeeId]: {
          ...prev[employeeId],
          [settingKey]: value
        }
      }))
      addLog(`Настройка "${settingKey}" обновлена`, 'success')
    } catch (error: any) {
      console.error('Error updating setting:', error)
      addLog('Ошибка обновления настроек', 'error')
    }
  }, [addLog])

  // Save employee settings
  const saveEmployeeSettings = useCallback(async (employeeId: number) => {
    try {
      const settings = employeeSettings[employeeId]
      if (!settings) return

      await notificationsApi.updateEmployeeSettings(employeeId, settings)
      addLog('Настройки сохранены', 'success')
      showToast('Настройки сохранены', 'success')
    } catch (error: any) {
      console.error('Error saving settings:', error)
      addLog('Ошибка сохранения настроек', 'error')
      showToast('Ошибка сохранения', 'error')
    }
  }, [employeeSettings, addLog, showToast])

  // Send test notification to employee
  const sendTestToEmployee = useCallback(async (employeeId: number) => {
    try {
      const data = await notificationsApi.sendTestNotification(employeeId)
      if (data.success) {
        addLog('Тестовое уведомление отправлено сотруднику', 'success')
        showToast('Уведомление отправлено', 'success')
      } else {
        addLog(`Ошибка: ${data.error}`, 'error')
        showToast('Ошибка отправки', 'error')
      }
    } catch (error: any) {
      console.error('Error:', error)
      addLog('Ошибка отправки уведомления', 'error')
      showToast('Ошибка отправки', 'error')
    }
  }, [addLog, showToast])

  useEffect(() => {
    loadData()
    checkBotStatus()
  }, [loadData, checkBotStatus])

  const statusOptions = [
    { value: 'new', label: 'Новый', icon: '🆕' },
    { value: 'review', label: 'На рассмотрении', icon: '👀' },
    { value: 'accepted', label: 'Принят', icon: '✅' },
    { value: 'in_progress', label: 'В работе', icon: '🔄' },
    { value: 'testing', label: 'Тестирование', icon: '🧪' },
    { value: 'completed', label: 'Завершен', icon: '🎉' },
    { value: 'cancelled', label: 'Отменен', icon: '❌' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
            <Bell className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Управление уведомлениями</h1>
            <p className="text-sm text-gray-200">Настройка и тестирование системы уведомлений</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Main Panel */}
        <div className="col-span-8 space-y-6">
          {/* Admin Notifications */}
          <div className="bg-white/30 backdrop-blur-xl rounded-2xl border border-white/40 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Send className="w-6 h-6 text-blue-400" />
              <h2 className="text-xl font-bold text-white">Уведомления администратору</h2>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <button
                onClick={testAdminNotification}
                className="px-6 py-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 rounded-xl text-white transition-all flex items-center justify-center gap-2 font-medium"
              >
                <Send className="w-5 h-5" />
                Тестовое уведомление
              </button>
              <button
                onClick={testErrorNotification}
                className="px-6 py-4 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 rounded-xl text-white transition-all flex items-center justify-center gap-2 font-medium"
              >
                <AlertTriangle className="w-5 h-5" />
                Тестовая ошибка
              </button>
              <button
                onClick={testDailyReport}
                className="px-6 py-4 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 rounded-xl text-white transition-all flex items-center justify-center gap-2 font-medium"
              >
                <BarChart3 className="w-5 h-5" />
                Ежедневный отчет
              </button>
            </div>
          </div>

          {/* Avito Notifications */}
          <div className="bg-white/30 backdrop-blur-xl rounded-2xl border border-white/40 p-6">
            <div className="flex items-center gap-3 mb-6">
              <MessageCircle className="w-6 h-6 text-orange-400" />
              <h2 className="text-xl font-bold text-white">Авито уведомления</h2>
            </div>
            <button
              onClick={testAvitoNotification}
              className="w-full px-6 py-4 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 rounded-xl text-white transition-all flex items-center justify-center gap-2 font-medium"
            >
              <MessageCircle className="w-5 h-5" />
              Тестовое сообщение с Авито
            </button>
          </div>

          {/* Client Notifications */}
          <div className="bg-white/30 backdrop-blur-xl rounded-2xl border border-white/40 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Users className="w-6 h-6 text-purple-400" />
              <h2 className="text-xl font-bold text-white">Уведомления клиентам</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Выберите проект
                </label>
                <select
                  value={selectedProject || ''}
                  onChange={(e) => setSelectedProject(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-white/30 border border-white/40 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">Выберите проект...</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      #{project.id} - {project.title}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Новый статус
                </label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="w-full px-4 py-2 bg-white/30 border border-white/40 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {statusOptions.map((status) => (
                    <option key={status.value} value={status.value}>
                      {status.icon} {status.label}
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={testStatusNotification}
                disabled={!selectedProject}
                className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 rounded-xl text-white transition-all flex items-center justify-center gap-2 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className="w-5 h-5" />
                Тестировать смену статуса
              </button>
            </div>
          </div>

          {/* Employee Settings */}
          <div className="bg-white/30 backdrop-blur-xl rounded-2xl border border-white/40 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Settings className="w-6 h-6 text-cyan-400" />
              <h2 className="text-xl font-bold text-white">Настройки уведомлений сотрудников</h2>
            </div>
            {loading ? (
              <div className="flex items-center justify-center p-8">
                <Loader className="w-6 h-6 animate-spin text-blue-500" />
              </div>
            ) : employees.length === 0 ? (
              <div className="text-center p-8 text-white">
                <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Нет зарегистрированных сотрудников</p>
              </div>
            ) : (
              <div className="space-y-4">
                {employees.map((employee) => {
                  const settings = employeeSettings[employee.id] || {}
                  const initials = employee.full_name
                    ? employee.full_name
                        .split(' ')
                        .map(n => n[0])
                        .join('')
                        .toUpperCase()
                    : '?'

                  return (
                    <div
                      key={employee.id}
                      className="p-4 bg-white/30 rounded-xl border border-white/40 hover:bg-white/40 transition-all"
                    >
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold">
                          {initials}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-white">{employee.full_name}</h3>
                          <p className="text-sm text-white">
                            {employee.role} • {employee.email}
                          </p>
                        </div>
                        <button
                          onClick={() => sendTestToEmployee(employee.id)}
                          className="px-3 py-1.5 bg-green-500 hover:bg-green-600 rounded-lg text-white text-sm transition-colors"
                        >
                          Тест
                        </button>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <label className="flex items-center justify-between p-2 bg-white/30 rounded-lg">
                          <span className="text-sm text-white">Новые задачи</span>
                          <input
                            type="checkbox"
                            checked={settings.project_assigned || false}
                            onChange={(e) =>
                              updateEmployeeSetting(employee.id, 'project_assigned', e.target.checked)
                            }
                            className="rounded border-white/40"
                          />
                        </label>
                        <label className="flex items-center justify-between p-2 bg-white/30 rounded-lg">
                          <span className="text-sm text-white">Дедлайны</span>
                          <input
                            type="checkbox"
                            checked={settings.project_deadline_reminder || false}
                            onChange={(e) =>
                              updateEmployeeSetting(employee.id, 'project_deadline_reminder', e.target.checked)
                            }
                            className="rounded border-white/40"
                          />
                        </label>
                        <label className="flex items-center justify-between p-2 bg-white/30 rounded-lg">
                          <span className="text-sm text-white">Изменения статуса</span>
                          <input
                            type="checkbox"
                            checked={settings.project_status_changed || false}
                            onChange={(e) =>
                              updateEmployeeSetting(employee.id, 'project_status_changed', e.target.checked)
                            }
                            className="rounded border-white/40"
                          />
                        </label>
                        <label className="flex items-center justify-between p-2 bg-white/30 rounded-lg">
                          <span className="text-sm text-white">Просроченные задачи</span>
                          <input
                            type="checkbox"
                            checked={settings.project_overdue || false}
                            onChange={(e) =>
                              updateEmployeeSetting(employee.id, 'project_overdue', e.target.checked)
                            }
                            className="rounded border-white/40"
                          />
                        </label>
                      </div>

                      <button
                        onClick={() => saveEmployeeSettings(employee.id)}
                        className="w-full mt-3 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-lg text-white transition-all flex items-center justify-center gap-2"
                      >
                        <CheckCircle className="w-4 h-4" />
                        Сохранить настройки
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Side Panel */}
        <div className="col-span-4 space-y-6">
          {/* Bot Status */}
          <div className="bg-white/30 backdrop-blur-xl rounded-2xl border border-white/40 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="w-6 h-6 text-green-400" />
              <h2 className="text-lg font-bold text-white">Статус бота</h2>
            </div>
            <div
              className={`p-4 rounded-xl border mb-4 ${
                botStatus.checking
                  ? 'bg-blue-500/20 border-blue-500/40'
                  : botStatus.online
                  ? 'bg-green-500/20 border-green-500/40'
                  : 'bg-red-500/20 border-red-500/40'
              }`}
            >
              <div className="flex items-center gap-2 text-white">
                {botStatus.checking ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Проверка статуса...
                  </>
                ) : botStatus.online ? (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Бот работает
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5" />
                    Бот недоступен
                  </>
                )}
              </div>
              {botStatus.username && (
                <p className="text-sm text-white mt-2">@{botStatus.username}</p>
              )}
            </div>
            <button
              onClick={checkBotStatus}
              className="w-full px-4 py-2 bg-white/30 hover:bg-white/40 rounded-xl text-white transition-colors flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Проверить статус
            </button>
          </div>

          {/* Activity Log */}
          <div className="bg-white/30 backdrop-blur-xl rounded-2xl border border-white/40 p-6">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-6 h-6 text-purple-400" />
              <h2 className="text-lg font-bold text-white">Лог активности</h2>
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {logs.length === 0 ? (
                <p className="text-sm text-white text-center py-8">
                  Логи активности будут отображаться здесь
                </p>
              ) : (
                logs.map((log) => (
                  <div
                    key={log.id}
                    className={`p-3 rounded-lg border-l-4 ${
                      log.type === 'success'
                        ? 'bg-green-500/20 border-green-500'
                        : log.type === 'error'
                        ? 'bg-red-500/20 border-red-500'
                        : 'bg-blue-500/20 border-blue-500'
                    }`}
                  >
                    <p className="text-sm text-white">{log.message}</p>
                    <p className="text-xs text-white mt-1">{log.timestamp}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Toasts */}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-4 py-3 rounded-xl shadow-lg backdrop-blur-sm border ${
              toast.type === 'success'
                ? 'bg-green-500/90 border-green-400'
                : toast.type === 'error'
                ? 'bg-red-500/90 border-red-400'
                : 'bg-blue-500/90 border-blue-400'
            } text-white`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  )
}
