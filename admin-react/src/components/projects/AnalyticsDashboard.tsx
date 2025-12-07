import { BarChart3, TrendingUp, DollarSign, Users, CheckCircle } from 'lucide-react'

interface AnalyticsDashboardProps {
  projects: any[]
}

export const AnalyticsDashboard = ({ projects }: AnalyticsDashboardProps) => {
  // Calculate statistics
  const stats = calculateStatistics(projects)

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<BarChart3 className="w-6 h-6" />}
          label="Всего проектов"
          value={stats.totalProjects}
          color="blue"
        />
        <StatCard
          icon={<DollarSign className="w-6 h-6" />}
          label="Общая стоимость"
          value={`${stats.totalCost.toLocaleString('ru-RU')} ₽`}
          color="green"
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6" />}
          label="Общая прибыль"
          value={`${stats.totalProfit.toLocaleString('ru-RU')} ₽`}
          color="purple"
        />
        <StatCard
          icon={<CheckCircle className="w-6 h-6" />}
          label="Полностью оплачено"
          value={stats.fullyPaidCount}
          color="emerald"
        />
      </div>

      {/* Status Distribution */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-indigo-600" />
          Распределение по статусам
        </h3>
        <div className="space-y-3">
          {Object.entries(stats.statusDistribution).map(([status, count]) => {
            const percentage = (count / stats.totalProjects) * 100
            return (
              <div key={status}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">{status || 'Без статуса'}</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {count} ({percentage.toFixed(0)}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2.5 rounded-full transition-all duration-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Executor Performance */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-blue-600" />
          Производительность исполнителей
        </h3>
        <div className="space-y-4">
          {stats.executorStats.slice(0, 5).map((executor) => (
            <div key={executor.name} className="border-l-4 border-blue-500 pl-4 py-2">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-gray-900">{executor.name}</span>
                <span className="text-sm text-gray-600">{executor.projectCount} проектов</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <span className="text-gray-500">Стоимость:</span>
                  <span className="ml-1 font-semibold text-blue-600">
                    {executor.totalCost.toLocaleString('ru-RU')} ₽
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Прибыль:</span>
                  <span className="ml-1 font-semibold text-purple-600">
                    {executor.totalProfit.toLocaleString('ru-RU')} ₽
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Средняя:</span>
                  <span className="ml-1 font-semibold text-green-600">
                    {Math.round(executor.totalProfit / executor.projectCount).toLocaleString('ru-RU')} ₽
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Payment Status */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-green-600" />
          Статус оплаты
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4">
            <div className="text-xs text-red-600 font-semibold mb-1">Не оплачено</div>
            <div className="text-2xl font-bold text-red-900">{stats.paymentStatus.unpaid}</div>
            <div className="text-xs text-red-600 mt-1">
              {((stats.paymentStatus.unpaid / stats.totalProjects) * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-lg p-4">
            <div className="text-xs text-yellow-600 font-semibold mb-1">Частично оплачено</div>
            <div className="text-2xl font-bold text-yellow-900">{stats.paymentStatus.partial}</div>
            <div className="text-xs text-yellow-600 mt-1">
              {((stats.paymentStatus.partial / stats.totalProjects) * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4">
            <div className="text-xs text-green-600 font-semibold mb-1">Полностью оплачено</div>
            <div className="text-2xl font-bold text-green-900">{stats.paymentStatus.paid}</div>
            <div className="text-xs text-green-600 mt-1">
              {((stats.paymentStatus.paid / stats.totalProjects) * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>

      {/* Financial Summary */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl shadow-lg p-6 text-white">
        <h3 className="text-lg font-bold mb-4">Финансовая сводка</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-indigo-200 mb-1">Общая стоимость</div>
            <div className="text-xl font-bold">{stats.totalCost.toLocaleString('ru-RU')} ₽</div>
          </div>
          <div>
            <div className="text-xs text-indigo-200 mb-1">Оплачено</div>
            <div className="text-xl font-bold">{stats.totalPaid.toLocaleString('ru-RU')} ₽</div>
          </div>
          <div>
            <div className="text-xs text-indigo-200 mb-1">Исполнителям</div>
            <div className="text-xl font-bold">{stats.totalExecutorCost.toLocaleString('ru-RU')} ₽</div>
          </div>
          <div>
            <div className="text-xs text-indigo-200 mb-1">Прибыль</div>
            <div className="text-xl font-bold">{stats.totalProfit.toLocaleString('ru-RU')} ₽</div>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-indigo-400">
          <div className="flex items-center justify-between text-sm">
            <span>Средняя прибыль на проект:</span>
            <span className="font-bold">
              {Math.round(stats.totalProfit / stats.totalProjects || 0).toLocaleString('ru-RU')} ₽
            </span>
          </div>
          <div className="flex items-center justify-between text-sm mt-2">
            <span>Процент прибыли:</span>
            <span className="font-bold">
              {((stats.totalProfit / stats.totalCost) * 100 || 0).toFixed(1)}%
            </span>
          </div>
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
  value: string | number
  color: 'blue' | 'green' | 'purple' | 'emerald'
}) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    emerald: 'from-emerald-500 to-emerald-600',
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${colorClasses[color]} text-white mb-4`}>
        {icon}
      </div>
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
    </div>
  )
}

const calculateStatistics = (projects: any[]) => {
  const totalProjects = projects.length
  const totalCost = projects.reduce((sum, p) => sum + (p.project_cost || 0), 0)
  const totalPaid = projects.reduce((sum, p) => sum + (p.paid_total || 0), 0)
  const totalExecutorCost = projects.reduce((sum, p) => sum + (p.executor_cost || 0), 0)
  const totalProfit = totalCost - totalExecutorCost

  // Status distribution
  const statusDistribution: Record<string, number> = {}
  projects.forEach((p) => {
    const status = p.status || 'Без статуса'
    statusDistribution[status] = (statusDistribution[status] || 0) + 1
  })

  // Payment status
  const paymentStatus = {
    unpaid: 0,
    partial: 0,
    paid: 0,
  }

  projects.forEach((p) => {
    const paid = p.paid_total || 0
    const cost = p.project_cost || 0
    if (paid === 0) {
      paymentStatus.unpaid++
    } else if (paid < cost) {
      paymentStatus.partial++
    } else {
      paymentStatus.paid++
    }
  })

  // Executor stats
  const executorMap: Record<
    string,
    { name: string; projectCount: number; totalCost: number; totalProfit: number }
  > = {}

  projects.forEach((p) => {
    if (p.assigned_to) {
      const name = p.assigned_to.username || p.assigned_to.first_name || 'Без имени'
      if (!executorMap[name]) {
        executorMap[name] = { name, projectCount: 0, totalCost: 0, totalProfit: 0 }
      }
      executorMap[name].projectCount++
      executorMap[name].totalCost += p.project_cost || 0
      executorMap[name].totalProfit += (p.project_cost || 0) - (p.executor_cost || 0)
    }
  })

  const executorStats = Object.values(executorMap).sort((a, b) => b.totalProfit - a.totalProfit)

  return {
    totalProjects,
    totalCost,
    totalPaid,
    totalExecutorCost,
    totalProfit,
    fullyPaidCount: paymentStatus.paid,
    statusDistribution,
    paymentStatus,
    executorStats,
  }
}
