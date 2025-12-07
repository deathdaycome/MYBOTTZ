import { useState, useEffect, useCallback } from 'react'
import {
  Server,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  Plus,
  RefreshCw,
  Edit2,
  Trash2,
  X,
  Calendar,
  Filter,
  Loader2,
  Network,
  Settings,
  CreditCard,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import hostingApi from '../api/hosting'
import { SearchableProjectDropdown } from '../components/SearchableProjectDropdown'
import ClientBalanceWidget from '../components/ClientBalanceWidget'
import type {
  HostingServer,
  HostingStats,
  HostingProject,
  ServerCreateData,
  PaymentCreateData,
  CalendarEvent,
} from '../api/hosting'

export const Hosting = () => {
  // ============= STATE =============
  const [loading, setLoading] = useState(false) // Изменено на false для мгновенной загрузки из кеша
  const [servers, setServers] = useState<HostingServer[]>([])
  const [filteredServers, setFilteredServers] = useState<HostingServer[]>([])
  const [stats, setStats] = useState<HostingStats | null>(null)
  const [projects, setProjects] = useState<HostingProject[]>([])
  const [lastUpdate, setLastUpdate] = useState<number>(0) // Время последнего обновления

  // Calendar
  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([])
  const [calendarMonth, setCalendarMonth] = useState(new Date().getMonth() + 1)
  const [calendarYear, setCalendarYear] = useState(new Date().getFullYear())

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [sortBy, setSortBy] = useState<'next_payment' | 'profit' | 'client_name'>('next_payment')

  // Modals
  const [showServerModal, setShowServerModal] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [editingServer, setEditingServer] = useState<HostingServer | null>(null)
  const [paymentServer, setPaymentServer] = useState<HostingServer | null>(null)

  // Active Tab
  const [activeTab, setActiveTab] = useState<'servers' | 'calendar'>('servers')

  // Toast notifications
  const [toasts, setToasts] = useState<
    Array<{ id: string; message: string; type: 'success' | 'error' | 'info' | 'warning' }>
  >([])

  const showToast = useCallback(
    (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
      const id = Date.now().toString()
      setToasts((prev) => [...prev, { id, message, type }])
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
      }, 4000)
    },
    []
  )

  // ============= CACHE MANAGEMENT =============

  const CACHE_KEY = 'hosting_data_cache'
  const CACHE_DURATION = 60 * 1000 // 1 минута

  const loadFromCache = useCallback(() => {
    try {
      const cached = localStorage.getItem(CACHE_KEY)
      if (cached) {
        const { data, timestamp } = JSON.parse(cached)
        const age = Date.now() - timestamp

        // Загружаем из кеша даже если устарело (для мгновенного отображения)
        if (data.stats) setStats(data.stats)
        if (data.servers) {
          setServers(data.servers)
          setFilteredServers(data.servers)
        }
        if (data.projects) setProjects(data.projects)
        setLastUpdate(timestamp)

        console.log(`📦 Loaded from cache (age: ${Math.round(age / 1000)}s)`)
        return true
      }
    } catch (error) {
      console.error('Error loading from cache:', error)
    }
    return false
  }, [])

  const saveToCache = useCallback((data: any) => {
    try {
      const timestamp = Date.now()
      localStorage.setItem(
        CACHE_KEY,
        JSON.stringify({
          data,
          timestamp,
        })
      )
      setLastUpdate(timestamp)
      console.log('💾 Saved to cache')
    } catch (error) {
      console.error('Error saving to cache:', error)
    }
  }, [])

  // ============= LOAD DATA =============

  const loadData = useCallback(
    async (silent = false) => {
      try {
        if (!silent) {
          setLoading(true)
        }

        const [statsRes, serversRes, projectsRes] = await Promise.all([
          hostingApi.getStats(),
          hostingApi.getServers(statusFilter || undefined),
          hostingApi.getProjects(),
        ])

        const data: any = {}

        if (statsRes.success) {
          setStats(statsRes.stats)
          data.stats = statsRes.stats
        }

        if (serversRes.success) {
          setServers(serversRes.servers)
          setFilteredServers(serversRes.servers)
          data.servers = serversRes.servers
        }

        if (projectsRes.success) {
          setProjects(projectsRes.projects)
          data.projects = projectsRes.projects
        }

        // Сохраняем в кеш
        saveToCache(data)

        if (silent) {
          console.log('🔄 Background update completed')
        }
      } catch (error: any) {
        console.error('Error loading hosting data:', error)
        if (!silent) {
          showToast('Ошибка загрузки данных', 'error')
        }
      } finally {
        if (!silent) {
          setLoading(false)
        }
      }
    },
    [statusFilter, showToast, saveToCache]
  )

  const loadCalendar = useCallback(async () => {
    try {
      const response = await hostingApi.getCalendar(calendarMonth, calendarYear)
      if (response.success) {
        setCalendarEvents(response.calendar)
      }
    } catch (error: any) {
      console.error('Error loading calendar:', error)
      showToast('Ошибка загрузки календаря', 'error')
    }
  }, [calendarMonth, calendarYear, showToast])

  const syncWithTimeweb = useCallback(async () => {
    try {
      showToast('Синхронизация с Timeweb Cloud...', 'info')
      const response = await hostingApi.syncWithTimeweb()

      if (response.success) {
        const message = `Синхронизация завершена: создано ${response.created_count}, обновлено ${response.updated_count}`
        showToast(message, 'success')

        // Перезагружаем данные после синхронизации
        await loadData(false)
      }
    } catch (error: any) {
      console.error('Error syncing with Timeweb:', error)
      showToast('Ошибка синхронизации с Timeweb Cloud', 'error')
    }
  }, [loadData, showToast])

  // Загрузка данных при первом открытии страницы
  useEffect(() => {
    const init = async () => {
      // 1. Сначала пытаемся загрузить из кеша (мгновенно)
      const hasCache = loadFromCache()

      // 2. Затем загружаем свежие данные в фоне
      if (hasCache) {
        // Если есть кеш - загружаем тихо в фоне
        setTimeout(() => loadData(true), 100)
      } else {
        // Если кеша нет - показываем загрузку
        await loadData(false)
      }
    }

    init()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Запускается только один раз при монтировании

  // Автоматическое обновление данных каждую минуту
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('⏰ Auto-refresh triggered')
      loadData(true) // Тихое обновление в фоне
    }, CACHE_DURATION)

    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [CACHE_DURATION])

  useEffect(() => {
    if (activeTab === 'calendar') {
      loadCalendar()
    }
  }, [activeTab, loadCalendar])

  // ============= FILTER & SORT =============

  useEffect(() => {
    let filtered = [...servers]

    // Search
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (server) =>
          server.client_name.toLowerCase().includes(query) ||
          server.server_name.toLowerCase().includes(query) ||
          server.client_company?.toLowerCase().includes(query) ||
          server.ip_address?.toLowerCase().includes(query)
      )
    }

    // Status filter
    if (statusFilter) {
      filtered = filtered.filter((server) => server.status === statusFilter)
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'next_payment') {
        return new Date(a.next_payment_date).getTime() - new Date(b.next_payment_date).getTime()
      } else if (sortBy === 'profit') {
        return b.profit_amount - a.profit_amount
      } else if (sortBy === 'client_name') {
        return a.client_name.localeCompare(b.client_name)
      }
      return 0
    })

    setFilteredServers(filtered)
  }, [servers, searchQuery, statusFilter, sortBy])

  // ============= SERVER HANDLERS =============

  const handleCreateServer = async (data: ServerCreateData) => {
    try {
      const response = await hostingApi.createServer(data)
      if (response.success) {
        showToast(response.message, 'success')
        setShowServerModal(false)
        setEditingServer(null)
        loadData(false)
      }
    } catch (error: any) {
      console.error('Error creating server:', error)
      showToast(error.response?.data?.detail || 'Ошибка создания сервера', 'error')
    }
  }

  const handleUpdateServer = async (serverId: number, data: ServerCreateData) => {
    try {
      const response = await hostingApi.updateServer(serverId, data)
      if (response.success) {
        showToast(response.message, 'success')
        setShowServerModal(false)
        setEditingServer(null)
        loadData(false)
      }
    } catch (error: any) {
      console.error('Error updating server:', error)
      showToast(error.response?.data?.detail || 'Ошибка обновления сервера', 'error')
    }
  }

  const handleDeleteServer = async (server: HostingServer) => {
    if (!confirm(`Вы уверены, что хотите удалить сервер "${server.server_name}"?`)) return

    try {
      const response = await hostingApi.deleteServer(server.id)
      if (response.success) {
        showToast(response.message, 'success')
        loadData(false)
      }
    } catch (error: any) {
      console.error('Error deleting server:', error)
      showToast(error.response?.data?.detail || 'Ошибка удаления сервера', 'error')
    }
  }

  // ============= PAYMENT HANDLERS =============

  const handleCreatePayment = async (data: PaymentCreateData) => {
    try {
      const response = await hostingApi.createPayment(data)
      if (response.success) {
        showToast(response.message, 'success')
        setShowPaymentModal(false)
        setPaymentServer(null)
        loadData(false)
      }
    } catch (error: any) {
      console.error('Error creating payment:', error)
      showToast(error.response?.data?.detail || 'Ошибка регистрации платежа', 'error')
    }
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
      month: '2-digit',
      day: '2-digit',
    })
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      active: 'bg-green-100 text-green-800',
      overdue: 'bg-red-100 text-red-800',
      suspended: 'bg-yellow-100 text-yellow-800',
      closed: 'bg-gray-100 text-gray-800',
    }

    const labels = {
      active: 'Активен',
      overdue: 'Просрочка',
      suspended: 'Приостановлен',
      closed: 'Закрыт',
    }

    return (
      <span
        className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[status as keyof typeof styles]}`}
      >
        {labels[status as keyof typeof labels]}
      </span>
    )
  }

  const getDaysUntilPayment = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
    return diff
  }

  // ============= CALENDAR HELPERS =============

  const changeMonth = (delta: number) => {
    let newMonth = calendarMonth + delta
    let newYear = calendarYear

    if (newMonth > 12) {
      newMonth = 1
      newYear++
    } else if (newMonth < 1) {
      newMonth = 12
      newYear--
    }

    setCalendarMonth(newMonth)
    setCalendarYear(newYear)
  }

  const getMonthName = (month: number) => {
    const names = [
      'Январь',
      'Февраль',
      'Март',
      'Апрель',
      'Май',
      'Июнь',
      'Июль',
      'Август',
      'Сентябрь',
      'Октябрь',
      'Ноябрь',
      'Декабрь',
    ]
    return names[month - 1]
  }

  // ============= RENDER =============

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-sky-600" />
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="max-w-[2000px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-sky-600 to-blue-600 bg-clip-text text-transparent">
              Хостинг
            </h1>
            <p className="text-gray-600 mt-1">Управление серверами и платежами</p>
          </div>

          <div className="flex items-center gap-3">
            {/* Индикатор последнего обновления */}
            {lastUpdate > 0 && (
              <div className="text-sm text-gray-500 mr-2">
                Обновлено:{' '}
                {new Date(lastUpdate).toLocaleTimeString('ru-RU', {
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                })}
              </div>
            )}

            <button
              onClick={() => loadData(false)}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
              disabled={loading}
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              Обновить
            </button>

            <button
              onClick={syncWithTimeweb}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg hover:from-emerald-600 hover:to-teal-600 transition-all shadow-md"
              title="Синхронизировать серверы с Timeweb Cloud (может занять время)"
            >
              <Network className="w-5 h-5" />
              Синхронизация с Timeweb
            </button>

            <button
              onClick={() => {
                setEditingServer(null)
                setShowServerModal(true)
              }}
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-sky-600 to-blue-600 text-white rounded-lg hover:from-sky-700 hover:to-blue-700 transition-all shadow-lg"
            >
              <Plus className="w-5 h-5" />
              Добавить сервер
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Profit All Time */}
            <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl shadow-lg p-6 border border-purple-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-violet-500 flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-purple-700 mb-1">
                {formatCurrency(stats.profit_all_time)}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">
                Прибыль за всё время
              </div>
            </div>

            {/* Profit Month */}
            <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl shadow-lg p-6 border border-pink-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center shadow-lg">
                  <DollarSign className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-pink-700 mb-1">
                {formatCurrency(stats.profit_month)}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Прибыль за месяц</div>
            </div>

            {/* Active Servers */}
            <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-xl shadow-lg p-6 border border-cyan-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center shadow-lg">
                  <Server className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-cyan-700 mb-1">{stats.active_servers}</div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Активных серверов</div>
            </div>

            {/* Overdue */}
            <div className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl shadow-lg p-6 border border-orange-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center shadow-lg">
                  <AlertTriangle className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-orange-700 mb-1">{stats.overdue_count}</div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">
                Просрочек ({formatCurrency(stats.overdue_sum)})
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-md">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('servers')}
                className={`flex items-center gap-2 px-6 py-4 font-semibold transition-all ${
                  activeTab === 'servers'
                    ? 'border-b-2 border-sky-600 text-sky-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <Server className="w-5 h-5" />
                Серверы
              </button>
              <button
                onClick={() => setActiveTab('calendar')}
                className={`flex items-center gap-2 px-6 py-4 font-semibold transition-all ${
                  activeTab === 'calendar'
                    ? 'border-b-2 border-sky-600 text-sky-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <Calendar className="w-5 h-5" />
                Календарь платежей
              </button>
            </div>
          </div>

          <div className="p-6">
            {/* Servers Tab */}
            {activeTab === 'servers' && (
              <div className="space-y-4">
                {/* Filters */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="relative">
                    <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Поиск по клиенту, серверу, IP..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>

                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
                  >
                    <option value="">Все статусы</option>
                    <option value="active">Активные</option>
                    <option value="overdue">Просрочка</option>
                    <option value="suspended">Приостановлен</option>
                    <option value="closed">Закрыт</option>
                  </select>

                  <select
                    value={sortBy}
                    onChange={(e) =>
                      setSortBy(e.target.value as 'next_payment' | 'profit' | 'client_name')
                    }
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500"
                  >
                    <option value="next_payment">По дате платежа</option>
                    <option value="profit">По прибыли</option>
                    <option value="client_name">По клиенту</option>
                  </select>
                </div>

                {/* Servers Table */}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-800 text-white">
                      <tr>
                        <th className="px-6 py-4 text-left font-semibold">Клиент</th>
                        <th className="px-6 py-4 text-left font-semibold">Баланс / Дни</th>
                        <th className="px-6 py-4 text-left font-semibold">Сервер</th>
                        <th className="px-6 py-4 text-left font-semibold">Конфигурация</th>
                        <th className="px-6 py-4 text-left font-semibold">Дата начала</th>
                        <th className="px-6 py-4 text-left font-semibold">Тариф</th>
                        <th className="px-6 py-4 text-left font-semibold">Прибыль</th>
                        <th className="px-6 py-4 text-left font-semibold">Следующий платеж</th>
                        <th className="px-6 py-4 text-left font-semibold">Статус</th>
                        <th className="px-6 py-4 text-center font-semibold">Действия</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredServers.length === 0 ? (
                        <tr>
                          <td colSpan={10} className="px-6 py-12 text-center">
                            <Server className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                            <p className="text-gray-500 text-lg">Нет серверов</p>
                            <p className="text-gray-400 text-sm mt-2">Добавьте первый сервер</p>
                          </td>
                        </tr>
                      ) : (
                        filteredServers.map((server) => {
                          const daysUntil = getDaysUntilPayment(server.next_payment_date)
                          const paymentClass =
                            daysUntil < 0
                              ? 'text-red-600 font-bold'
                              : daysUntil <= 3
                              ? 'text-yellow-600 font-bold'
                              : 'text-gray-600'

                          return (
                            <tr key={server.id} className="hover:bg-gray-50 transition-colors">
                              <td className="px-6 py-4">
                                <div>
                                  <div className="font-semibold text-gray-800">
                                    {server.client_name}
                                  </div>
                                  {server.client_company && (
                                    <div className="text-sm text-gray-500">
                                      {server.client_company}
                                    </div>
                                  )}
                                </div>
                              </td>
                              <td className="px-6 py-4">
                                <ClientBalanceWidget
                                  clientId={server.client_id}
                                  clientName={server.client_name}
                                  onBalanceUpdate={() => loadData(false)}
                                />
                              </td>
                              <td className="px-6 py-4">
                                <div>
                                  <div className="font-semibold text-gray-800">
                                    {server.server_name}
                                  </div>
                                  {server.ip_address && (
                                    <div className="text-sm text-gray-500 flex items-center gap-1">
                                      <Network className="w-3 h-3" />
                                      {server.ip_address}
                                    </div>
                                  )}
                                </div>
                              </td>
                              <td className="px-6 py-4">
                                <div className="text-sm text-gray-600">
                                  {server.configuration || '—'}
                                </div>
                              </td>
                              <td className="px-6 py-4 text-gray-600">
                                {formatDate(server.start_date)}
                              </td>
                              <td className="px-6 py-4">
                                <div>
                                  <div className="font-semibold text-gray-800">
                                    {formatCurrency(server.total_price)}/мес
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    Себест.: {formatCurrency(server.cost_price)}
                                  </div>
                                </div>
                              </td>
                              <td className="px-6 py-4">
                                <div className="text-green-600 font-semibold">
                                  {formatCurrency(server.profit_amount)}
                                </div>
                                <div className="text-xs text-gray-500">
                                  ({server.profit_percent}%)
                                </div>
                              </td>
                              <td className={`px-6 py-4 ${paymentClass}`}>
                                <div>{formatDate(server.next_payment_date)}</div>
                                <div className="text-xs">
                                  {daysUntil >= 0
                                    ? `через ${daysUntil} дн.`
                                    : `просрочено ${Math.abs(daysUntil)} дн.`}
                                </div>
                              </td>
                              <td className="px-6 py-4">{getStatusBadge(server.status)}</td>
                              <td className="px-6 py-4">
                                <div className="flex items-center justify-center gap-2">
                                  <button
                                    onClick={() => {
                                      setPaymentServer(server)
                                      setShowPaymentModal(true)
                                    }}
                                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                    title="Регистрировать платеж"
                                  >
                                    <CreditCard className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => {
                                      setEditingServer(server)
                                      setShowServerModal(true)
                                    }}
                                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                    title="Редактировать"
                                  >
                                    <Edit2 className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => handleDeleteServer(server)}
                                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                    title="Удалить"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          )
                        })
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Calendar Tab */}
            {activeTab === 'calendar' && (
              <CalendarView
                events={calendarEvents}
                month={calendarMonth}
                year={calendarYear}
                onChangeMonth={changeMonth}
                getMonthName={getMonthName}
                formatCurrency={formatCurrency}
              />
            )}
          </div>
        </div>
      </div>

      {/* Server Modal */}
      {showServerModal && (
        <ServerModal
          isOpen={showServerModal}
          onClose={() => {
            setShowServerModal(false)
            setEditingServer(null)
          }}
          onSave={editingServer ? handleUpdateServer : handleCreateServer}
          server={editingServer}
          projects={projects}
        />
      )}

      {/* Payment Modal */}
      {showPaymentModal && paymentServer && (
        <PaymentModal
          isOpen={showPaymentModal}
          onClose={() => {
            setShowPaymentModal(false)
            setPaymentServer(null)
          }}
          onSave={handleCreatePayment}
          server={paymentServer}
        />
      )}

      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`px-6 py-3 rounded-lg shadow-lg text-white ${
              toast.type === 'success'
                ? 'bg-green-500'
                : toast.type === 'error'
                ? 'bg-red-500'
                : toast.type === 'warning'
                ? 'bg-yellow-500'
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

// ============= SERVER MODAL =============

interface ServerModalProps {
  isOpen: boolean
  onClose: () => void
  onSave:
    | ((data: ServerCreateData) => Promise<void>)
    | ((id: number, data: ServerCreateData) => Promise<void>)
  server: HostingServer | null
  projects: HostingProject[]
}

const ServerModal = ({ isOpen, onClose, onSave, server, projects }: ServerModalProps) => {
  const [formData, setFormData] = useState<ServerCreateData>({
    project_id: server?.project_id || null,
    client_id: server?.client_id || null,
    client_name: server?.client_name || '',
    client_company: server?.client_company || null,
    client_telegram_id: server?.client_telegram_id || null,
    server_name: server?.server_name || '',
    configuration: server?.configuration || null,
    ip_address: server?.ip_address || null,
    cost_price: server?.cost_price || 0,
    client_price: server?.client_price || 0,
    service_fee: server?.service_fee || 0,
    start_date: server?.start_date
      ? server.start_date.split('T')[0]
      : new Date().toISOString().split('T')[0],
    next_payment_date: server?.next_payment_date
      ? server.next_payment_date.split('T')[0]
      : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    payment_period: server?.payment_period || 'monthly',
    notes: server?.notes || null,
  })

  const handleProjectChange = async (projectId: string) => {
    if (!projectId) {
      setFormData({ ...formData, project_id: null })
      return
    }

    try {
      const response = await hostingApi.getProjectData(parseInt(projectId))
      if (response.success && response.project) {
        setFormData({
          ...formData,
          project_id: parseInt(projectId),
          client_name: response.project.client_name,
          client_telegram_id: response.project.client_telegram_id || null,
          server_name: formData.server_name || `Сервер для "${response.project.title}"`,
        })
      }
    } catch (error) {
      console.error('Error loading project data:', error)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const dataToSend = {
      ...formData,
      start_date: formData.start_date + 'T00:00:00',
      next_payment_date: formData.next_payment_date + 'T00:00:00',
    }

    if (server) {
      ;(onSave as any)(server.id, dataToSend)
    } else {
      ;(onSave as any)(dataToSend)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">
            {server ? 'Редактировать сервер' : 'Добавить сервер'}
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Project Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Привязать к проекту (опционально)
              {projects.length > 0 && (
                <span className="ml-2 text-xs text-gray-500">
                  (Доступно проектов: {projects.length})
                </span>
              )}
            </label>
            {projects.length === 0 ? (
              <div className="px-4 py-3 border-2 border-yellow-300 bg-yellow-50 rounded-lg text-sm text-yellow-800">
                Проекты загружаются...
              </div>
            ) : (
              <SearchableProjectDropdown
                projects={projects}
                value={formData.project_id}
                onChange={(projectId) => {
                  handleProjectChange(projectId ? projectId.toString() : '')
                }}
                placeholder="Выберите проект или оставьте без привязки"
              />
            )}
            <p className="text-xs text-gray-500 mt-1">
              При выборе проекта данные клиента заполнятся автоматически
            </p>
          </div>

          <hr className="my-4" />

          {/* Client Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Имя клиента <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.client_name}
                onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Компания</label>
              <input
                type="text"
                value={formData.client_company || ''}
                onChange={(e) => setFormData({ ...formData, client_company: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Telegram ID (для уведомлений)
              </label>
              <input
                type="number"
                value={formData.client_telegram_id || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    client_telegram_id: e.target.value ? parseInt(e.target.value) : null,
                  })
                }
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Название сервера <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.server_name}
                onChange={(e) => setFormData({ ...formData, server_name: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                required
              />
            </div>
          </div>

          {/* Server Configuration */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Конфигурация (CPU, RAM, SSD)
            </label>
            <textarea
              value={formData.configuration || ''}
              onChange={(e) => setFormData({ ...formData, configuration: e.target.value })}
              rows={2}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
              placeholder="Например: 2 CPU, 4GB RAM, 50GB SSD"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">IP адрес</label>
            <input
              type="text"
              value={formData.ip_address || ''}
              onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
              placeholder="192.168.1.1"
            />
          </div>

          <hr className="my-4" />

          {/* Pricing */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Себестоимость (₽/мес) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.cost_price}
                onChange={(e) => setFormData({ ...formData, cost_price: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Цена для клиента (₽/мес) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.client_price}
                onChange={(e) =>
                  setFormData({ ...formData, client_price: parseFloat(e.target.value) })
                }
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Стоимость обслуживания (₽/мес)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.service_fee}
                onChange={(e) => setFormData({ ...formData, service_fee: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
              />
            </div>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Дата начала аренды <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Следующий платеж <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.next_payment_date}
                onChange={(e) => setFormData({ ...formData, next_payment_date: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Периодичность <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.payment_period}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    payment_period: e.target.value as 'monthly' | 'quarterly' | 'yearly',
                  })
                }
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                required
              >
                <option value="monthly">Ежемесячно</option>
                <option value="quarterly">Раз в 3 месяца</option>
                <option value="yearly">Раз в год</option>
              </select>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Заметки</label>
            <textarea
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all font-semibold"
            >
              Отмена
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-gradient-to-r from-sky-600 to-blue-600 text-white rounded-lg hover:from-sky-700 hover:to-blue-700 transition-all font-semibold shadow-lg"
            >
              {server ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ============= PAYMENT MODAL =============

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: PaymentCreateData) => Promise<void>
  server: HostingServer
}

const PaymentModal = ({ isOpen, onClose, onSave, server }: PaymentModalProps) => {
  const [formData, setFormData] = useState<PaymentCreateData>({
    server_id: server.id,
    amount: server.total_price,
    payment_date: new Date().toISOString().slice(0, 16),
    expected_date: server.next_payment_date,
    period_start: server.next_payment_date,
    period_end: server.next_payment_date,
    status: 'paid',
    payment_method: null,
    notes: null,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full">
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <h2 className="text-xl font-bold text-gray-800">Регистрация платежа</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="bg-sky-50 rounded-lg p-4 mb-4">
            <div className="font-semibold text-gray-800">Сервер:</div>
            <div className="text-gray-600">{server.server_name}</div>
            <div className="text-sm text-gray-500 mt-1">Клиент: {server.client_name}</div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Сумма платежа (₽) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Дата получения платежа <span className="text-red-500">*</span>
            </label>
            <input
              type="datetime-local"
              value={formData.payment_date || ''}
              onChange={(e) => setFormData({ ...formData, payment_date: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Способ оплаты</label>
            <select
              value={formData.payment_method || ''}
              onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
            >
              <option value="">Не указан</option>
              <option value="card">Карта</option>
              <option value="bank">Банковский перевод</option>
              <option value="cash">Наличные</option>
              <option value="other">Другое</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Период оплаты</label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="date"
                value={formData.period_start.split('T')[0]}
                onChange={(e) =>
                  setFormData({ ...formData, period_start: e.target.value + 'T00:00:00' })
                }
                className="px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                placeholder="Начало"
              />
              <input
                type="date"
                value={formData.period_end.split('T')[0]}
                onChange={(e) =>
                  setFormData({ ...formData, period_end: e.target.value + 'T00:00:00' })
                }
                className="px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
                placeholder="Конец"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Заметки</label>
            <textarea
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={2}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-sky-500 outline-none"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all font-semibold"
            >
              Отмена
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all font-semibold shadow-lg"
            >
              Зарегистрировать
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ============= CALENDAR VIEW =============

interface CalendarViewProps {
  events: CalendarEvent[]
  month: number
  year: number
  onChangeMonth: (delta: number) => void
  getMonthName: (month: number) => string
  formatCurrency: (amount: number) => string
}

const CalendarView = ({
  events,
  month,
  year,
  onChangeMonth,
  getMonthName,
  formatCurrency,
}: CalendarViewProps) => {
  // Группируем события по датам
  const eventsByDate: Record<string, CalendarEvent[]> = {}
  events.forEach((event) => {
    if (!eventsByDate[event.date]) {
      eventsByDate[event.date] = []
    }
    eventsByDate[event.date].push(event)
  })

  // Создаем календарную сетку
  const firstDay = new Date(year, month - 1, 1)
  const lastDay = new Date(year, month, 0)
  const daysInMonth = lastDay.getDate()
  const startDay = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1 // Понедельник = 0

  const weeks: Array<Array<number | null>> = []
  let currentWeek: Array<number | null> = Array(startDay).fill(null)
  let dayCounter = 1

  while (dayCounter <= daysInMonth) {
    currentWeek.push(dayCounter)
    dayCounter++

    if (currentWeek.length === 7) {
      weeks.push(currentWeek)
      currentWeek = []
    }
  }

  if (currentWeek.length > 0) {
    while (currentWeek.length < 7) {
      currentWeek.push(null)
    }
    weeks.push(currentWeek)
  }

  const getEventClass = (color: string) => {
    const classes = {
      green: 'bg-green-100 text-green-700 border-l-4 border-green-500',
      blue: 'bg-blue-100 text-blue-700 border-l-4 border-blue-500',
      yellow: 'bg-yellow-100 text-yellow-700 border-l-4 border-yellow-500',
      red: 'bg-red-100 text-red-700 border-l-4 border-red-500',
    }
    return classes[color as keyof typeof classes] || 'bg-gray-100 text-gray-700 border-l-4 border-gray-500'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h5 className="text-xl font-bold text-gray-800">Платежи по календарю</h5>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onChangeMonth(-1)}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="px-6 py-2 bg-sky-50 rounded-lg font-semibold text-gray-800 min-w-[200px] text-center">
            {getMonthName(month)} {year}
          </div>
          <button
            onClick={() => onChangeMonth(1)}
            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Weekday headers */}
      <div className="grid grid-cols-7 gap-2">
        {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map((day) => (
          <div key={day} className="text-center font-bold text-gray-600 py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-2">
        {weeks.map((week, weekIdx) =>
          week.map((day, dayIdx) => {
            if (!day) {
              return (
                <div
                  key={`${weekIdx}-${dayIdx}`}
                  className="min-h-[100px] bg-gray-50 rounded-lg border border-gray-200"
                />
              )
            }

            const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            const dayEvents = eventsByDate[dateStr] || []

            return (
              <div
                key={`${weekIdx}-${dayIdx}`}
                className="min-h-[100px] bg-white rounded-lg border border-gray-200 p-2 hover:bg-gray-50 transition-colors"
              >
                <div className="font-bold text-gray-700 mb-2">{day}</div>
                <div className="space-y-1">
                  {dayEvents.map((event) => (
                    <div
                      key={event.id}
                      className={`text-xs p-1 rounded ${getEventClass(event.color)}`}
                      title={event.title}
                    >
                      {formatCurrency(event.amount)}
                    </div>
                  ))}
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-sm">
        <span className="px-3 py-1 bg-green-100 text-green-700 border-l-4 border-green-500 rounded">
          Оплачено
        </span>
        <span className="px-3 py-1 bg-blue-100 text-blue-700 border-l-4 border-blue-500 rounded">
          Ожидается
        </span>
        <span className="px-3 py-1 bg-yellow-100 text-yellow-700 border-l-4 border-yellow-500 rounded">
          Скоро (≤3 дня)
        </span>
        <span className="px-3 py-1 bg-red-100 text-red-700 border-l-4 border-red-500 rounded">
          Просрочка
        </span>
      </div>
    </div>
  )
}
