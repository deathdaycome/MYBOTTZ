import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  TrendingUp,
  Users,
  BarChart2,
  DollarSign,
  Star,
  RefreshCw,
  Download,
  Clock,
  Activity,
  Zap,
  Target,
  Award,
  TrendingDown,
  Calendar,
  FileText,
  Loader2,
} from 'lucide-react'
import analyticsApi from '../api/analytics'
import type { DashboardAnalytics } from '../api/analytics'

// Chart.js imports
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line, Doughnut, Bar } from 'react-chartjs-2'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

type PeriodType = 7 | 30 | 90 | 365
type ChartType = 'users' | 'projects' | 'revenue'

export const Analytics = () => {
  // ============= STATE =============
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>(7)
  const [currentChart, setCurrentChart] = useState<ChartType>('users')
  const [analyticsData, setAnalyticsData] = useState<DashboardAnalytics | null>(null)

  // Toast notifications
  const [toasts, setToasts] = useState<
    Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>
  >([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  // ============= LOAD DATA =============

  const loadAnalyticsData = useCallback(async () => {
    setLoading(true)
    try {
      const response = await analyticsApi.getDashboard(selectedPeriod)
      if (response.success) {
        setAnalyticsData(response.data)
        showToast('Данные аналитики загружены', 'success')
      } else {
        showToast('Ошибка загрузки данных аналитики', 'error')
      }
    } catch (error) {
      console.error('Error loading analytics:', error)
      showToast('Ошибка загрузки данных аналитики', 'error')
    } finally {
      setLoading(false)
    }
  }, [selectedPeriod, showToast])

  useEffect(() => {
    loadAnalyticsData()
  }, [loadAnalyticsData])

  // ============= HANDLERS =============

  const handleRefresh = useCallback(() => {
    loadAnalyticsData()
  }, [loadAnalyticsData])

  const handlePeriodChange = useCallback((period: PeriodType) => {
    setSelectedPeriod(period)
  }, [])

  const handleExport = useCallback(async () => {
    setExporting(true)
    try {
      const response = await analyticsApi.exportAnalytics('json', selectedPeriod)
      if (response.success) {
        // Create and download JSON file
        const dataStr = JSON.stringify(response, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        const url = URL.createObjectURL(dataBlob)
        const link = document.createElement('a')
        link.href = url
        link.download = `analytics_report_${selectedPeriod}days_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        showToast('Отчет успешно экспортирован', 'success')
      } else {
        showToast('Ошибка экспорта отчета', 'error')
      }
    } catch (error) {
      console.error('Error exporting report:', error)
      showToast('Ошибка экспорта отчета', 'error')
    } finally {
      setExporting(false)
    }
  }, [selectedPeriod, showToast])

  const handleScheduledReport = useCallback(() => {
    showToast('Функционал автоматических отчетов будет доступен в следующей версии', 'info')
  }, [showToast])

  // ============= CHART DATA =============

  const growthChartData = useMemo(() => {
    if (!analyticsData) return null

    let labels: string[] = []
    let data: number[] = []
    let label = ''
    let borderColor = ''
    let backgroundColor = ''

    if (currentChart === 'users' && analyticsData.user_statistics?.daily_registrations) {
      labels = analyticsData.user_statistics.daily_registrations.map((item) =>
        new Date(item.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
      )
      data = analyticsData.user_statistics.daily_registrations.map((item) => item.registrations)
      label = 'Новые пользователи'
      borderColor = '#667eea'
      backgroundColor = 'rgba(102, 126, 234, 0.1)'
    } else if (currentChart === 'projects' && analyticsData.project_statistics?.daily_projects) {
      labels = analyticsData.project_statistics.daily_projects.map((item) =>
        new Date(item.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
      )
      data = analyticsData.project_statistics.daily_projects.map((item) => item.projects)
      label = 'Новые проекты'
      borderColor = '#28a745'
      backgroundColor = 'rgba(40, 167, 69, 0.1)'
    } else if (currentChart === 'revenue') {
      // Sample revenue data based on period
      const days = selectedPeriod
      labels = Array.from({ length: days }, (_, i) => {
        const date = new Date()
        date.setDate(date.getDate() - (days - 1 - i))
        return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
      })
      // Generate sample revenue data with growth trend
      const baseRevenue = 50000
      data = Array.from({ length: days }, (_, i) => {
        return Math.round(baseRevenue + Math.random() * 25000 + i * 500)
      })
      label = 'Доход (₽)'
      borderColor = '#ffc107'
      backgroundColor = 'rgba(255, 193, 7, 0.1)'
    }

    return {
      labels,
      datasets: [
        {
          label,
          data,
          borderColor,
          backgroundColor,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: borderColor,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    }
  }, [analyticsData, currentChart, selectedPeriod])

  const statusChartData = useMemo(() => {
    if (!analyticsData?.project_statistics?.status_distribution) return null

    const statusDist = analyticsData.project_statistics.status_distribution

    return {
      labels: ['Новые', 'Рассмотрение', 'Принятые', 'В работе', 'Тестирование', 'Завершенные', 'Отмененные'],
      datasets: [
        {
          data: [
            statusDist.new || 0,
            statusDist.review || 0,
            statusDist.accepted || 0,
            statusDist.in_progress || 0,
            statusDist.testing || 0,
            statusDist.completed || 0,
            statusDist.cancelled || 0,
          ],
          backgroundColor: [
            '#17a2b8',
            '#ffc107',
            '#28a745',
            '#007bff',
            '#6f42c1',
            '#20c997',
            '#dc3545',
          ],
          borderWidth: 0,
        },
      ],
    }
  }, [analyticsData])

  // Mock complexity chart data (not provided by backend)
  const complexityChartData = useMemo(() => {
    return {
      labels: ['Простые', 'Средние', 'Сложные', 'Премиум'],
      datasets: [
        {
          label: 'Количество проектов',
          data: [15, 25, 12, 8],
          backgroundColor: ['#28a745', '#ffc107', '#fd7e14', '#dc3545'],
          borderRadius: 8,
        },
      ],
    }
  }, [])

  const chartOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#fff',
          font: {
            size: 12,
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: '#9ca3af',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
      x: {
        ticks: {
          color: '#9ca3af',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
  }

  const doughnutOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#fff',
          font: {
            size: 11,
          },
        },
      },
    },
  }

  // ============= RENDER HELPERS =============

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ru-RU').format(Math.round(num))
  }

  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num)
  }

  if (loading && !analyticsData) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-purple-500 mx-auto mb-4" />
          <p className="text-gray-600">Загрузка аналитики...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-rose-500 to-orange-600 flex items-center justify-center shadow-lg shadow-rose-500/50">
              <Activity className="w-6 h-6 text-gray-900" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Аналитика и отчеты</h1>
              <p className="text-gray-600">Статистика и метрики системы</p>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="px-4 py-2.5 bg-gray-50 hover:bg-gray-100 text-gray-900 rounded-xl transition-all duration-300 flex items-center gap-2 border border-gray-200"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Обновить</span>
            </button>
            <button
              onClick={handleExport}
              disabled={exporting}
              className="px-4 py-2.5 bg-gradient-to-br from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-gray-900 rounded-xl transition-all duration-300 flex items-center gap-2 shadow-lg shadow-green-500/50"
            >
              {exporting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Download className="w-4 h-4" />
              )}
              <span>Экспорт отчета</span>
            </button>
            <button
              onClick={handleScheduledReport}
              className="px-4 py-2.5 bg-gradient-to-br from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 text-gray-900 rounded-xl transition-all duration-300 flex items-center gap-2 shadow-lg shadow-blue-500/50"
            >
              <Clock className="w-4 h-4" />
              <span>Отчет по расписанию</span>
            </button>
          </div>
        </div>

        {/* Period Selector */}
        <div className="bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h5 className="text-gray-900 font-semibold mb-1">Период анализа</h5>
              <p className="text-sm text-gray-600">Выберите период для отображения статистики</p>
            </div>
            <div className="flex gap-2">
              {([7, 30, 90, 365] as PeriodType[]).map((period) => (
                <button
                  key={period}
                  onClick={() => handlePeriodChange(period)}
                  className={`px-6 py-2.5 rounded-xl font-medium transition-all duration-300 ${
                    selectedPeriod === period
                      ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-gray-900 shadow-lg'
                      : 'bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 border border-gray-200'
                  }`}
                >
                  {period === 7 ? '7 дней' : period === 30 ? '30 дней' : period === 90 ? '90 дней' : 'Год'}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Users */}
        <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-purple-500/30 rounded-2xl p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
              <Users className="w-6 h-6 text-gray-900" />
            </div>
            <span className="text-xs text-purple-300 bg-purple-500/20 px-2 py-1 rounded-lg">
              +{analyticsData?.user_statistics?.new_users || 0} за период
            </span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">
            {formatNumber(analyticsData?.user_statistics?.total_users || 0)}
          </h3>
          <p className="text-purple-200">Всего пользователей</p>
        </div>

        {/* Conversion Rate */}
        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-sm border border-green-500/30 rounded-2xl p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-lg">
              <TrendingUp className="w-6 h-6 text-gray-900" />
            </div>
            <span className="text-xs text-green-300 bg-green-500/20 px-2 py-1 rounded-lg">
              Пользователи → Клиенты
            </span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">
            {(analyticsData?.conversion_funnel?.overall_conversion || 0).toFixed(1)}%
          </h3>
          <p className="text-green-200">Общая конверсия</p>
        </div>

        {/* Total Revenue */}
        <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-sm border border-blue-500/30 rounded-2xl p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
              <DollarSign className="w-6 h-6 text-gray-900" />
            </div>
            <span className="text-xs text-blue-300 bg-blue-500/20 px-2 py-1 rounded-lg">
              Ср. чек: {formatCurrency(analyticsData?.financial_report?.avg_check || 0)}
            </span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">
            {formatCurrency(analyticsData?.financial_report?.total_revenue || 0)}
          </h3>
          <p className="text-blue-200">Доход</p>
        </div>

        {/* Average Rating */}
        <div className="bg-gradient-to-br from-amber-500/20 to-orange-500/20 backdrop-blur-sm border border-amber-500/30 rounded-2xl p-6 hover:scale-105 transition-all duration-300">
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg">
              <Star className="w-6 h-6 text-gray-900" />
            </div>
            <span className="text-xs text-amber-300 bg-amber-500/20 px-2 py-1 rounded-lg">
              AI консультант
            </span>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-1">
            {(analyticsData?.consultant_statistics?.avg_rating || 0).toFixed(1)}
          </h3>
          <p className="text-amber-200">Средняя оценка</p>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Growth Chart */}
        <div className="lg:col-span-2 bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <BarChart2 className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-gray-900">Динамика роста</h3>
            </div>
            <div className="flex gap-2">
              {(['users', 'projects', 'revenue'] as ChartType[]).map((type) => (
                <button
                  key={type}
                  onClick={() => setCurrentChart(type)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                    currentChart === type
                      ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-gray-900'
                      : 'bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  {type === 'users' ? 'Пользователи' : type === 'projects' ? 'Проекты' : 'Доходы'}
                </button>
              ))}
            </div>
          </div>
          <div className="h-[300px]">
            {growthChartData && <Line data={growthChartData} options={chartOptions} />}
          </div>
        </div>

        {/* Conversion Funnel */}
        <div className="bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Target className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900">Воронка конверсии</h3>
          </div>
          <div className="space-y-3">
            {[
              {
                label: 'Пользователи',
                value: analyticsData?.conversion_funnel?.total_users || 0,
                width: 100,
                gradient: 'from-purple-500 to-pink-500',
              },
              {
                label: 'Создали проекты',
                value: analyticsData?.conversion_funnel?.users_with_projects || 0,
                width: analyticsData?.conversion_funnel?.project_creation_rate || 0,
                gradient: 'from-blue-500 to-cyan-500',
              },
              {
                label: 'Приняли предложение',
                value: analyticsData?.conversion_funnel?.users_with_accepted_projects || 0,
                width: analyticsData?.conversion_funnel?.project_acceptance_rate || 0,
                gradient: 'from-green-500 to-emerald-500',
              },
              {
                label: 'Завершили проекты',
                value: analyticsData?.conversion_funnel?.users_with_completed_projects || 0,
                width: analyticsData?.conversion_funnel?.project_completion_rate || 0,
                gradient: 'from-amber-500 to-orange-500',
              },
            ].map((stage, index) => (
              <div key={index} className="group">
                <div
                  className={`bg-gradient-to-br ${stage.gradient} rounded-xl p-4 transition-all duration-300 hover:scale-105 hover:shadow-lg`}
                  style={{ width: `${stage.width}%` }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-gray-900 text-sm font-medium">{stage.label}</span>
                    <span className="text-gray-900 text-lg font-bold bg-gray-100 px-2 py-1 rounded-lg">
                      {stage.value}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Project Status Chart */}
        <div className="bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <BarChart2 className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900">Статусы проектов</h3>
          </div>
          <div className="h-[300px]">
            {statusChartData && <Doughnut data={statusChartData} options={doughnutOptions} />}
          </div>
        </div>

        {/* Complexity Chart */}
        <div className="bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Award className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900">Сложность проектов</h3>
          </div>
          <div className="h-[300px]">
            <Bar data={complexityChartData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Performance Metrics & Top Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Performance Metrics */}
        <div className="bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Zap className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900">Метрики производительности</h3>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            {[
              {
                label: 'Время ответа AI',
                value: `${(analyticsData?.performance_metrics?.avg_response_time || 0).toFixed(1)}с`,
              },
              {
                label: 'До принятия заявки',
                value: `${(analyticsData?.performance_metrics?.avg_acceptance_time || 0).toFixed(1)}ч`,
              },
              {
                label: 'Время разработки',
                value: `${(analyticsData?.performance_metrics?.avg_development_time || 0).toFixed(1)}ч`,
              },
              {
                label: 'Точность оценок',
                value: `${(analyticsData?.performance_metrics?.time_estimation_accuracy || 0).toFixed(1)}%`,
              },
            ].map((metric, index) => (
              <div
                key={index}
                className="bg-white rounded-xl p-4 hover:bg-gray-50 transition-all duration-300"
              >
                <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
                <div className="text-sm text-gray-600">{metric.label}</div>
              </div>
            ))}
          </div>

          <div className="space-y-4">
            {[
              {
                label: 'Качество ответов AI',
                value: (analyticsData?.consultant_statistics?.avg_rating || 0) * 20,
                color: 'bg-green-500',
              },
              {
                label: 'Конверсия в клиентов',
                value: analyticsData?.conversion_funnel?.overall_conversion || 0,
                color: 'bg-blue-500',
              },
              {
                label: 'Удержание пользователей',
                value: analyticsData?.engagement_metrics?.retention_rate || 0,
                color: 'bg-cyan-500',
              },
            ].map((progress, index) => (
              <div key={index}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-700">{progress.label}</span>
                  <span className="text-sm font-semibold text-gray-900">{progress.value.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-gray-50 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${progress.color} rounded-full transition-all duration-500`}
                    style={{ width: `${progress.value}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Metrics */}
        <div className="bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <BarChart2 className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900">Топ метрики</h3>
          </div>

          <div className="space-y-4">
            {[
              {
                label: 'Активные пользователи (DAU)',
                value: analyticsData?.engagement_metrics?.daily_active_users || 0,
                width: 75,
              },
              {
                label: 'Новые проекты за период',
                value: analyticsData?.project_statistics?.new_projects || 0,
                width: 60,
              },
              {
                label: 'Завершенные проекты',
                value: analyticsData?.project_statistics?.completed_projects || 0,
                width: 45,
              },
              {
                label: 'Консультаций проведено',
                value: analyticsData?.consultant_statistics?.new_sessions || 0,
                width: 85,
              },
              {
                label: 'Средний доход с клиента',
                value: formatCurrency(analyticsData?.financial_report?.avg_check || 0),
                width: 70,
                isString: true,
              },
            ].map((metric, index) => (
              <div key={index} className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="text-sm text-gray-600 mb-2">{metric.label}</div>
                  <div className="h-8 bg-gray-50 rounded-lg overflow-hidden relative">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-500"
                      style={{ width: `${metric.width}%` }}
                    ></div>
                  </div>
                </div>
                <div className="text-lg font-bold text-gray-900 min-w-[80px] text-right">
                  {metric.isString ? metric.value : formatNumber(metric.value as number)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Clients */}
        <div className="bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Award className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900">Топ клиенты по доходу</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Клиент</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Проекты</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Доход</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: '@user123', projects: 3, revenue: 150000 },
                  { name: '@company_bot', projects: 2, revenue: 120000 },
                  { name: '@startup_xyz', projects: 1, revenue: 80000 },
                  { name: '@ecommerce_pro', projects: 2, revenue: 75000 },
                  { name: '@crypto_trader', projects: 1, revenue: 60000 },
                ].map((client, index) => (
                  <tr key={index} className="border-b border-gray-100 hover:bg-white transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-gray-900 text-xs font-bold">
                          {index + 1}
                        </span>
                        <span className="text-gray-900">{client.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-lg text-sm">
                        {client.projects}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-gray-900 font-semibold">{formatCurrency(client.revenue)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Popular Topics */}
        <div className="bg-white backdrop-blur-sm border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <FileText className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900">Популярные вопросы консультанту</h3>
          </div>
          <div className="space-y-4">
            {analyticsData?.consultant_statistics?.popular_topics &&
            Object.keys(analyticsData.consultant_statistics.popular_topics).length > 0 ? (
              Object.entries(analyticsData.consultant_statistics.popular_topics)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([topic, count], index) => {
                  const maxCount = Math.max(
                    ...Object.values(analyticsData.consultant_statistics?.popular_topics || {})
                  )
                  const width = (count / maxCount) * 100
                  return (
                    <div key={index}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-700">{topic}</span>
                        <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-lg text-xs font-semibold">
                          {count}
                        </span>
                      </div>
                      <div className="h-2 bg-gray-50 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                          style={{ width: `${width}%` }}
                        ></div>
                      </div>
                    </div>
                  )
                })
            ) : (
              <p className="text-center text-gray-600 py-8">Нет данных о консультациях</p>
            )}
          </div>
        </div>
      </div>

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-4 py-3 rounded-xl shadow-lg backdrop-blur-sm border transition-all duration-300 ${
              toast.type === 'success'
                ? 'bg-green-500/20 border-green-500/50 text-green-300'
                : toast.type === 'error'
                ? 'bg-red-500/20 border-red-500/50 text-red-300'
                : 'bg-blue-500/20 border-blue-500/50 text-blue-300'
            }`}
          >
            <div className="flex items-center gap-2">
              {toast.type === 'success' ? (
                <TrendingUp className="w-4 h-4" />
              ) : toast.type === 'error' ? (
                <TrendingDown className="w-4 h-4" />
              ) : (
                <Activity className="w-4 h-4" />
              )}
              <span>{toast.message}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
