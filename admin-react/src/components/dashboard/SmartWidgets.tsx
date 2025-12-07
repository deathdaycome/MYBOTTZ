import { TrendingUp, Clock, Users, AlertCircle } from 'lucide-react'

export const SmartWidgets = () => {
  // Demo data - replace with API when backend is ready
  const salesFunnel = {
    leads: 45,
    contacted: 32,
    proposals: 18,
    closed: 12,
  }

  const financialForecast = {
    current: 1250000,
    forecast: 1450000,
    growth: 16,
  }

  const urgentProjects = [
    { name: 'Редизайн сайта', deadline: '2 дня', status: 'critical' },
    { name: 'Мобильное приложение', deadline: '5 дней', status: 'warning' },
  ]

  const activeExecutors = {
    total: 8,
    working: 6,
    free: 2,
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Sales Funnel */}
      <div className="bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl p-6 text-white shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold">Воронка продаж</h3>
          <TrendingUp className="w-5 h-5 opacity-80" />
        </div>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm opacity-90">Лиды</span>
            <span className="font-bold">{salesFunnel.leads}</span>
          </div>
          <div className="h-2 bg-white/20 rounded-full overflow-hidden">
            <div className="h-full bg-white rounded-full" style={{ width: '100%' }} />
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm opacity-90">Контакт</span>
            <span className="font-bold">{salesFunnel.contacted}</span>
          </div>
          <div className="h-2 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-white rounded-full"
              style={{ width: `${(salesFunnel.contacted / salesFunnel.leads) * 100}%` }}
            />
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm opacity-90">Предложения</span>
            <span className="font-bold">{salesFunnel.proposals}</span>
          </div>
          <div className="h-2 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-white rounded-full"
              style={{ width: `${(salesFunnel.proposals / salesFunnel.leads) * 100}%` }}
            />
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm opacity-90">Закрыто</span>
            <span className="font-bold">{salesFunnel.closed}</span>
          </div>
          <div className="h-2 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-white rounded-full"
              style={{ width: `${(salesFunnel.closed / salesFunnel.leads) * 100}%` }}
            />
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-white/20">
          <p className="text-sm opacity-90">
            Конверсия: <span className="font-bold">{((salesFunnel.closed / salesFunnel.leads) * 100).toFixed(1)}%</span>
          </p>
        </div>
      </div>

      {/* Financial Forecast */}
      <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-6 text-white shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold">Финансовый прогноз</h3>
          <TrendingUp className="w-5 h-5 opacity-80" />
        </div>
        <div className="space-y-4">
          <div>
            <p className="text-sm opacity-90 mb-1">Текущая выручка</p>
            <p className="text-2xl font-bold">{(financialForecast.current / 1000000).toFixed(1)}М ₽</p>
          </div>
          <div className="h-px bg-white/20" />
          <div>
            <p className="text-sm opacity-90 mb-1">Прогноз на месяц</p>
            <p className="text-2xl font-bold">{(financialForecast.forecast / 1000000).toFixed(1)}М ₽</p>
          </div>
          <div className="h-px bg-white/20" />
          <div className="flex items-center justify-between">
            <span className="text-sm opacity-90">Рост</span>
            <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-full">
              <TrendingUp className="w-4 h-4" />
              <span className="font-bold">+{financialForecast.growth}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Urgent Projects */}
      <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl p-6 text-white shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold">Срочные проекты</h3>
          <AlertCircle className="w-5 h-5 opacity-80" />
        </div>
        <div className="space-y-3">
          {urgentProjects.map((project, index) => (
            <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-3">
              <div className="flex items-start justify-between mb-2">
                <p className="font-semibold text-sm">{project.name}</p>
                <Clock className="w-4 h-4 opacity-80 flex-shrink-0" />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs opacity-90">Дедлайн:</span>
                <span className="text-xs font-bold bg-white/20 px-2 py-1 rounded">
                  {project.deadline}
                </span>
              </div>
            </div>
          ))}
          {urgentProjects.length === 0 && (
            <div className="text-center py-8 opacity-60">
              <p className="text-sm">Нет срочных проектов</p>
            </div>
          )}
        </div>
        <div className="mt-4">
          <button className="w-full bg-white/20 hover:bg-white/30 backdrop-blur-sm px-4 py-2 rounded-xl font-semibold text-sm transition-all">
            Все проекты
          </button>
        </div>
      </div>

      {/* Active Executors */}
      <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl p-6 text-white shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold">Активные исполнители</h3>
          <Users className="w-5 h-5 opacity-80" />
        </div>
        <div className="text-center mb-6">
          <p className="text-5xl font-bold mb-2">{activeExecutors.working}</p>
          <p className="text-sm opacity-90">из {activeExecutors.total} работают</p>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between bg-white/10 backdrop-blur-sm rounded-xl p-3">
            <span className="text-sm">В работе</span>
            <span className="font-bold">{activeExecutors.working}</span>
          </div>
          <div className="flex items-center justify-between bg-white/10 backdrop-blur-sm rounded-xl p-3">
            <span className="text-sm">Свободны</span>
            <span className="font-bold">{activeExecutors.free}</span>
          </div>
        </div>
        <div className="mt-4">
          <div className="h-2 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-white rounded-full transition-all duration-500"
              style={{ width: `${(activeExecutors.working / activeExecutors.total) * 100}%` }}
            />
          </div>
          <p className="text-xs text-center mt-2 opacity-80">
            Загрузка: {((activeExecutors.working / activeExecutors.total) * 100).toFixed(0)}%
          </p>
        </div>
      </div>
    </div>
  )
}
