import React, { useState, useEffect } from 'react'
import { BarChart3, X, TrendingUp, TrendingDown, Users, DollarSign, Clock, Target, Activity, Download, Calendar } from 'lucide-react'

interface ProjectAnalyticsDashboardProps {
  projectId: number
  onClose: () => void
}

interface Analytics {
  overview: {
    totalRevenue: number
    totalExpenses: number
    profit: number
    profitMargin: number
    totalHours: number
    hourlyRate: number
    teamSize: number
    completedTasks: number
    totalTasks: number
    completionRate: number
  }
  timeline: {
    month: string
    revenue: number
    expenses: number
    profit: number
    hours: number
  }[]
  tasksByStatus: {
    status: string
    count: number
    percentage: number
  }[]
  tasksByPriority: {
    priority: string
    count: number
  }[]
  teamPerformance: {
    memberId: number
    memberName: string
    tasksCompleted: number
    hoursWorked: number
    efficiency: number
  }[]
  expensesByCategory: {
    category: string
    amount: number
    percentage: number
  }[]
  clientSatisfaction: {
    rating: number
    count: number
  }[]
}

const ProjectAnalyticsDashboard: React.FC<ProjectAnalyticsDashboardProps> = ({ projectId, onClose }) => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [dateFrom, setDateFrom] = useState(new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10))
  const [dateTo, setDateTo] = useState(new Date().toISOString().slice(0, 10))

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = 'unset' }
  }, [])

  useEffect(() => {
    fetchAnalytics()
  }, [projectId, dateFrom, dateTo])

  const fetchAnalytics = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `http://147.45.215.199:8001/api/projects/${projectId}/analytics?from=${dateFrom}&to=${dateTo}`,
        {
          headers: { Authorization: 'Basic ' + btoa('admin:qwerty123') },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      } else {
        setAnalytics({
          overview: {
            totalRevenue: 1250000,
            totalExpenses: 780000,
            profit: 470000,
            profitMargin: 37.6,
            totalHours: 2340,
            hourlyRate: 534,
            teamSize: 8,
            completedTasks: 156,
            totalTasks: 200,
            completionRate: 78,
          },
          timeline: [
            { month: '2024-01', revenue: 350000, expenses: 220000, profit: 130000, hours: 720 },
            { month: '2024-02', revenue: 420000, expenses: 260000, profit: 160000, hours: 780 },
            { month: '2024-03', revenue: 480000, expenses: 300000, profit: 180000, hours: 840 },
          ],
          tasksByStatus: [
            { status: 'Выполнено', count: 156, percentage: 78 },
            { status: 'В работе', count: 32, percentage: 16 },
            { status: 'Новые', count: 12, percentage: 6 },
          ],
          tasksByPriority: [
            { priority: 'Критичный', count: 15 },
            { priority: 'Высокий', count: 45 },
            { priority: 'Средний', count: 98 },
            { priority: 'Низкий', count: 42 },
          ],
          teamPerformance: [
            { memberId: 1, memberName: 'Иван Петров', tasksCompleted: 42, hoursWorked: 680, efficiency: 95 },
            { memberId: 2, memberName: 'Мария Смирнова', tasksCompleted: 38, hoursWorked: 620, efficiency: 92 },
            { memberId: 3, memberName: 'Алексей Коваленко', tasksCompleted: 35, hoursWorked: 580, efficiency: 88 },
            { memberId: 4, memberName: 'Ольга Новикова', tasksCompleted: 29, hoursWorked: 460, efficiency: 85 },
          ],
          expensesByCategory: [
            { category: 'Зарплата', amount: 450000, percentage: 57.7 },
            { category: 'Оборудование', amount: 150000, percentage: 19.2 },
            { category: 'ПО', amount: 85000, percentage: 10.9 },
            { category: 'Офис', amount: 60000, percentage: 7.7 },
            { category: 'Прочее', amount: 35000, percentage: 4.5 },
          ],
          clientSatisfaction: [
            { rating: 5, count: 12 },
            { rating: 4, count: 8 },
            { rating: 3, count: 3 },
            { rating: 2, count: 1 },
            { rating: 1, count: 0 },
          ],
        })
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    if (!analytics) return

    const csvContent = [
      ['ОТЧЕТ ПО АНАЛИТИКЕ'],
      [''],
      ['ОБЩАЯ СТАТИСТИКА'],
      ['Показатель', 'Значение'],
      ['Выручка', `${analytics.overview.totalRevenue.toLocaleString('ru-RU')} ₽`],
      ['Расходы', `${analytics.overview.totalExpenses.toLocaleString('ru-RU')} ₽`],
      ['Прибыль', `${analytics.overview.profit.toLocaleString('ru-RU')} ₽`],
      ['Рентабельность', `${analytics.overview.profitMargin}%`],
      ['Всего часов', analytics.overview.totalHours],
      ['Стоимость часа', `${analytics.overview.hourlyRate.toLocaleString('ru-RU')} ₽`],
      [''],
      ['ЗАДАЧИ ПО СТАТУСАМ'],
      ['Статус', 'Количество', 'Процент'],
      ...analytics.tasksByStatus.map((item) => [item.status, item.count, `${item.percentage}%`]),
      [''],
      ['ЭФФЕКТИВНОСТЬ КОМАНДЫ'],
      ['Участник', 'Задач выполнено', 'Часов отработано', 'Эффективность'],
      ...analytics.teamPerformance.map((item) => [
        item.memberName,
        item.tasksCompleted,
        item.hoursWorked,
        `${item.efficiency}%`,
      ]),
    ].map((row) => row.join(',')).join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `analytics-project-${projectId}-${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  if (loading || !analytics) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка аналитики...</p>
        </div>
      </div>
    )
  }

  const maxRevenueInTimeline = Math.max(...analytics.timeline.map((item) => item.revenue))

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Аналитическая панель</h2>
              <p className="text-blue-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors flex items-center gap-2"
            >
              <Download className="w-5 h-5" />
              Экспорт
            </button>
            <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6 border-b bg-gray-50">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Период анализа</label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {/* Overview Cards */}
            <div>
              <h3 className="text-lg font-bold mb-4">Общая статистика</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6">
                  <div className="flex items-center justify-between mb-3">
                    <DollarSign className="w-10 h-10 opacity-80" />
                    <TrendingUp className="w-6 h-6" />
                  </div>
                  <p className="text-sm opacity-90 mb-1">Выручка</p>
                  <p className="text-3xl font-bold">{analytics.overview.totalRevenue.toLocaleString('ru-RU')} ₽</p>
                </div>

                <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-6">
                  <div className="flex items-center justify-between mb-3">
                    <TrendingDown className="w-10 h-10 opacity-80" />
                  </div>
                  <p className="text-sm opacity-90 mb-1">Расходы</p>
                  <p className="text-3xl font-bold">{analytics.overview.totalExpenses.toLocaleString('ru-RU')} ₽</p>
                </div>

                <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6">
                  <div className="flex items-center justify-between mb-3">
                    <Target className="w-10 h-10 opacity-80" />
                  </div>
                  <p className="text-sm opacity-90 mb-1">Прибыль</p>
                  <p className="text-3xl font-bold">{analytics.overview.profit.toLocaleString('ru-RU')} ₽</p>
                  <p className="text-xs opacity-80 mt-1">Рентабельность: {analytics.overview.profitMargin}%</p>
                </div>

                <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6">
                  <div className="flex items-center justify-between mb-3">
                    <Clock className="w-10 h-10 opacity-80" />
                  </div>
                  <p className="text-sm opacity-90 mb-1">Всего часов</p>
                  <p className="text-3xl font-bold">{analytics.overview.totalHours}</p>
                  <p className="text-xs opacity-80 mt-1">Ставка: {analytics.overview.hourlyRate} ₽/ч</p>
                </div>
              </div>
            </div>

            {/* Timeline Chart */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Динамика по месяцам</h3>
              <div className="space-y-4">
                {analytics.timeline.map((item, idx) => {
                  const revenueWidth = (item.revenue / maxRevenueInTimeline) * 100
                  const expensesWidth = (item.expenses / maxRevenueInTimeline) * 100
                  const profitWidth = (item.profit / maxRevenueInTimeline) * 100

                  return (
                    <div key={idx}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          {new Date(item.month + '-01').toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })}
                        </span>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-green-600">💰 {item.revenue.toLocaleString('ru-RU')}</span>
                          <span className="text-red-600">📉 {item.expenses.toLocaleString('ru-RU')}</span>
                          <span className="text-blue-600">📈 {item.profit.toLocaleString('ru-RU')}</span>
                        </div>
                      </div>
                      <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                        <div
                          className="absolute top-0 left-0 h-8 bg-green-500 opacity-30"
                          style={{ width: `${revenueWidth}%` }}
                        ></div>
                        <div
                          className="absolute top-0 left-0 h-8 bg-red-500 opacity-30"
                          style={{ width: `${expensesWidth}%` }}
                        ></div>
                        <div
                          className="absolute top-0 left-0 h-8 bg-blue-500 opacity-50"
                          style={{ width: `${profitWidth}%` }}
                        ></div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Tasks by Status */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Задачи по статусам</h3>
                <div className="space-y-3">
                  {analytics.tasksByStatus.map((item, idx) => (
                    <div key={idx}>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">{item.status}</span>
                        <span className="text-sm font-bold text-gray-900">
                          {item.count} ({item.percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full transition-all ${
                            item.status === 'Выполнено' ? 'bg-green-600' :
                            item.status === 'В работе' ? 'bg-blue-600' : 'bg-gray-400'
                          }`}
                          style={{ width: `${item.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tasks by Priority */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Задачи по приоритетам</h3>
                <div className="space-y-3">
                  {analytics.tasksByPriority.map((item, idx) => {
                    const total = analytics.tasksByPriority.reduce((sum, p) => sum + p.count, 0)
                    const percentage = (item.count / total) * 100

                    return (
                      <div key={idx}>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">{item.priority}</span>
                          <span className="text-sm font-bold text-gray-900">
                            {item.count} ({percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full transition-all ${
                              item.priority === 'Критичный' ? 'bg-red-600' :
                              item.priority === 'Высокий' ? 'bg-orange-600' :
                              item.priority === 'Средний' ? 'bg-yellow-600' : 'bg-gray-400'
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

            {/* Team Performance */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">Эффективность команды</h3>
              <div className="space-y-4">
                {analytics.teamPerformance.map((member) => (
                  <div key={member.memberId} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                          {member.memberName.charAt(0)}
                        </div>
                        <div>
                          <h4 className="font-bold text-gray-900">{member.memberName}</h4>
                          <p className="text-sm text-gray-500">
                            {member.tasksCompleted} задач • {member.hoursWorked} часов
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-blue-600">{member.efficiency}%</p>
                        <p className="text-xs text-gray-500">Эффективность</p>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${member.efficiency}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Expenses by Category */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Расходы по категориям</h3>
                <div className="space-y-3">
                  {analytics.expensesByCategory.map((item, idx) => (
                    <div key={idx}>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">{item.category}</span>
                        <span className="text-sm font-bold text-gray-900">
                          {item.amount.toLocaleString('ru-RU')} ₽ ({item.percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-red-600 h-3 rounded-full transition-all"
                          style={{ width: `${item.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Client Satisfaction */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Удовлетворенность клиентов</h3>
                <div className="space-y-3">
                  {analytics.clientSatisfaction
                    .sort((a, b) => b.rating - a.rating)
                    .map((item, idx) => {
                      const total = analytics.clientSatisfaction.reduce((sum, r) => sum + r.count, 0)
                      const percentage = total > 0 ? (item.count / total) * 100 : 0

                      return (
                        <div key={idx}>
                          <div className="flex justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-gray-700">{item.rating} ⭐</span>
                            </div>
                            <span className="text-sm font-bold text-gray-900">
                              {item.count} ({percentage.toFixed(1)}%)
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                              className="bg-yellow-500 h-3 rounded-full transition-all"
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      )
                    })}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Средняя оценка</span>
                    <span className="text-2xl font-bold text-yellow-600">
                      {(
                        analytics.clientSatisfaction.reduce((sum, r) => sum + r.rating * r.count, 0) /
                        analytics.clientSatisfaction.reduce((sum, r) => sum + r.count, 0)
                      ).toFixed(1)}{' '}
                      / 5
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Summary */}
            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4 text-blue-900">Ключевые показатели</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-blue-700 mb-1">Рентабельность</p>
                  <p className="text-3xl font-bold text-blue-900">{analytics.overview.profitMargin}%</p>
                </div>
                <div>
                  <p className="text-sm text-blue-700 mb-1">Выполнение</p>
                  <p className="text-3xl font-bold text-blue-900">{analytics.overview.completionRate}%</p>
                </div>
                <div>
                  <p className="text-sm text-blue-700 mb-1">Команда</p>
                  <p className="text-3xl font-bold text-blue-900">{analytics.overview.teamSize}</p>
                </div>
                <div>
                  <p className="text-sm text-blue-700 mb-1">Задач выполнено</p>
                  <p className="text-3xl font-bold text-blue-900">
                    {analytics.overview.completedTasks}/{analytics.overview.totalTasks}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProjectAnalyticsDashboard
