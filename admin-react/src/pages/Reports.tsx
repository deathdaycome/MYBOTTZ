import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  PieChart as PieChartIcon,
  Users,
  FolderKanban,
  Trophy,
  Star,
  ArrowUp,
  ArrowDown,
  Loader2,
  FileText,
  ExternalLink,
} from 'lucide-react'
import reportsApi from '../api/reports'
import type {
  DashboardMetrics,
  ProjectsReport,
  FinancialReport,
  QuickStats,
  ExecutorReport,
} from '../api/reports'

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
import { Line, Doughnut } from 'react-chartjs-2'

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

type TabType = 'overview' | 'financial' | 'projects' | 'executors'
type PeriodType = 'today' | 'week' | 'month' | 'year'

export const Reports = () => {
  // ============= STATE =============
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>('week')

  // Data
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null)
  const [quickStats, setQuickStats] = useState<QuickStats['stats'] | null>(null)
  const [projectsReport, setProjectsReport] = useState<ProjectsReport | null>(null)
  const [financialReport, setFinancialReport] = useState<FinancialReport | null>(null)
  const [executorsData, setExecutorsData] = useState<any[]>([])

  // Filters
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [projectStatusFilter, setProjectStatusFilter] = useState('')
  const [executorFilter, setExecutorFilter] = useState('')

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

  const loadDashboardMetrics = useCallback(async () => {
    try {
      const response = await reportsApi.getDashboardMetrics()
      if (response.success) {
        setDashboardMetrics(response.metrics)
      }
    } catch (error) {
      console.error('Error loading dashboard metrics:', error)
      showToast('Ошибка загрузки метрик дашборда', 'error')
    }
  }, [showToast])

  const loadQuickStats = useCallback(
    async (period: PeriodType) => {
      try {
        const response = await reportsApi.getQuickStats(period)
        if (response.success) {
          setQuickStats(response.stats)
        }
      } catch (error) {
        console.error('Error loading quick stats:', error)
        showToast('Ошибка загрузки быстрой статистики', 'error')
      }
    },
    [showToast]
  )

  const loadProjectsReport = useCallback(async () => {
    try {
      const filters: any = {}
      if (startDate) filters.start_date = startDate
      if (endDate) filters.end_date = endDate
      if (projectStatusFilter) filters.status = projectStatusFilter
      if (executorFilter) filters.executor_id = parseInt(executorFilter)

      const response = await reportsApi.getProjectsReport(filters)
      if (response.success) {
        setProjectsReport(response.report)
      }
    } catch (error) {
      console.error('Error loading projects report:', error)
      showToast('Ошибка загрузки отчета по проектам', 'error')
    }
  }, [startDate, endDate, projectStatusFilter, executorFilter, showToast])

  const loadFinancialReport = useCallback(async () => {
    try {
      const filters: any = {}
      if (startDate) filters.start_date = startDate
      if (endDate) filters.end_date = endDate

      const response = await reportsApi.getFinancialReport(filters)
      if (response.success) {
        setFinancialReport(response.report)
      }
    } catch (error) {
      console.error('Error loading financial report:', error)
      showToast('Ошибка загрузки финансового отчета', 'error')
    }
  }, [startDate, endDate, showToast])

  useEffect(() => {
    const initData = async () => {
      setLoading(true)
      await Promise.all([loadDashboardMetrics(), loadQuickStats(selectedPeriod)])
      setLoading(false)
    }
    initData()
  }, [loadDashboardMetrics, loadQuickStats, selectedPeriod])

  useEffect(() => {
    if (activeTab === 'financial') {
      loadFinancialReport()
    } else if (activeTab === 'projects') {
      loadProjectsReport()
    }
  }, [activeTab, loadFinancialReport, loadProjectsReport])

  // ============= HANDLERS =============

  const handlePeriodChange = (period: PeriodType) => {
    setSelectedPeriod(period)
    setQuickPeriodDates(period)
    loadQuickStats(period)
  }

  const setQuickPeriodDates = (period: PeriodType) => {
    const now = new Date()
    let start: Date

    switch (period) {
      case 'today':
        start = now
        break
      case 'week':
        start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case 'month':
        start = new Date(now.getFullYear(), now.getMonth(), 1)
        break
      case 'year':
        start = new Date(now.getFullYear(), 0, 1)
        break
      default:
        start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    }

    setStartDate(start.toISOString().split('T')[0])
    setEndDate(now.toISOString().split('T')[0])
  }

  const handleApplyFilters = () => {
    if (activeTab === 'financial') {
      loadFinancialReport()
    } else if (activeTab === 'projects') {
      loadProjectsReport()
    }
  }

  const handleExportReport = async (reportType: 'projects' | 'financial' | 'executor') => {
    try {
      const filters: any = {}
      if (startDate) filters.start_date = startDate
      if (endDate) filters.end_date = endDate
      if (reportType === 'projects' && projectStatusFilter) filters.status = projectStatusFilter
      if (reportType === 'projects' && executorFilter)
        filters.executor_id = parseInt(executorFilter)

      await reportsApi.exportToExcel(reportType, filters)
      showToast('Отчет успешно экспортирован', 'success')
    } catch (error) {
      console.error('Error exporting report:', error)
      showToast('Ошибка экспорта отчета', 'error')
    }
  }

  const handleRefresh = async () => {
    setLoading(true)
    await Promise.all([loadDashboardMetrics(), loadQuickStats(selectedPeriod)])
    if (activeTab === 'financial') {
      await loadFinancialReport()
    } else if (activeTab === 'projects') {
      await loadProjectsReport()
    }
    setLoading(false)
    showToast('Данные обновлены', 'success')
  }

  // ============= UI HELPERS =============

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; className: string }> = {
      new: { label: 'Новый', className: 'bg-blue-100 text-blue-700' },
      in_progress: { label: 'В работе', className: 'bg-yellow-100 text-yellow-700' },
      completed: { label: 'Завершен', className: 'bg-green-100 text-green-700' },
      overdue: { label: 'Просрочен', className: 'bg-red-100 text-red-700' },
      cancelled: { label: 'Отменен', className: 'bg-gray-100 text-gray-700' },
    }

    const statusInfo = statusMap[status] || {
      label: status,
      className: 'bg-gray-100 text-gray-700',
    }

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusInfo.className}`}>
        {statusInfo.label}
      </span>
    )
  }

  // ============= CHART DATA =============

  const monthlyChartData = useMemo(() => {
    if (!financialReport?.monthly_data) {
      return {
        labels: [],
        datasets: [],
      }
    }

    return {
      labels: financialReport.monthly_data.map((m) => m.month),
      datasets: [
        {
          label: 'Доходы',
          data: financialReport.monthly_data.map((m) => m.income),
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: true,
        },
        {
          label: 'Расходы',
          data: financialReport.monthly_data.map((m) => m.expense),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          fill: true,
        },
      ],
    }
  }, [financialReport])

  const expenseCategoriesChartData = useMemo(() => {
    if (!financialReport?.expense_categories) {
      return {
        labels: [],
        datasets: [],
      }
    }

    const categories = Object.keys(financialReport.expense_categories)
    const values = Object.values(financialReport.expense_categories)

    return {
      labels: categories,
      datasets: [
        {
          data: values,
          backgroundColor: [
            '#667eea',
            '#764ba2',
            '#f093fb',
            '#f5576c',
            '#4facfe',
            '#00f2fe',
            '#43e97b',
            '#38f9d7',
          ],
        },
      ],
    }
  }, [financialReport])

  // ============= RENDER =============

  if (loading && !dashboardMetrics) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="max-w-[2000px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Отчеты и аналитика
            </h1>
            <p className="text-gray-600 mt-1">Детальная аналитика и статистика бизнеса</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200 disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Filters Section */}
        <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-200">
          <div className="flex flex-wrap items-center gap-4">
            {/* Date Range */}
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <span className="text-gray-500">до</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                onClick={handleApplyFilters}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all"
              >
                <Filter className="w-4 h-4" />
                Применить
              </button>
            </div>

            {/* Quick Period Buttons */}
            <div className="flex items-center gap-2 ml-auto">
              {(['today', 'week', 'month', 'year'] as PeriodType[]).map((period) => (
                <button
                  key={period}
                  onClick={() => handlePeriodChange(period)}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    selectedPeriod === period
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {period === 'today' && 'Сегодня'}
                  {period === 'week' && 'Неделя'}
                  {period === 'month' && 'Месяц'}
                  {period === 'year' && 'Год'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          <div className="flex border-b border-gray-200">
            {[
              { id: 'overview', label: 'Обзор', icon: PieChartIcon },
              { id: 'financial', label: 'Финансы', icon: DollarSign },
              { id: 'projects', label: 'Проекты', icon: FolderKanban },
              { id: 'executors', label: 'Исполнители', icon: Users },
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 font-medium transition-all relative ${
                    activeTab === tab.id
                      ? 'text-indigo-600 bg-indigo-50'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                  {activeTab === tab.id && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-600 to-purple-600"></div>
                  )}
                </button>
              )
            })}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Metrics Cards */}
                {dashboardMetrics && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {/* Income Card */}
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-lg p-6 border border-green-200">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-lg">
                          <TrendingUp className="w-6 h-6 text-white" />
                        </div>
                        <span
                          className={`flex items-center gap-1 text-sm font-medium ${
                            dashboardMetrics.changes.income_change >= 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {dashboardMetrics.changes.income_change >= 0 ? (
                            <ArrowUp className="w-4 h-4" />
                          ) : (
                            <ArrowDown className="w-4 h-4" />
                          )}
                          {Math.abs(dashboardMetrics.changes.income_change).toFixed(1)}%
                        </span>
                      </div>
                      <div className="text-3xl font-bold text-green-700 mb-1">
                        {formatCurrency(dashboardMetrics.current_month.income)}
                      </div>
                      <div className="text-sm text-gray-600">Доход за период</div>
                    </div>

                    {/* Expense Card */}
                    <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-xl shadow-lg p-6 border border-red-200">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-rose-500 flex items-center justify-center shadow-lg">
                          <TrendingDown className="w-6 h-6 text-white" />
                        </div>
                        <span
                          className={`flex items-center gap-1 text-sm font-medium ${
                            dashboardMetrics.changes.expense_change >= 0
                              ? 'text-red-600'
                              : 'text-green-600'
                          }`}
                        >
                          {dashboardMetrics.changes.expense_change >= 0 ? (
                            <ArrowUp className="w-4 h-4" />
                          ) : (
                            <ArrowDown className="w-4 h-4" />
                          )}
                          {Math.abs(dashboardMetrics.changes.expense_change).toFixed(1)}%
                        </span>
                      </div>
                      <div className="text-3xl font-bold text-red-700 mb-1">
                        {formatCurrency(dashboardMetrics.current_month.expense)}
                      </div>
                      <div className="text-sm text-gray-600">Расходы</div>
                    </div>

                    {/* Profit Card */}
                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl shadow-lg p-6 border border-blue-200">
                      <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
                          <DollarSign className="w-6 h-6 text-white" />
                        </div>
                      </div>
                      <div
                        className={`text-3xl font-bold mb-1 ${
                          dashboardMetrics.current_month.profit >= 0
                            ? 'text-blue-700'
                            : 'text-red-700'
                        }`}
                      >
                        {formatCurrency(dashboardMetrics.current_month.profit)}
                      </div>
                      <div className="text-sm text-gray-600">Прибыль</div>
                    </div>

                    {/* Projects Completed Card */}
                    {quickStats && (
                      <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl shadow-lg p-6 border border-purple-200">
                        <div className="flex items-center justify-between mb-4">
                          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-violet-500 flex items-center justify-center shadow-lg">
                            <FolderKanban className="w-6 h-6 text-white" />
                          </div>
                        </div>
                        <div className="text-3xl font-bold text-purple-700 mb-1">
                          {quickStats.projects.completed}
                        </div>
                        <div className="text-sm text-gray-600">
                          Проектов завершено ({quickStats.projects.completion_rate.toFixed(1)}%
                          успешность)
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Monthly Chart */}
                  <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">
                      Доходы и расходы по месяцам
                    </h3>
                    <div className="h-80">
                      <Line
                        data={monthlyChartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              display: true,
                              position: 'top',
                            },
                          },
                          scales: {
                            y: {
                              beginAtZero: true,
                              ticks: {
                                callback: function (value) {
                                  return formatCurrency(value as number)
                                },
                              },
                            },
                          },
                        }}
                      />
                    </div>
                  </div>

                  {/* Expense Categories Chart */}
                  <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">
                      Категории расходов
                    </h3>
                    <div className="h-80">
                      <Doughnut
                        data={expenseCategoriesChartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'bottom',
                            },
                          },
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Top Lists */}
                {quickStats && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Top Clients */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-yellow-500" />
                        Топ клиентов
                      </h3>
                      <div className="space-y-3">
                        {quickStats.top_clients.slice(0, 5).map((client, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-yellow-100 text-yellow-700 text-xs font-bold">
                                {index + 1}
                              </span>
                              <span className="text-gray-700">{client.name}</span>
                            </div>
                            <span className="font-semibold text-gray-900">
                              {formatCurrency(client.total_revenue)}
                            </span>
                          </div>
                        ))}
                        {quickStats.top_clients.length === 0 && (
                          <div className="text-center text-gray-500 py-4">Нет данных</div>
                        )}
                      </div>
                    </div>

                    {/* Top Projects */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                        <Star className="w-5 h-5 text-blue-500" />
                        Активные проекты
                      </h3>
                      <div className="space-y-3">
                        {quickStats.projects && (
                          <>
                            <div className="flex items-center justify-between p-3 rounded-lg bg-blue-50">
                              <span className="text-gray-700">Всего проектов</span>
                              <span className="font-semibold text-blue-700">
                                {quickStats.projects.total}
                              </span>
                            </div>
                            <div className="flex items-center justify-between p-3 rounded-lg bg-green-50">
                              <span className="text-gray-700">Завершено</span>
                              <span className="font-semibold text-green-700">
                                {quickStats.projects.completed}
                              </span>
                            </div>
                            <div className="flex items-center justify-between p-3 rounded-lg bg-yellow-50">
                              <span className="text-gray-700">В работе</span>
                              <span className="font-semibold text-yellow-700">
                                {quickStats.projects.in_progress}
                              </span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Top Executors */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                        <Users className="w-5 h-5 text-green-500" />
                        Лучшие исполнители
                      </h3>
                      <div className="space-y-3">
                        {quickStats.top_executors.slice(0, 5).map((executor, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-700 text-xs font-bold">
                                {index + 1}
                              </span>
                              <span className="text-gray-700">{executor.name}</span>
                            </div>
                            <span className="text-sm text-gray-600">
                              {executor.completed_count} проектов
                            </span>
                          </div>
                        ))}
                        {quickStats.top_executors.length === 0 && (
                          <div className="text-center text-gray-500 py-4">Нет данных</div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Financial Tab */}
            {activeTab === 'financial' && (
              <div className="space-y-6">
                {/* P&L Report Link */}
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl shadow-lg p-6 border border-indigo-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 mb-2 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-indigo-600" />
                        Отчет о прибылях и убытках (P&L)
                      </h3>
                      <p className="text-gray-600">
                        Детальный анализ доходов и расходов с графиками и сравнением периодов
                      </p>
                    </div>
                    <a
                      href="/admin/reports/pnl-page"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg"
                    >
                      <ExternalLink className="w-5 h-5" />
                      Открыть полный отчет
                    </a>
                  </div>

                  {financialReport && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                      <div className="text-center p-4 bg-white rounded-lg border border-gray-200">
                        <TrendingUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
                        <div className="text-sm text-gray-600">Доходы</div>
                        <div className="text-2xl font-bold text-green-700">
                          {formatCurrency(financialReport.summary.total_income)}
                        </div>
                      </div>
                      <div className="text-center p-4 bg-white rounded-lg border border-gray-200">
                        <TrendingDown className="w-8 h-8 text-red-500 mx-auto mb-2" />
                        <div className="text-sm text-gray-600">Расходы</div>
                        <div className="text-2xl font-bold text-red-700">
                          {formatCurrency(financialReport.summary.total_expense)}
                        </div>
                      </div>
                      <div className="text-center p-4 bg-white rounded-lg border border-gray-200">
                        <BarChart3 className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                        <div className="text-sm text-gray-600">Прибыль</div>
                        <div className="text-2xl font-bold text-blue-700">
                          {formatCurrency(financialReport.summary.profit)}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Financial Report Table */}
                {financialReport && (
                  <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-800">Финансовый отчет</h3>
                      <button
                        onClick={() => handleExportReport('financial')}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all"
                      >
                        <Download className="w-4 h-4" />
                        Excel
                      </button>
                    </div>

                    {financialReport.monthly_data && financialReport.monthly_data.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-gray-200">
                              <th className="text-left py-3 px-4 text-gray-600 font-semibold">
                                Месяц
                              </th>
                              <th className="text-right py-3 px-4 text-gray-600 font-semibold">
                                Доходы
                              </th>
                              <th className="text-right py-3 px-4 text-gray-600 font-semibold">
                                Расходы
                              </th>
                              <th className="text-right py-3 px-4 text-gray-600 font-semibold">
                                Прибыль
                              </th>
                              <th className="text-right py-3 px-4 text-gray-600 font-semibold">
                                Рентабельность
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {financialReport.monthly_data.map((row, index) => {
                              const profitMargin =
                                row.income > 0 ? (row.profit / row.income) * 100 : 0
                              return (
                                <tr
                                  key={index}
                                  className="border-b border-gray-100 hover:bg-gray-50"
                                >
                                  <td className="py-3 px-4 text-gray-700">{row.month}</td>
                                  <td className="py-3 px-4 text-right text-green-600 font-medium">
                                    {formatCurrency(row.income)}
                                  </td>
                                  <td className="py-3 px-4 text-right text-red-600 font-medium">
                                    {formatCurrency(row.expense)}
                                  </td>
                                  <td
                                    className={`py-3 px-4 text-right font-medium ${
                                      row.profit >= 0 ? 'text-green-600' : 'text-red-600'
                                    }`}
                                  >
                                    {formatCurrency(row.profit)}
                                  </td>
                                  <td className="py-3 px-4 text-right text-gray-700">
                                    {profitMargin.toFixed(1)}%
                                  </td>
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="text-center text-gray-500 py-8">
                        Нет данных за выбранный период
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Projects Tab */}
            {activeTab === 'projects' && (
              <div className="space-y-6">
                {/* Filters */}
                <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-200">
                  <div className="flex flex-wrap items-center gap-4">
                    <select
                      value={projectStatusFilter}
                      onChange={(e) => setProjectStatusFilter(e.target.value)}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="">Все статусы</option>
                      <option value="new">Новые</option>
                      <option value="in_progress">В работе</option>
                      <option value="completed">Завершенные</option>
                      <option value="overdue">Просроченные</option>
                    </select>

                    <select
                      value={executorFilter}
                      onChange={(e) => setExecutorFilter(e.target.value)}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="">Все исполнители</option>
                      {/* Add executors dynamically */}
                    </select>
                  </div>
                </div>

                {/* Projects Report Table */}
                {projectsReport && (
                  <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-800">Отчет по проектам</h3>
                      <button
                        onClick={() => handleExportReport('projects')}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all"
                      >
                        <Download className="w-4 h-4" />
                        Excel
                      </button>
                    </div>

                    {projectsReport.projects.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-gray-200">
                              <th className="text-left py-3 px-4 text-gray-600 font-semibold">
                                Проект
                              </th>
                              <th className="text-left py-3 px-4 text-gray-600 font-semibold">
                                Клиент
                              </th>
                              <th className="text-left py-3 px-4 text-gray-600 font-semibold">
                                Исполнитель
                              </th>
                              <th className="text-left py-3 px-4 text-gray-600 font-semibold">
                                Статус
                              </th>
                              <th className="text-right py-3 px-4 text-gray-600 font-semibold">
                                Стоимость
                              </th>
                              <th className="text-left py-3 px-4 text-gray-600 font-semibold">
                                Прогресс
                              </th>
                              <th className="text-left py-3 px-4 text-gray-600 font-semibold">
                                Дедлайн
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {projectsReport.projects.map((project) => (
                              <tr
                                key={project.id}
                                className="border-b border-gray-100 hover:bg-gray-50"
                              >
                                <td className="py-3 px-4 text-gray-700">{project.title}</td>
                                <td className="py-3 px-4 text-gray-700">{project.client}</td>
                                <td className="py-3 px-4 text-gray-700">
                                  {project.executor || '-'}
                                </td>
                                <td className="py-3 px-4">{getStatusBadge(project.status)}</td>
                                <td className="py-3 px-4 text-right text-gray-700">
                                  {formatCurrency(project.estimated_cost || 0)}
                                </td>
                                <td className="py-3 px-4">
                                  <div className="flex items-center gap-2">
                                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                      <div
                                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                                        style={{ width: `${project.completion_percentage}%` }}
                                      ></div>
                                    </div>
                                    <span className="text-sm text-gray-600 w-12">
                                      {project.completion_percentage}%
                                    </span>
                                  </div>
                                </td>
                                <td className="py-3 px-4 text-gray-700">
                                  {project.deadline ? formatDate(project.deadline) : '-'}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="text-center text-gray-500 py-8">Нет проектов</div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Executors Tab */}
            {activeTab === 'executors' && (
              <div className="space-y-6">
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">
                    Отчет по исполнителям
                  </h3>
                  <div className="text-center text-gray-500 py-8">Функция в разработке</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-6 py-3 rounded-lg shadow-lg text-white ${
              toast.type === 'success'
                ? 'bg-green-500'
                : toast.type === 'error'
                ? 'bg-red-500'
                : 'bg-blue-500'
            } animate-slide-in`}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  )
}
