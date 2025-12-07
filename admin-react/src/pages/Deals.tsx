import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Handshake,
  Plus,
  Search,
  Filter,
  RefreshCw,
  Download,
  X,
  DollarSign,
  Calendar,
  User,
  TrendingUp,
  Edit2,
  Trash2,
  ArrowRightCircle,
  Target,
  LayoutGrid,
  List,
  Briefcase,
} from 'lucide-react'
import dealsApi from '../api/deals'
import type { Deal, DealFilters, DealStats, PipelineData, PipelineStats } from '../api/deals'

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

export const Deals = () => {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<DealFilters>({ page: 1, limit: 20 })
  const [showFilters, setShowFilters] = useState(false)
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    limit: 20,
    pages: 1,
  })
  const [stats, setStats] = useState<DealStats>({
    total: 0,
    active: 0,
    completed_month: 0,
    total_amount: 0,
    paid_amount: 0,
    payment_progress: 0,
  })

  // View mode: table or kanban
  const [viewMode, setViewMode] = useState<'table' | 'kanban'>('table')
  const [pipelineData, setPipelineData] = useState<PipelineData | null>(null)
  const [pipelineStats, setPipelineStats] = useState<PipelineStats | null>(null)

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null)

  // Toast notifications
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  // Load deals
  const loadDeals = useCallback(async () => {
    try {
      setLoading(true)
      const response = await dealsApi.getDeals(filters)

      if (response.success) {
        setDeals(response.deals)
        setPagination(response.pagination)

        // Calculate stats from deals
        const totalDeals = response.pagination.total
        const activeStatuses = [
          'new',
          'discussion',
          'contract_prep',
          'contract_signed',
          'prepayment',
          'in_work',
          'testing',
          'acceptance',
          'payment',
        ]
        const activeDeals = response.deals.filter((d) => activeStatuses.includes(d.status)).length
        const totalAmount = response.deals.reduce((sum, d) => sum + (d.amount || 0), 0)
        const paidAmount = response.deals.reduce((sum, d) => sum + (d.paid_amount || 0), 0)

        setStats({
          total: totalDeals,
          active: activeDeals,
          completed_month: 0, // Would need separate API call for this
          total_amount: totalAmount,
          paid_amount: paidAmount,
          payment_progress: totalAmount > 0 ? (paidAmount / totalAmount) * 100 : 0,
        })
      }
    } catch (error) {
      console.error('Error loading deals:', error)
      showToast('Ошибка загрузки сделок', 'error')
    } finally {
      setLoading(false)
    }
  }, [filters, showToast])

  // Load pipeline data
  const loadPipeline = useCallback(async () => {
    try {
      const response = await dealsApi.getPipeline()
      if (response.success) {
        setPipelineData(response.pipeline)
        setPipelineStats(response.stats)
      }
    } catch (error) {
      console.error('Error loading pipeline:', error)
      showToast('Ошибка загрузки воронки', 'error')
    }
  }, [showToast])

  useEffect(() => {
    if (viewMode === 'table') {
      loadDeals()
    } else {
      loadPipeline()
    }
  }, [viewMode, loadDeals, loadPipeline])

  // Refresh all data
  const handleRefresh = useCallback(() => {
    if (viewMode === 'table') {
      loadDeals()
    } else {
      loadPipeline()
    }
  }, [viewMode, loadDeals, loadPipeline])

  // Apply filters
  const applyFilters = useCallback(() => {
    setFilters((prev) => ({ ...prev, page: 1 }))
  }, [])

  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({ page: 1, limit: 20 })
  }, [])

  // Toggle view mode
  const toggleViewMode = useCallback(() => {
    setViewMode((prev) => (prev === 'table' ? 'kanban' : 'table'))
  }, [])

  // Open create modal
  const openCreateModal = useCallback(() => {
    setShowCreateModal(true)
    document.body.style.overflow = 'hidden'
  }, [])

  // Close create modal
  const closeCreateModal = useCallback(() => {
    setShowCreateModal(false)
    document.body.style.overflow = 'auto'
  }, [])

  // Open payment modal
  const openPaymentModal = useCallback((deal: Deal) => {
    setSelectedDeal(deal)
    setShowPaymentModal(true)
    document.body.style.overflow = 'hidden'
  }, [])

  // Close payment modal
  const closePaymentModal = useCallback(() => {
    setShowPaymentModal(false)
    setSelectedDeal(null)
    document.body.style.overflow = 'auto'
  }, [])

  // Handle convert to project
  const handleConvertToProject = useCallback(
    async (dealId: number) => {
      if (!confirm('Создать проект на основе этой сделки?')) return

      try {
        const response = await dealsApi.convertToProject(dealId, {})
        if (response.success) {
          showToast('Сделка успешно конвертирована в проект', 'success')
          setTimeout(() => {
            window.location.href = '/projects'
          }, 1500)
        } else {
          showToast(response.message || 'Ошибка конвертации', 'error')
        }
      } catch (error: any) {
        console.error('Error converting deal:', error)
        showToast(error.response?.data?.message || 'Ошибка конвертации', 'error')
      }
    },
    [showToast]
  )

  // Handle page change
  const handlePageChange = useCallback((page: number) => {
    setFilters((prev) => ({ ...prev, page }))
  }, [])

  // Status label mapping
  const getStatusLabel = (status: string): string => {
    const labels: { [key: string]: string } = {
      new: 'Новая',
      discussion: 'Обсуждение',
      contract_prep: 'Подготовка договора',
      contract_signed: 'Договор подписан',
      prepayment: 'Ожидание предоплаты',
      in_work: 'В работе',
      testing: 'Тестирование',
      acceptance: 'Приемка',
      payment: 'Ожидание оплаты',
      completed: 'Завершена',
      cancelled: 'Отменена',
    }
    return labels[status] || status
  }

  // Status badge color
  const getStatusColor = (status: string): string => {
    const colors: { [key: string]: string } = {
      new: 'bg-blue-100 text-blue-700',
      discussion: 'bg-pink-100 text-pink-700',
      contract_prep: 'bg-orange-100 text-orange-700',
      contract_signed: 'bg-green-100 text-green-700',
      prepayment: 'bg-rose-100 text-rose-700',
      in_work: 'bg-teal-100 text-teal-700',
      testing: 'bg-cyan-100 text-cyan-700',
      acceptance: 'bg-purple-100 text-purple-700',
      payment: 'bg-amber-100 text-amber-700',
      completed: 'bg-emerald-100 text-emerald-700',
      cancelled: 'bg-red-100 text-red-700',
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  // Priority label mapping
  const getPriorityLabel = (priority: string): string => {
    const labels: { [key: string]: string } = {
      low: 'Низкий',
      normal: 'Обычный',
      high: 'Высокий',
      urgent: 'Срочный',
    }
    return labels[priority] || priority
  }

  // Priority badge color
  const getPriorityColor = (priority: string): string => {
    const colors: { [key: string]: string } = {
      low: 'bg-gray-100 text-gray-700',
      normal: 'bg-blue-100 text-blue-700',
      high: 'bg-orange-100 text-orange-700',
      urgent: 'bg-red-100 text-red-700',
    }
    return colors[priority] || 'bg-gray-100 text-gray-700'
  }

  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  // Check if deal can be converted to project
  const canConvertToProject = (deal: Deal): boolean => {
    return (
      ['contract_signed', 'prepayment', 'in_work'].includes(deal.status) && !deal.project_id
    )
  }

  return (
    <div className="p-6">
      <div className="max-w-[2000px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Handshake className="w-7 h-7 text-white" />
              </div>
              Управление сделками
            </h1>
            <p className="text-gray-600 mt-1">Контроль продаж и договоров</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
            >
              <Filter className="w-5 h-5" />
              Фильтры
            </button>

            <button className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200">
              <Download className="w-5 h-5" />
              Экспорт
            </button>

            <button
              onClick={handleRefresh}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
            >
              <RefreshCw className="w-5 h-5" />
            </button>

            <button
              onClick={toggleViewMode}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
            >
              {viewMode === 'table' ? (
                <>
                  <LayoutGrid className="w-5 h-5" />
                  Канбан
                </>
              ) : (
                <>
                  <List className="w-5 h-5" />
                  Таблица
                </>
              )}
            </button>

            <button
              onClick={openCreateModal}
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg"
            >
              <Plus className="w-5 h-5" />
              Новая сделка
            </button>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="text-4xl font-bold mb-2">{stats.total}</div>
            <div className="text-sm opacity-90">Всего сделок</div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="text-4xl font-bold mb-2">{stats.active}</div>
            <div className="text-sm opacity-90">Активных</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-amber-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="text-4xl font-bold mb-2">{formatCurrency(stats.total_amount)}</div>
            <div className="text-sm opacity-90">Сумма сделок</div>
          </div>

          <div className="bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
            <div className="text-4xl font-bold mb-2">{stats.payment_progress.toFixed(1)}%</div>
            <div className="text-sm opacity-90">Оплачено</div>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="grid grid-cols-6 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Поиск</label>
                <input
                  type="text"
                  value={filters.search || ''}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="Название, договор..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Статус</label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                >
                  <option value="">Все статусы</option>
                  <option value="new">Новая</option>
                  <option value="discussion">Обсуждение</option>
                  <option value="contract_prep">Подготовка договора</option>
                  <option value="contract_signed">Договор подписан</option>
                  <option value="prepayment">Ожидание предоплаты</option>
                  <option value="in_work">В работе</option>
                  <option value="testing">Тестирование</option>
                  <option value="acceptance">Приемка</option>
                  <option value="payment">Ожидание оплаты</option>
                  <option value="completed">Завершена</option>
                  <option value="cancelled">Отменена</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Приоритет</label>
                <select
                  value={filters.priority || ''}
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                >
                  <option value="">Все приоритеты</option>
                  <option value="low">Низкий</option>
                  <option value="normal">Обычный</option>
                  <option value="high">Высокий</option>
                  <option value="urgent">Срочный</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Клиент ID
                </label>
                <input
                  type="number"
                  value={filters.client_id || ''}
                  onChange={(e) =>
                    setFilters({ ...filters, client_id: e.target.value ? +e.target.value : undefined })
                  }
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="ID клиента"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Менеджер ID
                </label>
                <input
                  type="number"
                  value={filters.manager_id || ''}
                  onChange={(e) =>
                    setFilters({ ...filters, manager_id: e.target.value ? +e.target.value : undefined })
                  }
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="ID менеджера"
                />
              </div>

              <div className="flex items-end gap-2">
                <button
                  onClick={applyFilters}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all font-semibold"
                >
                  Применить
                </button>
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all font-semibold"
                >
                  Очистить
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Table View */}
        {viewMode === 'table' && (
          <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
              </div>
            ) : deals.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-gradient-to-br from-green-100 to-emerald-100 rounded-3xl flex items-center justify-center mb-6 mx-auto">
                  <Handshake className="w-12 h-12 text-green-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Сделки не найдены</h3>
                <p className="text-gray-600 mb-6">Добавьте первую сделку, чтобы начать работу</p>
                <button
                  onClick={openCreateModal}
                  className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-xl transition-all"
                >
                  <Plus className="w-5 h-5" />
                  Добавить первую сделку
                </button>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gradient-to-r from-gray-50 to-green-50">
                      <tr>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          ID
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          Название
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          Клиент
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          Статус
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          Сумма
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          Оплачено
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          Менеджер
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          Исполнитель
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                          Действия
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {deals.map((deal) => (
                        <tr
                          key={deal.id}
                          className="hover:bg-gradient-to-r hover:from-green-50/50 hover:to-emerald-50/50 transition-colors"
                        >
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            #{deal.id}
                          </td>
                          <td className="px-6 py-4">
                            <div className="font-semibold text-gray-900">{deal.title}</div>
                            {deal.priority !== 'normal' && (
                              <span
                                className={`inline-block mt-1 px-2 py-1 rounded-full text-xs font-semibold ${getPriorityColor(deal.priority)}`}
                              >
                                {getPriorityLabel(deal.priority)}
                              </span>
                            )}
                            {deal.project_id && (
                              <div className="mt-2">
                                <a
                                  href={`/projects/${deal.project_id}`}
                                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-md text-xs font-medium hover:bg-blue-200 transition-colors"
                                  title={`Проект #${deal.project_id}`}
                                >
                                  <Briefcase className="w-3 h-3" />
                                  <span>Проект #{deal.project_id}</span>
                                  <ArrowRightCircle className="w-3 h-3" />
                                </a>
                              </div>
                            )}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {deal.client_name || '-'}
                          </td>
                          <td className="px-6 py-4">
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(deal.status)}`}
                            >
                              {getStatusLabel(deal.status)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                            {formatCurrency(deal.amount)}
                          </td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900 font-medium mb-1">
                              {formatCurrency(deal.paid_amount || 0)}
                            </div>
                            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-red-500 via-orange-500 to-green-500 transition-all"
                                style={{ width: `${deal.payment_progress || 0}%` }}
                              ></div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {deal.manager_name || '-'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {deal.executor_name || '-'}
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => openPaymentModal(deal)}
                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                title="Добавить платеж"
                              >
                                <DollarSign className="w-4 h-4" />
                              </button>
                              {canConvertToProject(deal) && (
                                <button
                                  onClick={() => handleConvertToProject(deal.id)}
                                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                  title="Создать проект"
                                >
                                  <Briefcase className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {pagination.pages > 1 && (
                  <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Показано {deals.length} из {pagination.total} сделок
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handlePageChange(pagination.page - 1)}
                        disabled={pagination.page === 1}
                        className="px-4 py-2 bg-white border-2 border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        ‹ Назад
                      </button>

                      {[...Array(Math.min(pagination.pages, 5))].map((_, i) => {
                        const page = i + 1
                        return (
                          <button
                            key={page}
                            onClick={() => handlePageChange(page)}
                            className={`px-4 py-2 rounded-lg transition-all ${
                              pagination.page === page
                                ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
                                : 'bg-white border-2 border-gray-200 hover:bg-gray-50'
                            }`}
                          >
                            {page}
                          </button>
                        )
                      })}

                      <button
                        onClick={() => handlePageChange(pagination.page + 1)}
                        disabled={pagination.page === pagination.pages}
                        className="px-4 py-2 bg-white border-2 border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        Вперед ›
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Kanban View */}
        {viewMode === 'kanban' && pipelineData && (
          <KanbanView
            pipeline={pipelineData}
            stats={pipelineStats}
            formatCurrency={formatCurrency}
            getStatusLabel={getStatusLabel}
          />
        )}
      </div>

      {/* Create Deal Modal */}
      {showCreateModal && (
        <CreateDealModal
          onClose={closeCreateModal}
          onSuccess={() => {
            closeCreateModal()
            handleRefresh()
            showToast('Сделка успешно создана', 'success')
          }}
          showToast={showToast}
        />
      )}

      {/* Payment Modal */}
      {showPaymentModal && selectedDeal && (
        <PaymentModal
          deal={selectedDeal}
          onClose={closePaymentModal}
          onSuccess={() => {
            closePaymentModal()
            handleRefresh()
            showToast('Платеж успешно добавлен', 'success')
          }}
          showToast={showToast}
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

// Kanban View Component
interface KanbanViewProps {
  pipeline: PipelineData
  stats: PipelineStats | null
  formatCurrency: (amount: number) => string
  getStatusLabel: (status: string) => string
}

const KanbanView = ({ pipeline, stats, formatCurrency, getStatusLabel }: KanbanViewProps) => {
  const columns = [
    { key: 'new', label: 'Новые', gradient: 'from-purple-500 to-pink-600' },
    { key: 'discussion', label: 'Обсуждение', gradient: 'from-pink-500 to-red-500' },
    { key: 'contract_prep', label: 'Договор', gradient: 'from-cyan-400 to-blue-500' },
    { key: 'in_work', label: 'В работе', gradient: 'from-emerald-400 to-teal-500' },
    { key: 'testing', label: 'Тестирование', gradient: 'from-orange-400 to-pink-500' },
    { key: 'payment', label: 'Оплата', gradient: 'from-teal-500 to-blue-700' },
  ]

  return (
    <div className="bg-white rounded-3xl shadow-xl p-6">
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((column) => {
          const deals = (pipeline as any)[column.key] || []
          const columnStats = stats ? stats[column.key] : null

          return (
            <div key={column.key} className="flex-shrink-0" style={{ width: '300px' }}>
              <div className="bg-gray-50 rounded-2xl p-4 min-h-[500px]">
                <div
                  className={`bg-gradient-to-br ${column.gradient} text-white rounded-xl p-4 mb-4`}
                >
                  <div className="font-bold text-lg">{column.label}</div>
                  <div className="text-sm opacity-90 mt-1">
                    {columnStats ? `${columnStats.count} сделок` : `${deals.length} сделок`}
                  </div>
                </div>

                <div className="space-y-3">
                  {deals.length === 0 ? (
                    <div className="text-center text-gray-400 py-8">Нет сделок</div>
                  ) : (
                    deals.map((deal: any) => (
                      <div
                        key={deal.id}
                        className="bg-white rounded-xl p-4 border-l-4 border-green-500 shadow-md hover:shadow-lg transition-all cursor-move"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h6 className="font-bold text-gray-900">{deal.title}</h6>
                          <span className="text-xs font-semibold text-gray-500">#{deal.id}</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{deal.client_name}</p>
                        <div className="text-lg font-bold text-green-600 mb-2">
                          {formatCurrency(deal.amount)}
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
                          <div
                            className="h-full bg-gradient-to-r from-red-500 via-orange-500 to-green-500"
                            style={{ width: `${deal.payment_progress || 0}%` }}
                          ></div>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>{deal.manager_name || 'Не назначен'}</span>
                          <span>{deal.days_in_status || 0} дн.</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Create Deal Modal Component
interface CreateDealModalProps {
  onClose: () => void
  onSuccess: () => void
  showToast: (message: string, type: 'success' | 'error' | 'info') => void
}

const CreateDealModal = ({ onClose, onSuccess, showToast }: CreateDealModalProps) => {
  const [formData, setFormData] = useState({
    title: '',
    client_id: '',
    description: '',
    technical_requirements: '',
    amount: '',
    cost: '',
    discount: '0',
    prepayment_percent: '50',
    start_date: '',
    end_date: '',
    manager_id: '',
    executor_id: '',
    priority: 'normal',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim()) {
      showToast('Название обязательно', 'error')
      return
    }

    if (!formData.client_id) {
      showToast('Клиент обязателен', 'error')
      return
    }

    if (!formData.amount || +formData.amount <= 0) {
      showToast('Сумма сделки обязательна', 'error')
      return
    }

    setLoading(true)

    try {
      const data: any = {
        title: formData.title,
        client_id: +formData.client_id,
        description: formData.description || undefined,
        technical_requirements: formData.technical_requirements || undefined,
        amount: +formData.amount,
        cost: formData.cost ? +formData.cost : undefined,
        discount: formData.discount ? +formData.discount : 0,
        prepayment_percent: formData.prepayment_percent ? +formData.prepayment_percent : 50,
        start_date: formData.start_date || undefined,
        end_date: formData.end_date || undefined,
        manager_id: formData.manager_id ? +formData.manager_id : undefined,
        executor_id: formData.executor_id ? +formData.executor_id : undefined,
        priority: formData.priority,
      }

      const response = await dealsApi.createDeal(data)

      if (response.success) {
        onSuccess()
      } else {
        showToast(response.message || 'Ошибка создания сделки', 'error')
      }
    } catch (error: any) {
      console.error('Error creating deal:', error)
      showToast(error.response?.data?.message || 'Ошибка создания сделки', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl">
          {/* Header */}
          <div className="sticky top-0 bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-5 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-white">Новая сделка</h3>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-white" />
              </button>
            </div>
          </div>

          {/* Body */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
            {/* Title and Client */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Название <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="Название сделки"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  ID клиента <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="ID клиента"
                  required
                />
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Описание</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all resize-none"
                placeholder="Описание сделки"
              />
            </div>

            {/* Financial Details */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Сумма сделки <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="0"
                  min="0"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Себестоимость
                </label>
                <input
                  type="number"
                  value={formData.cost}
                  onChange={(e) => setFormData({ ...formData, cost: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="0"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Скидка</label>
                <input
                  type="number"
                  value={formData.discount}
                  onChange={(e) => setFormData({ ...formData, discount: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="0"
                  min="0"
                />
              </div>
            </div>

            {/* Priority and Prepayment */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Предоплата (%)
                </label>
                <input
                  type="number"
                  value={formData.prepayment_percent}
                  onChange={(e) =>
                    setFormData({ ...formData, prepayment_percent: e.target.value })
                  }
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  min="0"
                  max="100"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Приоритет</label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                >
                  <option value="low">Низкий</option>
                  <option value="normal">Обычный</option>
                  <option value="high">Высокий</option>
                  <option value="urgent">Срочный</option>
                </select>
              </div>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Дата начала
                </label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Дата окончания
                </label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                />
              </div>
            </div>

            {/* Managers */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  ID менеджера
                </label>
                <input
                  type="number"
                  value={formData.manager_id}
                  onChange={(e) => setFormData({ ...formData, manager_id: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="ID менеджера"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  ID исполнителя
                </label>
                <input
                  type="number"
                  value={formData.executor_id}
                  onChange={(e) => setFormData({ ...formData, executor_id: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                  placeholder="ID исполнителя"
                />
              </div>
            </div>
          </form>

          {/* Footer */}
          <div className="sticky bottom-0 bg-gray-50 px-6 py-4 rounded-b-3xl flex items-center justify-end gap-3 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-all"
            >
              Отмена
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Создание...' : 'Создать сделку'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Payment Modal Component
interface PaymentModalProps {
  deal: Deal
  onClose: () => void
  onSuccess: () => void
  showToast: (message: string, type: 'success' | 'error' | 'info') => void
}

const PaymentModal = ({ deal, onClose, onSuccess, showToast }: PaymentModalProps) => {
  const [formData, setFormData] = useState({
    amount: '',
    type: 'payment',
    description: '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.amount || +formData.amount <= 0) {
      showToast('Сумма платежа должна быть больше 0', 'error')
      return
    }

    setLoading(true)

    try {
      const response = await dealsApi.addPayment(
        deal.id,
        +formData.amount,
        formData.type,
        formData.description || undefined
      )

      if (response.success) {
        onSuccess()
      } else {
        showToast(response.message || 'Ошибка добавления платежа', 'error')
      }
    } catch (error: any) {
      console.error('Error adding payment:', error)
      showToast(error.response?.data?.message || 'Ошибка добавления платежа', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl">
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-5 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-white">Добавить платеж</h3>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-white" />
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Сумма платежа <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                placeholder="0"
                min="1"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Тип платежа
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
              >
                <option value="prepayment">Предоплата</option>
                <option value="payment">Оплата</option>
                <option value="final">Финальная оплата</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Описание</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all resize-none"
                placeholder="Дополнительное описание"
              />
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-all"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg disabled:opacity-50"
              >
                {loading ? 'Добавление...' : 'Добавить платеж'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
