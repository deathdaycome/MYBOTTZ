import React, { useState, useEffect } from 'react'
import { TrendingDown, X, Plus, Download, Filter, Calendar, DollarSign, Tag, User, FileText, Trash2, Edit2, PieChart } from 'lucide-react'

interface ExpenseTrackingProps {
  projectId: number
  onClose: () => void
}

interface Expense {
  id: number
  date: string
  category: 'salary' | 'equipment' | 'software' | 'marketing' | 'office' | 'travel' | 'consulting' | 'other'
  description: string
  amount: number
  paidTo: string
  paymentMethod: 'cash' | 'card' | 'transfer' | 'invoice'
  receipt?: string
  status: 'pending' | 'approved' | 'rejected' | 'paid'
  approvedBy?: string
  notes: string
  createdBy: string
}

const ExpenseTracking: React.FC<ExpenseTrackingProps> = ({ projectId, onClose }) => {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState(new Date().toISOString().slice(0, 10))
  const [viewMode, setViewMode] = useState<'list' | 'chart'>('list')

  const [newExpense, setNewExpense] = useState({
    date: new Date().toISOString().slice(0, 10),
    category: 'other' as Expense['category'],
    description: '',
    amount: 0,
    paidTo: '',
    paymentMethod: 'transfer' as Expense['paymentMethod'],
    notes: '',
    createdBy: 'Текущий пользователь',
  })

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = 'unset' }
  }, [])

  useEffect(() => {
    fetchExpenses()
  }, [projectId])

  const fetchExpenses = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `http://147.45.215.199:8001/api/projects/${projectId}/expenses`,
        {
          headers: { Authorization: 'Basic ' + btoa('admin:qwerty123') },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setExpenses(data)
      } else {
        setExpenses([
          {
            id: 1,
            date: '2024-03-15',
            category: 'salary',
            description: 'Зарплата разработчиков',
            amount: 150000,
            paidTo: 'Команда разработки',
            paymentMethod: 'transfer',
            status: 'paid',
            approvedBy: 'Иван Петров',
            notes: 'Зарплата за март 2024',
            createdBy: 'Мария Смирнова',
          },
          {
            id: 2,
            date: '2024-03-10',
            category: 'software',
            description: 'Подписка на IDE и сервисы',
            amount: 15000,
            paidTo: 'JetBrains, GitHub',
            paymentMethod: 'card',
            status: 'approved',
            approvedBy: 'Иван Петров',
            notes: 'Месячная подписка на инструменты',
            createdBy: 'Алексей Коваленко',
          },
          {
            id: 3,
            date: '2024-03-08',
            category: 'equipment',
            description: 'Ноутбук для нового сотрудника',
            amount: 85000,
            paidTo: 'DNS',
            paymentMethod: 'invoice',
            status: 'paid',
            approvedBy: 'Иван Петров',
            notes: 'MacBook Pro 14"',
            createdBy: 'Мария Смирнова',
          },
          {
            id: 4,
            date: '2024-03-05',
            category: 'marketing',
            description: 'Контекстная реклама',
            amount: 25000,
            paidTo: 'Яндекс.Директ',
            paymentMethod: 'card',
            status: 'pending',
            notes: 'Рекламная кампания на март',
            createdBy: 'Ольга Новикова',
          },
          {
            id: 5,
            date: '2024-03-01',
            category: 'office',
            description: 'Аренда офиса',
            amount: 120000,
            paidTo: 'Бизнес-центр "Москва-Сити"',
            paymentMethod: 'transfer',
            status: 'paid',
            approvedBy: 'Иван Петров',
            notes: 'Аренда за март 2024',
            createdBy: 'Мария Смирнова',
          },
          {
            id: 6,
            date: '2024-02-28',
            category: 'travel',
            description: 'Командировка в Санкт-Петербург',
            amount: 35000,
            paidTo: 'Авиакомпания, Отель',
            paymentMethod: 'card',
            status: 'approved',
            approvedBy: 'Иван Петров',
            notes: 'Встреча с клиентом',
            createdBy: 'Алексей Коваленко',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching expenses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddExpense = () => {
    if (!newExpense.description || !newExpense.paidTo || newExpense.amount <= 0) {
      alert('Заполните все обязательные поля')
      return
    }

    const expense: Expense = {
      id: Date.now(),
      date: newExpense.date,
      category: newExpense.category,
      description: newExpense.description,
      amount: newExpense.amount,
      paidTo: newExpense.paidTo,
      paymentMethod: newExpense.paymentMethod,
      status: 'pending',
      notes: newExpense.notes,
      createdBy: newExpense.createdBy,
    }

    setExpenses([expense, ...expenses])
    setShowAddModal(false)
    setNewExpense({
      date: new Date().toISOString().slice(0, 10),
      category: 'other',
      description: '',
      amount: 0,
      paidTo: '',
      paymentMethod: 'transfer',
      notes: '',
      createdBy: 'Текущий пользователь',
    })
  }

  const handleApproveExpense = (expenseId: number) => {
    setExpenses(
      expenses.map((exp) =>
        exp.id === expenseId
          ? { ...exp, status: 'approved' as const, approvedBy: 'Текущий пользователь' }
          : exp
      )
    )
  }

  const handleRejectExpense = (expenseId: number) => {
    if (!confirm('Отклонить расход?')) return
    setExpenses(
      expenses.map((exp) =>
        exp.id === expenseId ? { ...exp, status: 'rejected' as const } : exp
      )
    )
  }

  const handleMarkAsPaid = (expenseId: number) => {
    setExpenses(
      expenses.map((exp) =>
        exp.id === expenseId ? { ...exp, status: 'paid' as const } : exp
      )
    )
  }

  const handleDeleteExpense = (expenseId: number) => {
    if (!confirm('Удалить расход?')) return
    setExpenses(expenses.filter((exp) => exp.id !== expenseId))
  }

  const getCategoryIcon = (category: string) => {
    const icons = {
      salary: '💰',
      equipment: '💻',
      software: '📦',
      marketing: '📢',
      office: '🏢',
      travel: '✈️',
      consulting: '🤝',
      other: '📋',
    }
    return icons[category as keyof typeof icons] || '📋'
  }

  const getCategoryLabel = (category: string) => {
    const labels = {
      salary: 'Зарплата',
      equipment: 'Оборудование',
      software: 'ПО',
      marketing: 'Маркетинг',
      office: 'Офис',
      travel: 'Командировки',
      consulting: 'Консультации',
      other: 'Другое',
    }
    return labels[category as keyof typeof labels] || category
  }

  const getStatusColor = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-700',
      approved: 'bg-blue-100 text-blue-700',
      rejected: 'bg-red-100 text-red-700',
      paid: 'bg-green-100 text-green-700',
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-700'
  }

  const getStatusLabel = (status: string) => {
    const labels = {
      pending: 'На рассмотрении',
      approved: 'Одобрен',
      rejected: 'Отклонен',
      paid: 'Оплачен',
    }
    return labels[status as keyof typeof labels] || status
  }

  const getPaymentMethodLabel = (method: string) => {
    const labels = {
      cash: 'Наличные',
      card: 'Карта',
      transfer: 'Перевод',
      invoice: 'Счет',
    }
    return labels[method as keyof typeof labels] || method
  }

  const filteredExpenses = expenses.filter((expense) => {
    const matchesCategory = filterCategory === 'all' || expense.category === filterCategory
    const matchesStatus = filterStatus === 'all' || expense.status === filterStatus
    const matchesDate =
      (!dateFrom || expense.date >= dateFrom) && (!dateTo || expense.date <= dateTo)
    return matchesCategory && matchesStatus && matchesDate
  })

  const totalExpenses = filteredExpenses.reduce((sum, exp) => sum + exp.amount, 0)

  const expensesByCategory = Object.entries(
    filteredExpenses.reduce((acc, exp) => {
      acc[exp.category] = (acc[exp.category] || 0) + exp.amount
      return acc
    }, {} as Record<string, number>)
  ).sort((a, b) => b[1] - a[1])

  const expensesByStatus = {
    pending: filteredExpenses.filter((e) => e.status === 'pending').reduce((sum, e) => sum + e.amount, 0),
    approved: filteredExpenses.filter((e) => e.status === 'approved').reduce((sum, e) => sum + e.amount, 0),
    paid: filteredExpenses.filter((e) => e.status === 'paid').reduce((sum, e) => sum + e.amount, 0),
    rejected: filteredExpenses.filter((e) => e.status === 'rejected').reduce((sum, e) => sum + e.amount, 0),
  }

  const handleExport = () => {
    const csvContent = [
      ['Дата', 'Категория', 'Описание', 'Сумма', 'Получатель', 'Метод оплаты', 'Статус', 'Создал'].join(','),
      ...filteredExpenses.map((expense) =>
        [
          expense.date,
          getCategoryLabel(expense.category),
          `"${expense.description.replace(/"/g, '""')}"`,
          expense.amount,
          `"${expense.paidTo.replace(/"/g, '""')}"`,
          getPaymentMethodLabel(expense.paymentMethod),
          getStatusLabel(expense.status),
          expense.createdBy,
        ].join(',')
      ),
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `expenses-project-${projectId}-${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка расходов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="bg-gradient-to-r from-red-600 to-pink-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <TrendingDown className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Учет расходов</h2>
              <p className="text-red-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 border-b bg-gray-50">
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <DollarSign className="w-8 h-8 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-500">Всего расходов</p>
                  <p className="text-xl font-bold text-gray-900">{totalExpenses.toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 text-2xl">⏳</div>
                <div>
                  <p className="text-sm text-gray-500">На рассмотрении</p>
                  <p className="text-xl font-bold text-yellow-700">{expensesByStatus.pending.toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 text-2xl">✓</div>
                <div>
                  <p className="text-sm text-gray-500">Одобрено</p>
                  <p className="text-xl font-bold text-blue-700">{expensesByStatus.approved.toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 text-2xl">💳</div>
                <div>
                  <p className="text-sm text-gray-500">Оплачено</p>
                  <p className="text-xl font-bold text-green-700">{expensesByStatus.paid.toLocaleString('ru-RU')} ₽</p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setShowAddModal(true)}
              className="bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2 font-medium"
            >
              <Plus className="w-5 h-5" />
              Добавить расход
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            >
              <option value="all">Все категории</option>
              <option value="salary">Зарплата</option>
              <option value="equipment">Оборудование</option>
              <option value="software">ПО</option>
              <option value="marketing">Маркетинг</option>
              <option value="office">Офис</option>
              <option value="travel">Командировки</option>
              <option value="consulting">Консультации</option>
              <option value="other">Другое</option>
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            >
              <option value="all">Все статусы</option>
              <option value="pending">На рассмотрении</option>
              <option value="approved">Одобрен</option>
              <option value="paid">Оплачен</option>
              <option value="rejected">Отклонен</option>
            </select>

            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              placeholder="От"
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />

            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              placeholder="До"
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />

            <div className="flex gap-2">
              <button
                onClick={() => setViewMode(viewMode === 'list' ? 'chart' : 'list')}
                className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center gap-2"
              >
                <PieChart className="w-5 h-5" />
                {viewMode === 'list' ? 'График' : 'Список'}
              </button>
              <button
                onClick={handleExport}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" />
                Экспорт
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {viewMode === 'list' ? (
            <div className="space-y-4">
              {filteredExpenses.map((expense) => (
                <div
                  key={expense.id}
                  className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="text-4xl">{getCategoryIcon(expense.category)}</div>

                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">{expense.description}</h3>
                          <span className={`text-xs px-3 py-1 rounded-full ${getStatusColor(expense.status)}`}>
                            {getStatusLabel(expense.status)}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                          <div className="flex items-center gap-2">
                            <Tag className="w-4 h-4 text-gray-400" />
                            <div>
                              <p className="font-medium text-gray-900">{getCategoryLabel(expense.category)}</p>
                              <p className="text-xs text-gray-500">{getPaymentMethodLabel(expense.paymentMethod)}</p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-gray-400" />
                            <div>
                              <p className="text-gray-900">{expense.paidTo}</p>
                              <p className="text-xs text-gray-500">Получатель</p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-gray-400" />
                            <div>
                              <p className="text-gray-900">{new Date(expense.date).toLocaleDateString('ru-RU')}</p>
                              <p className="text-xs text-gray-500">Создал: {expense.createdBy}</p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <DollarSign className="w-4 h-4 text-gray-400" />
                            <div>
                              <p className="text-2xl font-bold text-red-600">{expense.amount.toLocaleString('ru-RU')} ₽</p>
                            </div>
                          </div>
                        </div>

                        {expense.notes && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <p className="text-sm text-gray-600">{expense.notes}</p>
                          </div>
                        )}

                        {expense.approvedBy && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <p className="text-sm text-green-600">✓ Одобрил: {expense.approvedBy}</p>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2 ml-4">
                      {expense.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleApproveExpense(expense.id)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Одобрить"
                          >
                            ✓
                          </button>
                          <button
                            onClick={() => handleRejectExpense(expense.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Отклонить"
                          >
                            ✗
                          </button>
                        </>
                      )}

                      {expense.status === 'approved' && (
                        <button
                          onClick={() => handleMarkAsPaid(expense.id)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Отметить как оплаченный"
                        >
                          💳
                        </button>
                      )}

                      <button
                        onClick={() => handleDeleteExpense(expense.id)}
                        className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {filteredExpenses.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <TrendingDown className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Расходы не найдены</p>
                </div>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Расходы по категориям</h3>
                <div className="space-y-3">
                  {expensesByCategory.map(([category, amount]) => {
                    const percentage = (amount / totalExpenses) * 100
                    return (
                      <div key={category}>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">
                            {getCategoryIcon(category)} {getCategoryLabel(category)}
                          </span>
                          <span className="text-sm font-bold text-gray-900">
                            {amount.toLocaleString('ru-RU')} ₽ ({percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-red-600 h-3 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Расходы по статусам</h3>
                <div className="space-y-4">
                  {Object.entries(expensesByStatus).map(([status, amount]) => {
                    const percentage = totalExpenses > 0 ? (amount / totalExpenses) * 100 : 0
                    const count = filteredExpenses.filter((e) => e.status === status).length
                    return (
                      <div key={status} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-2">
                          <div>
                            <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(status)}`}>
                              {getStatusLabel(status)}
                            </span>
                            <p className="text-xs text-gray-500 mt-1">{count} расходов</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xl font-bold text-gray-900">{amount.toLocaleString('ru-RU')} ₽</p>
                            <p className="text-xs text-gray-500">{percentage.toFixed(1)}%</p>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${
                              status === 'paid' ? 'bg-green-600' :
                              status === 'approved' ? 'bg-blue-600' :
                              status === 'pending' ? 'bg-yellow-600' : 'bg-red-600'
                            }`}
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="bg-gradient-to-r from-red-600 to-pink-600 text-white p-6 flex justify-between items-center">
              <h3 className="text-2xl font-bold">Добавить расход</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Дата *</label>
                    <input
                      type="date"
                      value={newExpense.date}
                      onChange={(e) => setNewExpense({ ...newExpense, date: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Категория *</label>
                    <select
                      value={newExpense.category}
                      onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value as Expense['category'] })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                      <option value="salary">Зарплата</option>
                      <option value="equipment">Оборудование</option>
                      <option value="software">ПО</option>
                      <option value="marketing">Маркетинг</option>
                      <option value="office">Офис</option>
                      <option value="travel">Командировки</option>
                      <option value="consulting">Консультации</option>
                      <option value="other">Другое</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Описание *</label>
                  <input
                    type="text"
                    value={newExpense.description}
                    onChange={(e) => setNewExpense({ ...newExpense, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Сумма (₽) *</label>
                    <input
                      type="number"
                      value={newExpense.amount}
                      onChange={(e) => setNewExpense({ ...newExpense, amount: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Метод оплаты</label>
                    <select
                      value={newExpense.paymentMethod}
                      onChange={(e) => setNewExpense({ ...newExpense, paymentMethod: e.target.value as Expense['paymentMethod'] })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                      <option value="cash">Наличные</option>
                      <option value="card">Карта</option>
                      <option value="transfer">Перевод</option>
                      <option value="invoice">Счет</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Получатель *</label>
                  <input
                    type="text"
                    value={newExpense.paidTo}
                    onChange={(e) => setNewExpense({ ...newExpense, paidTo: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Примечания</label>
                  <textarea
                    value={newExpense.notes}
                    onChange={(e) => setNewExpense({ ...newExpense, notes: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 border-t flex gap-3 justify-end">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleAddExpense}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
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

export default ExpenseTracking
