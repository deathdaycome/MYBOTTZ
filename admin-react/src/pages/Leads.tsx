import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  TrendingUp,
  Plus,
  Search,
  Filter,
  RefreshCw,
  Download,
  X,
  Phone,
  Mail,
  MessageCircle,
  DollarSign,
  Calendar,
  User,
  Briefcase,
  TrendingDown,
  Edit2,
  Trash2,
  ArrowRightCircle,
  Target,
} from 'lucide-react'
import leadsApi from '../api/leads'
import type { Lead, LeadFilters, FunnelStats } from '../api/leads'

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

export const Leads = () => {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<LeadFilters>({ page: 1, limit: 20 })
  const [showFilters, setShowFilters] = useState(false)
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    limit: 20,
    pages: 1,
  })
  const [funnelStats, setFunnelStats] = useState<FunnelStats | null>(null)
  const [conversionRate, setConversionRate] = useState(0)

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showStatusModal, setShowStatusModal] = useState(false)
  const [showConvertModal, setShowConvertModal] = useState(false)
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)

  // Toast notifications
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  // Load leads
  const loadLeads = useCallback(async () => {
    try {
      setLoading(true)
      const response = await leadsApi.getLeads(filters)

      if (response.success) {
        setLeads(response.leads)
        setPagination(response.pagination)
      }
    } catch (error) {
      console.error('Error loading leads:', error)
      showToast('Ошибка загрузки лидов', 'error')
    } finally {
      setLoading(false)
    }
  }, [filters, showToast])

  // Load funnel stats
  const loadFunnelStats = useCallback(async () => {
    try {
      const response = await leadsApi.getFunnelStats('month')
      if (response.success) {
        setFunnelStats(response.funnel)
        setConversionRate(response.metrics.win_rate || 0)
      }
    } catch (error) {
      console.error('Error loading funnel stats:', error)
    }
  }, [])

  useEffect(() => {
    loadLeads()
    loadFunnelStats()
  }, [loadLeads, loadFunnelStats])

  // Refresh all data
  const handleRefresh = useCallback(() => {
    loadLeads()
    loadFunnelStats()
  }, [loadLeads, loadFunnelStats])

  // Apply filters
  const applyFilters = useCallback(() => {
    setFilters((prev) => ({ ...prev, page: 1 }))
  }, [])

  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({ page: 1, limit: 20 })
  }, [])

  // Filter by status from funnel
  const filterByStatus = useCallback((status: string) => {
    setFilters((prev) => ({ ...prev, status, page: 1 }))
  }, [])

  // Handle delete lead
  const handleDeleteLead = useCallback(
    async (leadId: number) => {
      if (!confirm('Вы уверены, что хотите удалить этот лид?')) return

      try {
        // Note: Delete endpoint is not in the backend, would need to be added
        showToast('Функция удаления будет добавлена позже', 'info')
      } catch (error) {
        console.error('Error deleting lead:', error)
        showToast('Ошибка удаления лида', 'error')
      }
    },
    [showToast]
  )

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

  // Open edit modal
  const openEditModal = useCallback((lead: Lead) => {
    setSelectedLead(lead)
    setShowEditModal(true)
    document.body.style.overflow = 'hidden'
  }, [])

  // Close edit modal
  const closeEditModal = useCallback(() => {
    setShowEditModal(false)
    setSelectedLead(null)
    document.body.style.overflow = 'auto'
  }, [])

  // Open status modal
  const openStatusModal = useCallback((lead: Lead) => {
    setSelectedLead(lead)
    setShowStatusModal(true)
    document.body.style.overflow = 'hidden'
  }, [])

  // Close status modal
  const closeStatusModal = useCallback(() => {
    setShowStatusModal(false)
    setSelectedLead(null)
    document.body.style.overflow = 'auto'
  }, [])

  // Open convert modal
  const openConvertModal = useCallback((lead: Lead) => {
    setSelectedLead(lead)
    setShowConvertModal(true)
    document.body.style.overflow = 'hidden'
  }, [])

  // Close convert modal
  const closeConvertModal = useCallback(() => {
    setShowConvertModal(false)
    setSelectedLead(null)
    document.body.style.overflow = 'auto'
  }, [])

  // Handle page change
  const handlePageChange = useCallback((page: number) => {
    setFilters((prev) => ({ ...prev, page }))
  }, [])

  // Status label mapping
  const getStatusLabel = (status: string): string => {
    const labels: { [key: string]: string } = {
      new: 'Новый',
      contact_made: 'Контакт установлен',
      qualification: 'Квалификация',
      proposal_sent: 'Предложение отправлено',
      negotiation: 'Переговоры',
      won: 'Выиграно',
      lost: 'Проиграно',
      postponed: 'Отложено',
    }
    return labels[status] || status
  }

  // Status badge color
  const getStatusColor = (status: string): string => {
    const colors: { [key: string]: string } = {
      new: 'bg-blue-100 text-blue-700',
      contact_made: 'bg-pink-100 text-pink-700',
      qualification: 'bg-teal-100 text-teal-700',
      proposal_sent: 'bg-purple-100 text-purple-700',
      negotiation: 'bg-orange-100 text-orange-700',
      won: 'bg-green-100 text-green-700',
      lost: 'bg-red-100 text-red-700',
      postponed: 'bg-gray-100 text-gray-700',
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  // Format date
  const formatDate = (dateString?: string): string => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('ru-RU')
  }

  return (
    <div className="p-6">
      <div className="max-w-[2000px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                <TrendingUp className="w-7 h-7 text-white" />
              </div>
              Управление лидами
            </h1>
            <p className="text-gray-600 mt-1">База потенциальных сделок</p>
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
              onClick={openCreateModal}
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg hover:from-cyan-600 hover:to-blue-700 transition-all shadow-lg"
            >
              <Plus className="w-5 h-5" />
              Добавить лид
            </button>
          </div>
        </div>

        {/* Funnel Stats */}
        {funnelStats && (
          <div className="bg-white rounded-3xl shadow-xl p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h5 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Target className="w-5 h-5 text-cyan-600" />
                Воронка продаж
              </h5>
              <div className="px-4 py-1 bg-green-100 text-green-700 rounded-full text-sm font-semibold">
                Конверсия: {conversionRate.toFixed(1)}%
              </div>
            </div>

            <div className="grid grid-cols-7 gap-3">
              {/* New */}
              <button
                onClick={() => filterByStatus('new')}
                className="bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-xl p-4 hover:scale-105 transition-transform shadow-lg"
              >
                <div className="text-3xl font-bold">{funnelStats.new}</div>
                <div className="text-sm opacity-90 mt-1">Новые</div>
              </button>

              {/* Contact Made */}
              <button
                onClick={() => filterByStatus('contact_made')}
                className="bg-gradient-to-br from-pink-500 to-red-500 text-white rounded-xl p-4 hover:scale-105 transition-transform shadow-lg"
              >
                <div className="text-3xl font-bold">{funnelStats.contact_made}</div>
                <div className="text-sm opacity-90 mt-1">Контакт</div>
              </button>

              {/* Qualification */}
              <button
                onClick={() => filterByStatus('qualification')}
                className="bg-gradient-to-br from-cyan-400 to-blue-500 text-white rounded-xl p-4 hover:scale-105 transition-transform shadow-lg"
              >
                <div className="text-3xl font-bold">{funnelStats.qualification}</div>
                <div className="text-sm opacity-90 mt-1">Квалификация</div>
              </button>

              {/* Proposal Sent */}
              <button
                onClick={() => filterByStatus('proposal_sent')}
                className="bg-gradient-to-br from-emerald-400 to-teal-500 text-white rounded-xl p-4 hover:scale-105 transition-transform shadow-lg"
              >
                <div className="text-3xl font-bold">{funnelStats.proposal_sent}</div>
                <div className="text-sm opacity-90 mt-1">Предложение</div>
              </button>

              {/* Negotiation */}
              <button
                onClick={() => filterByStatus('negotiation')}
                className="bg-gradient-to-br from-orange-400 to-pink-500 text-white rounded-xl p-4 hover:scale-105 transition-transform shadow-lg"
              >
                <div className="text-3xl font-bold">{funnelStats.negotiation}</div>
                <div className="text-sm opacity-90 mt-1">Переговоры</div>
              </button>

              {/* Won */}
              <button
                onClick={() => filterByStatus('won')}
                className="bg-gradient-to-br from-teal-500 to-blue-700 text-white rounded-xl p-4 hover:scale-105 transition-transform shadow-lg"
              >
                <div className="text-3xl font-bold">{funnelStats.won}</div>
                <div className="text-sm opacity-90 mt-1">Выиграно</div>
              </button>

              {/* Lost */}
              <button
                onClick={() => filterByStatus('lost')}
                className="text-gray-800 rounded-xl p-4 hover:scale-105 transition-transform shadow-lg"
              >
                <div className="text-3xl font-bold">{funnelStats.lost}</div>
                <div className="text-sm opacity-90 mt-1">Проиграно</div>
              </button>
            </div>
          </div>
        )}

        {/* Filters */}
        {showFilters && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="grid grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Поиск</label>
                <input
                  type="text"
                  value={filters.search || ''}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                  placeholder="Название, контакты..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Статус</label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                >
                  <option value="">Все статусы</option>
                  <option value="new">Новый</option>
                  <option value="contact_made">Контакт установлен</option>
                  <option value="qualification">Квалификация</option>
                  <option value="proposal_sent">Предложение отправлено</option>
                  <option value="negotiation">Переговоры</option>
                  <option value="won">Выиграно</option>
                  <option value="lost">Проиграно</option>
                  <option value="postponed">Отложено</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Источник</label>
                <select
                  value={filters.source || ''}
                  onChange={(e) => setFilters({ ...filters, source: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                >
                  <option value="">Все источники</option>
                  <option value="website">Сайт</option>
                  <option value="telegram">Telegram</option>
                  <option value="referral">Рекомендация</option>
                  <option value="ads">Реклама</option>
                  <option value="social">Соц. сети</option>
                  <option value="cold">Холодный</option>
                  <option value="other">Другое</option>
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
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                  placeholder="ID клиента"
                />
              </div>

              <div className="flex items-end gap-2">
                <button
                  onClick={applyFilters}
                  className="flex-1 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-all font-semibold"
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

        {/* Leads Table */}
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
            </div>
          ) : leads.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-3xl flex items-center justify-center mb-6 mx-auto">
                <TrendingUp className="w-12 h-12 text-cyan-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Лиды не найдены</h3>
              <p className="text-gray-600 mb-6">Добавьте первый лид, чтобы начать работу</p>
              <button
                onClick={openCreateModal}
                className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-semibold hover:shadow-xl transition-all"
              >
                <Plus className="w-5 h-5" />
                Добавить первый лид
              </button>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gradient-to-r from-gray-50 to-cyan-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        ID
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Название
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Статус
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Клиент/Контакт
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Бюджет
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Вероятность
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Менеджер
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Дней в воронке
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Действия
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {leads.map((lead) => (
                      <tr
                        key={lead.id}
                        className="hover:bg-gradient-to-r hover:from-cyan-50/50 hover:to-blue-50/50 transition-colors"
                      >
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                          #{lead.id}
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-semibold text-gray-900">{lead.title}</div>
                          {lead.source && (
                            <div className="text-xs text-gray-500 mt-1">
                              Источник: {lead.source}
                            </div>
                          )}
                          {lead.converted_to_deal_id && (
                            <div className="mt-2">
                              <a
                                href={`/deals`}
                                className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-md text-xs font-medium hover:bg-green-200 transition-colors"
                                title={`Конвертирован в сделку #${lead.converted_to_deal_id}`}
                              >
                                <Briefcase className="w-3 h-3" />
                                <span>Сделка #{lead.converted_to_deal_id}</span>
                                <ArrowRightCircle className="w-3 h-3" />
                              </a>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(lead.status)}`}
                          >
                            {getStatusLabel(lead.status)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {lead.client_name && (
                            <div className="font-semibold text-gray-900">{lead.client_name}</div>
                          )}
                          <div className="text-sm text-gray-600">
                            {lead.contact_name || lead.contact_phone || '-'}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                          {lead.budget ? formatCurrency(lead.budget) : '-'}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="text-sm font-semibold text-gray-900">
                              {lead.probability}%
                            </div>
                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 transition-all"
                                style={{ width: `${lead.probability}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {lead.manager_name || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {lead.days_in_funnel || 0} дн.
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => openStatusModal(lead)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Изменить статус"
                            >
                              <ArrowRightCircle className="w-4 h-4" />
                            </button>
                            {lead.status !== 'won' && lead.status !== 'lost' && (
                              <button
                                onClick={() => openConvertModal(lead)}
                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                title="Конвертировать в сделку"
                              >
                                <Briefcase className="w-4 h-4" />
                              </button>
                            )}
                            <button
                              onClick={() => openEditModal(lead)}
                              className="p-2 text-cyan-600 hover:bg-cyan-50 rounded-lg transition-colors"
                              title="Редактировать"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteLead(lead.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Удалить"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
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
                    Показано {leads.length} из {pagination.total} лидов
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
                              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white'
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
      </div>

      {/* Create Lead Modal */}
      {showCreateModal && (
        <CreateLeadModal
          onClose={closeCreateModal}
          onSuccess={() => {
            closeCreateModal()
            handleRefresh()
            showToast('Лид успешно создан', 'success')
          }}
          showToast={showToast}
        />
      )}

      {/* Edit Lead Modal */}
      {showEditModal && selectedLead && (
        <EditLeadModal
          lead={selectedLead}
          onClose={closeEditModal}
          onSuccess={() => {
            closeEditModal()
            handleRefresh()
            showToast('Лид успешно обновлен', 'success')
          }}
          showToast={showToast}
        />
      )}

      {/* Status Change Modal */}
      {showStatusModal && selectedLead && (
        <StatusChangeModal
          lead={selectedLead}
          onClose={closeStatusModal}
          onSuccess={() => {
            closeStatusModal()
            handleRefresh()
            showToast('Статус успешно изменен', 'success')
          }}
          showToast={showToast}
        />
      )}

      {/* Convert to Deal Modal */}
      {showConvertModal && selectedLead && (
        <ConvertToDealModal
          lead={selectedLead}
          onClose={closeConvertModal}
          onSuccess={() => {
            closeConvertModal()
            handleRefresh()
            showToast('Лид успешно конвертирован в сделку', 'success')
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

// Create Lead Modal Component
interface CreateLeadModalProps {
  onClose: () => void
  onSuccess: () => void
  showToast: (message: string, type: 'success' | 'error' | 'info') => void
}

const CreateLeadModal = ({ onClose, onSuccess, showToast }: CreateLeadModalProps) => {
  const [formData, setFormData] = useState({
    title: '',
    source: '',
    client_id: '',
    contact_name: '',
    contact_phone: '',
    contact_email: '',
    contact_telegram: '',
    contact_whatsapp: '',
    description: '',
    requirements: '',
    budget: '',
    probability: '50',
    expected_close_date: '',
    next_action_date: '',
    notes: '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim()) {
      showToast('Название обязательно', 'error')
      return
    }

    setLoading(true)

    try {
      const data: any = {
        title: formData.title,
        source: formData.source || undefined,
        client_id: formData.client_id ? +formData.client_id : undefined,
        contact_name: formData.contact_name || undefined,
        contact_phone: formData.contact_phone || undefined,
        contact_email: formData.contact_email || undefined,
        contact_telegram: formData.contact_telegram || undefined,
        contact_whatsapp: formData.contact_whatsapp || undefined,
        description: formData.description || undefined,
        requirements: formData.requirements || undefined,
        budget: formData.budget ? +formData.budget : undefined,
        probability: formData.probability ? +formData.probability : 50,
        expected_close_date: formData.expected_close_date || undefined,
        next_action_date: formData.next_action_date || undefined,
        notes: formData.notes || undefined,
      }

      const response = await leadsApi.createLead(data)

      if (response.success) {
        onSuccess()
      } else {
        showToast(response.message || 'Ошибка создания лида', 'error')
      }
    } catch (error: any) {
      console.error('Error creating lead:', error)
      showToast(error.response?.data?.message || 'Ошибка создания лида', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl">
          {/* Header */}
          <div className="sticky top-0 bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-5 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-white">Новый лид</h3>
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
            {/* Title */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Название <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                placeholder="Название лида"
                required
              />
            </div>

            {/* Source and Client */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Источник
                </label>
                <select
                  value={formData.source}
                  onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                >
                  <option value="">Не указан</option>
                  <option value="website">Сайт</option>
                  <option value="telegram">Telegram</option>
                  <option value="referral">Рекомендация</option>
                  <option value="ads">Реклама</option>
                  <option value="social">Соц. сети</option>
                  <option value="cold">Холодный</option>
                  <option value="other">Другое</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  ID клиента
                </label>
                <input
                  type="number"
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                  placeholder="Оставьте пустым для нового"
                />
              </div>
            </div>

            {/* Contact Info */}
            <div className="space-y-4">
              <h4 className="font-bold text-gray-900">Контактная информация</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Имя контакта
                  </label>
                  <input
                    type="text"
                    value={formData.contact_name}
                    onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                    placeholder="Имя"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Телефон
                  </label>
                  <input
                    type="tel"
                    value={formData.contact_phone}
                    onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                    placeholder="+7 (999) 123-45-67"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                    placeholder="email@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Telegram
                  </label>
                  <input
                    type="text"
                    value={formData.contact_telegram}
                    onChange={(e) =>
                      setFormData({ ...formData, contact_telegram: e.target.value })
                    }
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                    placeholder="@username"
                  />
                </div>
              </div>
            </div>

            {/* Description and Requirements */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Описание
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all resize-none"
                  placeholder="Описание лида"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Требования
                </label>
                <textarea
                  value={formData.requirements}
                  onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all resize-none"
                  placeholder="Требования клиента"
                />
              </div>
            </div>

            {/* Budget and Probability */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Бюджет</label>
                <input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                  placeholder="0"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Вероятность (%)
                </label>
                <input
                  type="number"
                  value={formData.probability}
                  onChange={(e) => setFormData({ ...formData, probability: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                  min="0"
                  max="100"
                />
              </div>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Ожидаемая дата закрытия
                </label>
                <input
                  type="date"
                  value={formData.expected_close_date}
                  onChange={(e) =>
                    setFormData({ ...formData, expected_close_date: e.target.value })
                  }
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Дата следующего действия
                </label>
                <input
                  type="date"
                  value={formData.next_action_date}
                  onChange={(e) =>
                    setFormData({ ...formData, next_action_date: e.target.value })
                  }
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                />
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Примечания
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all resize-none"
                placeholder="Дополнительные заметки"
              />
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
              className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Создание...' : 'Создать лид'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Edit Lead Modal Component (similar structure to Create)
interface EditLeadModalProps {
  lead: Lead
  onClose: () => void
  onSuccess: () => void
  showToast: (message: string, type: 'success' | 'error' | 'info') => void
}

const EditLeadModal = ({ lead, onClose, onSuccess, showToast }: EditLeadModalProps) => {
  const [formData, setFormData] = useState({
    title: lead.title || '',
    source: lead.source || '',
    client_id: lead.client_id?.toString() || '',
    contact_name: lead.contact_name || '',
    contact_phone: lead.contact_phone || '',
    contact_email: lead.contact_email || '',
    contact_telegram: lead.contact_telegram || '',
    description: lead.description || '',
    requirements: lead.requirements || '',
    budget: lead.budget?.toString() || '',
    probability: lead.probability?.toString() || '50',
    expected_close_date: lead.expected_close_date || '',
    notes: lead.notes || '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim()) {
      showToast('Название обязательно', 'error')
      return
    }

    setLoading(true)

    try {
      const data: any = {
        title: formData.title,
        source: formData.source || undefined,
        client_id: formData.client_id ? +formData.client_id : undefined,
        contact_name: formData.contact_name || undefined,
        contact_phone: formData.contact_phone || undefined,
        contact_email: formData.contact_email || undefined,
        contact_telegram: formData.contact_telegram || undefined,
        description: formData.description || undefined,
        requirements: formData.requirements || undefined,
        budget: formData.budget ? +formData.budget : undefined,
        probability: formData.probability ? +formData.probability : 50,
        expected_close_date: formData.expected_close_date || undefined,
        notes: formData.notes || undefined,
      }

      const response = await leadsApi.updateLead(lead.id, data)

      if (response.success) {
        onSuccess()
      } else {
        showToast(response.message || 'Ошибка обновления лида', 'error')
      }
    } catch (error: any) {
      console.error('Error updating lead:', error)
      showToast(error.response?.data?.message || 'Ошибка обновления лида', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl">
          <div className="sticky top-0 bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-5 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-white">Редактировать лид</h3>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-white" />
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Название <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Источник
                </label>
                <select
                  value={formData.source}
                  onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                >
                  <option value="">Не указан</option>
                  <option value="website">Сайт</option>
                  <option value="telegram">Telegram</option>
                  <option value="referral">Рекомендация</option>
                  <option value="ads">Реклама</option>
                  <option value="social">Соц. сети</option>
                  <option value="cold">Холодный</option>
                  <option value="other">Другое</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Бюджет
                </label>
                <input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                  min="0"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Вероятность (%)
              </label>
              <input
                type="number"
                value={formData.probability}
                onChange={(e) => setFormData({ ...formData, probability: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                min="0"
                max="100"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Описание
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all resize-none"
              />
            </div>
          </form>

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
              className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all shadow-lg disabled:opacity-50"
            >
              {loading ? 'Сохранение...' : 'Сохранить'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Status Change Modal Component
interface StatusChangeModalProps {
  lead: Lead
  onClose: () => void
  onSuccess: () => void
  showToast: (message: string, type: 'success' | 'error' | 'info') => void
}

const StatusChangeModal = ({ lead, onClose, onSuccess, showToast }: StatusChangeModalProps) => {
  const [status, setStatus] = useState(lead.status)
  const [lostReason, setLostReason] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    setLoading(true)

    try {
      const response = await leadsApi.updateLeadStatus(lead.id, status, lostReason || undefined)

      if (response.success) {
        onSuccess()
      } else {
        showToast(response.message || 'Ошибка изменения статуса', 'error')
      }
    } catch (error: any) {
      console.error('Error updating status:', error)
      showToast(error.response?.data?.message || 'Ошибка изменения статуса', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl">
          <div className="bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-5 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-white">Изменить статус</h3>
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
                Новый статус
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
              >
                <option value="new">Новый</option>
                <option value="contact_made">Контакт установлен</option>
                <option value="qualification">Квалификация</option>
                <option value="proposal_sent">Предложение отправлено</option>
                <option value="negotiation">Переговоры</option>
                <option value="won">Выиграно</option>
                <option value="lost">Проиграно</option>
                <option value="postponed">Отложено</option>
              </select>
            </div>

            {status === 'lost' && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Причина отказа
                </label>
                <textarea
                  value={lostReason}
                  onChange={(e) => setLostReason(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all resize-none"
                  placeholder="Укажите причину..."
                />
              </div>
            )}

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
                className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all shadow-lg disabled:opacity-50"
              >
                {loading ? 'Сохранение...' : 'Изменить'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

// Convert to Deal Modal Component
interface ConvertToDealModalProps {
  lead: Lead
  onClose: () => void
  onSuccess: () => void
  showToast: (message: string, type: 'success' | 'error' | 'info') => void
}

const ConvertToDealModal = ({
  lead,
  onClose,
  onSuccess,
  showToast,
}: ConvertToDealModalProps) => {
  const [formData, setFormData] = useState({
    title: lead.title,
    amount: lead.budget?.toString() || '',
    prepayment_percent: '50',
    priority: 'normal',
    start_date: '',
    end_date: lead.expected_close_date || '',
    description: lead.description || '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.amount || +formData.amount <= 0) {
      showToast('Укажите сумму сделки', 'error')
      return
    }

    setLoading(true)

    try {
      const data: any = {
        title: formData.title,
        amount: +formData.amount,
        prepayment_percent: formData.prepayment_percent ? +formData.prepayment_percent : undefined,
        priority: formData.priority,
        start_date: formData.start_date || undefined,
        end_date: formData.end_date || undefined,
        description: formData.description || undefined,
      }

      const response = await leadsApi.convertLead(lead.id, data)

      if (response.success) {
        onSuccess()
        // Optionally redirect to deals page
        setTimeout(() => {
          window.location.href = '/deals'
        }, 1500)
      } else {
        showToast(response.message || 'Ошибка конвертации', 'error')
      }
    } catch (error: any) {
      console.error('Error converting lead:', error)
      showToast(error.response?.data?.message || 'Ошибка конвертации', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm">
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="w-full max-w-2xl bg-white rounded-3xl shadow-2xl">
          <div className="bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-5 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-white">Конвертировать в сделку</h3>
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
                Название сделки
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Сумма сделки <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                required
                min="0"
              />
            </div>

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
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                  min="0"
                  max="100"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Приоритет
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                >
                  <option value="low">Низкий</option>
                  <option value="normal">Обычный</option>
                  <option value="high">Высокий</option>
                  <option value="urgent">Срочный</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Дата начала
                </label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
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
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Описание</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring-2 focus:ring-cyan-200 outline-none transition-all resize-none"
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
                className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all shadow-lg disabled:opacity-50"
              >
                {loading ? 'Конвертация...' : 'Конвертировать'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
