import { useState, useEffect, useCallback } from 'react'
import { Plus, Filter, RefreshCw, Download, BarChart } from 'lucide-react'
import contractorsApi from '../api/contractors'
import type { Contractor } from '../api/contractors'
import { ContractorCard } from '../components/contractors/ContractorCard'
import { ContractorCreateModal } from '../components/contractors/ContractorCreateModal'
import { ContractorEditModal } from '../components/contractors/ContractorEditModal'
import { ContractorViewModal } from '../components/contractors/ContractorViewModal'
import { PaymentModal } from '../components/contractors/PaymentModal'
import { ToastContainer } from '../components/common/Toast'

interface ContractorFiltersState {
  search?: string
  specialization?: string
  status?: string
}

export const Contractors = () => {
  const [contractors, setContractors] = useState<Contractor[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<ContractorFiltersState>({})
  const [showFilters, setShowFilters] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalContractors, setTotalContractors] = useState(0)
  const itemsPerPage = 12

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [selectedContractor, setSelectedContractor] = useState<Contractor | null>(null)

  // Toast notifications
  const [toasts, setToasts] = useState<
    Array<{ id: string; message: string; type: 'success' | 'error' | 'info' | 'warning' }>
  >([])

  const showToast = useCallback(
    (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
      const id = Date.now().toString()
      setToasts((prev) => [...prev, { id, message, type }])
    },
    []
  )

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  // Load contractors
  const loadContractors = useCallback(async () => {
    try {
      setLoading(true)
      const response = await contractorsApi.getContractors({
        ...filters,
        page: currentPage,
        limit: itemsPerPage,
      })

      if (response.success) {
        setContractors(response.data)
        setTotalContractors(response.total)
      }
    } catch (error) {
      console.error('Error loading contractors:', error)
      showToast('Ошибка загрузки исполнителей', 'error')
    } finally {
      setLoading(false)
    }
  }, [filters, currentPage, showToast])

  useEffect(() => {
    loadContractors()
  }, [loadContractors])

  // Handle contractor creation
  const handleCreateContractor = () => {
    setShowCreateModal(false)
    showToast('Исполнитель успешно создан', 'success')
    loadContractors()
  }

  // Handle contractor update
  const handleUpdateContractor = () => {
    setShowEditModal(false)
    setSelectedContractor(null)
    showToast('Исполнитель успешно обновлен', 'success')
    loadContractors()
  }

  // Handle contractor delete
  const handleDeleteContractor = async (contractorId: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого исполнителя? Это действие нельзя отменить.'))
      return

    try {
      const response = await contractorsApi.deleteContractor(contractorId)
      if (response.success) {
        showToast('Исполнитель удален', 'success')
        loadContractors()
        setShowViewModal(false)
        setSelectedContractor(null)
      } else {
        alert('Ошибка удаления: ' + response.message)
      }
    } catch (error) {
      console.error('Error deleting contractor:', error)
      showToast('Ошибка удаления исполнителя', 'error')
    }
  }

  // Handle contractor view
  const handleViewContractor = (contractor: Contractor) => {
    setSelectedContractor(contractor)
    setShowViewModal(true)
  }

  // Handle contractor edit
  const handleEditContractor = (contractor: Contractor) => {
    setSelectedContractor(contractor)
    setShowEditModal(true)
  }

  // Handle payment creation
  const handleCreatePayment = (contractor: Contractor) => {
    setSelectedContractor(contractor)
    setShowPaymentModal(true)
  }

  const handlePaymentCreated = () => {
    setShowPaymentModal(false)
    setSelectedContractor(null)
    showToast('Выплата успешно создана', 'success')
    loadContractors()
  }

  // Apply filters
  const applyFilters = () => {
    setCurrentPage(1)
    loadContractors()
  }

  // Clear filters
  const clearFilters = () => {
    setFilters({})
    setCurrentPage(1)
  }

  // Pagination
  const totalPages = Math.ceil(totalContractors / itemsPerPage)

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  return (
    <div className="p-6">
      <div className="max-w-[2000px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Управление исполнителями</h1>
            <p className="text-gray-600 mt-1">Все исполнители системы</p>
          </div>

          <div className="flex items-center gap-3">
            {/* Filter button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
            >
              <Filter className="w-5 h-5" />
              Фильтры
            </button>

            {/* Export button */}
            <button className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200">
              <Download className="w-5 h-5" />
              Экспорт
            </button>

            {/* Stats button */}
            <button className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200">
              <BarChart className="w-5 h-5" />
              Статистика
            </button>

            {/* Refresh button */}
            <button
              onClick={loadContractors}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
            >
              <RefreshCw className="w-5 h-5" />
            </button>

            {/* Create contractor button */}
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg"
            >
              <Plus className="w-5 h-5" />
              Добавить исполнителя
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Поиск</label>
                <input
                  type="text"
                  value={filters.search || ''}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                  placeholder="Имя, email, username..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Специализация
                </label>
                <select
                  value={filters.specialization || ''}
                  onChange={(e) => setFilters({ ...filters, specialization: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                >
                  <option value="">Все специализации</option>
                  <option value="developer">Разработчик</option>
                  <option value="designer">Дизайнер</option>
                  <option value="tester">Тестировщик</option>
                  <option value="manager">Менеджер</option>
                  <option value="analyst">Аналитик</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Статус</label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                >
                  <option value="">Все статусы</option>
                  <option value="active">Активные</option>
                  <option value="inactive">Неактивные</option>
                </select>
              </div>

              <div className="flex items-end gap-2">
                <button
                  onClick={applyFilters}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-semibold"
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

        {/* Contractors Grid */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : contractors.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">Исполнители не найдены</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {contractors.map((contractor) => (
                  <ContractorCard
                    key={contractor.id}
                    contractor={contractor}
                    onView={() => handleViewContractor(contractor)}
                    onEdit={() => handleEditContractor(contractor)}
                    onDelete={() => handleDeleteContractor(contractor.id)}
                    onCreatePayment={() => handleCreatePayment(contractor)}
                  />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-6 flex items-center justify-center gap-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-4 py-2 bg-white border-2 border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    ‹ Предыдущая
                  </button>

                  {[...Array(totalPages)].map((_, i) => {
                    const page = i + 1
                    if (
                      page === 1 ||
                      page === totalPages ||
                      (page >= currentPage - 1 && page <= currentPage + 1)
                    ) {
                      return (
                        <button
                          key={page}
                          onClick={() => handlePageChange(page)}
                          className={`px-4 py-2 rounded-lg transition-all ${
                            currentPage === page
                              ? 'bg-indigo-600 text-white'
                              : 'bg-white border-2 border-gray-200 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      )
                    } else if (page === currentPage - 2 || page === currentPage + 2) {
                      return <span key={page}>...</span>
                    }
                    return null
                  })}

                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="px-4 py-2 bg-white border-2 border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    Следующая ›
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Modals */}
      {showCreateModal && (
        <ContractorCreateModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateContractor}
        />
      )}

      {showEditModal && selectedContractor && (
        <ContractorEditModal
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false)
            setSelectedContractor(null)
          }}
          onSuccess={handleUpdateContractor}
          contractor={selectedContractor}
        />
      )}

      {showViewModal && selectedContractor && (
        <ContractorViewModal
          isOpen={showViewModal}
          onClose={() => {
            setShowViewModal(false)
            setSelectedContractor(null)
          }}
          contractor={selectedContractor}
          onEdit={() => {
            setShowViewModal(false)
            handleEditContractor(selectedContractor)
          }}
          onDelete={() => handleDeleteContractor(selectedContractor.id)}
        />
      )}

      {showPaymentModal && selectedContractor && (
        <PaymentModal
          isOpen={showPaymentModal}
          onClose={() => {
            setShowPaymentModal(false)
            setSelectedContractor(null)
          }}
          onSuccess={handlePaymentCreated}
          contractor={selectedContractor}
        />
      )}

      {/* Toast Container */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  )
}
