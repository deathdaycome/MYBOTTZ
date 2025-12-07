import { useState, useEffect } from 'react'
import {
  X,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  Users,
  CheckCircle,
  AlertCircle,
  Calendar,
  DollarSign,
} from 'lucide-react'

interface PerformanceMetric {
  name: string
  value: number
  target: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  trendValue: number
  icon: any
  color: string
}

interface TimelineData {
  date: string
  completedTasks: number
  plannedTasks: number
  hoursSpent: number
  hoursPlanned: number
}

interface TeamMemberPerformance {
  id: number
  name: string
  tasksCompleted: number
  tasksAssigned: number
  hoursWorked: number
  efficiency: number
}

interface PerformanceAnalyticsProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

export const PerformanceAnalytics = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: PerformanceAnalyticsProps) => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([])
  const [timeline, setTimeline] = useState<TimelineData[]>([])
  const [teamPerformance, setTeamPerformance] = useState<TeamMemberPerformance[]>([])
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'quarter'>('month')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && projectId) {
      loadAnalytics()
    }
  }, [isOpen, projectId, selectedPeriod])

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

  const loadAnalytics = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/analytics?period=${selectedPeriod}`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setMetrics(data.metrics || [])
        setTimeline(data.timeline || [])
        setTeamPerformance(data.teamPerformance || [])
      } else {
        // Mock data
        setMetrics([
          {
            name: 'Завершено задач',
            value: 42,
            target: 50,
            unit: 'шт',
            trend: 'up',
            trendValue: 12,
            icon: CheckCircle,
            color: '#10B981',
          },
          {
            name: 'Затрачено времени',
            value: 245,
            target: 280,
            unit: 'ч',
            trend: 'stable',
            trendValue: 0,
            icon: Clock,
            color: '#3B82F6',
          },
          {
            name: 'Выполнено в срок',
            value: 85,
            target: 90,
            unit: '%',
            trend: 'up',
            trendValue: 5,
            icon: Target,
            color: '#8B5CF6',
          },
          {
            name: 'Производительность',
            value: 92,
            target: 100,
            unit: '%',
            trend: 'down',
            trendValue: -3,
            icon: TrendingUp,
            color: '#F59E0B',
          },
          {
            name: 'Активных участников',
            value: 8,
            target: 10,
            unit: 'чел',
            trend: 'stable',
            trendValue: 0,
            icon: Users,
            color: '#EC4899',
          },
          {
            name: 'Бюджет использован',
            value: 67,
            target: 100,
            unit: '%',
            trend: 'up',
            trendValue: 8,
            icon: DollarSign,
            color: '#14B8A6',
          },
        ])

        setTimeline([
          {
            date: '2025-01-20',
            completedTasks: 8,
            plannedTasks: 10,
            hoursSpent: 45,
            hoursPlanned: 50,
          },
          {
            date: '2025-01-21',
            completedTasks: 7,
            plannedTasks: 8,
            hoursSpent: 38,
            hoursPlanned: 40,
          },
          {
            date: '2025-01-22',
            completedTasks: 9,
            plannedTasks: 12,
            hoursSpent: 52,
            hoursPlanned: 60,
          },
          {
            date: '2025-01-23',
            completedTasks: 6,
            plannedTasks: 7,
            hoursSpent: 35,
            hoursPlanned: 35,
          },
          {
            date: '2025-01-24',
            completedTasks: 12,
            plannedTasks: 13,
            hoursSpent: 75,
            hoursPlanned: 65,
          },
        ])

        setTeamPerformance([
          {
            id: 1,
            name: 'Иван Иванов',
            tasksCompleted: 15,
            tasksAssigned: 18,
            hoursWorked: 92,
            efficiency: 95,
          },
          {
            id: 2,
            name: 'Мария Петрова',
            tasksCompleted: 12,
            tasksAssigned: 14,
            hoursWorked: 78,
            efficiency: 88,
          },
          {
            id: 3,
            name: 'Алексей Сидоров',
            tasksCompleted: 10,
            tasksAssigned: 12,
            hoursWorked: 65,
            efficiency: 92,
          },
          {
            id: 4,
            name: 'Елена Козлова',
            tasksCompleted: 5,
            tasksAssigned: 6,
            hoursWorked: 30,
            efficiency: 78,
          },
        ])
      }
    } catch (err) {
      console.error('Error loading analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
    }).format(date)
  }

  const getProgressColor = (value: number, target: number): string => {
    const percent = (value / target) * 100
    if (percent >= 90) return 'bg-green-500'
    if (percent >= 70) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') return <TrendingUp className="w-4 h-4" />
    if (trend === 'down') return <TrendingDown className="w-4 h-4" />
    return <span className="w-4 h-4 inline-block" />
  }

  const getTrendColor = (trend: string): string => {
    if (trend === 'up') return 'text-green-600'
    if (trend === 'down') return 'text-red-600'
    return 'text-gray-600'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-7xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Аналитика производительности</h3>
              <p className="text-blue-100 text-sm mt-1">{projectName}</p>
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

        {/* Period Selector */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
          <div className="flex gap-2">
            <button
              onClick={() => setSelectedPeriod('week')}
              className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                selectedPeriod === 'week'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Неделя
            </button>
            <button
              onClick={() => setSelectedPeriod('month')}
              className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                selectedPeriod === 'month'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Месяц
            </button>
            <button
              onClick={() => setSelectedPeriod('quarter')}
              className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                selectedPeriod === 'quarter'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Квартал
            </button>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Calendar className="w-4 h-4" />
            <span>Обновлено: {new Date().toLocaleDateString('ru-RU')}</span>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Загрузка аналитики...</div>
          ) : (
            <>
              {/* Key Metrics */}
              <div>
                <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Target className="w-5 h-5 text-blue-600" />
                  Ключевые показатели
                </h4>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {metrics.map((metric, index) => {
                    const Icon = metric.icon
                    const progressPercent = (metric.value / metric.target) * 100

                    return (
                      <div
                        key={index}
                        className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-blue-400 transition-all"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center text-white"
                            style={{ backgroundColor: metric.color }}
                          >
                            <Icon className="w-5 h-5" />
                          </div>

                          <div className={`flex items-center gap-1 ${getTrendColor(metric.trend)}`}>
                            {getTrendIcon(metric.trend)}
                            {metric.trendValue !== 0 && (
                              <span className="text-xs font-bold">
                                {metric.trendValue > 0 ? '+' : ''}
                                {metric.trendValue}
                                {metric.unit === '%' ? '%' : ''}
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="text-xs text-gray-600 mb-1">{metric.name}</div>
                        <div className="text-2xl font-bold text-gray-900 mb-1">
                          {metric.value} {metric.unit}
                        </div>
                        <div className="text-xs text-gray-500 mb-2">
                          Цель: {metric.target} {metric.unit}
                        </div>

                        {/* Progress Bar */}
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all ${getProgressColor(
                              metric.value,
                              metric.target
                            )}`}
                            style={{ width: `${Math.min(progressPercent, 100)}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Timeline Chart */}
              <div>
                <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  Динамика выполнения задач
                </h4>

                <div className="bg-white border-2 border-gray-200 rounded-xl p-6">
                  <div className="space-y-4">
                    {timeline.map((day, index) => {
                      const completionRate = (day.completedTasks / day.plannedTasks) * 100
                      const hoursRate = (day.hoursSpent / day.hoursPlanned) * 100

                      return (
                        <div key={index} className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="font-semibold text-gray-700">
                              {formatDate(day.date)}
                            </span>
                            <div className="flex items-center gap-4 text-xs text-gray-600">
                              <span>
                                Задачи: {day.completedTasks}/{day.plannedTasks}
                              </span>
                              <span>
                                Часы: {day.hoursSpent}/{day.hoursPlanned}
                              </span>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-2">
                            {/* Tasks Bar */}
                            <div>
                              <div className="h-8 bg-gray-200 rounded-lg overflow-hidden relative">
                                <div
                                  className="h-full bg-blue-500 transition-all flex items-center justify-center text-xs font-bold text-white"
                                  style={{ width: `${Math.min(completionRate, 100)}%` }}
                                >
                                  {completionRate >= 30 && `${completionRate.toFixed(0)}%`}
                                </div>
                                {completionRate < 30 && (
                                  <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-gray-600">
                                    {completionRate.toFixed(0)}%
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Hours Bar */}
                            <div>
                              <div className="h-8 bg-gray-200 rounded-lg overflow-hidden relative">
                                <div
                                  className="h-full bg-purple-500 transition-all flex items-center justify-center text-xs font-bold text-white"
                                  style={{ width: `${Math.min(hoursRate, 100)}%` }}
                                >
                                  {hoursRate >= 30 && `${hoursRate.toFixed(0)}%`}
                                </div>
                                {hoursRate < 30 && (
                                  <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-gray-600">
                                    {hoursRate.toFixed(0)}%
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200 flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-500 rounded"></div>
                      <span>Выполнение задач</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-purple-500 rounded"></div>
                      <span>Использование времени</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Team Performance */}
              <div>
                <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-green-600" />
                  Производительность команды
                </h4>

                <div className="bg-white border-2 border-gray-200 rounded-xl overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700">
                          Участник
                        </th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700">
                          Задачи
                        </th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700">
                          Завершено
                        </th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700">
                          Часы
                        </th>
                        <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700">
                          Эффективность
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {teamPerformance.map((member) => {
                        const completionRate =
                          (member.tasksCompleted / member.tasksAssigned) * 100

                        return (
                          <tr key={member.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-xs">
                                  {member.name[0]}
                                </div>
                                <span className="font-semibold text-gray-900 text-sm">
                                  {member.name}
                                </span>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-center text-sm text-gray-700">
                              {member.tasksAssigned}
                            </td>
                            <td className="px-4 py-3 text-center">
                              <div className="flex flex-col items-center">
                                <span className="text-sm font-bold text-gray-900">
                                  {member.tasksCompleted}
                                </span>
                                <span
                                  className={`text-xs font-semibold ${
                                    completionRate >= 90
                                      ? 'text-green-600'
                                      : completionRate >= 70
                                        ? 'text-yellow-600'
                                        : 'text-red-600'
                                  }`}
                                >
                                  {completionRate.toFixed(0)}%
                                </span>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-center text-sm text-gray-700">
                              {member.hoursWorked}ч
                            </td>
                            <td className="px-4 py-3 text-center">
                              <div className="flex items-center justify-center gap-2">
                                <div className="flex-1 max-w-[100px] h-2 bg-gray-200 rounded-full overflow-hidden">
                                  <div
                                    className={`h-full ${getProgressColor(
                                      member.efficiency,
                                      100
                                    )} transition-all`}
                                    style={{ width: `${member.efficiency}%` }}
                                  />
                                </div>
                                <span className="text-sm font-bold text-gray-900 w-10">
                                  {member.efficiency}%
                                </span>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end flex-shrink-0">
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
