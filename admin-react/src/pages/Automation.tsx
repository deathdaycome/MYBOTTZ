import { useState, useEffect, useCallback } from 'react'
import {
  Zap,
  Play,
  Pause,
  Clock,
  DollarSign,
  AlertTriangle,
  Users,
  Activity,
  Send,
  FileText,
  TrendingUp,
  Calendar,
  CheckCircle2,
} from 'lucide-react'
// API imports
import automationApi from '../api/automation'
import type { AutomationSummary } from '../api/automation'

interface LogEntry {
  message: string
  type: 'info' | 'success' | 'error' | 'warning'
  timestamp: Date
}

export const Automation = () => {
  const [summary, setSummary] = useState<AutomationSummary | null>(null)
  const [schedulerRunning, setSchedulerRunning] = useState(false)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)

  // Toast
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(
    null
  )

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }, [])

  const addLog = useCallback((message: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') => {
    setLogs((prev) => [{ message, type, timestamp: new Date() }, ...prev].slice(0, 50))
  }, [])

  // Load data
  const loadSummary = useCallback(async () => {
    try {
      setLoading(true)
      const response = await automationApi.getSummary()
      if (response.success) {
        setSummary(response.summary)
        setSchedulerRunning(response.scheduler_running)
        addLog('Статистика обновлена', 'success')
      }
    } catch (error) {
      showToast('Ошибка загрузки статистики', 'error')
      addLog('Ошибка загрузки статистики', 'error')
    } finally {
      setLoading(false)
    }
  }, [showToast, addLog])

  useEffect(() => {
    loadSummary()
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadSummary, 30000)
    return () => clearInterval(interval)
  }, [loadSummary])

  // Toggle scheduler
  const toggleScheduler = async () => {
    try {
      const response = schedulerRunning
        ? await automationApi.stopScheduler()
        : await automationApi.startScheduler()

      if (response.success) {
        setSchedulerRunning(!schedulerRunning)
        addLog(response.message, 'success')
        showToast(response.message, 'success')
      }
    } catch (error) {
      showToast('Ошибка управления планировщиком', 'error')
      addLog('Ошибка управления планировщиком', 'error')
    }
  }

  // Run task
  const runTask = async (taskName: string) => {
    try {
      const response = await automationApi.runTask(taskName)
      if (response.success) {
        addLog(response.message, 'success')
        showToast(response.message, 'success')
        setTimeout(loadSummary, 2000)
      } else {
        addLog(response.message, 'warning')
      }
    } catch (error) {
      showToast('Ошибка запуска задачи', 'error')
      addLog('Ошибка запуска задачи', 'error')
    }
  }

  // Check overdue
  const checkOverdue = async () => {
    try {
      const response = await automationApi.checkOverdue()
      if (response.success) {
        addLog(response.message, 'success')
        if (response.projects.length > 0) {
          response.projects.forEach((project) => {
            addLog(`Проект #${project.id} "${project.title}" помечен как просроченный`, 'warning')
          })
        }
        showToast(response.message, 'success')
        loadSummary()
      }
    } catch (error) {
      showToast('Ошибка проверки просроченных', 'error')
      addLog('Ошибка проверки просроченных', 'error')
    }
  }

  // Check unpaid
  const checkUnpaid = async () => {
    try {
      const response = await automationApi.checkUnpaid()
      if (response.success) {
        let message = ''
        if (response.unpaid_projects.length > 0) {
          message += `Неоплаченных проектов: ${response.unpaid_projects.length}. `
          response.unpaid_projects.forEach((project) => {
            addLog(
              `Проект #${project.id} "${project.title}" - остаток ${project.remaining}₽`,
              'warning'
            )
          })
        }
        if (response.unpaid_executors.length > 0) {
          message += `Долгов исполнителям: ${response.unpaid_executors.length}.`
          response.unpaid_executors.forEach((item) => {
            addLog(`Исполнитель "${item.executor_name}" - остаток ${item.remaining}₽`, 'warning')
          })
        }
        if (message) {
          addLog(message, 'info')
          showToast(message, 'info')
        } else {
          const msg = 'Неоплаченных проектов и долгов не найдено'
          addLog(msg, 'success')
          showToast(msg, 'success')
        }
        loadSummary()
      }
    } catch (error) {
      showToast('Ошибка проверки неоплаченных', 'error')
      addLog('Ошибка проверки неоплаченных', 'error')
    }
  }

  // Send test notification
  const sendTestNotification = async () => {
    const message = prompt('Введите текст уведомления:')
    if (!message) return

    try {
      const response = await automationApi.sendNotification(message)
      if (response.success) {
        addLog('Уведомление отправлено успешно', 'success')
        showToast('Уведомление отправлено', 'success')
      } else {
        addLog('Не удалось отправить уведомление', 'error')
        showToast('Ошибка отправки', 'error')
      }
    } catch (error) {
      showToast('Ошибка отправки уведомления', 'error')
      addLog('Ошибка отправки уведомления', 'error')
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  return (
    <div className="p-8 max-w-[1920px] mx-auto">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg ${
            toast.type === 'success'
              ? 'bg-green-500'
              : toast.type === 'error'
              ? 'bg-red-500'
              : 'bg-blue-500'
          } text-white`}
        >
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-yellow-500 to-amber-600 flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            Автоматизация и уведомления
          </h1>
          <p className="text-gray-500 mt-1">Управление автоматическими проверками и уведомлениями</p>
        </div>
      </div>

      {/* Scheduler Status */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6 text-gray-400" />
            <h2 className="text-xl font-bold text-gray-900">Планировщик задач</h2>
          </div>
          <div
            className={`px-4 py-2 rounded-full flex items-center gap-2 ${
              schedulerRunning ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}
          >
            {schedulerRunning ? (
              <>
                <Activity className="w-4 h-4 animate-pulse" />
                Работает
              </>
            ) : (
              <>
                <Pause className="w-4 h-4" />
                Остановлен
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Schedule */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Расписание задач:</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="flex items-center gap-2 text-sm text-gray-700">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  Ежедневные проверки
                </span>
                <span className="text-sm text-gray-500">09:00</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="flex items-center gap-2 text-sm text-gray-700">
                  <Clock className="w-4 h-4 text-gray-400" />
                  Проверка просроченных
                </span>
                <span className="text-sm text-gray-500">Каждые 4 часа</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="flex items-center gap-2 text-sm text-gray-700">
                  <DollarSign className="w-4 h-4 text-gray-400" />
                  Финансовый статус
                </span>
                <span className="text-sm text-gray-500">18:00</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="flex items-center gap-2 text-sm text-gray-700">
                  <FileText className="w-4 h-4 text-gray-400" />
                  Еженедельный отчет
                </span>
                <span className="text-sm text-gray-500">Пн 10:00</span>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Управление:</h3>
            <div className="space-y-2">
              <button
                onClick={toggleScheduler}
                className={`w-full px-4 py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-all ${
                  schedulerRunning
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {schedulerRunning ? (
                  <>
                    <Pause className="w-4 h-4" />
                    Остановить планировщик
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Запустить планировщик
                  </>
                )}
              </button>
              <button
                onClick={() => runTask('daily_checks')}
                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center justify-center gap-2"
              >
                <Play className="w-4 h-4" />
                Запустить ежедневные проверки
              </button>
              <button
                onClick={() => runTask('financial_status')}
                className="w-full px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium flex items-center justify-center gap-2"
              >
                <DollarSign className="w-4 h-4" />
                Проверить финансы
              </button>
              <button
                onClick={() => runTask('weekly_report')}
                className="w-full px-4 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-medium flex items-center justify-center gap-2"
              >
                <FileText className="w-4 h-4" />
                Сгенерировать отчет
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <FileText className="w-5 h-5" />
              </div>
              <TrendingUp className="w-5 h-5 opacity-50" />
            </div>
            <div className="text-3xl font-bold mb-1">{summary.total_projects}</div>
            <div className="text-sm opacity-90">Всего проектов</div>
          </div>

          <div className="bg-gradient-to-br from-pink-500 to-red-600 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <AlertTriangle className="w-5 h-5 opacity-50" />
            </div>
            <div className="text-3xl font-bold mb-1">{summary.overdue_count}</div>
            <div className="text-sm opacity-90">Просроченных</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-amber-600 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <DollarSign className="w-5 h-5" />
              </div>
              <DollarSign className="w-5 h-5 opacity-50" />
            </div>
            <div className="text-3xl font-bold mb-1">{summary.unpaid_projects_count}</div>
            <div className="text-sm opacity-90">Неоплаченных</div>
          </div>

          <div className="bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
              <Users className="w-5 h-5 opacity-50" />
            </div>
            <div className="text-3xl font-bold mb-1">{summary.unpaid_executors_count}</div>
            <div className="text-sm opacity-90">Долги исполнителям</div>
          </div>
        </div>
      )}

      {/* Financial Summary */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className="text-sm text-blue-700 font-medium">Ожидается от клиентов</div>
                <div className="text-2xl font-bold text-blue-900">
                  {formatCurrency(summary.total_unpaid_clients)}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-orange-50 border-l-4 border-orange-500 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <div className="text-sm text-orange-700 font-medium">К выплате исполнителям</div>
                <div className="text-2xl font-bold text-orange-900">
                  {formatCurrency(summary.total_unpaid_executors)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manual Checks */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-gray-400" />
          Ручные проверки
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={checkOverdue}
            className="px-6 py-4 border-2 border-red-200 rounded-xl hover:bg-red-50 transition-colors text-red-700 font-medium flex items-center justify-center gap-2"
          >
            <AlertTriangle className="w-5 h-5" />
            Проверить просроченные
          </button>
          <button
            onClick={checkUnpaid}
            className="px-6 py-4 border-2 border-amber-200 rounded-xl hover:bg-amber-50 transition-colors text-amber-700 font-medium flex items-center justify-center gap-2"
          >
            <DollarSign className="w-5 h-5" />
            Проверить неоплаченные
          </button>
          <button
            onClick={sendTestNotification}
            className="px-6 py-4 border-2 border-blue-200 rounded-xl hover:bg-blue-50 transition-colors text-blue-700 font-medium flex items-center justify-center gap-2"
          >
            <Send className="w-5 h-5" />
            Тестовое уведомление
          </button>
        </div>
      </div>

      {/* Event Log */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-gray-400" />
          Последние события
        </h2>
        <div className="bg-gray-50 rounded-xl p-4 h-96 overflow-y-auto space-y-2">
          {logs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">Нет событий</div>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg font-mono text-sm ${
                  log.type === 'error'
                    ? 'bg-red-50 text-red-700 border-l-4 border-red-500'
                    : log.type === 'warning'
                    ? 'bg-yellow-50 text-yellow-700 border-l-4 border-yellow-500'
                    : log.type === 'success'
                    ? 'bg-green-50 text-green-700 border-l-4 border-green-500'
                    : 'bg-white text-gray-700 border-l-4 border-blue-500'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="flex-1">{log.message}</span>
                  <span className="text-xs opacity-70">
                    {log.timestamp.toLocaleTimeString('ru-RU')}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
