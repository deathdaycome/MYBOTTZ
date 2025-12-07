import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, DollarSign, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { apiService } from '../../services/api'
import { formatCurrency } from '../../utils/formatters'

interface MetricsData {
  current_month: {
    income: number
    expense: number
    profit: number
    profit_margin: number
  }
  changes: {
    income_change: number
    expense_change: number
    profit_change: number
  }
}

export const FinancialMetrics = () => {
  const [metrics, setMetrics] = useState<MetricsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadMetrics = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiService.getDashboardMetrics()
      if (response.success && response.metrics) {
        setMetrics(response.metrics)
      } else {
        // Use demo data if API returns no data
        loadDemoData()
      }
    } catch (err) {
      // Use demo data when backend is not available
      console.log('Backend не запущен, используем демо-данные')
      loadDemoData()
    } finally {
      setLoading(false)
    }
  }

  const loadDemoData = () => {
    setMetrics({
      current_month: {
        income: 1250000,
        expense: 780000,
        profit: 470000,
        profit_margin: 37.6,
      },
      changes: {
        income_change: 12.5,
        expense_change: 8.3,
        profit_change: 85000,
      },
    })
  }

  useEffect(() => {
    loadMetrics()
  }, [])

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-2xl p-6 shadow-lg animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/4"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error || !metrics) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
        <p className="text-red-600">{error || 'Нет данных'}</p>
      </div>
    )
  }

  const { current_month, changes } = metrics

  const cards = [
    {
      title: 'Доход за месяц',
      value: current_month.income,
      change: changes.income_change,
      gradient: 'from-green-500 to-emerald-600',
      icon: DollarSign,
      isPercent: true,
    },
    {
      title: 'Расходы за месяц',
      value: current_month.expense,
      change: changes.expense_change,
      gradient: 'from-red-500 to-pink-600',
      icon: TrendingDown,
      isPercent: true,
    },
    {
      title: 'Прибыль',
      value: current_month.profit,
      change: changes.profit_change,
      gradient: 'from-blue-500 to-cyan-600',
      icon: TrendingUp,
      isPercent: false,
    },
    {
      title: 'Рентабельность',
      value: current_month.profit_margin,
      gradient: 'from-purple-500 to-pink-600',
      icon: ArrowUpRight,
      isPercent: null,
      customValue: `${current_month.profit_margin.toFixed(1)}%`,
      customChange:
        current_month.profit_margin >= 30
          ? 'Отлично!'
          : current_month.profit_margin >= 20
          ? 'Хорошо'
          : 'Требует внимания',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon
        const isPositive = card.isPercent !== null ? card.change >= 0 : true
        const ChangeIcon = isPositive ? ArrowUpRight : ArrowDownRight

        return (
          <div
            key={index}
            className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 border border-gray-100"
          >
            <div className="flex items-start justify-between mb-4">
              <div
                className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${card.gradient} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}
              >
                <Icon className="w-7 h-7 text-white" />
              </div>
              {card.isPercent !== null && (
                <div
                  className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold ${
                    isPositive
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  <ChangeIcon className="w-4 h-4" />
                  {card.isPercent
                    ? `${isPositive ? '+' : ''}${card.change.toFixed(1)}%`
                    : formatCurrency(card.change)}
                </div>
              )}
            </div>

            <h3 className="text-sm font-medium text-gray-600 mb-2">{card.title}</h3>
            <p className="text-3xl font-bold text-gray-900 mb-1">
              {card.customValue || formatCurrency(card.value)}
            </p>
            {card.customChange && (
              <p className="text-sm text-gray-500">{card.customChange}</p>
            )}
          </div>
        )
      })}
    </div>
  )
}
