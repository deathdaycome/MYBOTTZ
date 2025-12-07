import { useState, useEffect } from 'react'
import {
  X,
  DollarSign,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  Plus,
  Trash2,
  Edit2,
  Check,
  Calendar,
  FileText,
  PieChart,
} from 'lucide-react'

interface BudgetItem {
  id: number
  category: string
  description: string
  plannedAmount: number
  actualAmount: number
  date: string
  createdBy: string
}

interface BudgetCategory {
  name: string
  planned: number
  actual: number
  color: string
}

interface BudgetTrackingProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
  totalBudget: number
}

const EXPENSE_CATEGORIES = [
  'Разработка',
  'Дизайн',
  'Тестирование',
  'Хостинг',
  'Маркетинг',
  'Менеджмент',
  'Консультации',
  'Лицензии',
  'Прочее',
]

const CATEGORY_COLORS: Record<string, string> = {
  Разработка: '#3B82F6',
  Дизайн: '#EC4899',
  Тестирование: '#10B981',
  Хостинг: '#F59E0B',
  Маркетинг: '#8B5CF6',
  Менеджмент: '#14B8A6',
  Консультации: '#6366F1',
  Лицензии: '#EF4444',
  Прочее: '#6B7280',
}

export const BudgetTracking = ({
  isOpen,
  onClose,
  projectId,
  projectName,
  totalBudget,
}: BudgetTrackingProps) => {
  const [budgetItems, setBudgetItems] = useState<BudgetItem[]>([])
  const [isAddingItem, setIsAddingItem] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [newItem, setNewItem] = useState({
    category: EXPENSE_CATEGORIES[0],
    description: '',
    plannedAmount: 0,
    actualAmount: 0,
    date: new Date().toISOString().slice(0, 10),
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && projectId) {
      loadBudgetItems()
    }
  }, [isOpen, projectId])

  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }, [isOpen])

  const loadBudgetItems = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/budget`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })

      if (response.ok) {
        const data = await response.json()
        setBudgetItems(data.items || [])
      } else {
        // Mock data
        setBudgetItems([
          {
            id: 1,
            category: 'Разработка',
            description: 'Фронтенд разработка',
            plannedAmount: 150000,
            actualAmount: 135000,
            date: '2025-01-10',
            createdBy: 'admin',
          },
          {
            id: 2,
            category: 'Дизайн',
            description: 'UI/UX дизайн',
            plannedAmount: 80000,
            actualAmount: 85000,
            date: '2025-01-15',
            createdBy: 'admin',
          },
          {
            id: 3,
            category: 'Хостинг',
            description: 'Облачный хостинг на год',
            plannedAmount: 30000,
            actualAmount: 30000,
            date: '2025-01-20',
            createdBy: 'admin',
          },
        ])
      }
    } catch (err) {
      console.error('Error loading budget items:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddItem = async () => {
    if (!newItem.description.trim()) return

    try {
      const response = await fetch(`http://localhost:8001/admin/api/projects/${projectId}/budget`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(newItem),
      })

      if (response.ok) {
        setNewItem({
          category: EXPENSE_CATEGORIES[0],
          description: '',
          plannedAmount: 0,
          actualAmount: 0,
          date: new Date().toISOString().slice(0, 10),
        })
        setIsAddingItem(false)
        await loadBudgetItems()
      }
    } catch (err) {
      console.error('Error adding item:', err)
    }
  }

  const handleDeleteItem = async (id: number) => {
    if (!confirm('Удалить эту запись бюджета?')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/budget/${id}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadBudgetItems()
      }
    } catch (err) {
      console.error('Error deleting item:', err)
    }
  }

  const calculateTotals = () => {
    const totalPlanned = budgetItems.reduce((sum, item) => sum + item.plannedAmount, 0)
    const totalActual = budgetItems.reduce((sum, item) => sum + item.actualAmount, 0)
    const remaining = totalBudget - totalActual
    const variance = totalActual - totalPlanned

    return { totalPlanned, totalActual, remaining, variance }
  }

  const calculateCategoryTotals = (): BudgetCategory[] => {
    const categoryMap = new Map<string, { planned: number; actual: number }>()

    budgetItems.forEach((item) => {
      const current = categoryMap.get(item.category) || { planned: 0, actual: 0 }
      categoryMap.set(item.category, {
        planned: current.planned + item.plannedAmount,
        actual: current.actual + item.actualAmount,
      })
    })

    return Array.from(categoryMap.entries()).map(([name, totals]) => ({
      name,
      planned: totals.planned,
      actual: totals.actual,
      color: CATEGORY_COLORS[name] || '#6B7280',
    }))
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    }).format(date)
  }

  if (!isOpen) return null

  const totals = calculateTotals()
  const categoryTotals = calculateCategoryTotals()
  const budgetUsagePercent = (totals.totalActual / totalBudget) * 100

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <DollarSign className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Отслеживание бюджета</h3>
              <p className="text-emerald-100 text-sm mt-1">{projectName}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Summary Cards */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex-shrink-0">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Total Budget */}
            <div className="bg-white rounded-xl p-4 border-2 border-blue-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Общий бюджет</div>
              <div className="text-2xl font-bold text-blue-600">{formatCurrency(totalBudget)}</div>
            </div>

            {/* Planned */}
            <div className="bg-white rounded-xl p-4 border-2 border-purple-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Запланировано</div>
              <div className="text-2xl font-bold text-purple-600">
                {formatCurrency(totals.totalPlanned)}
              </div>
            </div>

            {/* Actual */}
            <div className="bg-white rounded-xl p-4 border-2 border-emerald-200">
              <div className="text-xs font-semibold text-gray-600 mb-1">Потрачено</div>
              <div className="text-2xl font-bold text-emerald-600">
                {formatCurrency(totals.totalActual)}
              </div>
              <div className="text-xs text-gray-500 mt-1">{budgetUsagePercent.toFixed(1)}% бюджета</div>
            </div>

            {/* Remaining */}
            <div
              className={`bg-white rounded-xl p-4 border-2 ${
                totals.remaining >= 0 ? 'border-green-200' : 'border-red-200'
              }`}
            >
              <div className="text-xs font-semibold text-gray-600 mb-1">Остаток</div>
              <div
                className={`text-2xl font-bold ${
                  totals.remaining >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {formatCurrency(totals.remaining)}
              </div>
              {totals.variance !== 0 && (
                <div className="flex items-center gap-1 mt-1">
                  {totals.variance > 0 ? (
                    <TrendingUp className="w-3.5 h-3.5 text-red-600" />
                  ) : (
                    <TrendingDown className="w-3.5 h-3.5 text-green-600" />
                  )}
                  <span
                    className={`text-xs ${totals.variance > 0 ? 'text-red-600' : 'text-green-600'}`}
                  >
                    {Math.abs(totals.variance).toLocaleString()} ₽ от плана
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Budget Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700">Использование бюджета</span>
              <span className="text-sm font-bold text-gray-900">{budgetUsagePercent.toFixed(1)}%</span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  budgetUsagePercent > 100
                    ? 'bg-red-500'
                    : budgetUsagePercent > 80
                      ? 'bg-yellow-500'
                      : 'bg-emerald-500'
                }`}
                style={{ width: `${Math.min(budgetUsagePercent, 100)}%` }}
              />
            </div>
            {budgetUsagePercent > 90 && (
              <div className="mt-2 flex items-center gap-2 text-xs text-orange-600">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Внимание! Бюджет почти исчерпан</span>
              </div>
            )}
          </div>
        </div>

        {/* Category Breakdown */}
        {categoryTotals.length > 0 && (
          <div className="px-6 py-4 bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-gray-200 flex-shrink-0">
            <div className="flex items-center gap-2 mb-3">
              <PieChart className="w-5 h-5 text-emerald-600" />
              <h4 className="font-bold text-gray-900">Расходы по категориям</h4>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {categoryTotals.map((category) => (
                <div key={category.name} className="bg-white rounded-lg p-3 border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: category.color }}
                    />
                    <span className="text-xs font-semibold text-gray-700">{category.name}</span>
                  </div>
                  <div className="text-sm font-bold text-gray-900">
                    {formatCurrency(category.actual)}
                  </div>
                  <div className="text-xs text-gray-500">
                    План: {formatCurrency(category.planned)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Add Item Button */}
          {!isAddingItem && (
            <button
              onClick={() => setIsAddingItem(true)}
              className="w-full mb-4 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg hover:from-emerald-700 hover:to-teal-700 transition-all font-semibold"
            >
              <Plus className="w-5 h-5" />
              Добавить расход
            </button>
          )}

          {/* Add Item Form */}
          {isAddingItem && (
            <div className="mb-4 bg-emerald-50 border-2 border-emerald-200 rounded-xl p-4">
              <h4 className="font-bold text-gray-900 mb-3">Новая запись бюджета</h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Категория
                  </label>
                  <select
                    value={newItem.category}
                    onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none"
                  >
                    {EXPENSE_CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Дата</label>
                  <input
                    type="date"
                    value={newItem.date}
                    onChange={(e) => setNewItem({ ...newItem, date: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Описание
                  </label>
                  <input
                    type="text"
                    value={newItem.description}
                    onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                    className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none"
                    placeholder="Опишите расход..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Плановая сумма (₽)
                  </label>
                  <input
                    type="number"
                    value={newItem.plannedAmount}
                    onChange={(e) =>
                      setNewItem({ ...newItem, plannedAmount: Number(e.target.value) })
                    }
                    className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none"
                    min="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Фактическая сумма (₽)
                  </label>
                  <input
                    type="number"
                    value={newItem.actualAmount}
                    onChange={(e) =>
                      setNewItem({ ...newItem, actualAmount: Number(e.target.value) })
                    }
                    className="w-full px-4 py-2 border-2 border-emerald-300 rounded-lg focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none"
                    min="0"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleAddItem}
                  disabled={!newItem.description.trim()}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-semibold"
                >
                  <Check className="w-4 h-4" />
                  Добавить
                </button>
                <button
                  onClick={() => {
                    setIsAddingItem(false)
                    setNewItem({
                      category: EXPENSE_CATEGORIES[0],
                      description: '',
                      plannedAmount: 0,
                      actualAmount: 0,
                      date: new Date().toISOString().slice(0, 10),
                    })
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                >
                  Отмена
                </button>
              </div>
            </div>
          )}

          {/* Budget Items List */}
          {loading ? (
            <div className="text-center py-8 text-gray-500">Загрузка...</div>
          ) : budgetItems.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg font-semibold">Нет записей бюджета</p>
              <p className="text-sm mt-2">Добавьте первую запись расходов</p>
            </div>
          ) : (
            <div className="space-y-3">
              {budgetItems.map((item) => {
                const variance = item.actualAmount - item.plannedAmount
                const variancePercent = ((variance / item.plannedAmount) * 100).toFixed(1)

                return (
                  <div
                    key={item.id}
                    className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-emerald-400 transition-all"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: CATEGORY_COLORS[item.category] }}
                          />
                          <span className="font-bold text-gray-900 text-lg">{item.description}</span>
                          <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full">
                            {item.category}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-2">
                          <div>
                            <div className="text-xs text-gray-600">Планировалось</div>
                            <div className="text-sm font-bold text-purple-600">
                              {formatCurrency(item.plannedAmount)}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-600">Потрачено</div>
                            <div className="text-sm font-bold text-emerald-600">
                              {formatCurrency(item.actualAmount)}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-600">Отклонение</div>
                            <div
                              className={`text-sm font-bold flex items-center gap-1 ${
                                variance > 0 ? 'text-red-600' : variance < 0 ? 'text-green-600' : 'text-gray-600'
                              }`}
                            >
                              {variance > 0 && <TrendingUp className="w-3.5 h-3.5" />}
                              {variance < 0 && <TrendingDown className="w-3.5 h-3.5" />}
                              {variance !== 0 ? `${variance > 0 ? '+' : ''}${variancePercent}%` : '—'}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-600">Дата</div>
                            <div className="text-sm font-semibold text-gray-900 flex items-center gap-1">
                              <Calendar className="w-3.5 h-3.5" />
                              {formatDate(item.date)}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => handleDeleteItem(item.id)}
                          className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="text-sm text-gray-600">
            Всего записей: <span className="font-bold text-emerald-600">{budgetItems.length}</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
