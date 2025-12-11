import { useState, useEffect } from 'react'
import axiosInstance from '../services/api'
import { useNavigate } from 'react-router-dom'
import MagicBento, { type BentoCardProps } from '../components/common/MagicBentoNew'
import BlurText from '../components/effects/BlurText'
import {
  FolderKanban,
  CheckSquare,
  Users,
  DollarSign,
  TrendingUp,
  Clock,
  AlertCircle,
  Activity,
  FileText,
  Zap
} from 'lucide-react'
import { API_BASE_URL } from '../config'

// Интерфейсы для нового API dashboard/stats
interface DashboardData {
  user: {
    id: number
    username: string
    role: 'owner' | 'teamlead' | 'executor'
    full_name?: string
  }
  greeting: {
    title: string
    subtitle: string
  }
  summary: {
    active_projects?: number
    active_clients?: number
    month_revenue?: number
    projects_in_work?: number
    overdue_tasks?: number
    tasks_today?: number
  }
  projects: Array<{
    id: number
    title: string
    client_name?: string
    status: string
    deadline?: string
    progress: number
  }>
  tasks: {
    overdue: Array<{
      id: number
      title: string
      deadline: string
      priority: string
      status: string
      executor_name?: string
    }>
    upcoming: Array<{
      id: number
      title: string
      deadline: string
      priority: string
      status: string
      executor_name?: string
    }>
    new: Array<{
      id: number
      title: string
      created_at: string
      priority: string
      status: string
      executor_name?: string
    }>
  }
  clients: {
    active_count: number
    new_leads_week: number
    recent: Array<{
      id: number
      name: string
      contact?: string
      created_at: string
    }>
  }
  finance: {
    month_revenue: number
    paid: number
    pending: number
    overdue: number
  }
  alerts: Array<{
    type: string
    message: string
    level: 'warning' | 'error' | 'info'
    count?: number
    link?: string
  }>
  documents: Array<{
    id: number
    filename: string
    uploaded_at: string
    project_title?: string
    uploader_name?: string
  }>
  activity: Array<{
    user: string
    action: string
    text: string[]
    target: string
    time_ago: string
    timestamp: string
  }>
  quick_actions: Array<{
    id: string
    label: string
    link: string
    icon: string
  }>
  charts?: {
    tasks_by_status: Record<string, number>
    projects_distribution: Record<string, number>
  }
}

// Старый интерфейс для совместимости с MagicBento
interface DashboardStats {
  projects: {
    total: number
    active: number
    completed: number
  }
  tasks: {
    total: number
    pending: number
    completed: number
  }
  clients: {
    total: number
    active: number
  }
  finance: {
    totalRevenue: number
    pending: number
    received: number
  }
}

// Helper Components
interface TaskItemProps {
  title: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high'
  deadline: string
}

const TaskItem = ({ title, status, priority, deadline }: TaskItemProps) => {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    in_progress: 'bg-blue-100 text-blue-800 border-blue-300',
    completed: 'bg-green-100 text-green-800 border-green-300'
  }

  const priorityColors = {
    low: 'text-gray-500',
    medium: 'text-orange-600',
    high: 'text-red-600'
  }

  const statusLabels = {
    pending: 'Ожидает',
    in_progress: 'В работе',
    completed: 'Завершено'
  }

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-200 hover:border-purple-300 transition-all cursor-pointer group shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-gray-900 font-normal mb-2 group-hover:text-purple-600 transition-colors text-sm">
            {title}
          </h3>
          <div className="flex items-center gap-3 flex-wrap">
            <span className={`text-xs px-2 py-1 rounded-full border ${statusColors[status]}`}>
              {statusLabels[status]}
            </span>
            <div className="flex items-center gap-1">
              <AlertCircle className={`w-3 h-3 ${priorityColors[priority]}`} />
              <span className={`text-xs ${priorityColors[priority]}`}>
                {priority === 'high' ? 'Высокий' : priority === 'medium' ? 'Средний' : 'Низкий'}
              </span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-1 text-gray-600">
            <Clock className="w-3 h-3" />
            <span className="text-xs">{deadline}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

interface ActivityItemProps {
  user: string
  action: string
  item: string
  time: string
  avatar: string
  color: 'purple' | 'pink' | 'blue' | 'green'
}

const ActivityItem = ({ user, action, item, time, avatar, color }: ActivityItemProps) => {
  const avatarColors = {
    purple: 'bg-purple-100 text-purple-700 border-purple-200',
    pink: 'bg-pink-100 text-pink-700 border-pink-200',
    blue: 'bg-blue-100 text-blue-700 border-blue-200',
    green: 'bg-green-100 text-green-700 border-green-200'
  }

  return (
    <div className="flex items-start gap-3 group">
      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-medium text-sm flex-shrink-0 border ${avatarColors[color]}`}>
        {avatar}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900 font-normal">
          <span className="font-medium">{user}</span>{' '}
          <span className="text-gray-600">{action}</span>
        </p>
        <p className="text-sm text-gray-600 truncate">{item}</p>
        <p className="text-xs text-gray-500 mt-1">{time}</p>
      </div>
    </div>
  )
}

interface ProjectCardProps {
  title: string
  client: string
  progress: number
  status: 'in_progress' | 'completed' | 'on_hold'
  deadline: string
}

const ProjectCard = ({ title, client, progress, status, deadline }: ProjectCardProps) => {
  const statusColors = {
    in_progress: 'bg-blue-100 text-blue-800 border-blue-300',
    completed: 'bg-green-100 text-green-800 border-green-300',
    on_hold: 'bg-orange-100 text-orange-800 border-orange-300'
  }

  const statusLabels = {
    in_progress: 'В работе',
    completed: 'Завершено',
    on_hold: 'Приостановлено'
  }

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-200 hover:border-purple-300 transition-all cursor-pointer group shadow-sm">
      <div className="mb-3">
        <h3 className="text-gray-900 font-normal mb-1 group-hover:text-purple-600 transition-colors text-sm">
          {title}
        </h3>
        <p className="text-xs text-gray-600">{client}</p>
      </div>

      <div className="mb-3">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-600">Прогресс</span>
          <span className="text-xs text-gray-900 font-medium">{progress}%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <span className={`text-xs px-2 py-1 rounded-full border ${statusColors[status]}`}>
          {statusLabels[status]}
        </span>
        <div className="flex items-center gap-1 text-gray-600">
          <Clock className="w-3 h-3" />
          <span className="text-xs">{deadline}</span>
        </div>
      </div>
    </div>
  )
}

interface QuickActionButtonProps {
  icon: React.ReactNode
  text: string
  onClick: () => void
  color: 'purple' | 'pink' | 'blue' | 'green'
}

const QuickActionButton = ({ icon, text, onClick, color }: QuickActionButtonProps) => {
  const colorClasses = {
    purple: 'hover:bg-purple-50 hover:border-purple-300 text-purple-700',
    pink: 'hover:bg-pink-50 hover:border-pink-300 text-pink-700',
    blue: 'hover:bg-blue-50 hover:border-blue-300 text-blue-700',
    green: 'hover:bg-green-50 hover:border-green-300 text-green-700'
  }

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 p-4 rounded-xl bg-white border border-gray-200 transition-all shadow-sm ${colorClasses[color]}`}
    >
      <div className="flex-shrink-0">
        {icon}
      </div>
      <span className="text-sm font-normal text-gray-900">{text}</span>
    </button>
  )
}

interface ProgressBarProps {
  label: string
  value: number
  max: number
  color: 'purple' | 'green' | 'red' | 'blue'
}

const ProgressBar = ({ label, value, max, color }: ProgressBarProps) => {
  const percentage = max > 0 ? Math.round((value / max) * 100) : 0

  const colorClasses = {
    purple: 'bg-gradient-to-r from-purple-500 to-purple-600',
    green: 'bg-gradient-to-r from-green-500 to-green-600',
    red: 'bg-gradient-to-r from-red-500 to-red-600',
    blue: 'bg-gradient-to-r from-blue-500 to-blue-600'
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-gray-900 font-normal">{label}</span>
        <span className="text-xs text-gray-600">
          {value} / {max} ({percentage}%)
        </span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${colorClasses[color]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

const motivationalPhrases = [
  'Как насчет поработать сегодня? 💪',
  'Время создавать что-то крутое! 🚀',
  'Давайте покорим новые высоты! ⚡'
]

export const Dashboard = () => {
  const navigate = useNavigate()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [stats, setStats] = useState<DashboardStats>({
    projects: { total: 0, active: 0, completed: 0 },
    tasks: { total: 0, pending: 0, completed: 0 },
    clients: { total: 0, active: 0 },
    finance: { totalRevenue: 0, pending: 0, received: 0 }
  })
  const [loading, setLoading] = useState(true)
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPhraseIndex((prev) => (prev + 1) % motivationalPhrases.length)
    }, 8000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Check if user is authenticated
    const authString = localStorage.getItem('auth')
    if (!authString) {
      navigate('/login')
      return
    }

    fetchDashboardStats()

    // Обновляем данные при возврате на страницу/вкладку
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('🔄 Page visible again, refreshing dashboard...')
        fetchDashboardStats()
      }
    }

    const handleFocus = () => {
      console.log('🔄 Window focused, refreshing dashboard...')
      fetchDashboardStats()
    }

    // Слушаем кастомное событие обновления данных (когда создается/изменяется проект)
    const handleDataUpdate = () => {
      console.log('🔄 Data update event received, refreshing dashboard...')
      fetchDashboardStats()
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    window.addEventListener('focus', handleFocus)
    window.addEventListener('dashboardUpdate', handleDataUpdate)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      window.removeEventListener('focus', handleFocus)
      window.removeEventListener('dashboardUpdate', handleDataUpdate)
    }
  }, [])

  const fetchDashboardStats = async () => {
    try {
      setLoading(true)
      console.log('🔄 Fetching dashboard stats from new API...')

      // Используем новый endpoint /admin/api/dashboard/stats
      const response = await axiosInstance.get('/admin/api/dashboard/stats')

      if (response.data.success && response.data.data) {
        const data: DashboardData = response.data.data
        console.log('✅ Dashboard data fetched:', data)

        setDashboardData(data)

        // Преобразуем данные для старого формата stats (для совместимости с MagicBento)
        const projectsTotal = data.projects.length
        const projectsActive = data.projects.filter(p => p.status === 'in_progress').length
        const projectsCompleted = data.projects.filter(p => p.status === 'completed').length

        const tasksTotal =
          data.tasks.overdue.length +
          data.tasks.upcoming.length +
          data.tasks.new.length
        const tasksPending = data.tasks.overdue.length + data.tasks.upcoming.length

        const newStats = {
          projects: {
            total: projectsTotal,
            active: projectsActive,
            completed: projectsCompleted
          },
          tasks: {
            total: tasksTotal,
            pending: tasksPending,
            completed: 0 // Будем показывать из графиков если есть
          },
          clients: {
            total: data.clients.active_count + data.clients.new_leads_week,
            active: data.clients.active_count
          },
          finance: {
            totalRevenue: data.finance.month_revenue,
            pending: data.finance.pending,
            received: data.finance.paid
          }
        }

        console.log('📈 Setting stats:', newStats)
        setStats(newStats)
      }
    } catch (error) {
      console.error('❌ Error fetching dashboard stats:', error)
      // Axios interceptor will handle 401 redirects
    } finally {
      setLoading(false)
    }
  }

  const bentoCards: BentoCardProps[] = [
    {
      color: '#ffffff',
      title: loading ? 'Загрузка...' : `${stats.projects.total}`,
      description: loading ? 'Загрузка данных...' : `Активных: ${stats.projects.active} • Завершено: ${stats.projects.completed}`,
      label: 'Проекты',
      icon: <FolderKanban />,
      onClick: () => navigate('/projects')
    },
    {
      color: '#f8fafc',
      title: loading ? 'Загрузка...' : `${stats.tasks.total}`,
      description: loading ? 'Загрузка данных...' : `В работе: ${stats.tasks.pending} • Выполнено: ${stats.tasks.completed}`,
      label: 'Задачи',
      icon: <CheckSquare />,
      onClick: () => navigate('/tasks')
    },
    {
      color: '#ffffff',
      title: loading ? 'Загрузка...' : `${stats.clients.total}`,
      description: loading ? 'Загрузка данных...' : `Активных клиентов: ${stats.clients.active}`,
      label: 'Клиенты',
      icon: <Users />,
      onClick: () => navigate('/clients')
    },
    {
      color: '#ffffff',
      title: loading ? 'Загрузка...' : `${(stats.finance.totalRevenue / 1000).toFixed(0)}K ₽`,
      description: loading ? 'Загрузка данных...' : `Получено: ${(stats.finance.received / 1000).toFixed(0)}K • Ожидается: ${(stats.finance.pending / 1000).toFixed(0)}K`,
      label: 'Финансы',
      icon: <DollarSign />,
      onClick: () => navigate('/finance')
    },
    {
      color: '#f1f5f9',
      title: loading ? 'Загрузка...' : `${stats.projects.active}`,
      description: loading ? 'Загрузка данных...' : `Активных проектов требуют внимания`,
      label: 'Отчеты',
      icon: <TrendingUp />,
      onClick: () => navigate('/analytics')
    },
    {
      color: '#e2e8f0',
      title: loading ? 'Загрузка...' : `${stats.tasks.pending}`,
      description: loading ? 'Загрузка данных...' : `Задач в работе автоматизированы`,
      label: 'Настройки',
      icon: <Zap />,
      onClick: () => navigate('/automation')
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      {/* Header - Greeting */}
      <div className="mb-8">
        <div className="bg-white backdrop-blur-xl rounded-2xl p-12 border border-gray-200 shadow-lg min-h-[200px]">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-pulse text-gray-400 text-2xl">Загрузка...</div>
            </div>
          ) : dashboardData ? (
            <div className="space-y-4">
              <BlurText
                key={dashboardData.greeting.title}
                text={dashboardData.greeting.title}
                delay={80}
                direction="top"
                animateBy="words"
                className="text-4xl text-gray-900 font-normal text-center"
              />
              {/* Резюме по роли */}
              {dashboardData.summary && (
                <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
                  {dashboardData.summary.active_projects !== undefined && (
                    <div className="flex items-center gap-2">
                      <FolderKanban className="w-4 h-4 text-purple-600" />
                      <span>Активных проектов: <strong>{dashboardData.summary.active_projects}</strong></span>
                    </div>
                  )}
                  {dashboardData.summary.active_clients !== undefined && (
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-blue-600" />
                      <span>Активных клиентов: <strong>{dashboardData.summary.active_clients}</strong></span>
                    </div>
                  )}
                  {dashboardData.summary.month_revenue !== undefined && (
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <span>Доход за месяц: <strong>{dashboardData.summary.month_revenue.toLocaleString('ru-RU')} ₽</strong></span>
                    </div>
                  )}
                  {dashboardData.summary.projects_in_work !== undefined && (
                    <div className="flex items-center gap-2">
                      <FolderKanban className="w-4 h-4 text-purple-600" />
                      <span>Проектов в работе: <strong>{dashboardData.summary.projects_in_work}</strong></span>
                    </div>
                  )}
                  {dashboardData.summary.overdue_tasks !== undefined && (
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-600" />
                      <span>Просроченных задач: <strong>{dashboardData.summary.overdue_tasks}</strong></span>
                    </div>
                  )}
                  {dashboardData.summary.tasks_today !== undefined && (
                    <div className="flex items-center gap-2">
                      <CheckSquare className="w-4 h-4 text-blue-600" />
                      <span>Задач на сегодня: <strong>{dashboardData.summary.tasks_today}</strong></span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center">
              <BlurText
                key={currentPhraseIndex}
                text={motivationalPhrases[currentPhraseIndex]}
                delay={80}
                direction="top"
                animateBy="words"
                className="text-5xl text-gray-900 font-normal text-center"
              />
            </div>
          )}
        </div>
      </div>

      {/* MagicBento Grid */}
      <MagicBento
        textAutoHide={true}
        enableStars={true}
        enableSpotlight={true}
        enableBorderGlow={true}
        enableTilt={true}
        enableMagnetism={true}
        clickEffect={true}
        spotlightRadius={300}
        particleCount={12}
        glowColor="132, 0, 255"
        cards={bentoCards}
      />

      {/* Stats Cards - Финансы, Клиенты, Алерты, Документы */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Финансы */}
        <div
          onClick={() => navigate('/finance')}
          className="bg-gradient-to-br from-green-50 to-emerald-100 backdrop-blur-xl rounded-2xl p-6 border border-green-200 shadow-lg hover:shadow-xl transition-all cursor-pointer"
        >
          <div className="flex items-center gap-3 mb-3">
            <DollarSign className="w-6 h-6 text-green-600" />
            <span className="text-sm text-green-700 font-semibold">Финансы за месяц</span>
          </div>
          {dashboardData ? (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-600">Доход:</span>
                <span className="text-sm font-bold text-gray-900">
                  {dashboardData.finance.month_revenue.toLocaleString('ru-RU')} ₽
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-green-600">Оплачено:</span>
                <span className="text-sm font-medium text-green-700">
                  {dashboardData.finance.paid.toLocaleString('ru-RU')} ₽
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-yellow-600">Ожидается:</span>
                <span className="text-sm font-medium text-yellow-700">
                  {dashboardData.finance.pending.toLocaleString('ru-RU')} ₽
                </span>
              </div>
              {dashboardData.finance.overdue > 0 && (
                <div className="flex justify-between items-center">
                  <span className="text-xs text-red-600">Просрочено:</span>
                  <span className="text-sm font-medium text-red-700">
                    {dashboardData.finance.overdue.toLocaleString('ru-RU')} ₽
                  </span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xl font-normal text-gray-900">Загрузка...</p>
          )}
        </div>

        {/* Клиенты */}
        <div
          onClick={() => navigate('/clients')}
          className="bg-gradient-to-br from-blue-50 to-sky-100 backdrop-blur-xl rounded-2xl p-6 border border-blue-200 shadow-lg hover:shadow-xl transition-all cursor-pointer"
        >
          <div className="flex items-center gap-3 mb-3">
            <Users className="w-6 h-6 text-blue-600" />
            <span className="text-sm text-blue-700 font-semibold">Клиенты</span>
          </div>
          {dashboardData ? (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-600">Активных:</span>
                <span className="text-lg font-bold text-gray-900">{dashboardData.clients.active_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-blue-600">Новых лидов:</span>
                <span className="text-sm font-medium text-blue-700">{dashboardData.clients.new_leads_week}</span>
              </div>
              {dashboardData.clients.recent.length > 0 && (
                <div className="text-xs text-gray-500 mt-2">
                  Последний: {dashboardData.clients.recent[0].name}
                </div>
              )}
            </div>
          ) : (
            <p className="text-xl font-normal text-gray-900">Загрузка...</p>
          )}
        </div>

        {/* Требует внимания */}
        <div className="bg-gradient-to-br from-orange-50 to-red-100 backdrop-blur-xl rounded-2xl p-6 border border-orange-200 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <AlertCircle className="w-6 h-6 text-orange-600" />
            <span className="text-sm text-orange-700 font-semibold">Требует внимания</span>
          </div>
          {dashboardData && dashboardData.alerts.length > 0 ? (
            <div className="space-y-2">
              {dashboardData.alerts.slice(0, 3).map((alert, index) => (
                <div key={index} className="text-xs text-gray-700 flex items-start gap-2">
                  <span
                    className={`w-2 h-2 rounded-full mt-1 flex-shrink-0 ${
                      alert.level === 'error'
                        ? 'bg-red-500'
                        : alert.level === 'warning'
                        ? 'bg-yellow-500'
                        : 'bg-blue-500'
                    }`}
                  ></span>
                  <span className="line-clamp-2">{alert.message}</span>
                </div>
              ))}
              {dashboardData.alerts.length > 3 && (
                <div className="text-xs text-gray-500 mt-2">+{dashboardData.alerts.length - 3} еще</div>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500">Все в порядке ✓</p>
          )}
        </div>

        {/* Документы */}
        <div
          onClick={() => navigate('/documents')}
          className="bg-gradient-to-br from-purple-50 to-pink-100 backdrop-blur-xl rounded-2xl p-6 border border-purple-200 shadow-lg hover:shadow-xl transition-all cursor-pointer"
        >
          <div className="flex items-center gap-3 mb-3">
            <FileText className="w-6 h-6 text-purple-600" />
            <span className="text-sm text-purple-700 font-semibold">Документы</span>
          </div>
          {dashboardData && dashboardData.documents.length > 0 ? (
            <div className="space-y-2">
              {dashboardData.documents.slice(0, 3).map((doc) => (
                <div key={doc.id} className="text-xs text-gray-700">
                  <div className="font-medium truncate">{doc.filename}</div>
                  <div className="text-gray-500">
                    {doc.project_title ? `${doc.project_title}` : 'Без проекта'}
                  </div>
                </div>
              ))}
              {dashboardData.documents.length > 3 && (
                <div className="text-xs text-gray-500">+{dashboardData.documents.length - 3} еще</div>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500">Нет документов</p>
          )}
        </div>
      </div>

      {/* Content Grid - Recent Activity, Tasks, Projects */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Tasks */}
        <div className="lg:col-span-2 bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <CheckSquare className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-normal text-gray-900">Задачи</h2>
            </div>
            <button
              onClick={() => navigate('/tasks')}
              className="text-sm text-gray-400 hover:text-gray-900 transition-colors font-normal"
            >
              Все задачи →
            </button>
          </div>
          <div className="space-y-3">
            {loading ? (
              <div className="text-center py-8 text-gray-400">Загрузка...</div>
            ) : dashboardData ? (
              <>
                {/* Просроченные */}
                {dashboardData.tasks.overdue.length > 0 && (
                  <>
                    <div className="text-xs font-semibold text-red-600 uppercase mb-2">Просроченные ({dashboardData.tasks.overdue.length})</div>
                    {dashboardData.tasks.overdue.slice(0, 2).map((task) => (
                      <TaskItem
                        key={task.id}
                        title={task.title}
                        status="pending"
                        priority={task.priority as 'low' | 'medium' | 'high'}
                        deadline={new Date(task.deadline).toLocaleDateString('ru-RU')}
                      />
                    ))}
                  </>
                )}

                {/* Предстоящие */}
                {dashboardData.tasks.upcoming.length > 0 && (
                  <>
                    <div className="text-xs font-semibold text-blue-600 uppercase mb-2">Предстоящие ({dashboardData.tasks.upcoming.length})</div>
                    {dashboardData.tasks.upcoming.slice(0, 3).map((task) => (
                      <TaskItem
                        key={task.id}
                        title={task.title}
                        status="in_progress"
                        priority={task.priority as 'low' | 'medium' | 'high'}
                        deadline={new Date(task.deadline).toLocaleDateString('ru-RU')}
                      />
                    ))}
                  </>
                )}

                {/* Новые */}
                {dashboardData.tasks.new.length > 0 && (
                  <>
                    <div className="text-xs font-semibold text-green-600 uppercase mb-2">Новые задачи ({dashboardData.tasks.new.length})</div>
                    {dashboardData.tasks.new.slice(0, 1).map((task) => (
                      <TaskItem
                        key={task.id}
                        title={task.title}
                        status="pending"
                        priority={task.priority as 'low' | 'medium' | 'high'}
                        deadline={new Date(task.created_at).toLocaleDateString('ru-RU')}
                      />
                    ))}
                  </>
                )}

                {dashboardData.tasks.overdue.length === 0 &&
                  dashboardData.tasks.upcoming.length === 0 &&
                  dashboardData.tasks.new.length === 0 && (
                    <div className="text-center py-8 text-gray-400">Нет задач</div>
                  )}
              </>
            ) : (
              <div className="text-center py-8 text-gray-400">Нет данных</div>
            )}
          </div>
        </div>

        {/* Team Activity */}
        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <Activity className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-normal text-gray-900">Активность команды</h2>
          </div>
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-8 text-gray-400">Загрузка...</div>
            ) : dashboardData && dashboardData.activity.length > 0 ? (
              dashboardData.activity.map((activity, index) => {
                const colors: ('purple' | 'pink' | 'blue' | 'green')[] = ['purple', 'pink', 'blue', 'green']
                const color = colors[index % colors.length]
                const avatar = activity.user.charAt(0).toUpperCase()

                return (
                  <ActivityItem
                    key={index}
                    user={activity.user}
                    action={activity.action}
                    item={activity.target}
                    time={activity.timestamp}
                    avatar={avatar}
                    color={color}
                  />
                )
              })
            ) : (
              <div className="text-center py-8 text-gray-400">Нет активности</div>
            )}
          </div>
        </div>

        {/* Recent Projects */}
        <div className="lg:col-span-2 bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <FolderKanban className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-normal text-gray-900">Топ проектов</h2>
            </div>
            <button
              onClick={() => navigate('/projects')}
              className="text-sm text-gray-400 hover:text-gray-900 transition-colors font-normal"
            >
              Все проекты →
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {loading ? (
              <div className="col-span-2 text-center py-8 text-gray-400">Загрузка...</div>
            ) : dashboardData && dashboardData.projects.length > 0 ? (
              dashboardData.projects.map((project) => (
                <ProjectCard
                  key={project.id}
                  title={project.title}
                  client={project.client_name || 'Без клиента'}
                  progress={project.progress}
                  status={project.status as 'in_progress' | 'completed' | 'on_hold'}
                  deadline={project.deadline ? new Date(project.deadline).toLocaleDateString('ru-RU') : 'Не указан'}
                />
              ))
            ) : (
              <div className="col-span-2 text-center py-8 text-gray-400">Нет проектов</div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <Zap className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-normal text-gray-900">Быстрые действия</h2>
          </div>
          <div className="space-y-3">
            {loading ? (
              <div className="text-center py-8 text-gray-400">Загрузка...</div>
            ) : dashboardData && dashboardData.quick_actions.length > 0 ? (
              dashboardData.quick_actions.map((action, index) => {
                const colors: ('purple' | 'pink' | 'blue' | 'green')[] = ['purple', 'pink', 'blue', 'green']
                const color = colors[index % colors.length]
                const icons = {
                  tasks: <CheckSquare className="w-5 h-5" />,
                  projects: <FolderKanban className="w-5 h-5" />,
                  clients: <Users className="w-5 h-5" />,
                  documents: <FileText className="w-5 h-5" />,
                }
                const icon = icons[action.icon as keyof typeof icons] || <Zap className="w-5 h-5" />

                return (
                  <QuickActionButton
                    key={index}
                    icon={icon}
                    text={action.label}
                    onClick={() => navigate(action.link)}
                    color={color}
                  />
                )
              })
            ) : (
              <>
                <QuickActionButton
                  icon={<CheckSquare className="w-5 h-5" />}
                  text="Создать задачу"
                  onClick={() => navigate('/tasks')}
                  color="purple"
                />
                <QuickActionButton
                  icon={<FolderKanban className="w-5 h-5" />}
                  text="Новый проект"
                  onClick={() => navigate('/projects')}
                  color="pink"
                />
              </>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Stats - Charts Section - только для OWNER */}
      {dashboardData && dashboardData.user.role === 'owner' && dashboardData.charts && (
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Task Distribution Chart */}
          <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
            <div className="flex items-center gap-3 mb-6">
              <Activity className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-normal text-gray-900">Распределение задач</h2>
            </div>
            <div className="space-y-4">
              {Object.entries(dashboardData.charts.tasks_by_status).map(([status, count], index) => {
                const colors: ('purple' | 'green' | 'red' | 'blue')[] = ['purple', 'green', 'red', 'blue']
                const color = colors[index % colors.length]
                const labels: Record<string, string> = {
                  pending: 'Ожидает',
                  in_progress: 'В работе',
                  completed: 'Выполнено',
                  overdue: 'Просрочено',
                }
                const label = labels[status] || status

                return (
                  <ProgressBar
                    key={status}
                    label={label}
                    value={count}
                    max={stats.tasks.total}
                    color={color}
                  />
                )
              })}
            </div>
          </div>

          {/* Projects Distribution Chart */}
          <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-normal text-gray-900">Распределение проектов</h2>
            </div>
            <div className="space-y-4">
              {Object.entries(dashboardData.charts.projects_distribution).map(([status, count], index) => {
                const colors: ('purple' | 'green' | 'red' | 'blue')[] = ['blue', 'green', 'red', 'purple']
                const color = colors[index % colors.length]
                const labels: Record<string, string> = {
                  in_progress: 'В работе',
                  completed: 'Завершено',
                  on_hold: 'На паузе',
                  planning: 'Планирование',
                }
                const label = labels[status] || status

                return (
                  <ProgressBar
                    key={status}
                    label={label}
                    value={count}
                    max={stats.projects.total}
                    color={color}
                  />
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
