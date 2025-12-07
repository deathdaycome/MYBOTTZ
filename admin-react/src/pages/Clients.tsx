import { useState, useEffect, useCallback } from 'react'
import {
  Users,
  Plus,
  Search,
  Filter,
  X,
  Edit2,
  Trash2,
  Phone,
  Mail,
  MessageCircle,
  Building2,
  User,
  Star,
  RefreshCw,
  Eye,
  TrendingUp,
  FileText,
  Calendar
} from 'lucide-react'
import clientsApi from '../api/clients'
import type { Client, ClientFilters, ClientType, ClientStatus } from '../api/clients'

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

export const Clients = () => {
  // ============= STATE =============
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<ClientFilters>({ page: 1, limit: 20 })
  const [showFilters, setShowFilters] = useState(false)
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    limit: 20,
    pages: 1
  })
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    vip: 0,
    new_month: 0
  })

  // Toast notifications
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 4000)
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  // ============= DATA LOADING =============

  const loadClients = useCallback(async () => {
    try {
      setLoading(true)
      const response = await clientsApi.getClients(filters)

      if (response.success) {
        setClients(response.clients)
        setPagination(response.pagination)
        if (response.stats) {
          setStats(response.stats)
        }
      } else {
        showToast(response.message || 'Ошибка загрузки клиентов', 'error')
      }
    } catch (error) {
      console.error('Error loading clients:', error)
      showToast('Ошибка загрузки клиентов', 'error')
    } finally {
      setLoading(false)
    }
  }, [filters, showToast])

  useEffect(() => {
    loadClients()
  }, [loadClients])

  // ============= HANDLERS =============

  const handleDeleteClient = async (clientId: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого клиента?')) return

    const response = await clientsApi.deleteClient(clientId)
    if (response.success) {
      showToast('Клиент успешно удален', 'success')
      loadClients()
    } else {
      showToast(response.message, 'error')
    }
  }

  const handleSearch = (search: string) => {
    setFilters(prev => ({ ...prev, search, page: 1 }))
  }

  const handleFilterChange = (key: keyof ClientFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }))
  }

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }))
  }

  const handleRefresh = () => {
    loadClients()
  }

  // ============= UTILITY FUNCTIONS =============

  const getTypeLabel = (type: ClientType) => {
    const labels = {
      individual: 'Физ. лицо',
      company: 'Компания',
      ip: 'ИП',
      self_employed: 'Самозанятый'
    }
    return labels[type] || type
  }

  const getStatusLabel = (status: ClientStatus) => {
    const labels = {
      new: 'Новый',
      active: 'Активный',
      inactive: 'Неактивный',
      vip: 'VIP',
      blacklist: 'Черный список'
    }
    return labels[status] || status
  }

  const getStatusColor = (status: ClientStatus) => {
    const colors = {
      new: 'bg-blue-100 text-blue-700',
      active: 'bg-green-100 text-green-700',
      inactive: 'bg-gray-100 text-gray-700',
      vip: 'bg-purple-100 text-purple-700',
      blacklist: 'bg-red-100 text-red-700'
    }
    return colors[status] || 'bg-gray-100 text-gray-700'
  }

  const getTypeIcon = (type: ClientType) => {
    const icons = {
      individual: User,
      company: Building2,
      ip: Building2,
      self_employed: User
    }
    const Icon = icons[type] || User
    return <Icon className="w-4 h-4" />
  }

  // ============= RENDER =============

  return (
    <div className="p-8 space-y-6">
      {/* Header with Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Клиенты</h1>
          <p className="text-gray-600">Управление базой клиентов CRM</p>
        </div>
        <button
          className="bg-gradient-to-r from-orange-600 to-red-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Новый клиент
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-2xl font-bold text-gray-900">{stats.total}</span>
          </div>
          <p className="text-gray-600 text-sm">Всего клиентов</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <span className="text-2xl font-bold text-gray-900">{stats.active}</span>
          </div>
          <p className="text-gray-600 text-sm">Активных</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <Star className="w-6 h-6 text-purple-600" />
            </div>
            <span className="text-2xl font-bold text-gray-900">{stats.vip}</span>
          </div>
          <p className="text-gray-600 text-sm">VIP клиентов</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
              <Calendar className="w-6 h-6 text-orange-600" />
            </div>
            <span className="text-2xl font-bold text-gray-900">{stats.new_month}</span>
          </div>
          <p className="text-gray-600 text-sm">Новых за месяц</p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Поиск по имени, email, телефону, компании..."
            className="w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
            value={filters.search || ''}
            onChange={(e) => handleSearch(e.target.value)}
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`px-6 py-3 bg-white border border-gray-200 rounded-xl hover:border-orange-500 transition-all flex items-center gap-2 font-medium ${
            showFilters ? 'border-orange-500 text-orange-600' : 'text-gray-700'
          }`}
        >
          <Filter className="w-5 h-5" />
          Фильтры
        </button>
        <button
          onClick={handleRefresh}
          className="px-6 py-3 bg-white border border-gray-200 rounded-xl hover:border-gray-300 transition-all flex items-center gap-2 font-medium text-gray-700"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Статус</label>
              <select
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                value={filters.status || ''}
                onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
              >
                <option value="">Все статусы</option>
                <option value="new">Новый</option>
                <option value="active">Активный</option>
                <option value="inactive">Неактивный</option>
                <option value="vip">VIP</option>
                <option value="blacklist">Черный список</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Тип</label>
              <select
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                value={filters.type || ''}
                onChange={(e) => handleFilterChange('type', e.target.value || undefined)}
              >
                <option value="">Все типы</option>
                <option value="individual">Физ. лицо</option>
                <option value="company">Компания</option>
                <option value="ip">ИП</option>
                <option value="self_employed">Самозанятый</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Сегмент</label>
              <input
                type="text"
                placeholder="Введите сегмент..."
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                value={filters.segment || ''}
                onChange={(e) => handleFilterChange('segment', e.target.value || undefined)}
              />
            </div>
          </div>
        </div>
      )}

      {/* Clients Table/List */}
      {loading ? (
        <div className="bg-white rounded-3xl p-16 shadow-xl border border-gray-100 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
        </div>
      ) : clients.length === 0 ? (
        <div className="bg-white rounded-3xl p-16 shadow-xl border border-gray-100">
          <div className="flex flex-col items-center justify-center text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-orange-100 to-red-100 rounded-3xl flex items-center justify-center mb-6">
              <Users className="w-12 h-12 text-orange-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {filters.search || filters.status || filters.type ? 'Клиенты не найдены' : 'Нет клиентов'}
            </h3>
            <p className="text-gray-600 mb-6 max-w-md">
              {filters.search || filters.status || filters.type
                ? 'Попробуйте изменить параметры поиска'
                : 'Добавьте первого клиента, чтобы начать вести учёт и управление'}
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Клиент
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Контакты
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Тип
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Статус
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Проекты/Сделки
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Действия
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {clients.map((client) => (
                    <tr
                      key={client.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center text-white font-semibold">
                            {client.name.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900">{client.name}</div>
                            {client.company_name && (
                              <div className="text-sm text-gray-500">{client.company_name}</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="space-y-1">
                          {client.email && (
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Mail className="w-4 h-4" />
                              {client.email}
                            </div>
                          )}
                          {client.phone && (
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Phone className="w-4 h-4" />
                              {client.phone}
                            </div>
                          )}
                          {client.telegram && (
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <MessageCircle className="w-4 h-4" />
                              {client.telegram}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {getTypeIcon(client.type)}
                          <span className="text-sm text-gray-700">{getTypeLabel(client.type)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                            client.status
                          )}`}
                        >
                          {getStatusLabel(client.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          {client.projects_count !== undefined && (
                            <div className="flex items-center gap-1">
                              <FileText className="w-4 h-4" />
                              {client.projects_count}
                            </div>
                          )}
                          {client.deals_count !== undefined && (
                            <div className="flex items-center gap-1">
                              <TrendingUp className="w-4 h-4" />
                              {client.deals_count}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            className="p-2 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Просмотр"
                          >
                            <Eye className="w-4 h-4 text-blue-600" />
                          </button>
                          <button
                            className="p-2 hover:bg-green-50 rounded-lg transition-colors"
                            title="Редактировать"
                          >
                            <Edit2 className="w-4 h-4 text-green-600" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteClient(client.id)
                            }}
                            className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                            title="Удалить"
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex items-center justify-between bg-white rounded-2xl p-4 shadow-lg border border-gray-100">
              <div className="text-sm text-gray-600">
                Показано {clients.length} из {pagination.total} клиентов
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={pagination.page === 1}
                  className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  Назад
                </button>
                <div className="flex gap-1">
                  {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                    const page = i + 1
                    return (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`px-4 py-2 rounded-lg transition-all ${
                          pagination.page === page
                            ? 'bg-orange-600 text-white'
                            : 'border border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    )
                  })}
                </div>
                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={pagination.page === pagination.pages}
                  className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  Вперед
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Toast Container */}
      <div className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`flex items-center gap-3 px-6 py-4 rounded-xl shadow-2xl border backdrop-blur-sm animate-slide-in-right ${
              toast.type === 'success'
                ? 'bg-green-50 border-green-200 text-green-800'
                : toast.type === 'error'
                ? 'bg-red-50 border-red-200 text-red-800'
                : 'bg-blue-50 border-blue-200 text-blue-800'
            }`}
          >
            <span className="flex-1 font-medium">{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              className="p-1 hover:bg-white/50 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
