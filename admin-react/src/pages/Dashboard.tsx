import { useState, useEffect } from 'react'
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
  }, [])

  const fetchDashboardStats = async () => {
    try {
      setLoading(true)
      console.log('🔄 Fetching dashboard stats...')

      // Get auth credentials
      const authString = localStorage.getItem('auth')
      if (!authString) {
        navigate('/login')
        return
      }

      const { username, password } = JSON.parse(authString)
      const authHeader = `Basic ${btoa(`${username}:${password}`)}`

      // Fetch projects
      console.log('📊 Fetching projects from:', `${API_BASE_URL}/api/projects/?show_archived=false`)
      const projectsRes = await fetch(`${API_BASE_URL}/api/projects/?show_archived=false`, {
        headers: { 'Authorization': authHeader }
      })
      const projectsData = await projectsRes.json()
      const projects = projectsData.projects || []
      console.log('✅ Projects fetched:', projects.length, projects)

      // Fetch tasks
      console.log('📋 Fetching tasks from:', `${API_BASE_URL}/tasks/`)
      const tasksRes = await fetch(`${API_BASE_URL}/tasks/`, {
        headers: { 'Authorization': authHeader }
      })
      const tasksData = await tasksRes.json()
      const tasks = tasksData.tasks || []
      console.log('✅ Tasks fetched:', tasks.length, tasks)

      // Fetch clients
      console.log('👥 Fetching clients from:', `${API_BASE_URL}/api/clients/simple`)
      const clientsRes = await fetch(`${API_BASE_URL}/api/clients/simple`, {
        headers: { 'Authorization': authHeader }
      })
      const clientsData = await clientsRes.json()
      const clients = clientsData.clients || []
      console.log('✅ Clients fetched:', clients.length, clients)

      const newStats = {
        projects: {
          total: projects.length,
          active: projects.filter((p: any) => p.status === 'in_progress').length,
          completed: projects.filter((p: any) => p.status === 'completed').length
        },
        tasks: {
          total: tasks.length,
          pending: tasks.filter((t: any) => t.status === 'pending' || t.status === 'in_progress').length,
          completed: tasks.filter((t: any) => t.status === 'completed').length
        },
        clients: {
          total: clients.length,
          active: clients.filter((c: any) => c.is_active).length
        },
        finance: {
          totalRevenue: projects.reduce((sum: number, p: any) => sum + (p.project_cost || 0), 0),
          pending: projects.reduce((sum: number, p: any) => sum + ((p.project_cost || 0) - (p.paid_total || 0)), 0),
          received: projects.reduce((sum: number, p: any) => sum + (p.paid_total || 0), 0)
        }
      }

      console.log('📈 Setting stats:', newStats)
      setStats(newStats)
    } catch (error) {
      console.error('❌ Error fetching dashboard stats:', error)
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
      {/* Header */}
      <div className="mb-8">
        <div className="bg-white backdrop-blur-xl rounded-2xl p-12 border border-gray-200 shadow-lg flex items-center justify-center min-h-[200px]">
          <BlurText
            key={currentPhraseIndex}
            text={motivationalPhrases[currentPhraseIndex]}
            delay={80}
            direction="top"
            animateBy="words"
            className="text-5xl text-gray-900 font-normal text-center"
          />
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

      {/* Quick Stats Footer */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-purple-600" />
            <span className="text-sm text-gray-600 font-normal">Активность</span>
          </div>
          <p className="text-xl font-normal text-gray-900">Высокая</p>
        </div>

        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-blue-600" />
            <span className="text-sm text-gray-600 font-normal">Ближайший дедлайн</span>
          </div>
          <p className="text-xl font-normal text-gray-900">3 дня</p>
        </div>

        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <AlertCircle className="w-5 h-5 text-orange-600" />
            <span className="text-sm text-gray-600 font-normal">Требует внимания</span>
          </div>
          <p className="text-xl font-normal text-gray-900">{stats.tasks.pending}</p>
        </div>

        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="w-5 h-5 text-green-600" />
            <span className="text-sm text-gray-600 font-normal">Документы</span>
          </div>
          <p className="text-xl font-normal text-gray-900">Актуальны</p>
        </div>
      </div>

      {/* Content Grid - Recent Activity, Tasks, Projects */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Tasks */}
        <div className="lg:col-span-2 bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <CheckSquare className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-normal text-gray-900">Последние задачи</h2>
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
            ) : (
              <>
                <TaskItem
                  title="Доработка функционала CRM"
                  status="in_progress"
                  priority="high"
                  deadline="Сегодня"
                />
                <TaskItem
                  title="Оптимизация базы данных"
                  status="pending"
                  priority="medium"
                  deadline="Завтра"
                />
                <TaskItem
                  title="Тестирование новых функций"
                  status="in_progress"
                  priority="high"
                  deadline="2 дня"
                />
                <TaskItem
                  title="Написание документации"
                  status="pending"
                  priority="low"
                  deadline="Неделя"
                />
              </>
            )}
          </div>
        </div>

        {/* Team Activity */}
        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <Users className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-normal text-gray-900">Активность команды</h2>
          </div>
          <div className="space-y-4">
            <ActivityItem
              user="Алексей"
              action="завершил задачу"
              item="Дизайн главной страницы"
              time="5 мин назад"
              avatar="A"
              color="purple"
            />
            <ActivityItem
              user="Мария"
              action="создала проект"
              item="Интернет-магазин"
              time="1 час назад"
              avatar="M"
              color="pink"
            />
            <ActivityItem
              user="Дмитрий"
              action="обновил статус"
              item="Рефакторинг кода"
              time="2 часа назад"
              avatar="Д"
              color="blue"
            />
            <ActivityItem
              user="Екатерина"
              action="добавила комментарий"
              item="Баг в форме авторизации"
              time="3 часа назад"
              avatar="Е"
              color="green"
            />
          </div>
        </div>

        {/* Recent Projects */}
        <div className="lg:col-span-2 bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <FolderKanban className="w-5 h-5 text-purple-600" />
              <h2 className="text-xl font-normal text-gray-900">Активные проекты</h2>
            </div>
            <button
              onClick={() => navigate('/projects')}
              className="text-sm text-gray-400 hover:text-gray-900 transition-colors font-normal"
            >
              Все проекты →
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ProjectCard
              title="CRM Система"
              client="ООО Технологии"
              progress={75}
              status="in_progress"
              deadline="15 дней"
            />
            <ProjectCard
              title="Корпоративный сайт"
              client="ИП Иванов"
              progress={45}
              status="in_progress"
              deadline="30 дней"
            />
            <ProjectCard
              title="Мобильное приложение"
              client="Магазин Электроники"
              progress={90}
              status="in_progress"
              deadline="5 дней"
            />
            <ProjectCard
              title="Редизайн интерфейса"
              client="Финансовая компания"
              progress={20}
              status="in_progress"
              deadline="45 дней"
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <Zap className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-normal text-gray-900">Быстрые действия</h2>
          </div>
          <div className="space-y-3">
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
            <QuickActionButton
              icon={<Users className="w-5 h-5" />}
              text="Добавить клиента"
              onClick={() => navigate('/clients')}
              color="blue"
            />
            <QuickActionButton
              icon={<FileText className="w-5 h-5" />}
              text="Создать документ"
              onClick={() => navigate('/documents')}
              color="green"
            />
          </div>
        </div>
      </div>

      {/* Bottom Stats - Charts Section */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <TrendingUp className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-normal text-gray-900">Доход за месяц</h2>
          </div>
          <div className="h-64 flex items-end justify-between gap-2">
            {[65, 45, 80, 55, 90, 70, 85, 60, 95, 75, 88, 92].map((height, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div
                  className="w-full bg-white rounded-t-lg transition-all hover:bg-gray-300"
                  style={{ height: `${height}%` }}
                />
                <span className="text-xs text-gray-400">{i + 1}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Task Distribution */}
        <div className="bg-white backdrop-blur-xl rounded-2xl p-6 border border-gray-200 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <Activity className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-normal text-gray-900">Распределение задач</h2>
          </div>
          <div className="space-y-4">
            <ProgressBar label="В работе" value={stats.tasks.pending} max={stats.tasks.total} color="purple" />
            <ProgressBar label="Выполнено" value={stats.tasks.completed} max={stats.tasks.total} color="green" />
            <ProgressBar label="Просрочено" value={3} max={stats.tasks.total} color="red" />
            <ProgressBar label="На проверке" value={5} max={stats.tasks.total} color="blue" />
          </div>
        </div>
      </div>
    </div>
  )
}
