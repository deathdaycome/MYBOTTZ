import { useState, useEffect, useCallback } from 'react'
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Wallet,
  PieChart,
  Plus,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  Edit2,
  Trash2,
  X,
  ArrowUpCircle,
  ArrowDownCircle,
  Loader2,
} from 'lucide-react'
import financeApi from '../api/finance'
import type {
  FinanceTransaction,
  FinanceCategory,
  FinanceSummary,
  TransactionCreateData,
  CategoryCreateData,
} from '../api/finance'

export const Finance = () => {
  // ============= STATE =============
  const [loading, setLoading] = useState(true)
  const [transactions, setTransactions] = useState<FinanceTransaction[]>([])
  const [categories, setCategories] = useState<FinanceCategory[]>([])
  const [summary, setSummary] = useState<FinanceSummary | null>(null)

  // Filters
  const [filterType, setFilterType] = useState<'all' | 'income' | 'expense'>('all')
  const [filterDateFrom, setFilterDateFrom] = useState<string>('')
  const [filterDateTo, setFilterDateTo] = useState<string>('')
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null)

  // Modals
  const [showTransactionModal, setShowTransactionModal] = useState(false)
  const [showCategoryModal, setShowCategoryModal] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState<FinanceTransaction | null>(null)
  const [transactionType, setTransactionType] = useState<'income' | 'expense'>('income')

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

  // ============= LOAD DATA =============

  const loadData = useCallback(async () => {
    try {
      setLoading(true)

      // Загружаем транзакции с фильтрами
      const filters: any = { limit: 50, offset: 0 }
      if (filterType !== 'all') filters.type = filterType
      if (filterDateFrom) filters.date_from = filterDateFrom
      if (filterDateTo) filters.date_to = filterDateTo
      if (selectedCategoryId) filters.category_id = selectedCategoryId

      const [transactionsRes, categoriesRes, summaryRes] = await Promise.all([
        financeApi.getTransactions(filters),
        financeApi.getCategories(),
        financeApi.getSummary(filterDateFrom, filterDateTo),
      ])

      if (transactionsRes.success) {
        setTransactions(transactionsRes.data)
      }

      if (categoriesRes.success) {
        setCategories(categoriesRes.data)
      }

      if (summaryRes.success) {
        setSummary(summaryRes.data)
      }
    } catch (error) {
      console.error('Error loading finance data:', error)
      showToast('Ошибка загрузки данных', 'error')
    } finally {
      setLoading(false)
    }
  }, [filterType, filterDateFrom, filterDateTo, selectedCategoryId, showToast])

  useEffect(() => {
    loadData()
  }, [loadData])

  // ============= TRANSACTION HANDLERS =============

  const handleCreateTransaction = async (data: TransactionCreateData) => {
    try {
      const response = await financeApi.createTransaction(data)
      if (response.success) {
        showToast(response.message, 'success')
        setShowTransactionModal(false)
        setEditingTransaction(null)
        loadData()
      }
    } catch (error: any) {
      console.error('Error creating transaction:', error)
      showToast(error.response?.data?.detail || 'Ошибка создания транзакции', 'error')
    }
  }

  const handleUpdateTransaction = async (id: number, data: TransactionCreateData) => {
    try {
      const response = await financeApi.updateTransaction(id, data)
      if (response.success) {
        showToast(response.message, 'success')
        setShowTransactionModal(false)
        setEditingTransaction(null)
        loadData()
      }
    } catch (error: any) {
      console.error('Error updating transaction:', error)
      showToast(error.response?.data?.detail || 'Ошибка обновления транзакции', 'error')
    }
  }

  const handleDeleteTransaction = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту транзакцию?')) return

    try {
      const response = await financeApi.deleteTransaction(id)
      if (response.success) {
        showToast(response.message, 'success')
        loadData()
      }
    } catch (error: any) {
      console.error('Error deleting transaction:', error)
      showToast(error.response?.data?.detail || 'Ошибка удаления транзакции', 'error')
    }
  }

  // ============= CATEGORY HANDLERS =============

  const handleCreateCategory = async (data: CategoryCreateData) => {
    try {
      const response = await financeApi.createCategory(data)
      if (response.success) {
        showToast(response.message, 'success')
        setShowCategoryModal(false)
        loadData()
      }
    } catch (error: any) {
      console.error('Error creating category:', error)
      showToast(error.response?.data?.detail || 'Ошибка создания категории', 'error')
    }
  }

  const handleDeleteCategory = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту категорию?')) return

    try {
      const response = await financeApi.deleteCategory(id)
      if (response.success) {
        showToast(response.message, 'success')
        loadData()
      }
    } catch (error: any) {
      console.error('Error deleting category:', error)
      showToast(error.response?.data?.detail || 'Ошибка удаления категории', 'error')
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
      month: 'short',
      day: 'numeric',
    })
  }

  // ============= RENDER =============

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="max-w-[2000px] mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
              Финансы
            </h1>
            <p className="text-gray-600 mt-1">Управление доходами и расходами</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCategoryModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
            >
              <PieChart className="w-5 h-5" />
              Категории
            </button>

            <button
              onClick={loadData}
              className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-200"
            >
              <RefreshCw className="w-5 h-5" />
            </button>

            <button
              onClick={() => {
                setTransactionType('income')
                setEditingTransaction(null)
                setShowTransactionModal(true)
              }}
              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg hover:from-emerald-700 hover:to-teal-700 transition-all shadow-lg"
            >
              <Plus className="w-5 h-5" />
              Добавить операцию
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Income Card */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-lg p-6 border border-green-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <span className="text-sm text-green-600 font-medium">
                  {summary.income.count} операций
                </span>
              </div>
              <div className="text-3xl font-bold text-green-700 mb-1">
                {formatCurrency(summary.income.total)}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Доходы</div>
            </div>

            {/* Expenses Card */}
            <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-xl shadow-lg p-6 border border-red-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-rose-500 flex items-center justify-center shadow-lg">
                  <TrendingDown className="w-6 h-6 text-white" />
                </div>
                <span className="text-sm text-red-600 font-medium">
                  {summary.expenses.count} операций
                </span>
              </div>
              <div className="text-3xl font-bold text-red-700 mb-1">
                {formatCurrency(summary.expenses.total)}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Расходы</div>
            </div>

            {/* Profit Card */}
            <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl shadow-lg p-6 border border-purple-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-violet-500 flex items-center justify-center shadow-lg">
                  <DollarSign className="w-6 h-6 text-white" />
                </div>
              </div>
              <div
                className={`text-3xl font-bold mb-1 ${
                  summary.profit >= 0 ? 'text-purple-700' : 'text-red-700'
                }`}
              >
                {formatCurrency(summary.profit)}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Прибыль</div>
            </div>

            {/* Balance Card */}
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl shadow-lg p-6 border border-blue-200">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
                  <Wallet className="w-6 h-6 text-white" />
                </div>
              </div>
              <div className="text-3xl font-bold text-blue-700 mb-1">
                {formatCurrency(summary.income.total - summary.expenses.total)}
              </div>
              <div className="text-sm text-gray-600 uppercase tracking-wide">Баланс</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-500" />
              <span className="font-semibold text-gray-700">Фильтры:</span>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setFilterType('all')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  filterType === 'all'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Все
              </button>
              <button
                onClick={() => setFilterType('income')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  filterType === 'income'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Доходы
              </button>
              <button
                onClick={() => setFilterType('expense')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  filterType === 'expense'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Расходы
              </button>
            </div>

            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-gray-500" />
              <input
                type="date"
                value={filterDateFrom}
                onChange={(e) => setFilterDateFrom(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none"
              />
              <span className="text-gray-500">—</span>
              <input
                type="date"
                value={filterDateTo}
                onChange={(e) => setFilterDateTo(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>

            {(filterDateFrom || filterDateTo || filterType !== 'all') && (
              <button
                onClick={() => {
                  setFilterType('all')
                  setFilterDateFrom('')
                  setFilterDateTo('')
                  setSelectedCategoryId(null)
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
              >
                Сбросить
              </button>
            )}
          </div>
        </div>

        {/* Transactions List */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800">Последние операции</h2>
            <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all">
              <Download className="w-4 h-4" />
              Экспорт
            </button>
          </div>

          <div className="space-y-3">
            {transactions.length === 0 ? (
              <div className="text-center py-12">
                <DollarSign className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">Транзакций не найдено</p>
                <p className="text-gray-400 text-sm mt-2">Добавьте первую операцию</p>
              </div>
            ) : (
              transactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all"
                >
                  {/* Icon */}
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      transaction.type === 'income'
                        ? 'bg-green-100 text-green-600'
                        : 'bg-red-100 text-red-600'
                    }`}
                  >
                    {transaction.type === 'income' ? (
                      <ArrowUpCircle className="w-6 h-6" />
                    ) : (
                      <ArrowDownCircle className="w-6 h-6" />
                    )}
                  </div>

                  {/* Details */}
                  <div className="flex-1">
                    <div className="font-semibold text-gray-800">{transaction.description}</div>
                    <div className="text-sm text-gray-500 flex items-center gap-3 mt-1">
                      <span
                        className="px-2 py-0.5 rounded text-xs font-medium"
                        style={{
                          backgroundColor: transaction.category.color + '20',
                          color: transaction.category.color,
                        }}
                      >
                        {transaction.category.name}
                      </span>
                      <span>{formatDate(transaction.date)}</span>
                      {transaction.project && (
                        <span className="text-blue-600">• {transaction.project.title}</span>
                      )}
                    </div>
                  </div>

                  {/* Amount */}
                  <div
                    className={`text-xl font-bold ${
                      transaction.type === 'income' ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {transaction.type === 'income' ? '+' : '-'}
                    {formatCurrency(transaction.amount)}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        setEditingTransaction(transaction)
                        setTransactionType(transaction.type)
                        setShowTransactionModal(true)
                      }}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                      title="Редактировать"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteTransaction(transaction.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-all"
                      title="Удалить"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Top Categories */}
        {summary && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Income Categories */}
            {summary.top_income_categories.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Топ категорий доходов</h3>
                <div className="space-y-3">
                  {summary.top_income_categories.map((cat, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-green-100 text-green-600 flex items-center justify-center font-bold text-sm">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-800">{cat.name}</div>
                        <div className="text-sm text-green-600 font-semibold">
                          {formatCurrency(cat.total)}
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {((cat.total / summary.income.total) * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top Expense Categories */}
            {summary.top_expense_categories.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Топ категорий расходов</h3>
                <div className="space-y-3">
                  {summary.top_expense_categories.map((cat, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-red-100 text-red-600 flex items-center justify-center font-bold text-sm">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-800">{cat.name}</div>
                        <div className="text-sm text-red-600 font-semibold">
                          {formatCurrency(cat.total)}
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {((cat.total / summary.expenses.total) * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Transaction Modal */}
      {showTransactionModal && (
        <TransactionModal
          isOpen={showTransactionModal}
          onClose={() => {
            setShowTransactionModal(false)
            setEditingTransaction(null)
          }}
          onSave={editingTransaction ? handleUpdateTransaction : handleCreateTransaction}
          transaction={editingTransaction}
          categories={categories}
          type={transactionType}
          onTypeChange={setTransactionType}
        />
      )}

      {/* Category Modal */}
      {showCategoryModal && (
        <CategoryModal
          isOpen={showCategoryModal}
          onClose={() => {
            setShowCategoryModal(false)
          }}
          onCreate={handleCreateCategory}
          onDelete={handleDeleteCategory}
          categories={categories}
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

// ============= TRANSACTION MODAL =============

interface TransactionModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: ((data: TransactionCreateData) => Promise<void>) | ((id: number, data: TransactionCreateData) => Promise<void>)
  transaction: FinanceTransaction | null
  categories: FinanceCategory[]
  type: 'income' | 'expense'
  onTypeChange: (type: 'income' | 'expense') => void
}

const TransactionModal = ({
  isOpen,
  onClose,
  onSave,
  transaction,
  categories,
  type,
  onTypeChange,
}: TransactionModalProps) => {
  const [formData, setFormData] = useState<TransactionCreateData>({
    amount: transaction?.amount || 0,
    type: transaction?.type || type,
    description: transaction?.description || '',
    date: transaction?.date ? transaction.date.split('T')[0] : new Date().toISOString().split('T')[0],
    category_id: transaction?.category.id || 0,
    project_id: transaction?.project?.id,
    contractor_name: transaction?.contractor_name || '',
    account: transaction?.account || 'card',
    receipt_url: transaction?.receipt_url || '',
    notes: transaction?.notes || '',
    is_recurring: transaction?.is_recurring || false,
    recurring_period: transaction?.recurring_period || '',
  })

  const filteredCategories = categories.filter((c) => c.type === formData.type)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (transaction) {
      ;(onSave as any)(transaction.id, formData)
    } else {
      ;(onSave as any)(formData)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">
            {transaction ? 'Редактировать операцию' : 'Новая операция'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Type Toggle */}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                setFormData({ ...formData, type: 'income', category_id: 0 })
                onTypeChange('income')
              }}
              className={`flex-1 py-3 rounded-lg font-semibold transition-all ${
                formData.type === 'income'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              Доход
            </button>
            <button
              type="button"
              onClick={() => {
                setFormData({ ...formData, type: 'expense', category_id: 0 })
                onTypeChange('expense')
              }}
              className={`flex-1 py-3 rounded-lg font-semibold transition-all ${
                formData.type === 'expense'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              Расход
            </button>
          </div>

          {/* Amount */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Сумма *</label>
            <input
              type="number"
              step="0.01"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
              className="w-full px-4 py-3 text-2xl font-bold border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all text-center"
              placeholder="0.00"
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Категория *</label>
            <select
              value={formData.category_id}
              onChange={(e) =>
                setFormData({ ...formData, category_id: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
              required
            >
              <option value={0}>Выберите категорию</option>
              {filteredCategories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Описание *</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
              placeholder="Краткое описание"
              required
            />
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Дата *</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
              required
            />
          </div>

          {/* Account */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Счет</label>
            <select
              value={formData.account}
              onChange={(e) => setFormData({ ...formData, account: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
            >
              <option value="card">Карта</option>
              <option value="cash">Наличные</option>
              <option value="bank">Банк</option>
            </select>
          </div>

          {/* Contractor Name */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Контрагент
            </label>
            <input
              type="text"
              value={formData.contractor_name || ''}
              onChange={(e) =>
                setFormData({ ...formData, contractor_name: e.target.value })
              }
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
              placeholder="Имя исполнителя/поставщика"
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Примечания
            </label>
            <textarea
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none transition-all"
              rows={3}
              placeholder="Дополнительная информация"
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
              className="flex-1 px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg hover:from-emerald-700 hover:to-teal-700 transition-all font-semibold shadow-lg"
            >
              {transaction ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ============= CATEGORY MODAL =============

interface CategoryModalProps {
  isOpen: boolean
  onClose: () => void
  onCreate: (data: CategoryCreateData) => void
  onDelete: (id: number) => void
  categories: FinanceCategory[]
}

const CategoryModal = ({ isOpen, onClose, onCreate, onDelete, categories }: CategoryModalProps) => {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<CategoryCreateData>({
    name: '',
    type: 'income',
    description: '',
    color: '#10b981',
    icon: 'fas fa-circle',
  })

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'income',
      description: '',
      color: '#10b981',
      icon: 'fas fa-circle',
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onCreate(formData)
    setShowForm(false)
    resetForm()
  }

  if (!isOpen) return null

  const incomeCategories = categories.filter((c) => c.type === 'income')
  const expenseCategories = categories.filter((c) => c.type === 'expense')

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">Управление категориями</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Add Category Button */}
          {!showForm && (
            <button
              onClick={() => setShowForm(true)}
              className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg hover:from-emerald-700 hover:to-teal-700 transition-all font-semibold shadow-lg flex items-center justify-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Добавить категорию
            </button>
          )}

          {/* Add Category Form */}
          {showForm && (
            <form onSubmit={handleSubmit} className="bg-gray-50 rounded-lg p-4 space-y-3">
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, type: 'income' })}
                  className={`flex-1 py-2 rounded-lg font-semibold transition-all ${
                    formData.type === 'income'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  Доход
                </button>
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, type: 'expense' })}
                  className={`flex-1 py-2 rounded-lg font-semibold transition-all ${
                    formData.type === 'expense'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  Расход
                </button>
              </div>

              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-emerald-500 outline-none"
                placeholder="Название категории"
                required
              />

              <input
                type="text"
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-emerald-500 outline-none"
                placeholder="Описание (необязательно)"
              />

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all font-semibold"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-all font-semibold"
                >
                  Создать
                </button>
              </div>
            </form>
          )}

          {/* Income Categories */}
          <div>
            <h3 className="text-lg font-bold text-green-700 mb-3">Категории доходов</h3>
            <div className="space-y-2">
              {incomeCategories.map((cat) => (
                <div
                  key={cat.id}
                  className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: cat.color + '40', color: cat.color }}
                    >
                      <DollarSign className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">{cat.name}</div>
                      {cat.description && (
                        <div className="text-sm text-gray-500">{cat.description}</div>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => onDelete(cat.id)}
                    className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
              {incomeCategories.length === 0 && (
                <p className="text-gray-400 text-center py-4">Нет категорий доходов</p>
              )}
            </div>
          </div>

          {/* Expense Categories */}
          <div>
            <h3 className="text-lg font-bold text-red-700 mb-3">Категории расходов</h3>
            <div className="space-y-2">
              {expenseCategories.map((cat) => (
                <div
                  key={cat.id}
                  className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: cat.color + '40', color: cat.color }}
                    >
                      <DollarSign className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">{cat.name}</div>
                      {cat.description && (
                        <div className="text-sm text-gray-500">{cat.description}</div>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => onDelete(cat.id)}
                    className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
              {expenseCategories.length === 0 && (
                <p className="text-gray-400 text-center py-4">Нет категорий расходов</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
