import { Users, FolderKanban, MessageSquare, DollarSign } from 'lucide-react'
import { formatCurrency, formatNumber } from '../../utils/formatters'

interface StatisticsData {
  total_users?: number
  total_projects?: number
  consultations?: number
  revenue?: number
}

interface StatisticsCardsProps {
  data?: StatisticsData
}

export const StatisticsCards = ({ data }: StatisticsCardsProps) => {
  const stats = data || {
    total_users: 156,
    total_projects: 42,
    consultations: 28,
    revenue: 1250000,
  }

  const cards = [
    {
      title: 'Всего пользователей',
      value: formatNumber(stats.total_users || 0),
      icon: Users,
      gradient: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Всего проектов',
      value: formatNumber(stats.total_projects || 0),
      icon: FolderKanban,
      gradient: 'from-purple-500 to-pink-500',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Консультации',
      value: formatNumber(stats.consultations || 0),
      icon: MessageSquare,
      gradient: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Выручка',
      value: formatCurrency(stats.revenue || 0),
      icon: DollarSign,
      gradient: 'from-orange-500 to-red-500',
      bgColor: 'bg-orange-50',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon

        return (
          <div
            key={index}
            className={`${card.bgColor} rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition-all duration-300 hover:-translate-y-1`}
          >
            <div className="flex items-center justify-between mb-4">
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.gradient} flex items-center justify-center shadow-md`}
              >
                <Icon className="w-6 h-6 text-white" />
              </div>
            </div>

            <h3 className="text-sm font-medium text-gray-600 mb-1">{card.title}</h3>
            <p className="text-2xl font-bold text-gray-900">{card.value}</p>
          </div>
        )
      })}
    </div>
  )
}
