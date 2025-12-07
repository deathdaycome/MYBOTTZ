import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Package,
  Plus,
  Filter,
  TrendingUp,
  DollarSign,
  CheckCircle2,
  Server,
  Edit,
  Trash2,
  Eye,
  X,
  Loader2,
  RefreshCw,
  Download,
} from 'lucide-react'
// API imports
import servicesApi from '../api/services'
import type { Service, ServiceStats } from '../api/services'
import { apiService } from '../services/api'

export const Services = () => {
  const [services, setServices] = useState<Service[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<ServiceStats | null>(null)

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showExpenseModal, setShowExpenseModal] = useState(false)
  const [selectedService, setSelectedService] = useState<Service | null>(null)

  // Forms
  const [createForm, setCreateForm] = useState({
    name: '',
    provider_type: 'ai',
    description: '',
    website: '',
    pricing_model: 'monthly',
    contact_info: '{}',
  })

  const [editForm, setEditForm] = useState({
    name: '',
    provider_type: 'ai',
    description: '',
    website: '',
    pricing_model: 'monthly',
    status: 'active',
    contact_info: '{}',
  })

  const [expenseForm, setExpenseForm] = useState({
    amount: '',
    expense_type: 'subscription' as 'subscription' | 'usage' | 'one_time',
    description: '',
    expense_date: new Date().toISOString().split('T')[0],
    project_id: '',
    is_recurring: false,
    recurring_period: 'monthly' as 'monthly' | 'yearly',
  })

  const [projects, setProjects] = useState<any[]>([])

  // Toast notification
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(
    null
  )

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }, [])

  // Load data
  const loadServices = useCallback(async () => {
    try {
      setLoading(true)
      const response = await servicesApi.getServices({
        service_type: typeFilter || undefined,
        status: statusFilter || undefined,
      })
      if (response.success) {
        setServices(response.services)
      }
    } catch (error) {
      showToast('Ошибка загрузки сервисов', 'error')
    } finally {
      setLoading(false)
    }
  }, [typeFilter, statusFilter, showToast])

  const loadStats = useCallback(async () => {
    try {
      const response = await servicesApi.getStats('month')
      if (response.success) {
        setStats(response.statistics)
      }
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }, [])

  const loadProjects = useCallback(async () => {
    try {
      const response = await apiService.getProjects()
      if (response.success) {
        setProjects(response.projects)
      }
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }, [])

  useEffect(() => {
    loadServices()
    loadStats()
    loadProjects()
  }, [loadServices, loadStats, loadProjects])

  // Create service
  const handleCreateService = async () => {
    if (!createForm.name || !createForm.provider_type) {
      showToast('Заполните обязательные поля', 'error')
      return
    }

    try {
      let contactInfo = {}
      try {
        contactInfo = JSON.parse(createForm.contact_info)
      } catch {
        showToast('Неверный формат JSON в контактной информации', 'error')
        return
      }

      const response = await servicesApi.createService({
        ...createForm,
        contact_info: contactInfo,
      })

      if (response.success) {
        showToast('Сервис успешно создан', 'success')
        setShowCreateModal(false)
        setCreateForm({
          name: '',
          provider_type: 'ai',
          description: '',
          website: '',
          pricing_model: 'monthly',
          contact_info: '{}',
        })
        loadServices()
        loadStats()
      }
    } catch (error) {
      showToast('Ошибка при создании сервиса', 'error')
    }
  }

  // Edit service
  const openEditModal = (service: Service) => {
    setSelectedService(service)
    setEditForm({
      name: service.name,
      provider_type: service.provider_type,
      description: service.description || '',
      website: service.website || '',
      pricing_model: service.pricing_model || 'monthly',
      status: service.status,
      contact_info: JSON.stringify(service.contact_info || {}, null, 2),
    })
    setShowEditModal(true)
  }

  const handleEditService = async () => {
    if (!selectedService) return

    try {
      let contactInfo = {}
      try {
        contactInfo = JSON.parse(editForm.contact_info)
      } catch {
        showToast('Неверный формат JSON в контактной информации', 'error')
        return
      }

      const response = await servicesApi.updateService(selectedService.id, {
        ...editForm,
        contact_info: contactInfo,
      })

      if (response.success) {
        showToast('Сервис успешно обновлен', 'success')
        setShowEditModal(false)
        loadServices()
        loadStats()
      }
    } catch (error) {
      showToast('Ошибка при обновлении сервиса', 'error')
    }
  }

  // Delete service
  const handleDeleteService = async (serviceId: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот сервис?')) return

    try {
      const response = await servicesApi.deleteService(serviceId)
      if (response.success) {
        showToast('Сервис удален', 'success')
        loadServices()
        loadStats()
      }
    } catch (error) {
      showToast('Ошибка при удалении сервиса', 'error')
    }
  }

  // Add expense
  const openExpenseModal = (service: Service) => {
    setSelectedService(service)
    setExpenseForm({
      amount: '',
      expense_type: 'subscription',
      description: '',
      expense_date: new Date().toISOString().split('T')[0],
      project_id: '',
      is_recurring: false,
      recurring_period: 'monthly',
    })
    setShowExpenseModal(true)
  }

  const handleAddExpense = async () => {
    if (!selectedService || !expenseForm.amount) {
      showToast('Заполните сумму расхода', 'error')
      return
    }

    try {
      const response = await servicesApi.createExpense(selectedService.id, {
        amount: parseFloat(expenseForm.amount),
        expense_type: expenseForm.expense_type,
        description: expenseForm.description,
        expense_date: expenseForm.expense_date,
        project_id: expenseForm.project_id ? parseInt(expenseForm.project_id) : undefined,
        is_recurring: expenseForm.is_recurring,
        recurring_period: expenseForm.is_recurring ? expenseForm.recurring_period : undefined,
      })

      if (response.success) {
        showToast('Расход добавлен', 'success')
        setShowExpenseModal(false)
        loadServices()
        loadStats()
      }
    } catch (error) {
      showToast('Ошибка при добавлении расхода', 'error')
    }
  }

  const getServiceTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      ai: 'ИИ-сервисы',
      hosting: 'Хостинг',
      payment: 'Платежи',
      analytics: 'Аналитика',
      storage: 'Хранилище',
      email: 'Email',
      sms: 'SMS',
      cdn: 'CDN',
      monitoring: 'Мониторинг',
      other: 'Другое',
    }
    return labels[type] || type
  }

  const getPricingModelLabel = (model: string) => {
    const labels: Record<string, string> = {
      monthly: 'Ежемесячно',
      yearly: 'Ежегодно',
      usage: 'По использованию',
      per_request: 'За запрос',
      one_time: 'Разовый',
      custom: 'Индивидуальная',
    }
    return labels[model] || model
  }

  const filteredServices = useMemo(() => {
    return services.filter((service) => {
      const matchesSearch =
        !searchQuery ||
        service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        service.description?.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesSearch
    })
  }, [services, searchQuery])

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
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center">
              <Package className="w-6 h-6 text-white" />
            </div>
            Управление сервисами
          </h1>
          <p className="text-gray-500 mt-1">Контроль подписок и расходов на внешние сервисы</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={loadServices}
            className="px-4 py-2 border border-gray-200 rounded-xl hover:bg-gray-50 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Обновить
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-xl hover:shadow-lg transition-all flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Добавить сервис
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-teal-100 flex items-center justify-center">
                <Server className="w-6 h-6 text-teal-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.total_services}</div>
                <div className="text-sm text-gray-500">Всего сервисов</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.active_services}</div>
                <div className="text-sm text-gray-500">Активные</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(stats.month_cost_so_far)}₽
                </div>
                <div className="text-sm text-gray-500">Расходы за месяц</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(stats.projected_month_cost)}₽
                </div>
                <div className="text-sm text-gray-500">Прогноз на месяц</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <h3 className="font-semibold text-gray-900">Фильтры</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Поиск сервисов..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          />

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          >
            <option value="">Все типы</option>
            <option value="ai">ИИ-сервисы</option>
            <option value="hosting">Хостинг</option>
            <option value="payment">Платежи</option>
            <option value="analytics">Аналитика</option>
            <option value="storage">Хранилище</option>
            <option value="other">Другое</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
          >
            <option value="">Все статусы</option>
            <option value="active">Активные</option>
            <option value="inactive">Неактивные</option>
          </select>

          <button
            onClick={() => {
              setSearchQuery('')
              setTypeFilter('')
              setStatusFilter('')
            }}
            className="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            Сбросить
          </button>
        </div>
      </div>

      {/* Services Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Название</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Тип</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">
                  Модель ценообразования
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">
                  Месячный расход
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Статус</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto text-teal-500" />
                  </td>
                </tr>
              ) : filteredServices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    Сервисы не найдены
                  </td>
                </tr>
              ) : (
                filteredServices.map((service) => (
                  <tr key={service.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{service.name}</div>
                      <div className="text-xs text-gray-500 line-clamp-1">
                        {service.description || 'Нет описания'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-teal-100 text-teal-700">
                        {getServiceTypeLabel(service.provider_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {getPricingModelLabel(service.pricing_model || 'monthly')}
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-bold text-gray-900">
                        {service.statistics?.monthly_cost || 0}₽
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          service.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {service.status === 'active' ? 'Активный' : 'Неактивный'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => openEditModal(service)}
                          className="p-2 hover:bg-teal-100 rounded-lg transition-colors"
                          title="Редактировать"
                        >
                          <Edit className="w-4 h-4 text-teal-600" />
                        </button>
                        <button
                          onClick={() => openExpenseModal(service)}
                          className="p-2 hover:bg-green-100 rounded-lg transition-colors"
                          title="Добавить расход"
                        >
                          <Plus className="w-4 h-4 text-green-600" />
                        </button>
                        <button
                          onClick={() => handleDeleteService(service.id)}
                          className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Добавить новый сервис</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Название сервиса *
                  </label>
                  <input
                    type="text"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Тип сервиса *
                  </label>
                  <select
                    value={createForm.provider_type}
                    onChange={(e) =>
                      setCreateForm({ ...createForm, provider_type: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  >
                    <option value="ai">ИИ-сервисы</option>
                    <option value="hosting">Хостинг</option>
                    <option value="payment">Платежные системы</option>
                    <option value="analytics">Аналитика</option>
                    <option value="storage">Хранилище</option>
                    <option value="other">Другое</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                <textarea
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Веб-сайт</label>
                  <input
                    type="url"
                    value={createForm.website}
                    onChange={(e) => setCreateForm({ ...createForm, website: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Модель ценообразования
                  </label>
                  <select
                    value={createForm.pricing_model}
                    onChange={(e) =>
                      setCreateForm({ ...createForm, pricing_model: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  >
                    <option value="monthly">Ежемесячная подписка</option>
                    <option value="yearly">Годовая подписка</option>
                    <option value="usage">По использованию</option>
                    <option value="per_request">За запрос</option>
                    <option value="one_time">Разовый платеж</option>
                    <option value="custom">Индивидуальная</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Контактная информация (JSON)
                </label>
                <textarea
                  value={createForm.contact_info}
                  onChange={(e) => setCreateForm({ ...createForm, contact_info: e.target.value })}
                  rows={3}
                  placeholder='{"email": "support@service.com", "phone": "+1234567890"}'
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent font-mono text-sm"
                />
              </div>
            </div>

            <div className="p-6 border-t border-gray-100 flex justify-end gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-6 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateService}
                className="px-6 py-2 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-lg hover:shadow-lg"
              >
                Добавить
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal - Similar structure to Create Modal */}
      {showEditModal && selectedService && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Редактировать сервис</h2>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Название</label>
                  <input
                    type="text"
                    value={editForm.name}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Статус</label>
                  <select
                    value={editForm.status}
                    onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500"
                  >
                    <option value="active">Активный</option>
                    <option value="inactive">Неактивный</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                <textarea
                  value={editForm.description}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            <div className="p-6 border-t border-gray-100 flex justify-end gap-3">
              <button
                onClick={() => setShowEditModal(false)}
                className="px-6 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                Отмена
              </button>
              <button
                onClick={handleEditService}
                className="px-6 py-2 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-lg hover:shadow-lg"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Expense Modal */}
      {showExpenseModal && selectedService && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Добавить расход</h2>
                <button
                  onClick={() => setShowExpenseModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-1">Сервис: {selectedService.name}</p>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Сумма *</label>
                <input
                  type="number"
                  step="0.01"
                  value={expenseForm.amount}
                  onChange={(e) => setExpenseForm({ ...expenseForm, amount: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500"
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Тип расхода</label>
                <select
                  value={expenseForm.expense_type}
                  onChange={(e) =>
                    setExpenseForm({
                      ...expenseForm,
                      expense_type: e.target.value as 'subscription' | 'usage' | 'one_time',
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500"
                >
                  <option value="subscription">Подписка</option>
                  <option value="usage">Использование</option>
                  <option value="one_time">Разовый платеж</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                <textarea
                  value={expenseForm.description}
                  onChange={(e) => setExpenseForm({ ...expenseForm, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Дата расхода</label>
                <input
                  type="date"
                  value={expenseForm.expense_date}
                  onChange={(e) =>
                    setExpenseForm({ ...expenseForm, expense_date: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={expenseForm.is_recurring}
                    onChange={(e) =>
                      setExpenseForm({ ...expenseForm, is_recurring: e.target.checked })
                    }
                    className="w-4 h-4 text-teal-600 rounded focus:ring-2 focus:ring-teal-500"
                  />
                  <span className="text-sm text-gray-700">Повторяющийся расход</span>
                </label>
              </div>
            </div>

            <div className="p-6 border-t border-gray-100 flex justify-end gap-3">
              <button
                onClick={() => setShowExpenseModal(false)}
                className="px-6 py-2 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                Отмена
              </button>
              <button
                onClick={handleAddExpense}
                className="px-6 py-2 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-lg hover:shadow-lg"
              >
                Добавить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
