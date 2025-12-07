import { useState } from 'react'
import { FileText, Radio, Download, Trash2, CheckCircle, AlertCircle } from 'lucide-react'
import { apiService } from '../../services/api'

interface QuickActionsProps {
  onRefresh?: () => void
}

export const QuickActions = ({ onRefresh }: QuickActionsProps) => {
  const [loading, setLoading] = useState<string | null>(null)
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const showAlert = (type: 'success' | 'error', message: string) => {
    setAlert({ type, message })
    setTimeout(() => setAlert(null), 3000)
  }

  const handleSendReport = async () => {
    setLoading('report')
    try {
      const response = await apiService.sendDailyReport()
      if (response.success) {
        showAlert('success', 'Отчет отправлен успешно!')
      } else {
        showAlert('error', 'Ошибка отправки отчета')
      }
    } catch (error) {
      showAlert('error', 'Ошибка отправки отчета')
    } finally {
      setLoading(null)
    }
  }

  const handleBroadcast = () => {
    showAlert('success', 'Функция в разработке')
  }

  const handleExport = async () => {
    setLoading('export')
    try {
      const response = await apiService.exportProjects()
      if (response.success) {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], {
          type: 'application/json',
        })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `projects_export_${new Date().toISOString().split('T')[0]}.json`
        a.click()
        window.URL.revokeObjectURL(url)
        showAlert('success', 'Данные экспортированы!')
      } else {
        showAlert('error', 'Ошибка экспорта данных')
      }
    } catch (error) {
      showAlert('error', 'Ошибка экспорта данных')
    } finally {
      setLoading(null)
    }
  }

  const handleClearCache = async () => {
    if (!confirm('Вы уверены, что хотите очистить кэш? Страница будет перезагружена.')) {
      return
    }

    setLoading('cache')
    try {
      const response = await apiService.clearCache()
      if (response.success) {
        showAlert('success', 'Кэш очищен! Перезагрузка...')
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      } else {
        showAlert('error', 'Ошибка очистки кэша')
        setLoading(null)
      }
    } catch (error) {
      showAlert('error', 'Ошибка очистки кэша')
      setLoading(null)
    }
  }

  const actions = [
    {
      id: 'report',
      icon: FileText,
      label: 'Отправить отчет',
      onClick: handleSendReport,
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      id: 'broadcast',
      icon: Radio,
      label: 'Рассылка',
      onClick: handleBroadcast,
      gradient: 'from-green-500 to-emerald-500',
    },
    {
      id: 'export',
      icon: Download,
      label: 'Экспорт данных',
      onClick: handleExport,
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      id: 'cache',
      icon: Trash2,
      label: 'Очистить кэш',
      onClick: handleClearCache,
      gradient: 'from-orange-500 to-red-500',
    },
  ]

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Быстрые действия</h3>

      <div className="space-y-3">
        {actions.map((action) => {
          const Icon = action.icon
          const isLoading = loading === action.id

          return (
            <button
              key={action.id}
              onClick={action.onClick}
              disabled={isLoading || loading !== null}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
                isLoading || loading !== null
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:shadow-lg hover:-translate-y-0.5'
              } bg-gradient-to-r ${action.gradient} text-white`}
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Icon className="w-5 h-5" />
              )}
              <span>{action.label}</span>
            </button>
          )
        })}
      </div>

      {/* Alert */}
      {alert && (
        <div
          className={`mt-4 flex items-center gap-2 px-4 py-3 rounded-xl ${
            alert.type === 'success'
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}
        >
          {alert.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span className="font-medium text-sm">{alert.message}</span>
        </div>
      )}
    </div>
  )
}
