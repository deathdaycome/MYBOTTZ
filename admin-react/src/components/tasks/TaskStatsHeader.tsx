import {
  ListTodo,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Flame,
  AlertCircle,
} from 'lucide-react'
import type { TaskStats } from '../../api/tasks'

interface TaskStatsHeaderProps {
  stats: TaskStats
}

export const TaskStatsHeader = ({ stats }: TaskStatsHeaderProps) => {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-lg font-bold text-gray-900 mb-4">Статистика задач</h2>

      {/* Main stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        <StatCard
          icon={<ListTodo className="w-5 h-5" />}
          label="Всего задач"
          value={stats.total_tasks}
          color="blue"
        />
        <StatCard
          icon={<Clock className="w-5 h-5" />}
          label="Новые"
          value={stats.pending_tasks}
          color="indigo"
        />
        <StatCard
          icon={<TrendingUp className="w-5 h-5" />}
          label="В работе"
          value={stats.in_progress_tasks}
          color="yellow"
        />
        <StatCard
          icon={<CheckCircle className="w-5 h-5" />}
          label="Завершено"
          value={stats.completed_tasks}
          color="green"
        />
        <StatCard
          icon={<AlertTriangle className="w-5 h-5" />}
          label="Просрочено"
          value={stats.overdue_tasks}
          color="red"
        />
        <StatCard
          icon={<Flame className="w-5 h-5" />}
          label="Сегодня"
          value={stats.today_tasks}
          color="orange"
        />
      </div>

      {/* Priority stats */}
      <div className="border-t border-gray-200 pt-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">По приоритетам</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <PriorityCard
            label="Срочные"
            value={stats.priority_stats.urgent}
            color="red"
            icon={<AlertCircle className="w-4 h-4" />}
          />
          <PriorityCard
            label="Высокие"
            value={stats.priority_stats.high}
            color="orange"
            icon={<AlertTriangle className="w-4 h-4" />}
          />
          <PriorityCard
            label="Обычные"
            value={stats.priority_stats.normal}
            color="blue"
            icon={<ListTodo className="w-4 h-4" />}
          />
          <PriorityCard
            label="Низкие"
            value={stats.priority_stats.low}
            color="gray"
            icon={<Clock className="w-4 h-4" />}
          />
        </div>
      </div>
    </div>
  )
}

const StatCard = ({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: number
  color: 'blue' | 'indigo' | 'yellow' | 'green' | 'red' | 'orange'
}) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    indigo: 'from-indigo-500 to-indigo-600',
    yellow: 'from-yellow-500 to-yellow-600',
    green: 'from-green-500 to-green-600',
    red: 'from-red-500 to-red-600',
    orange: 'from-orange-500 to-orange-600',
  }

  return (
    <div className="flex items-center gap-3">
      <div className={`p-3 rounded-lg bg-gradient-to-r ${colorClasses[color]} text-white`}>
        {icon}
      </div>
      <div>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="text-xs text-gray-600">{label}</div>
      </div>
    </div>
  )
}

const PriorityCard = ({
  label,
  value,
  color,
  icon,
}: {
  label: string
  value: number
  color: 'red' | 'orange' | 'blue' | 'gray'
  icon: React.ReactNode
}) => {
  const colorClasses = {
    red: 'bg-red-50 border-red-200 text-red-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    gray: 'bg-gray-50 border-gray-200 text-gray-700',
  }

  return (
    <div className={`flex items-center gap-2 p-3 rounded-lg border ${colorClasses[color]}`}>
      {icon}
      <div className="flex-1">
        <div className="text-sm font-medium">{label}</div>
        <div className="text-lg font-bold">{value}</div>
      </div>
    </div>
  )
}
